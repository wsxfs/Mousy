# -*- coding: utf-8 -*-
# @Time    : 2024/11/7 19:33
# @Author  : GZA
# @File    : base.py.py
"""
base.py - 英雄联盟客户端的核心连接逻辑。
提供 LolClientConnector 类用于与客户端通信和控制游戏流程。
"""

import asyncio
from .session import SessionManager
from .websocket import LcuWebSocket
from .decorators import retry
from .api import ApiClient

class LolClientConnector:
    def __init__(self):
        """初始化连接器"""
        self.loop = asyncio.get_event_loop()
        self.session_manager = SessionManager()
        self.websocket = None
        self.api_client = None
        self.connected = False

    async def start(self):
        """
        启动连接器，初始化会话和 WebSocket 连接。
        """
        self.session_manager.initialize()
        self.api_client = ApiClient(self.session_manager)
        port = self.session_manager.port
        token = self.session_manager.token

        self.websocket = LcuWebSocket(port, token)
        await self.websocket.start()
        self.connected = True

    async def close(self):
        """关闭连接器，清理会话和 WebSocket"""
        if self.websocket:
            await self.websocket.close()
        await self.session_manager.close()
        self.connected = False

    @retry()
    async def get_summoner_by_name(self, name: str):
        """通过召唤师名称获取信息"""
        return await self.api_client.get(f"/lol-summoner/v1/summoners?name={name}")

    # 更多 API 调用和业务逻辑在此扩展
