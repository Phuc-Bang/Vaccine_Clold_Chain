"""
Vaccine Cold Chain Monitoring - MQTT Client Module
Kết nối với MQTT Broker, nhận dữ liệu từ Gateway, gửi lệnh điều khiển
"""

import json
import threading
from typing import Callable, Optional, Dict
from datetime import datetime

import paho.mqtt.client as mqtt

# ==================== MQTT CONFIG ====================
# Connect to SAME broker as Gateway (192.168.99.85)
BROKER = "192.168.99.85"
PORT = 1883
KEEPALIVE = 60

# Topics
TOPIC_TELEMETRY_SUB = "vaccine/gateway/+/telemetry"    # Dữ liệu đơn
TOPIC_BATCH_SUB = "vaccine/gateway/+/batch"            # Dữ liệu batch
TOPIC_STATUS_SUB = "vaccine/node/+/status"             # Trạng thái node
TOPIC_COMMAND_PUB = "vaccine/gateway/{gateway_id}/command"  # Gửi lệnh

# ==================== GLOBAL VARIABLES ====================
_client_lock = threading.Lock()
_client: Optional[mqtt.Client] = None

# Callbacks
_on_telemetry_callback: Optional[Callable[[Dict], None]] = None
_on_batch_callback: Optional[Callable[[Dict], None]] = None
_on_status_callback: Optional[Callable[[Dict], None]] = None


# ==================== CALLBACK SETTERS ====================

def set_on_telemetry_callback(cb: Callable[[Dict], None]):
    """Callback nhận dữ liệu telemetry đơn"""
    global _on_telemetry_callback
    _on_telemetry_callback = cb


def set_on_batch_callback(cb: Callable[[Dict], None]):
    """Callback nhận dữ liệu batch"""
    global _on_batch_callback
    _on_batch_callback = cb


def set_on_status_callback(cb: Callable[[Dict], None]):
    """Callback nhận trạng thái node"""
    global _on_status_callback
    _on_status_callback = cb


# ==================== MQTT CALLBACKS ====================

def _on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("[MQTT] Connected to broker")
        
        # Subscribe tất cả topics
        client.subscribe(TOPIC_TELEMETRY_SUB)
        client.subscribe(TOPIC_BATCH_SUB)
        client.subscribe(TOPIC_STATUS_SUB)
        
        print(f"[MQTT] Subscribed: {TOPIC_TELEMETRY_SUB}")
        print(f"[MQTT] Subscribed: {TOPIC_BATCH_SUB}")
        print(f"[MQTT] Subscribed: {TOPIC_STATUS_SUB}")
    else:
        print(f"[MQTT] Connect failed, rc={rc}")


def _on_message(client, userdata, msg):
    try:
        topic = msg.topic
        payload = msg.payload.decode("utf-8", errors="replace").strip()
        
        print(f"\n[MQTT] Received on: {topic}")
        
        # Parse topic để lấy gateway/node ID
        parts = topic.split("/")
        
        # vaccine/gateway/<id>/telemetry
        if "telemetry" in topic and len(parts) >= 4:
            gateway_id = int(parts[2])
            data = json.loads(payload)
            data["gateway_id"] = gateway_id
            data["received_at"] = datetime.now().isoformat()
            
            print(f"[MQTT] Telemetry from Gateway {gateway_id}: {data.get('temperature', 'N/A')}°C")
            
            if _on_telemetry_callback:
                _on_telemetry_callback(data)
        
        # vaccine/gateway/<id>/batch
        elif "batch" in topic and len(parts) >= 4:
            gateway_id = int(parts[2])
            data = json.loads(payload)
            data["gateway_id"] = gateway_id
            data["received_at"] = datetime.now().isoformat()
            
            count = data.get("count", len(data.get("data", [])))
            print(f"[MQTT] Batch from Gateway {gateway_id}: {count} records")
            
            if _on_batch_callback:
                _on_batch_callback(data)
        
        # vaccine/node/<id>/status
        elif "status" in topic and len(parts) >= 4:
            node_id = int(parts[2])
            data = {"node_id": node_id, "status": payload}
            
            print(f"[MQTT] Status from Node {node_id}: {payload}")
            
            if _on_status_callback:
                _on_status_callback(data)
        
        else:
            print(f"[MQTT] Unknown topic: {topic}")
            print(f"[MQTT] Payload: {payload[:200]}")
            
    except json.JSONDecodeError as e:
        print(f"[MQTT] JSON parse error: {e}")
    except Exception as e:
        print(f"[MQTT] Error: {e}")


def _on_disconnect(client, userdata, rc):
    if rc != 0:
        print(f"[MQTT] Unexpected disconnect, rc={rc}")


# ==================== CLIENT FUNCTIONS ====================

def start_mqtt() -> mqtt.Client:
    """Khởi động MQTT client"""
    global _client
    
    with _client_lock:
        if _client is not None:
            return _client
        
        print(f"[MQTT] Connecting to {BROKER}:{PORT}")
        
        c = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        c.on_connect = _on_connect
        c.on_message = _on_message
        c.on_disconnect = _on_disconnect
        
        try:
            c.connect(BROKER, PORT, KEEPALIVE)
            c.loop_start()
            _client = c
            print("[MQTT] Client started")
        except Exception as e:
            print(f"[MQTT] Connection error: {e}")
            raise
        
        return c


def stop_mqtt():
    """Dừng MQTT client"""
    global _client
    
    with _client_lock:
        if _client is None:
            return
        
        _client.loop_stop()
        _client.disconnect()
        _client = None
        print("[MQTT] Client stopped")


def publish_command(gateway_id: int, command: str, device_id: int = None) -> bool:
    """
    Gửi lệnh điều khiển đến Gateway
    
    Commands:
    - TURN_ON_BACKUP_COOLER: Bật máy lạnh dự phòng
    - TURN_OFF_BACKUP_COOLER: Tắt máy lạnh dự phòng
    - RESET_ALARM: Reset còi hú
    """
    global _client
    
    if _client is None:
        start_mqtt()
    
    if _client is None:
        print("[MQTT] Cannot publish, client not connected")
        return False
    
    topic = TOPIC_COMMAND_PUB.format(gateway_id=gateway_id)
    
    # Tạo payload JSON
    payload = {
        "command": command,
        "device_id": device_id or 0,
        "timestamp": datetime.now().isoformat()
    }
    
    message = json.dumps(payload)
    
    try:
        info = _client.publish(topic, message, qos=1, retain=False)
        info.wait_for_publish(timeout=5)
        
        print(f"[MQTT] Published to {topic}: {command}")
        return True
        
    except Exception as e:
        print(f"[MQTT] Publish error: {e}")
        return False


def is_connected() -> bool:
    """Kiểm tra trạng thái kết nối"""
    return _client is not None and _client.is_connected()
