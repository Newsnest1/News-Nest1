from fastapi import WebSocket
from typing import List, Dict, Optional
import json

class EnhancedWebSocketManager:
    def __init__(self):
        # Track connections with user info: {websocket: user_id}
        self.active_connections: Dict[WebSocket, Optional[int]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: Optional[int] = None):
        await websocket.accept()
        self.active_connections[websocket] = user_id
        print(f"Client connected. User ID: {user_id}. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            user_id = self.active_connections.pop(websocket)
            print(f"Client disconnected. User ID: {user_id}. Total connections: {len(self.active_connections)}")
    
    async def broadcast(self, message: str):
        """Broadcast to all connected clients (existing functionality)"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
    
    async def send_personalized_notification(self, user_id: int, notification: dict):
        """Send notification to a specific user"""
        disconnected = []
        for connection, conn_user_id in self.active_connections.items():
            if conn_user_id == user_id:
                try:
                    await connection.send_text(json.dumps(notification))
                except:
                    disconnected.append(connection)
        
        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
    
    async def send_notification_to_users(self, user_ids: List[int], notification: dict):
        """Send notification to multiple specific users"""
        disconnected = []
        for connection, conn_user_id in self.active_connections.items():
            if conn_user_id in user_ids:
                try:
                    await connection.send_text(json.dumps(notification))
                except:
                    disconnected.append(connection)
        
        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
    
    def get_connected_users(self) -> List[int]:
        """Get list of user IDs currently connected"""
        return [user_id for user_id in self.active_connections.values() if user_id is not None]

manager = EnhancedWebSocketManager()
