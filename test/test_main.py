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
            # Dono users ko peer_joined event milna chahiye
            join_msg1 = ws1.receive_text()
            assert "peer_joined" in join_msg1
            join_msg2 = ws2.receive_text()
            assert "peer_joined" in join_msg2

            # Ab actual encrypted message relay test karein
            ws1.send_text("encrypted_payload_123")
            data = ws2.receive_text()
            assert data == "encrypted_payload_123"

# 7. Test The Fortress Security Headers (OWASP & Anti-Forensics)
def test_security_headers():
    response = client.get("/")
    assert response.status_code == 200
    headers = response.headers
    # Anti-Forensics Zero Disk Cache
    assert "no-store" in headers["cache-control"]
    # Clickjacking Defense
    assert headers["x-frame-options"] == "DENY"
    # MIME Sniffing Defense
    assert headers["x-content-type-options"] == "nosniff"
    # Strict CSP
    assert "default-src 'self'" in headers["content-security-policy"]
    assert "frame-ancestors 'none'" in headers["content-security-policy"]

# 8. Test Room Creation DDoS Rate Limiter (HTTP 429)
def test_rate_limiter():
    from app.main import room_creation_history
    room_creation_history.clear()
    
    # 15 requests allow honi chahiye
    for _ in range(15):
        res = client.post("/api/room/create")
        assert res.status_code == 200
        
    # 16th request par 429 Too Many Requests aana chahiye
    rate_limited_res = client.post("/api/room/create")
    assert rate_limited_res.status_code == 429
    assert "Too many room creation requests" in rate_limited_res.json()["detail"]
    
    room_creation_history.clear()