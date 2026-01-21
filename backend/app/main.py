from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from app.core.database import engine, Base
from app.services.mqtt_service import mqtt_service
import logging
from app.core.logging import setup_logging

# Setup Logging
setup_logging()
logger = logging.getLogger(__name__)

# Create DB Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS Handing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up...")
    mqtt_service.start()

@app.get("/")
def root():
    return {"message": "Welcome to Vaccine Cold Chain Monitor API", "docs": "/docs"}
