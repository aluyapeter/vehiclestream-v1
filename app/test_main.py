from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    """Test that the API is alive and responding."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "Telematics Gateway is running"}

def test_create_alert_config():
    """Test that we can successfully save a new alert configuration."""
    test_vin = "PYTEST-VIN-999"
    payload = {
        "metric": "speed",
        "threshold": 150.0
    }
    
    response = client.post(f"/vehicles/{test_vin}/alert-config", json=payload)
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "Alert configured successfully"
    assert data["data"]["vin"] == test_vin
    assert data["data"]["metric"] == "speed"
    assert data["data"]["threshold"] == 150.0

def test_get_latest_telemetry_not_found():
    """Test that querying a vehicle that doesn't exist returns a proper 404 error."""
    ghost_vin = "GHOST-VIN-000"
    
    response = client.get(f"/vehicles/{ghost_vin}/latest")
    
    assert response.status_code == 404
    assert response.json() == {"detail": f"No telemetry found for VIN: {ghost_vin}"}