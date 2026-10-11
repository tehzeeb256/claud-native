from fastapi.testclient import TestClient
from app.main import app

# Test client setup
client = TestClient(app)

# 1. Test Root UI Endpoint (GhostWire HTML Page)
def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "GhostWire" in response.text

# 2. Test Kubernetes Liveness Probe
def test_liveness_probe():
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data 

# 3. Test Kubernetes Readiness Probe
def test_readiness_probe():
    response = client.get("/readyz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"

# 4. Test System Info Endpoint
def test_system_info():
    response = client.get("/api/v1/info")
    assert response.status_code == 200
    data = response.json()
    assert data["app_name"] == "cloud-native platform"
    assert "hostname" in data 
    assert "uptime_seconds" in data 

# 5. Test Burner Room Creation
def test_create_burner_room():
    response = client.post("/api/room/create")
    assert response.status_code == 200
    data = response.json()
    assert "room_id" in data
    assert data["status"] == "created"
    assert len(data["room_id"]) >= 6

# 6. Test Real-Time WebSocket Relay
def test_websocket_chat():
    # Room create karein
    create_res = client.post("/api/room/create")
    room_id = create_res.json()["room_id"]

    # 2 users ko connect karke live message test karein
    with client.websocket_connect(f"/ws/{room_id}") as ws1:
        with client.websocket_connect(f"/ws/{room_id}") as ws2:
            ws1.send_text("encrypted_payload_123")
            data = ws2.receive_text()
            assert data == "encrypted_payload_123"