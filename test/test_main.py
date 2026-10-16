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

# 9. Test Dead Man's Switch Heartbeat (Ping-Pong)
def test_websocket_heartbeat_ping_pong():
    create_res = client.post("/api/room/create")
    room_id = create_res.json()["room_id"]

    with client.websocket_connect(f"/ws/{room_id}") as ws1:
        # Ping bheinjein aur pong verify karein
        ws1.send_text('{"type": "ping"}')
        pong_res = ws1.receive_text()
        assert pong_res == '{"type": "pong"}'

# 10. Test Instant Nuclear Purge Broadcast
def test_instant_burn_broadcast():
    create_res = client.post("/api/room/create")
    room_id = create_res.json()["room_id"]

    with client.websocket_connect(f"/ws/{room_id}") as ws1:
        with client.websocket_connect(f"/ws/{room_id}") as ws2:
            # Drain join messages
            ws1.receive_text()
            ws2.receive_text()

            # User 1 burns room with instant broadcast command
            ws1.send_text('{"type": "room_burned"}')

            # User 2 should immediately receive room_burned
            burn_event = ws2.receive_text()
            assert "room_burned" in burn_event

# 11. Test Real IP Extraction via Cloud Proxy Headers (Issue #4)
def test_real_ip_proxy_header_rate_limiting():
    from app.main import room_creation_history
    room_creation_history.clear()

    user_a_ip = "203.0.113.195"
    user_b_ip = "198.51.100.42"

    # User A 15 requests bhejta hai via proxy
    for _ in range(15):
        res = client.post("/api/room/create", headers={"x-forwarded-for": f"{user_a_ip}, 10.0.0.1"})
        assert res.status_code == 200

    # User A ka 16th request block hona chahiye
    blocked_res = client.post("/api/room/create", headers={"x-forwarded-for": f"{user_a_ip}, 10.0.0.1"})
    assert blocked_res.status_code == 429

    # Lekin User B (same proxy se) block NAHI hona chahiye! (No DoS on innocent users)
    user_b_res = client.post("/api/room/create", headers={"x-forwarded-for": f"{user_b_ip}, 10.0.0.1"})
    assert user_b_res.status_code == 200

    # Cloudflare CF-Connecting-IP check
    cf_user = "192.0.2.1"
    cf_res = client.post("/api/room/create", headers={"cf-connecting-ip": cf_user})
    assert cf_res.status_code == 200
    assert cf_user in room_creation_history

    room_creation_history.clear()

# 12. Test Auto-Purge of Stale Rate Limit History (Issue #6)
def test_stale_rate_limit_purge():
    import time
    from app.main import room_creation_history, purge_stale_rate_limits

    room_creation_history.clear()
    now = time.time()
    # Add an expired IP (older than 60 seconds)
    room_creation_history["stale.ip.address"] = [now - 120.0]
    room_creation_history["active.ip.address"] = [now]

    purge_stale_rate_limits(now)

    assert "stale.ip.address" not in room_creation_history
    assert "active.ip.address" in room_creation_history
    room_creation_history.clear()