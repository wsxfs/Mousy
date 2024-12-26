from fastapi import WebSocket
from typing import Dict, Set, List, Optional
import asyncio

class SyncFrontData:
    current_puuid: Optional[str] = None
    my_team_puuid_list: Optional[List[str]] = None
    their_team_puuid_list: Optional[List[str]] = None
    current_champion: Optional[int] = None
    bench_champions: Optional[List[int]] = None
    gameflow_phase: Optional[str] = None
    swap_champion_button: Optional[bool] = None
    selected_champion_id: Optional[int] = None
    summoner_id: Optional[int] = None
    lcu_connected: Optional[bool] = None

    def __init__(self, w2front):
        self.w2front = w2front

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        # 执行异步方法
        if hasattr(self, 'w2front') and name != 'w2front':  # 避免初始化时的递归
            asyncio.create_task(self.async_set_value(name, value))

    async def async_set_value(self, name, new_value):
        if self.w2front and new_value is not None:
            # 将消息格式改为标准 JSON 格式
            message = {
                "type": "attribute_change",
                "data": {
                    "attribute": name,
                    "value": new_value
                }
            }
            await self.w2front.broadcast_event("attribute_change", message)

class Websocket2Front:
    def __init__(self):
        # 存储所有活跃的websocket连接
        self.active_connections: Set[WebSocket] = set()
        self.sync_data = SyncFrontData(self)
        
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