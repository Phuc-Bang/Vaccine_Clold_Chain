from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Vaccine Cold Chain Monitor API", "docs": "/docs"}

def test_telemetry_endpoint():
    # Mock DB would be better here, but for now checking structure
    response = client.get("/api/v1/telemetry")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
