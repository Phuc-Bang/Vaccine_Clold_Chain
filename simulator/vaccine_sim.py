# Simulator - Giả lập kho lạnh vắc-xin
# File: simulator/vaccine_sim.py

import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime

# === CONFIGURATION ===

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
DEVICE_ID = "NODE_01"

# Topics
TOPIC_DATA = f"coldchain/sensor/{DEVICE_ID}/data"      # Gửi dữ liệu nhiệt độ
TOPIC_CMD = f"coldchain/device/{DEVICE_ID}/cmd"        # Nhận lệnh điều khiển
TOPIC_STAT = f"coldchain/device/{DEVICE_ID}/stat"      # Gửi trạng thái thiết bị

# Trạng thái thiết bị
device_state = {
    "cooler_on": False,      # Máy lạnh bật/tắt
    "target_temp": 4.0,      # Nhiệt độ mục tiêu (°C)
    "current_temp": 6.0,     # Nhiệt độ hiện tại
    "power_level": 100       # Công suất máy lạnh (%)
}

# === MQTT CALLBACKS ===

def on_connect(client, userdata, flags, rc):
    """Callback khi kết nối thành công"""
    if rc == 0:
        print(f"✅ Simulator {DEVICE_ID} connected to broker")
        client.subscribe(TOPIC_CMD)
        print(f"📡 Subscribed to {TOPIC_CMD}")
    else:
        print(f"❌ Connection failed with code {rc}")

def on_message(client, userdata, msg):
    """Callback khi nhận lệnh điều khiển"""
    try:
        payload = json.loads(msg.payload.decode())
        command = payload.get("command")
        param = payload.get("param", 100)
        
        print(f"\n📬 Received command: {command} (power: {param}%)")
        
        # Giả lập độ trễ xử lý lệnh (2 giây)
        print("⏳ Processing command...")
        time.sleep(2)
        
        # Xử lý lệnh
        if command == "ON":
            device_state["cooler_on"] = True
            device_state["power_level"] = param
            status = "ON"
            print("❄️ Cooler turned ON")
            
        elif command == "OFF":
            device_state["cooler_on"] = False
            status = "OFF"
            print("🔥 Cooler turned OFF")
        else:
            print(f"⚠️ Unknown command: {command}")
            return
        
        # Gửi trạng thái xác nhận
        client.publish(TOPIC_STAT, status)
        print(f"✅ Status published: {status}")
        
    except Exception as e:
        print(f"❌ Error processing command: {e}")

# === SIMULATION LOGIC ===

def simulate_temperature():
    """
    Mô phỏng nhiệt độ kho lạnh:
    - Nếu máy lạnh BẬT: nhiệt độ giảm dần về target
    - Nếu máy lạnh TẮT: nhiệt độ tăng dần (môi trường ấm hơn)
    - Thêm nhiễu ngẫu nhiên để mô phỏng thực tế
    """
    current = device_state["current_temp"]
    target = device_state["target_temp"]
    
    if device_state["cooler_on"]:
        # Máy lạnh bật: nhiệt độ giảm về target
        power_factor = device_state["power_level"] / 100.0
        delta = (target - current) * 0.1 * power_factor  # Giảm 10% mỗi lần
        
    else:
        # Máy lạnh tắt: nhiệt độ tăng lên (môi trường ~20°C)
        ambient_temp = 20.0
        delta = (ambient_temp - current) * 0.05  # Tăng 5% mỗi lần
    
    # Thêm nhiễu ngẫu nhiên (±0.2°C)
    noise = random.uniform(-0.2, 0.2)
    
    # Cập nhật nhiệt độ
    new_temp = current + delta + noise
    
    # Giới hạn nhiệt độ trong khoảng hợp lý (0-25°C)
    new_temp = max(0.0, min(25.0, new_temp))
    
    device_state["current_temp"] = round(new_temp, 2)
    
    return device_state["current_temp"]

def generate_spike():
    """
    Đôi khi tạo spike nhiễu để test bộ lọc
    (1% cơ hội mỗi lần đọc)
    """
    if random.random() < 0.01:  # 1% chance
        spike = random.uniform(15, 30)  # Spike cao
        print(f"⚡ SPIKE: {spike}°C")
        return spike
    return None

# === MAIN LOOP ===

def main():
    """Chạy simulator"""
    print("=" * 60)
    print(f"🧊 ColdChain Vaccine Simulator - Device: {DEVICE_ID}")
    print("=" * 60)
    
    # Tạo MQTT client
    client = mqtt.Client(client_id=f"simulator_{DEVICE_ID}")
    client.on_connect = on_connect
    client.on_message = on_message
    
    # Kết nối
    try:
        print(f"🔌 Connecting to broker {MQTT_BROKER}:{MQTT_PORT}...")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
        
        print("🚀 Simulator started. Sending data every 3 seconds...")
        print("📊 Initial state:")
        print(f"   Temperature: {device_state['current_temp']}°C")
        print(f"   Cooler: {'ON' if device_state['cooler_on'] else 'OFF'}")
        print("\n👂 Listening for commands... (Ctrl+C to stop)\n")
        
        # Loop vô hạn gửi dữ liệu
        while True:
            # Kiểm tra spike (để test bộ lọc)
            spike = generate_spike()
            
            if spike:
                temperature = spike
            else:
                # Mô phỏng nhiệt độ bình thường
                temperature = simulate_temperature()
            
            # Tạo payload
            payload = {
                "temperature": temperature,
                "humidity": random.randint(60, 80),  # Độ ẩm ngẫu nhiên
                "cooler_status": "ON" if device_state["cooler_on"] else "OFF",
                "timestamp": datetime.now().isoformat()
            }
            
            # Publish dữ liệu
            client.publish(TOPIC_DATA, json.dumps(payload))
            
            # In log
            status_icon = "❄️" if device_state["cooler_on"] else "🔥"
            print(f"{status_icon} Temp: {temperature:6.2f}°C | "
                  f"Cooler: {'ON ' if device_state['cooler_on'] else 'OFF'} | "
                  f"Time: {datetime.now().strftime('%H:%M:%S')}")
            
            # Đợi 3 giây
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\n⏹️ Simulator stopped by user")
        client.loop_stop()
        client.disconnect()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()