from typing import List, Dict
import asyncio
import json

class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, List] = {}
    
    async def connect(self, websocket, client_id: str):
        """Accept new connection"""
        await websocket.accept()
        if client_id not in self.active_connections:
            self.active_connections[client_id] = []
        self.active_connections[client_id].append(websocket)
        print(f"Client {client_id} connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket, client_id: str):
        """Remove disconnected client"""
        if client_id in self.active_connections:
            self.active_connections[client_id].remove(websocket)
            if not self.active_connections[client_id]:
                del self.active_connections[client_id]
        print(f"Client {client_id} disconnected")
    
    async def send_message(self, message: str, client_id: str):
        """Send message to specific client"""
        if client_id in self.active_connections:
            for connection in self.active_connections[client_id]:
                try:
                    await connection.send_text(message)
                except:
                    pass
    
    async def broadcast(self, message: str):
        """Broadcast to all clients"""
        for client_id in self.active_connections:
            await self.send_message(message, client_id)

# Create global manager instance
manager = ConnectionManager()