# MQTT Worker - Nhận dữ liệu từ thiết bị và ghi vào database
# File: worker/mqtt_worker.py

import paho.mqtt.client as mqtt
import json
import sqlite3
import requests
from datetime import datetime

# === CONFIGURATION - TÙY CHỈNH ===

MQTT_BROKER = "localhost"  # Địa chỉ MQTT broker
MQTT_PORT = 1883
MQTT_USERNAME = None  # Nếu broker cần authentication
MQTT_PASSWORD = None

# Topics để subscribe
TOPIC_DATA = "coldchain/sensor/+/data"     # Nhận dữ liệu nhiệt độ
TOPIC_STATUS = "coldchain/device/+/stat"   # Nhận trạng thái thiết bị

# Backend API URL
API_BASE_URL = "http://localhost:8000/api/v1"

# Database path
DB_PATH = "../database/iot_industrial.db"  # TÙY CHỈNH đường dẫn

# === DATABASE FUNCTIONS ===

def get_db_connection():
    """Kết nối database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def save_measurement(node_id: str, value: float):
    """Lưu dữ liệu nhiệt độ vào database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO measurements (node_id, sensor_value)
            VALUES (?, ?)
        """, (node_id, value))
        
        conn.commit()
        conn.close()
        print(f"💾 Saved: {node_id} = {value}°C")
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def update_device_status_api(device_id: str, status: str):
    """Cập nhật trạng thái thiết bị qua Backend API"""
    try:
        url = f"{API_BASE_URL}/device/{device_id}/status"
        params = {"status": status}
        response = requests.post(url, params=params, timeout=5)
        
        if response.status_code == 200:
            print(f"✅ Updated {device_id} status to {status}")
            return True
        else:
            print(f"⚠️ Failed to update status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API error: {e}")
        return False

# === MQTT CALLBACKS ===

def on_connect(client, userdata, flags, rc):
    """Callback khi kết nối MQTT thành công"""
    if rc == 0:
        print("✅ Connected to MQTT Broker!")
        
        # Subscribe các topics
        client.subscribe(TOPIC_DATA)
        print(f"📡 Subscribed to {TOPIC_DATA}")
        
        client.subscribe(TOPIC_STATUS)
        print(f"📡 Subscribed to {TOPIC_STATUS}")
        
    else:
        print(f"❌ Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    """Callback khi nhận được message từ MQTT"""
    topic = msg.topic
    payload = msg.payload.decode()
    
    print(f"\n📬 Received: {topic}")
    print(f"   Payload: {payload}")
    
    try:
        # Xử lý dữ liệu nhiệt độ
        if "/data" in topic:
            handle_sensor_data(topic, payload)
        
        # Xử lý trạng thái thiết bị
        elif "/stat" in topic:
            handle_device_status(topic, payload)
            
    except Exception as e:
        print(f"❌ Error processing message: {e}")

def handle_sensor_data(topic: str, payload: str):
    """
    Xử lý dữ liệu từ cảm biến nhiệt độ
    Topic format: coldchain/sensor/NODE_01/data
    Payload: {"temperature": 5.2, "humidity": 65}
    """
    # Parse topic để lấy node_id
    parts = topic.split("/")
    if len(parts) >= 3:
        node_id = parts[2]  # NODE_01
    else:
        print("⚠️ Invalid topic format")
        return
    
    # Parse JSON payload
    try:
        data = json.loads(payload)
        temperature = data.get("temperature")
        
        if temperature is not None:
            # Lưu vào database
            save_measurement(node_id, temperature)
        else:
            print("⚠️ No temperature field in payload")
            
    except json.JSONDecodeError:
        # Nếu payload là số thuần (không phải JSON)
        try:
            temperature = float(payload)
            save_measurement(node_id, temperature)
        except ValueError:
            print(f"⚠️ Invalid payload format: {payload}")

def handle_device_status(topic: str, payload: str):
    """
    Xử lý trạng thái thiết bị
    Topic format: coldchain/device/NODE_01/stat
    Payload: "ON" hoặc "OFF"
    """
    # Parse topic để lấy device_id
    parts = topic.split("/")
    if len(parts) >= 3:
        device_id = parts[2]  # NODE_01
    else:
        print("⚠️ Invalid topic format")
        return
    
    # Cập nhật trạng thái qua API
    status = payload.strip().upper()
    if status in ["ON", "OFF"]:
        update_device_status_api(device_id, status)
    else:
        print(f"⚠️ Invalid status: {status}")

def on_disconnect(client, userdata, rc):
    """Callback khi mất kết nối"""
    if rc != 0:
        print(f"⚠️ Unexpected disconnection. Return code: {rc}")
        print("🔄 Attempting to reconnect...")

# === MAIN ===

def main():
    """Khởi động MQTT Worker"""
    print("=" * 50)
    print("🚀 Starting MQTT Worker for ColdChain Dashboard")
    print("=" * 50)
    
    # Tạo MQTT client
    client = mqtt.Client(client_id="coldchain_worker")
    
    # Set username/password nếu cần
    if MQTT_USERNAME and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    
    # Gán callbacks
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    
    # Kết nối đến broker
    try:
        print(f"🔌 Connecting to MQTT Broker at {MQTT_BROKER}:{MQTT_PORT}...")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        
        # Bắt đầu loop (blocking)
        print("👂 Listening for messages... (Press Ctrl+C to stop)")
        client.loop_forever()
        
    except KeyboardInterrupt:
        print("\n⏹️ Worker stopped by user")
        client.disconnect()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()