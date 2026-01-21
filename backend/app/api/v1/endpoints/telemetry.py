from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.telemetry import Telemetry
from app.schemas.telemetry import Telemetry as TelemetrySchema

router = APIRouter()

@router.get("/", response_model=List[TelemetrySchema])
def read_telemetry(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    readings = db.query(Telemetry).order_by(Telemetry.timestamp.desc()).offset(skip).limit(limit).all()
    return readings

@router.get("/{node_id}", response_model=List[TelemetrySchema])
def read_node_telemetry(node_id: str, limit: int = 50, db: Session = Depends(get_db)):
    readings = db.query(Telemetry).filter(Telemetry.node_id == node_id).order_by(Telemetry.timestamp.desc()).limit(limit).all()
    return readings
