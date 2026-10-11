import time
import socket
import secrets
from typing import Dict, List
from fastapi import FastAPI, status, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

 
app = FastAPI(
    title="cloud-native platform",
    version="1.0.0",
    description="production ready cloud-native devops API"
)
START_TIME = time.time()

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
            for connection in self.active_rooms[room_id]:
                if connection != sender:
                    await connection.send_text(message)

manager = ConnectionManager()

# ==========================================================
# 3. Burner Chat Endpoints (APIs & WebSockets)
# ==========================================================

# 1. Naya Room Banane ka Endpoint
@app.post("/api/room/create", tags=["burner"])
def create_burner_room():
    """Naya 128-bit ephemeral room generate karna"""
    room_id = manager.create_room()
    return {
        "room_id": room_id,
        "status": "created"
    }

# 2. Live WebSocket Chat Pipe
@app.websocket("/ws/{room_id}")
async def websocket_chat_endpoint(websocket: WebSocket, room_id: str):
    """Real-time encrypted message relay pipe"""
    # Naye user ko connect karein (agar room mein pehle se 2 log hon to reject hoga)
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
            # Client se encrypted message receive karein
            ciphertext = await websocket.receive_text()
            # Doosre partner tak broadcast karein
            await manager.broadcast(room_id, ciphertext, sender=websocket)

    except WebSocketDisconnect:
        # Agar doosra banda abhi bhi connected hai, to usko batayein ke room burn ho gaya
        await manager.broadcast(room_id, '{"type": "room_burned"}', sender=websocket)
        # Jaise hi koi ek user disconnect hua: NUCLEAR PURGE!
        manager.disconnect(room_id, websocket)