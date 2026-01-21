"""
Vaccine Cold Chain Monitoring - FastAPI Server
Dashboard realtime + API điều khiển + WebSocket broadcast
"""

import asyncio
import json
from typing import Set, Optional
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from mqtt_client import (
    start_mqtt, stop_mqtt, 
    set_on_telemetry_callback, set_on_batch_callback, set_on_status_callback,
    publish_command, is_connected
)
from database import (
    init_db, 
    get_all_devices, get_device, add_device,
    save_telemetry, save_batch_telemetry, get_recent_telemetry, get_telemetry_stats, get_latest_telemetry,
    create_alert, get_active_alerts, acknowledge_alert,
    save_command, get_command_history
)

# ==================== APP CONFIG ====================
app = FastAPI(
    title="Vaccine Cold Chain Monitoring",
    description="Hệ thống giám sát kho lạnh vắc-xin thông minh",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# WebSocket clients
clients: Set[WebSocket] = set()
_loop: Optional[asyncio.AbstractEventLoop] = None

# Ngưỡng cảnh báo
# Ngưỡng nhiệt độ phòng thực tế
TEMP_MIN = 20.0
TEMP_MAX = 30.0
TEMP_ALARM = 35.0


# ==================== PYDANTIC MODELS ====================

class CommandRequest(BaseModel):
    command: str  # TURN_ON_BACKUP_COOLER, RESET_ALARM, etc.
    device_id: Optional[int] = None


class BatchDataRequest(BaseModel):
    gateway_id: int
    data: list
    batch_time: Optional[int] = None
    count: Optional[int] = None


class DeviceCreate(BaseModel):
    device_id: int
    name: str
    location: Optional[str] = None


# ==================== WEBSOCKET BROADCAST ====================

async def broadcast_json(obj: dict):
    """Gửi dữ liệu đến tất cả WebSocket clients"""
    dead = []
    msg = json.dumps(obj, ensure_ascii=False, default=str)
    
    for ws in list(clients):
        try:
            await ws.send_text(msg)
        except Exception:
            dead.append(ws)
    
    for ws in dead:
        clients.discard(ws)


# ==================== MQTT CALLBACKS ====================

def on_telemetry(data: dict):
    """Xử lý dữ liệu telemetry từ Gateway"""
    device_id = data.get("device_id", 0)
    temperature = data.get("temperature", 0)
    humidity = data.get("humidity")
    alarm_state = data.get("alarm_state", False)
    cooler_state = data.get("cooler_state", False)
    gateway_id = data.get("gateway_id")
    
    # Lưu vào database
    save_telemetry(
        device_id=device_id,
        temperature=temperature,
        humidity=humidity,
        alarm_state=alarm_state,
        cooler_state=cooler_state,
        gateway_id=gateway_id
    )
    
    # Kiểm tra cảnh báo
    if temperature > TEMP_MAX:
        create_alert(
            device_id=device_id,
            alert_type="OVER_TEMP",
            temperature=temperature,
            message=f"Nhiệt độ vượt ngưỡng: {temperature}°C > {TEMP_MAX}°C"
        )
    elif temperature < TEMP_MIN:
        create_alert(
            device_id=device_id,
            alert_type="UNDER_TEMP",
            temperature=temperature,
            message=f"Nhiệt độ thấp: {temperature}°C < {TEMP_MIN}°C"
        )
    
    # Broadcast qua WebSocket
    if _loop:
        ws_data = {
            "type": "telemetry",
            "device_id": device_id,
            "temperature": temperature,
            "humidity": humidity,
            "alarm_state": alarm_state,
            "cooler_state": cooler_state,
            "timestamp": datetime.now().isoformat()
        }
        asyncio.run_coroutine_threadsafe(broadcast_json(ws_data), _loop)


def on_batch(data: dict):
    """Xử lý batch data từ Gateway (Store & Forward)"""
    gateway_id = data.get("gateway_id", 0)
    batch_data = data.get("data", [])
    count = data.get("count", len(batch_data))
    
    print(f"[BATCH] Nhận {count} mẫu từ Gateway {gateway_id}")
    
    # Lưu batch vào database
    saved = save_batch_telemetry(gateway_id, batch_data)
    
    # Broadcast thông báo
    if _loop:
        ws_data = {
            "type": "batch_received",
            "gateway_id": gateway_id,
            "count": saved,
            "timestamp": datetime.now().isoformat()
        }
        asyncio.run_coroutine_threadsafe(broadcast_json(ws_data), _loop)


def on_status(data: dict):
    """Xử lý trạng thái từ Node (phản hồi lệnh)"""
    node_id = data.get("node_id", 0)
    status = data.get("status", "")
    
    print(f"[STATUS] Node {node_id}: {status}")
    
    # Broadcast qua WebSocket để Dashboard cập nhật
    if _loop:
        ws_data = {
            "type": "status",
            "node_id": node_id,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        asyncio.run_coroutine_threadsafe(broadcast_json(ws_data), _loop)


# ==================== LIFECYCLE EVENTS ====================

@app.on_event("startup")
async def on_startup():
    global _loop
    _loop = asyncio.get_running_loop()
    
    # Khởi tạo database
    init_db()
    
    # Đăng ký callbacks
    set_on_telemetry_callback(on_telemetry)
    set_on_batch_callback(on_batch)
    set_on_status_callback(on_status)
    
    # Khởi động MQTT
    try:
        start_mqtt()
    except Exception as e:
        print(f"[WARNING] MQTT connection failed: {e}")


@app.on_event("shutdown")
async def on_shutdown():
    stop_mqtt()


# ==================== WEB ROUTES ====================

@app.get("/", response_class=HTMLResponse)
def index():
    """Trang Dashboard chính"""
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    """WebSocket endpoint cho realtime updates"""
    await ws.accept()
    clients.add(ws)
    
    try:
        await ws.send_text(json.dumps({
            "type": "connected",
            "message": "WebSocket connected",
            "timestamp": datetime.now().isoformat()
        }))
        
        while True:
            # Keep alive
            data = await ws.receive_text()
            
            # Có thể xử lý lệnh từ client ở đây
            if data.startswith("ping"):
                await ws.send_text(json.dumps({"type": "pong"}))
                
    except WebSocketDisconnect:
        clients.discard(ws)
    except Exception:
        clients.discard(ws)


# ==================== API ROUTES - DEVICES ====================

@app.get("/api/devices")
def api_get_devices():
    """Lấy danh sách thiết bị"""
    devices = get_all_devices()
    return {"devices": devices}


@app.get("/api/devices/{device_id}")
def api_get_device(device_id: int):
    """Lấy thông tin một thiết bị"""
    device = get_device(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@app.post("/api/devices")
def api_create_device(body: DeviceCreate):
    """Thêm thiết bị mới"""
    success = add_device(body.device_id, body.name, body.location)
    if not success:
        raise HTTPException(status_code=400, detail="Device already exists")
    return {"ok": True, "device_id": body.device_id}


# ==================== API ROUTES - TELEMETRY ====================

@app.get("/api/telemetry")
def api_get_telemetry(
    device_id: Optional[int] = Query(None),
    limit: int = Query(100, ge=1, le=1000)
):
    """Lấy dữ liệu telemetry"""
    data = get_recent_telemetry(device_id=device_id, limit=limit)
    return {"count": len(data), "data": data}


@app.get("/api/telemetry/latest/{device_id}")
def api_get_latest(device_id: int):
    """Lấy dữ liệu mới nhất của thiết bị"""
    data = get_latest_telemetry(device_id)
    if not data:
        raise HTTPException(status_code=404, detail="No data found")
    return data


@app.get("/api/telemetry/stats/{device_id}")
def api_get_stats(device_id: int):
    """Lấy thống kê của thiết bị"""
    return get_telemetry_stats(device_id)


@app.post("/api/batch")
def api_receive_batch(body: BatchDataRequest):
    """
    API nhận batch data từ Gateway (50 mẫu/lần)
    Tách ra và lưu đúng thời gian đo thực tế
    """
    count = save_batch_telemetry(body.gateway_id, body.data)
    return {"ok": True, "saved": count}


# ==================== API ROUTES - COMMANDS ====================

@app.post("/api/command/{gateway_id}")
def api_send_command(gateway_id: int, body: CommandRequest):
    """
    Gửi lệnh điều khiển đến Gateway
    
    Commands:
    - TURN_ON_BACKUP_COOLER
    - TURN_OFF_BACKUP_COOLER
    - RESET_ALARM
    """
    command = body.command.strip().upper()
    
    # Lưu lệnh vào database
    cmd_id = save_command(
        device_id=body.device_id or 0,
        command=command,
        gateway_id=gateway_id
    )
    
    # Gửi qua MQTT
    success = publish_command(
        gateway_id=gateway_id,
        command=command,
        device_id=body.device_id
    )
    
    if not success:
        return {"ok": False, "error": "MQTT not connected", "cmd_id": cmd_id}
    
    return {"ok": True, "cmd_id": cmd_id, "command": command, "gateway_id": gateway_id}


@app.get("/api/commands")
def api_get_commands(device_id: Optional[int] = None, limit: int = 50):
    """Lấy lịch sử lệnh"""
    data = get_command_history(device_id=device_id, limit=limit)
    return {"count": len(data), "data": data}


# ==================== API ROUTES - ALERTS ====================

@app.get("/api/alerts")
def api_get_alerts():
    """Lấy danh sách cảnh báo chưa xử lý"""
    alerts = get_active_alerts()
    return {"count": len(alerts), "alerts": alerts}


@app.post("/api/alerts/{alert_id}/acknowledge")
def api_acknowledge_alert(alert_id: int):
    """Xác nhận đã xử lý cảnh báo"""
    success = acknowledge_alert(alert_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"ok": True}


# ==================== API ROUTES - STATUS ====================

@app.get("/api/status")
def api_status():
    """Trạng thái hệ thống"""
    return {
        "mqtt_connected": is_connected(),
        "websocket_clients": len(clients),
        "timestamp": datetime.now().isoformat()
    }


# ==================== MAIN ====================

if __name__ == "__main__":
    import uvicorn
    
    print()
    print("╔════════════════════════════════════════════════════════╗")
    print("║    VACCINE COLD CHAIN MONITORING SYSTEM                ║")
    print("║    Backend Server v1.0                                 ║")
    print("╠════════════════════════════════════════════════════════╣")
    print("║  🌐 Dashboard: http://127.0.0.1:8000                   ║")
    print("║  📖 API Docs:  http://127.0.0.1:8000/docs              ║")
    print("║  📊 WebSocket: ws://127.0.0.1:8000/ws                  ║")
    print("╚════════════════════════════════════════════════════════╝")
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
