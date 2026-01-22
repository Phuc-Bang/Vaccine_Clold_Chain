import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path

import paho.mqtt.client as mqtt
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = Path(os.getenv("DB_PATH", BASE_DIR / "database" / "iot_industrial.db"))

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC_BASE = os.getenv("MQTT_TOPIC_BASE", "coldchain/device")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lưu trạng thái thiết bị trong RAM để frontend polling
DEVICE_STATES = {
    "NODE_01": "UNKNOWN"
}


class ControlCommand(BaseModel):
    device_id: str
    command: str
    param: int | None = None


class TelemetryIn(BaseModel):
    node_id: str
    value: float
    timestamp: str | None = None


def get_db_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
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


@app.on_event("startup")
def startup():
    init_db()


@app.get("/api/v1/history/{node_id}")
def get_history(node_id: str, limit: int = Query(20, ge=1, le=200)):
    conn = get_db_connection()
    rows = conn.execute(
        """
        SELECT sensor_value, timestamp
        FROM measurements
        WHERE node_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
        """,
        (node_id, limit),
    ).fetchall()
    conn.close()

    data = [
        {"value": row["sensor_value"], "time": row["timestamp"]}
        for row in rows
    ]
    data.reverse()
    return data


@app.post("/api/v1/ingest")
def ingest_data(payload: TelemetryIn):
    # Cho phép simulator gửi trực tiếp vào DB
    timestamp = payload.timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO measurements (node_id, sensor_value, timestamp) VALUES (?, ?, ?)",
        (payload.node_id, payload.value, timestamp),
    )
    conn.commit()
    conn.close()
    return {"msg": "ok"}


@app.get("/api/v1/device/{device_id}/status")
def get_device_status(device_id: str):
    return {"status": DEVICE_STATES.get(device_id, "UNKNOWN")}


@app.post("/api/v1/device/{device_id}/status")
def update_device_status(device_id: str, status: str):
    DEVICE_STATES[device_id] = status
    return {"msg": "Updated"}


@app.post("/api/v1/control/device")
def control_device(cmd: ControlCommand):
    topic = f"{MQTT_TOPIC_BASE}/{cmd.device_id}/cmd"
    payload = json.dumps({"command": cmd.command, "param": cmd.param})

    client = mqtt.Client()
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.publish(topic, payload)
        client.disconnect()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"MQTT error: {exc}") from exc

    return {"msg": "Command sent", "topic": topic}