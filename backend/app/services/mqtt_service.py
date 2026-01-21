import json
import logging
import paho.mqtt.client as mqtt
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.telemetry import Telemetry, Alert

logger = logging.getLogger(__name__)

class MQTTService:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.db: Session = SessionLocal()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("Connected to MQTT Broker!")
            # Subscribe to all gateway telemetry topics
            client.subscribe("vaccine/gateway/+/telemetry")
            client.subscribe("vaccine/gateway/+/alert")
        else:
            logger.error(f"Failed to connect, return code {rc}")

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            topic = msg.topic
            
            logger.info(f"Received message on {topic}: {payload}")

            if "telemetry" in topic:
                self.process_telemetry(payload)
            elif "alert" in topic:
                self.process_alert(payload)

        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def process_telemetry(self, data: dict):
        try:
            telemetry = Telemetry(
                node_id=data.get("node_id"),
                temperature=data.get("temperature"),
                humidity=data.get("humidity"),
                battery_level=data.get("battery_level"),
                signal_strength=data.get("signal_strength")
            )
            self.db.add(telemetry)
            self.db.commit()
        except Exception as e:
            logger.error(f"DB Error: {e}")
            self.db.rollback()

    def process_alert(self, data: dict):
        try:
            alert = Alert(
                node_id=data.get("node_id"),
                alert_type=data.get("alert_type"),
                threshold=data.get("threshold"),
                value=data.get("current_value")
            )
            self.db.add(alert)
            self.db.commit()
        except Exception as e:
            logger.error(f"DB Error: {e}")
            self.db.rollback()

    def start(self):
        try:
            self.client.connect(settings.MQTT_BROKER, settings.MQTT_PORT, settings.MQTT_KEEPALIVE)
            self.client.loop_start()
        except Exception as e:
            logger.error(f"Could not connect to MQTT Broker: {e}")

mqtt_service = MQTTService()
