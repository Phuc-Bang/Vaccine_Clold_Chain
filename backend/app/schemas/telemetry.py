from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TelemetryBase(BaseModel):
    node_id: str
    temperature: float
    humidity: Optional[float] = None
    battery_level: Optional[int] = None
    signal_strength: Optional[int] = None

class TelemetryCreate(TelemetryBase):
    pass

class Telemetry(TelemetryBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class AlertBase(BaseModel):
    node_id: str
    alert_type: str
    threshold: float
    value: float

class Alert(AlertBase):
    id: int
    timestamp: datetime
    is_resolved: bool

    class Config:
        from_attributes = True
