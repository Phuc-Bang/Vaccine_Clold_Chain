import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path

import paho.mqtt.client as mqtt
import requests

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = Path(os.getenv("DB_PATH", BASE_DIR / "database" / "iot_industrial.db"))

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC_BASE = os.getenv("MQTT_TOPIC_BASE", "coldchain/device")

API_BASE = os.getenv("API_BASE", "http://localhost:8000/api/v1")


def get_db_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node_id TEXT NOT NULL,
            sensor_value REAL NOT NULL,
            timestamp TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def insert_measurement(node_id: str, value: float, timestamp: str):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO measurements (node_id, sensor_value, timestamp) VALUES (?, ?, ?)",
        (node_id, value, timestamp),
    )
    conn.commit()
    conn.close()


def handle_stat(device_id: str, status: str):
    # Cập nhật status qua API để frontend polling thấy ngay
    try:
        requests.post(
            f"{API_BASE}/device/{device_id}/status",
            params={"status": status},
            timeout=5,
        )
    except requests.RequestException as exc:
        print("Status update failed:", exc)


def parse_payload(payload: bytes):
    try:
        data = json.loads(payload.decode("utf-8"))
        return data
    except json.JSONDecodeError:
        text = payload.decode("utf-8")
        return {"value": text}


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        telemetry_topic = f"{MQTT_TOPIC_BASE}/+/telemetry"
        stat_topic = f"{MQTT_TOPIC_BASE}/+/stat"
        client.subscribe([(telemetry_topic, 0), (stat_topic, 0)])
        print("Subscribed to topics")
    else:
        print("Failed to connect:", rc)


def on_message(client, userdata, msg):
    topic = msg.topic
    parts = topic.split("/")
    if len(parts) < 4:
        return

    device_id = parts[2]
    payload = parse_payload(msg.payload)

    if topic.endswith("/telemetry"):
        value = float(payload.get("value", 0))
        timestamp = payload.get("timestamp") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        insert_measurement(device_id, value, timestamp)
    elif topic.endswith("/stat"):
        status = payload.get("status") or payload.get("value") or "UNKNOWN"
        handle_stat(device_id, str(status))


def main():
    init_db()
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    print("MQTT worker running...")
    client.loop_forever()


if __name__ == "__main__":
    main()