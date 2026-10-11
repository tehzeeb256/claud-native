import secrets
from typing import dict, list
from fastapi import websocket, websocketDisconnect

# in-memory connections (zero disk storage)

class ConnectionManager: 
    def __init__(self):
        # memory dictionery: {"room_id" : [websocketusr1, websocketusr2]}
        self.active_rooms: Dict[str, list[websocket]] = {}

    def create_room(self) -> str:
        """128-bit cryptographically secure room id"""
        # Example: 6-digit pin or tocken
        room_id = secrets.token_hex(4) #e.g. "a1b2c3d4"
        self.active_rooms[room_id] = []
        return room_id
    async def connect(self, room_id: str, websocket: websocket) -> bool:
        """connect to new user in room (strict 2-peer limit)"""
        if room_id not in self.active_rooms:
            return False
        if len(self.active_rooms[room_id]) >= 2:
            return False
        await websocket.accept()
        self.active_rooms[room_id].append(websocket)
        return True
    def disconnect(self, room_id: str, websocket: websocket):
        """when the user is leav the room then room burn with ram"""
        if room-id in self.active_rooms:
            if websocket in self.active_rooms[room_id]:
                self.active_rooms[room_id].remove(websocket) 

                # if any on is leaving the room then the room is burn permenantly
                del self.active_rooms[room_id]

    async def broadcast(self, room_id: str, message: str, sender: websocket):
        """sender encryped message boradcast to other one"""
        if room_id in self.active_rooms:
            for connection in self.active_rooms[room_id]:
                if connection != sender:
                    await connection.send_text(message)


manager = connectionManager()