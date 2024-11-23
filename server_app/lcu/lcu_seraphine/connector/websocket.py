# -*- coding: utf-8 -*-
# @Time    : 2024/11/7 19:33
# @Author  : GZA
# @File    : websocket.py.py

"""
websocket.py - WebSocket 连接模块。
用于订阅英雄联盟客户端的实时事件。
"""

import aiohttp
import asyncio
import json
from aiohttp import WSMsgType

class LcuWebSocket:
    def __init__(self, port: int, token: str):
        """
        初始化 WebSocket 连接。

        Args:
            port (int): 客户端 WebSocket 监听的端口。
            token (str): 认证令牌，用于连接 WebSocket。
        """
        self.port = port
        self.token = token
        self.session = None
        self.ws = None
        self.events = []  # 需要订阅的事件列表
        self.subscribers = []  # 事件回调函数的订阅者

    def subscribe(self, event: str, callback):
        """
        订阅指定事件。

        Args:
            event (str): 要订阅的事件名称。
            callback (callable): 事件触发时调用的回调函数。
        """
        self.events.append(event)
        self.subscribers.append((event, callback))

    async def start(self):
        """
        启动 WebSocket 连接并监听事件。
        """
        self.session = aiohttp.ClientSession(auth=aiohttp.BasicAuth('riot', self.token))
        address = f'wss://127.0.0.1:{self.port}/'
        self.ws = await self.session.ws_connect(address, ssl=False)

        # 订阅事件
        for event in self.events:
            await self.ws.send_json([5, event])

        asyncio.create_task(self._listen())

    async def close(self):
        """关闭 WebSocket 连接和会话。"""
        if self.ws:
            await self.ws.close()
        if self.session:
            await self.session.close()

    async def _listen(self):
        """监听 WebSocket 消息，并调用相应的回调函数。"""
        try:
            async for msg in self.ws:
                if msg.type == WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    await self._handle_message(data)
                elif msg.type == WSMsgType.CLOSED:
                    print("WebSocket connection closed.")
                    break
        except Exception as e:
            print(f"WebSocket error: {e}")
        finally:
            await self.close()

    async def _handle_message(self, data):
        """
        处理接收到的 WebSocket 消息，并触发订阅的回调。

        Args:
            data (dict): WebSocket 消息数据。
        """
        if not isinstance(data, list) or len(data) < 3:
            return

        event_name = data[1]
        event_payload = data[2]

        for event, callback in self.subscribers:
            if event == event_name:
                asyncio.create_task(callback(event_payload))
