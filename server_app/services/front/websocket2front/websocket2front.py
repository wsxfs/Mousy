from fastapi import WebSocket
from typing import Dict, Set

class Websocket2Front:
    def __init__(self):
        # 存储所有活跃的websocket连接
        self.active_connections: Set[WebSocket] = set()
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
    
    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        
    async def broadcast(self, message: dict):
        """向所有连接的客户端广播消息"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"发送消息失败: {e}")
                await self.disconnect(connection)