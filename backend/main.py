# Backend FastAPI cho ColdChain Dashboard
# File: backend/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sqlite3
import json
from datetime import datetime
import paho.mqtt.client as mqtt

# Khởi tạo FastAPI app
app = FastAPI(title="ColdChain Dashboard API", version="1.0.0")

# CORS - cho phép frontend gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong production nên giới hạn domain cụ thể
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lưu trạng thái thiết bị trong memory (có thể chuyển sang Redis sau)
device_states = {
    "NODE_01": "UNKNOWN"
}

# MQTT Configuration - TÙY CHỈNH theo broker của bạn
MQTT_BROKER = "localhost"  # Hoặc broker.hivemq.com nếu dùng public
MQTT_PORT = 1883
MQTT_TOPIC_CONTROL = "coldchain/device/{}/cmd"  # Topic gửi lệnh

# Kết nối MQTT client (để gửi lệnh điều khiển)
mqtt_client = mqtt.Client()
try:
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()
except:
    print("⚠️ Không kết nối được MQTT broker, chạy ở chế độ giới hạn")

# === DATABASE FUNCTIONS ===

def get_db_connection():
    """Kết nối đến SQLite database"""
    conn = sqlite3.connect("../database/iot_industrial.db")  # TÙY CHỈNH đường dẫn
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Khởi tạo database nếu chưa có"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tạo bảng measurements
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node_id TEXT NOT NULL,
            sensor_value REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            sensor_type TEXT DEFAULT 'temperature'
        )
    """)
    
    # Tạo bảng control_logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS control_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            command TEXT NOT NULL,
            param INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'sent'
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Database initialized")

# === MODELS ===

class ControlCommand(BaseModel):
    device_id: str
    command: str  # ON hoặc OFF
    param: Optional[int] = 100  # Công suất %

class StatusUpdate(BaseModel):
    status: str  # ON, OFF, UNKNOWN

# === API ENDPOINTS ===

@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "service": "ColdChain Dashboard API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/api/v1/history/{node_id}")
def get_history(node_id: str, limit: int = 20):
    """
    Lấy lịch sử nhiệt độ từ database
    - node_id: ID của thiết bị (ví dụ: NODE_01)
    - limit: số lượng bản ghi (mặc định 20)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query dữ liệu mới nhất, sắp xếp giảm dần theo thời gian
        cursor.execute("""
            SELECT sensor_value, timestamp
            FROM measurements
            WHERE node_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (node_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        # Chuyển đổi sang JSON và đảo ngược để vẽ chart từ cũ đến mới
        result = [
            {
                "value": row["sensor_value"],
                "time": row["timestamp"]
            }
            for row in rows
        ]
        
        # Đảo ngược để chart vẽ từ trái (cũ) sang phải (mới)
        result.reverse()
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/ingest")
def ingest_data(node_id: str, value: float):
    """
    Endpoint để nhận dữ liệu từ thiết bị (nếu không dùng MQTT)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO measurements (node_id, sensor_value)
            VALUES (?, ?)
        """, (node_id, value))
        
        conn.commit()
        conn.close()
        
        return {"status": "success", "node_id": node_id, "value": value}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/control/device")
def control_device(cmd: ControlCommand):
    """
    Gửi lệnh điều khiển thiết bị qua MQTT
    """
    try:
        # Tạo payload JSON
        payload = {
            "command": cmd.command,
            "param": cmd.param,
            "timestamp": datetime.now().isoformat()
        }
        
        # Gửi lệnh qua MQTT
        topic = MQTT_TOPIC_CONTROL.format(cmd.device_id)
        mqtt_client.publish(topic, json.dumps(payload))
        
        # Lưu log điều khiển vào database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO control_logs (device_id, command, param)
            VALUES (?, ?, ?)
        """, (cmd.device_id, cmd.command, cmd.param))
        conn.commit()
        conn.close()
        
        print(f"📤 Sent command {cmd.command} to {cmd.device_id}")
        
        return {
            "status": "sent",
            "device_id": cmd.device_id,
            "command": cmd.command,
            "topic": topic
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/device/{device_id}/status")
def get_device_status(device_id: str):
    """
    Lấy trạng thái hiện tại của thiết bị
    """
    status = device_states.get(device_id, "UNKNOWN")
    return {"device_id": device_id, "status": status}

@app.post("/api/v1/device/{device_id}/status")
def update_device_status(device_id: str, status: str):
    """
    Cập nhật trạng thái thiết bị (được gọi từ MQTT worker)
    """
    device_states[device_id] = status
    print(f"🔄 Updated {device_id} status to {status}")
    return {"device_id": device_id, "status": status, "message": "Updated"}

# === STARTUP ===

@app.on_event("startup")
def startup_event():
    """Khởi tạo khi start server"""
    print("🚀 Starting ColdChain Dashboard API...")
    init_database()
    print("✅ Server ready on http://localhost:8000")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)