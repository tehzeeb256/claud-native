from fastapi.testclient import TestClient
from app.main import app

# Test client setup
client = TestClient(app)

# test root endpoint 
def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
    assert "welcome" in data["message"].lower()


# test kubernetes 
def test_liveness_probe():
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data 

# test readiness probe 
def test_readiness_probe():
    response = client.get("/readyz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"

# test system info endpoint 
def test_system_info():
    response = client.get("/api/v1/info")
    assert response.status_code == 200
    data = response.json()
    assert data["app_name"] == "cloud-native platform"
    assert "hostname" in data 
    assert "uptime_seconds" in data 