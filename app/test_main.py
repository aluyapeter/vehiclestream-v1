import pytest
import os
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from database import get_db
from models import Base

load_dotenv()

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

if TEST_DATABASE_URL is None:
    raise ValueError("No test db url")

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    """
    Because autouse=True, Pytest will run this before EVERY single test function.
    """
    Base.metadata.create_all(bind=engine)
    
    yield
    
    Base.metadata.drop_all(bind=engine)

def override_get_db():
    """This function behaves exactly like your normal get_db, but uses the test session."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

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