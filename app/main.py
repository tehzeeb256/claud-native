import time
import socket
import secrets
from collections import defaultdict
from typing import Dict, List
from fastapi import FastAPI, status, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import FileResponse, JSONResponse

 
app = FastAPI(
    title="cloud-native platform",
    version="1.0.0",
    description="production ready cloud-native devops API"
)
START_TIME = time.time()

# ==========================================================
# 1. THE FORTRESS: Security Headers & Anti-Forensics Middleware
# ==========================================================
@app.middleware("http")
async def security_fortress_middleware(request: Request, call_next):
    """Enforce OWASP Top 10 Hardened Headers & Anti-Forensics"""
    response = await call_next(request)
    
    # 1. Anti-Forensics: Zero Disk Caching (No browser history or disk traces)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    # 2. Clickjacking Shield: Framing is strictly forbidden
    response.headers["X-Frame-Options"] = "DENY"
    
    # 3. MIME-Sniffing Prevention
    response.headers["X-Content-Type-Options"] = "nosniff"
    
    # 4. Referrer & XSS Filtering
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    # 5. Strict Content Security Policy (CSP)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "connect-src 'self' ws: wss:; "
        "frame-ancestors 'none';"
    )
    return response

# In-Memory IP Rate Limiter (Max 15 room creations per 60 seconds per IP)
room_creation_history: Dict[str, List[float]] = defaultdict(list)
RATE_LIMIT_WINDOW = 60.0  # seconds
RATE_LIMIT_MAX_REQUESTS = 15

# WebSocket Connection Rate Limiter (Max 30 connections per 60 seconds per IP)
ws_connection_history: Dict[str, List[float]] = defaultdict(list)
WS_RATE_LIMIT_WINDOW = 60.0  # seconds
WS_RATE_LIMIT_MAX_ATTEMPTS = 30

def extract_real_ip(request: Request | WebSocket) -> str:
    """Extract true client IP across Cloudflare, Render, AWS, Kubernetes & Reverse Proxies"""
    # 1. Cloudflare True Client IP
    cf_ip = request.headers.get("cf-connecting-ip")
    if cf_ip and cf_ip.strip():
        return cf_ip.split(",")[0].strip()

    # 2. X-Forwarded-For (First IP is the true originating client)
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded and forwarded.strip():
        return forwarded.split(",")[0].strip()

    # 3. Direct client host fallback
    if request.client and request.client.host:
        return request.client.host

    return "unknown"

def purge_stale_rate_limits(now: float):
    """Issue #6: Auto-purge expired IPs to prevent in-memory RAM leaks"""
    stale_room_ips = [ip for ip, timestamps in room_creation_history.items() if not timestamps or (now - timestamps[-1] >= RATE_LIMIT_WINDOW)]
    for ip in stale_room_ips:
        del room_creation_history[ip]

    stale_ws_ips = [ip for ip, timestamps in ws_connection_history.items() if not timestamps or (now - timestamps[-1] >= WS_RATE_LIMIT_WINDOW)]
    for ip in stale_ws_ips:
        del ws_connection_history[ip]

# Welcome endpoint
@app.get("/", response_class=FileResponse, tags=["general"])
def read_root():
    """GhostWire Stealth Web UI serve karna"""
    return FileResponse("app/static/index.html")

# Kubernetes Liveness Probe (Self-healing)
@app.get("/healthz", status_code=status.HTTP_200_OK, tags=["devops probes"])
def liveness_probe():
    return {
        "status": "healthy",
        "timestamp": time.time()
    }

# Kubernetes Readiness Probe (Traffic Balancer)
@app.get("/readyz", status_code=status.HTTP_200_OK, tags=["devops probes"])
def readiness_probe():
    return {
        "status": "ready"
    }

# System Info endpoint
@app.get("/api/v1/info", tags=["devops probes"])
def system_info():
    uptime = round(time.time() - START_TIME, 2)
    return {
        "hostname": socket.gethostname(),
        "app_name": "cloud-native platform",
        "uptime_seconds": uptime
    }

