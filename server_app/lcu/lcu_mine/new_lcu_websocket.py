# -*- coding: utf-8 -*-
# @Time    : 2024/11/6 23:34
# @Author  : GZA
# @File    : _lcu_websocket.py

import asyncio
import json

import aiohttp

import _endpoints


class WebsocketManager:
    session: aiohttp.ClientSession
    ws: aiohttp.ClientWebSocketResponse

    def __init__(self, port, token):
        self.port = port
        self.token = token
        self.is_connected = False

    # 更新port和token
    def update_port_token(self, port, token):
        self.port, self.token = port, token

    # 连接Websocket
    async def connect(self):
        # 创建一个 aiohttp.ClientSession 实例
        self.session = aiohttp.ClientSession(
            auth=aiohttp.BasicAuth('riot', self.token),
            headers={
                'Content-type': 'application/json',
                'Accept': 'application/json'
            }
        )

        # 构建 WebSocket 地址
        address = f'wss://127.0.0.1:{self.port}/'

        # 连接到 WebSocket 服务器
        try:  # 尝试建立 WebSocket 连接
            self.ws = await self.session.ws_connect(address, ssl=False)
            print("WebSocket 连接已建立")
        except Exception as e:
            print(f"WebSocket 连接失败: {str(e)}")
            return

    # 关闭Websocket连接
    async def close(self):
        await self.ws.close()

    # 发送订阅消息
    async def subscribe(self, lcu_event: str):
        await self.ws.send_json([5, lcu_event])

    # 发送取消订阅消息
    async def unsubscribe(self, lcu_event: str):
        await self.ws.send_json([6, lcu_event])

    # 接收消息
    async def receive(self):
        msg = await self.ws.receive()
        msg_type = msg.type
        msg_data = msg.data
        msg_extra = msg.extra

        if msg_type != aiohttp.WSMsgType.TEXT:
            if msg.type == aiohttp.WSMsgType.CLOSED:
                print("WebSocket 连接被关闭")
                self.is_connected = False
                return aiohttp.WSMsgType.CLOSED

        if msg_data == '':
            return ''

        # print(f'接收到的msg_data:{msg_data}')
        return msg_data


class Websocket2Lcu():
    def __init__(self, port=None, token=None) -> None:
        self.port, self.token = port, token
        self.ws = WebsocketManager(port=port, token=token)
        self.call_back_dict = dict()
        self.is_connected = False
        self.events = Events()
        # 添加一个事件循环任务的引用
        self.event_loop_task = None

    # 更新port和token,以及ws的port和token
    def update_port_token(self, port, token):
        self.port, self.token = port, token
        self.ws.update_port_token(port, token)

    # 连接Websocket
    async def connect(self):
        await self.ws.connect()
        self.is_connected = True

    # 注册事件及回调函数
    async def subscribe_func(self, lcu_event, call_back_function):
        await self.ws.subscribe(lcu_event)
        self.call_back_dict[lcu_event] = call_back_function

    # 取消注册事件及回调函数
    async def unsubscribe_func(self, lcu_event):
        await self.ws.unsubscribe(lcu_event)
        self.call_back_dict.pop(lcu_event, None)

    async def start(self):
        # 连接
        await self.connect()
        # 订阅
        await self.ws.subscribe("OnJsonApiEvent_lol-gameflow_v1_gameflow-phase")
        # 创建事件循环任务
        self.event_loop_task = asyncio.create_task(self._event_loop())
        
    async def _event_loop(self):
        while self.is_connected:
            msg = await self.ws.receive()
            if msg == '':
                continue
            if msg == aiohttp.WSMsgType.CLOSED:
                print("WebSocket 连接已关闭，停止接收消息")
                self.is_connected = False
                break

            try:
                json_data = json.loads(msg)
                call_back_function = self.events.match_event(json_data)
                if call_back_function is not None:
                    asyncio.create_task(call_back_function(json_data))
            except json.JSONDecodeError:
                print("接收到的消息无法解析为JSON:", msg)

    # 结束
    async def close(self):
        await self.ws.close()
        self.is_connected = False
        print("WebSocket 连接已关闭")


class Events:
    on_gameflow_phase_lobby = None
    on_gameflow_phase_none = None
    on_gameflow_phase_match_making = None

    def match_event(self, json_data):
        # 根据 json_data 的内容匹配并执行相应的事件
        if json_data[1] == 'OnJsonApiEvent_lol-gameflow_v1_gameflow-phase':
            if json_data[2]['data'] == 'Lobby':
                return self.on_gameflow_phase_lobby
            if json_data[2]['data'] == 'None':
                return self.on_gameflow_phase_none
            if json_data[2]['data'] == 'MatchMaking':
                return self.on_gameflow_phase_match_making

        return None


# 修改回调函数为异步函数
async def on_gameflow_phase_lobby(json_data):
    print("进入组队界面")

async def on_gameflow_phase_none(json_data):
    print("进入大厅")

async def on_gameflow_phase_match_making(json_data):
    print("进入匹配界面")

async def main_w2l():
    w2lcu = Websocket2Lcu()
    w2lcu.update_port_token(port=59578, token="TXgXXPK77dTA_bpQAVC4-A")
    
    # 先启动WebSocket连接和事件循环
    await w2lcu.start()
    
    # 后续可以随时更新事件处理函数
    w2lcu.events.on_gameflow_phase_lobby = on_gameflow_phase_lobby
    w2lcu.events.on_gameflow_phase_none = on_gameflow_phase_none
    w2lcu.events.on_gameflow_phase_match_making = on_gameflow_phase_match_making
    
    # 保持程序运行
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await w2lcu.close()



async def main_wm():
    ws = WebsocketManager(port=59578, token="TXgXXPK77dTA_bpQAVC4-A")
    await ws.connect()
    await ws.subscribe("OnJsonApiEvent_lol-gameflow_v1_gameflow-phase")
    while True:
        data = await ws.receive()
        print("已接收websocket消息:", data)


if __name__ == '__main__':
    asyncio.run(main_w2l())
