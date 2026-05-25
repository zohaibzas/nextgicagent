import json
import logging
from typing import List, Dict, Any
from fastapi import WebSocket, WebSocketDisconnect

log = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        log.info(f"WebSocket connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            log.info(f"WebSocket disconnected. Total clients: {len(self.active_connections)}")

    async def broadcast(self, event_type: str, data: Dict[str, Any]):
        message = json.dumps({
            "event": event_type,
            "data": data,
            "timestamp": __import__("datetime").datetime.utcnow().isoformat()
        })
        
        # Identify broken connections
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                log.warning(f"Failed to send WS message: {e}")
                dead_connections.append(connection)
                
        # Clean up dead connections
        for dead in dead_connections:
            self.disconnect(dead)

# Global manager instance
manager = ConnectionManager()
