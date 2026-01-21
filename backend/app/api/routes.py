"""
API Routes for VaccineColdChain
"""

import logging
from typing import List

logger = logging.getLogger(__name__)


def create_device_routes(app, device_service):
    """Create device-related routes"""

    @app.route("/api/devices", methods=["GET"])
    def list_devices():
        """List all devices"""
        devices = device_service.get_all_devices()
        return {"devices": devices}, 200

    @app.route("/api/devices/<device_id>", methods=["GET"])
    def get_device(device_id):
        """Get device details"""
        device = device_service.get_device(device_id)
        if not device:
            return {"error": "Device not found"}, 404
        return {"device": device}, 200

    @app.route("/api/devices", methods=["POST"])
    def create_device():
        """Create new device"""
        # Implementation here
        return {"message": "Device created"}, 201


def create_telemetry_routes(app, telemetry_service):
    """Create telemetry-related routes"""

    @app.route("/api/devices/<device_id>/telemetry", methods=["GET"])
    def get_telemetry(device_id):
        """Get telemetry data"""
        telemetry = telemetry_service.get_telemetry(device_id)
        return {"telemetry": telemetry}, 200

    @app.route("/api/devices/<device_id>/telemetry/latest", methods=["GET"])
    def get_latest_telemetry(device_id):
        """Get latest telemetry"""
        latest = telemetry_service.get_latest_telemetry(device_id)
        if not latest:
            return {"error": "No data"}, 404
        return {"telemetry": latest}, 200

    @app.route("/api/devices/<device_id>/telemetry", methods=["POST"])
    def save_telemetry(device_id):
        """Save new telemetry data"""
        # Implementation here
        return {"message": "Telemetry saved"}, 201
