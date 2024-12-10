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
        await websocket.send_json({"type": "connect", "content": "WebSocket连接成功"})
    
    async def disconnect(self, websocket: WebSocket, reason: str = "正常断开"):
        try:
            await websocket.send_json({
                "type": "disconnect",
                "content": "WebSocket连接断开",
                "reason": reason
            })
        except:
            pass  # 如果发送失败，直接忽略，因为可能连接已经断开
        self.active_connections.remove(websocket)
        
    async def broadcast(self, message_content: str):
        """向所有连接的客户端广播消息"""
        disconnected = set()
        print("广播消息：", message_content)
        print("活跃连接数：", len(self.active_connections))
        print("活跃连接：", self.active_connections)
        for connection in self.active_connections:
            try:
                await connection.send_json({"type": "message", "content": message_content})
                print("向", connection, "发送消息:", message_content)
            except Exception as e:
                print(f"发送消息失败: {e}")
                disconnected.add((connection, str(e)))  # 保存错误信息
        
        # 移除断开的连接
        for connection, error_msg in disconnected:
            await self.disconnect(connection, f"连接异常：{error_msg}")
    
    async def broadcast_event(self, event:str, message_content: str):
        """向所有连接的客户端广播事件消息"""
        disconnected = set()
        print("广播事件消息：", event, message_content)
        print("活跃连接数：", len(self.active_connections))
        print("活跃连接：", self.active_connections)
        for connection in self.active_connections:
            try:
                await connection.send_json({"type": "event_message", "event": event, "content": message_content})
                print("向", connection, "发送事件消息:", event, message_content)
            except Exception as e:
                print(f"发送事件消息失败: {e}")
                disconnected.add((connection, str(e)))  # 保存错误信息
        
        # 移除断开的连接
        for connection, error_msg in disconnected:
            await self.disconnect(connection, f"连接异常：{error_msg}")