"""Test fixtures and mock data"""


def mock_device():
    """Create mock device"""
    return {
        "id": "device_001",
        "name": "Kho Lạnh A",
        "location": "Hà Nội",
    }


def mock_telemetry():
    """Create mock telemetry data"""
    return {
        "device_id": "device_001",
        "temperature": 5.2,
        "humidity": 45.3,
        "timestamp": "2026-01-22T10:30:00",
    }
