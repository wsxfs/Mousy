from fastapi import WebSocket
from typing import Dict, Set

class Websocket2Front:
    def __init__(self):
        # 存储所有活跃的websocket连接
        self.active_connections: Set[WebSocket] = set()
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        # 发送连接成功消息
        await websocket.send_json({"type": "system", "message": "WebSocket连接成功"})
    
    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        
    async def broadcast(self, message: dict):
        """向所有连接的客户端广播消息"""
        disconnected = set()
        print("广播消息：", message)
        print("活跃连接数：", len(self.active_connections))
        print("活跃连接：", self.active_connections)
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
                print("向", connection, "发送消息:", message)
            except Exception as e:
                print(f"发送消息失败: {e}")
                disconnected.add(connection)
        
        # 移除断开的连接
        for connection in disconnected:
            await self.disconnect(connection)