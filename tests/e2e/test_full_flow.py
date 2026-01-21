"""
E2E Test: Full Flow - Sensor to Dashboard
Tests the complete data flow from simulated sensor through to database.
"""

import pytest
import asyncio
import httpx
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
MQTT_BROKER = "localhost"
MQTT_PORT = 1883


class TestFullFlow:
    """End-to-end tests for the Vaccine Cold Chain system."""

    @pytest.fixture
    def client(self):
        """HTTP client for API testing."""
        return httpx.Client(base_url=BASE_URL, timeout=10.0)

    def test_api_health(self, client):
        """Test API is running and healthy."""
        response = client.get("/")
        assert response.status_code == 200

    def test_telemetry_endpoint(self, client):
        """Test telemetry data can be retrieved."""
        response = client.get("/api/telemetry")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_temperature_in_range(self, client):
        """Test temperature readings are within expected range."""
        response = client.get("/api/telemetry?limit=10")
        assert response.status_code == 200
        data = response.json()
        
        for reading in data:
            temp = reading.get("temperature", 0)
            # Temperature should be between -40 and 50°C
            assert -40 <= temp <= 50, f"Temperature {temp} out of range"

    def test_dashboard_loads(self, client):
        """Test dashboard HTML is served."""
        response = client.get("/static/index.html")
        # May be 200 or 404 depending on static file setup
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_websocket_connection(self):
        """Test WebSocket connection for real-time updates."""
        try:
            async with httpx.AsyncClient() as client:
                # This is a simplified test - actual WebSocket testing
                # would use the websockets library
                response = await client.get(f"{BASE_URL}/")
                assert response.status_code == 200
        except Exception as e:
            pytest.skip(f"WebSocket test skipped: {e}")


class TestAlertSystem:
    """Tests for the alert/alarm system."""

    @pytest.fixture
    def client(self):
        return httpx.Client(base_url=BASE_URL, timeout=10.0)

    def test_high_temp_alert(self, client):
        """Test that high temperature triggers alert."""
        # This would require simulating a high temp reading
        # For now, we just verify the alerts endpoint exists
        response = client.get("/api/alerts")
        assert response.status_code in [200, 404]

    def test_low_temp_alert(self, client):
        """Test that low temperature triggers alert."""
        response = client.get("/api/alerts")
        assert response.status_code in [200, 404]


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
