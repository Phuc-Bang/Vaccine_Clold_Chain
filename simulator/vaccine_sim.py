import json
import os
import random
import threading
import time
from datetime import datetime

import paho.mqtt.client as mqtt

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC_BASE = os.getenv("MQTT_TOPIC_BASE", "coldchain/device")

DEVICE_ID = os.getenv("DEVICE_ID", "NODE_01")

state = {
    "device_on": False,
    "current_temp": 8.5,
}


def publish_status(client, status: str):
    topic = f"{MQTT_TOPIC_BASE}/{DEVICE_ID}/stat"
    client.publish(topic, json.dumps({"status": status}))


def apply_command(client, command: str):
    # Giả lập độ trễ thiết bị 2s rồi mới phản hồi trạng thái
    def delayed_update():
        if command == "ON":
            state["device_on"] = True
            publish_status(client, "ON")
        elif command == "OFF":
            state["device_on"] = False
            publish_status(client, "OFF")

    timer = threading.Timer(2.0, delayed_update)
    timer.start()


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        command = payload.get("command")
    except json.JSONDecodeError:
        command = msg.payload.decode("utf-8")

    if command in {"ON", "OFF"}:
        apply_command(client, command)


def update_temperature():
    if state["device_on"]:
        target = 4.0
        delta = -0.2
    else:
        target = 9.5
        delta = 0.15

    temp = state["current_temp"]
    if (delta < 0 and temp > target) or (delta > 0 and temp < target):
        temp += delta

    state["current_temp"] = max(0.5, min(12.0, temp))


def generate_value():
    # Thỉnh thoảng bắn nhiễu 30°C để test UI
    if random.random() < 0.05:
        return 30.0
    return round(state["current_temp"] + random.uniform(-0.3, 0.3), 2)


def should_drop_packet():
    # Giả lập mất tín hiệu ngẫu nhiên
    return random.random() < 0.1


def main():
    client = mqtt.Client()
    client.on_message = on_message
    cmd_topic = f"{MQTT_TOPIC_BASE}/{DEVICE_ID}/cmd"
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.subscribe(cmd_topic)
    client.loop_start()

    print("Simulator running...")

    while True:
        update_temperature()

        if not should_drop_packet():
            value = generate_value()
            payload = {
                "value": value,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            telemetry_topic = f"{MQTT_TOPIC_BASE}/{DEVICE_ID}/telemetry"
            client.publish(telemetry_topic, json.dumps(payload))

        time.sleep(2)


if __name__ == "__main__":
    main()