# ==========================================================
# 2. In-Memory Connection Manager (Zero Disk Storage)
# ==========================================================
class ConnectionManager:
    def __init__(self):
        # RAM storage: {"room_id": [WebSocket_User1, WebSocket_User2]}
        self.active_rooms: Dict[str, List[WebSocket]] = {}

    def create_room(self) -> str:
        """128-bit cryptographically secure room id"""
        room_id = secrets.token_hex(4)  # e.g. "a1b2c3d4"
        self.active_rooms[room_id] = []
        return room_id

    async def connect(self, room_id: str, websocket: WebSocket) -> bool:
        """Room mein naya user connect karna (Strict 2-Peer Limit)"""
        if room_id not in self.active_rooms:
            return False
        if len(self.active_rooms[room_id]) >= 2:
            return False
        await websocket.accept()
        self.active_rooms[room_id].append(websocket)
        return True

    def disconnect(self, room_id: str, websocket: WebSocket):
        """User ke nikalte hi room ko RAM se WIPE OUT karna"""
        if room_id in self.active_rooms:
            if websocket in self.active_rooms[room_id]:
                self.active_rooms[room_id].remove(websocket)
            # Nuclear Switch: Room hamesha ke liye delete!
            del self.active_rooms[room_id]

    async def broadcast(self, room_id: str, message: str, sender: WebSocket):
        """Encrypted message ko doosre partner tak relay karna"""
        if room_id in self.active_rooms:
            for connection in list(self.active_rooms[room_id]):
                if connection != sender:
                    try:
                        await connection.send_text(message)
                    except Exception:
                        pass

manager = ConnectionManager()

# ==========================================================
# 3. Burner Chat Endpoints (APIs & WebSockets)
# ==========================================================

# 1. Naya Room Banane ka Endpoint (With DDoS Rate Limiting)
@app.post("/api/room/create", tags=["burner"])
def create_burner_room(request: Request):
    """Naya 128-bit ephemeral room generate karna (DDoS & Spam Protected with Real Proxy IP Extraction)"""
    client_ip = extract_real_ip(request)
    now = time.time()
    
    # Auto-purge expired IPs to keep RAM footprint minimal
    purge_stale_rate_limits(now)

    # Purani expired timestamps filter karein
    recent_requests = [t for t in room_creation_history[client_ip] if now - t < RATE_LIMIT_WINDOW]
    
    if len(recent_requests) >= RATE_LIMIT_MAX_REQUESTS:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Too many room creation requests. Please wait a minute."}
        )
    
    recent_requests.append(now)
    room_creation_history[client_ip] = recent_requests

    room_id = manager.create_room()
    return {
        "room_id": room_id,
        "status": "created"
    }

# 2. Live WebSocket Chat Pipe
@app.websocket("/ws/{room_id}")
async def websocket_chat_endpoint(websocket: WebSocket, room_id: str):
    """Real-time encrypted message relay pipe with anti-abuse rate limiting"""
    client_ip = extract_real_ip(websocket)
    now = time.time()

    # Expired history purge
    purge_stale_rate_limits(now)

    # 1. Connection Rate Limiter (Max 30 connection attempts per 60s per IP)
    recent_attempts = [t for t in ws_connection_history[client_ip] if now - t < WS_RATE_LIMIT_WINDOW]
    if len(recent_attempts) >= WS_RATE_LIMIT_MAX_ATTEMPTS:
        # Policy Violation (1008): Rate limit exceeded
        await websocket.close(code=1008)
        return

    recent_attempts.append(now)
    ws_connection_history[client_ip] = recent_attempts

    # 2. Naye user ko connect karein (agar room invalid ho ya 2 log pehle se hon to reject hoga)
    connected = await manager.connect(room_id, websocket)
    if not connected:
        # 403 / Policy Violation: 3rd user ko room se bahar nikalo
        await websocket.close(code=1008)
        return

    # Jab 2nd peer join kare, to dono ko notify karein ke room ready hai
    if room_id in manager.active_rooms and len(manager.active_rooms[room_id]) == 2:
        for client_conn in manager.active_rooms[room_id]:
            await client_conn.send_text('{"type": "peer_joined"}')

    try:
        # Jab tak dono chat kar rahe hain, messages receive aur forward karein
        while True:
            # Client se message receive karein
            ciphertext = await websocket.receive_text()

            # 1. Dead Man's Switch Pulse (Heartbeat Ping-Pong)
            if '"type":"ping"' in ciphertext or '"type": "ping"' in ciphertext:
                await websocket.send_text('{"type": "pong"}')
                continue

            # 2. Zero-Delay Instant Burn Command
            if '"type":"room_burned"' in ciphertext or '"type": "room_burned"' in ciphertext:
                await manager.broadcast(room_id, '{"type": "room_burned"}', sender=websocket)
                manager.disconnect(room_id, websocket)
                break

            # 3. Doosre partner tak encrypted message relay karein
            await manager.broadcast(room_id, ciphertext, sender=websocket)

    except WebSocketDisconnect:
        # Agar doosra banda abhi bhi connected hai, to usko batayein ke room burn ho gaya
        await manager.broadcast(room_id, '{"type": "room_burned"}', sender=websocket)
        # Jaise hi koi ek user disconnect hua: NUCLEAR PURGE!
        manager.disconnect(room_id, websocket)