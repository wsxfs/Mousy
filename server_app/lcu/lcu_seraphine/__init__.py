# -*- coding: utf-8 -*-
# @Time    : 2024/11/7 19:22
# @Author  : GZA
# @File    : __init__.py
import re

import aiohttp
import asyncio
import json
import os

import psutil
from aiohttp import ClientSession, BasicAuth, WSMsgType
import sys

# Set event loop policy for Windows systems
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class LcuWebSocket:
    def __init__(self, port, token):
        self.port = port
        self.token = token
        self.session = None
        self.ws = None
        self.events = []
        self.subscribes = []

    def subscribe(self, event: str, uri: str = '', types=('Update', 'Create', 'Delete')):
        def wrapper(func):
            self.events.append(event)
            self.subscribes.append({
                'uri': uri,
                'type': types,
                'callable': func
            })
            return func

        return wrapper

    async def matchUri(self, data):
        for s in self.subscribes:
            if not (s.get('uri') or s.get('type')) or (
                    data.get('uri') == s['uri'] and data.get('eventType') in s['type']
            ):
                await s['callable'](data)

    async def run_ws(self):
        self.session = ClientSession(
            auth=BasicAuth('riot', self.token),
            headers={
                'Content-type': 'application/json',
                'Accept': 'application/json'
            }
        )
        address = f'wss://127.0.0.1:{self.port}/'
        self.ws = await self.session.ws_connect(address, ssl=False)

        for event in self.events:
            await self.ws.send_json([5, event])

        async for msg in self.ws:
            if msg.type == WSMsgType.TEXT:
                data = json.loads(msg.data)[2]
                await self.matchUri(data)
            elif msg.type == WSMsgType.CLOSED:
                break

        await self.session.close()

    async def start(self):
        self.task = asyncio.create_task(self.run_ws())

    async def close(self):
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        if self.session:
            await self.session.close()


class LolClientConnector:
    def __init__(self):
        self.port = None
        self.token = None
        self.lcuSess = None
        self.listener = None

    async def start(self, port, token):
        self.port = port
        self.token = token
        self.lcuSess = ClientSession(
            base_url=f'https://127.0.0.1:{port}',
            auth=BasicAuth('riot', token),
            connector=aiohttp.TCPConnector(ssl=False)
        )
        await self.__run_listener()

    async def __run_listener(self):
        self.listener = LcuWebSocket(self.port, self.token)

        @self.listener.subscribe(event='OnJsonApiEvent_lol-summoner_v1_current-summoner',
                                 uri='/lol-summoner/v1/current-summoner',
                                 types=('Update',))
        async def on_current_summoner_profile_changed(event):
            print(f"Summoner profile updated: {event['data']}")

        await self.listener.start()

    async def close(self):
        if self.listener:
            await self.listener.close()
        if self.lcuSess:
            await self.lcuSess.close()

    async def get(self, path, params=None):
        async with self.lcuSess.get(path, params=params) as resp:
            return await resp.json()

    async def post(self, path, data=None):
        async with self.lcuSess.post(path, json=data) as resp:
            return await resp.json()

    async def put(self, path, data=None):
        async with self.lcuSess.put(path, json=data) as resp:
            return await resp.json()

    async def delete(self, path):
        async with self.lcuSess.delete(path) as resp:
            return await resp.json()

    async def patch(self, path, data=None):
        async with self.lcuSess.patch(path, json=data) as resp:
            return await resp.json()

    # Example LCU API calls
    async def get_current_summoner(self):
        return await self.get("/lol-summoner/v1/current-summoner")

    async def set_profile_background(self, skin_id):
        data = {
            "key": "backgroundSkinId",
            "value": skin_id
        }
        return await self.post("/lol-summoner/v1/current-summoner/summoner-profile", data)

    async def get_game_status(self):
        return await self.get("/lol-gameflow/v1/gameflow-phase")

    async def accept_matchmaking(self):
        return await self.post("/lol-matchmaking/v1/ready-check/accept")


# Example usage
def get_port_and_token():
    """
    使用 psutil 获取 LeagueClientUx 进程的端口和 token
    """
    for process in psutil.process_iter(['name', 'cmdline']):
        if process.info['name'] == "LeagueClientUx.exe":
            # 从命令行参数中解析端口和 token
            cmdline = " ".join(process.info['cmdline'])
            port_match = re.search(r"--app-port=([0-9]*)", cmdline)
            token_match = re.search(r"--remoting-auth-token=([\w-]*)", cmdline)

            if port_match and token_match:
                port = port_match.group(1)
                token = token_match.group(1)
                return port, token
    raise Exception("无法找到 LeagueClientUx 进程或解析端口和 token 失败")


async def main():
    connector = LolClientConnector()
    port, token = get_port_and_token()

    await connector.start(port, token)

    summoner = await connector.get_current_summoner()
    print(f"Current summoner: {summoner}")

    await connector.close()




    websocket = LcuWebSocket(port, token)

    # 订阅召唤师信息更新事件
    @websocket.subscribe(event='OnJsonApiEvent_lol-summoner_v1_current-summoner',
                         uri='/lol-summoner/v1/current-summoner',
                         types=('Update',))
    async def on_summoner_update(data):
        print("Summoner profile updated:", data['data'])

    # 订阅游戏状态更新事件
    @websocket.subscribe(event='OnJsonApiEvent_lol-gameflow_v1_gameflow-phase',
                         uri='/lol-gameflow/v1/gameflow-phase',
                         types=('Update',))
    async def on_gameflow_update(data):
        print("Gameflow phase changed:", data['data'])

    try:
        print("Starting WebSocket...")
        await websocket.start()  # 启动 WebSocket 连接

        # 模拟长时间运行
        await asyncio.sleep(60)  # 监听事件 60 秒
    finally:
        print("Closing WebSocket...")
        await websocket.close()  # 关闭 WebSocket 连接


if __name__ == "__main__":
    asyncio.run(main())
