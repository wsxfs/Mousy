# -*- coding: utf-8 -*-
# @Time    : 2024/12/3 21:40
# @Author  : GZA
# @File    : websocket2lcu.py

import asyncio
import json

import aiohttp
from typing import List

from server_app.services.front.websocket2front import Websocket2Front
from server_app.services.lcu.get_port_and_token import get_port_and_token_by_tasklist

class WebsocketManager:
    session: aiohttp.ClientSession
    ws: aiohttp.ClientWebSocketResponse

    def __init__(self, port, token):
        self.port = port
        self.token = token
        self.is_connected = False
        # 已订阅事件集合
        self.subscribed_events = set()

    # 更新port和token
    def update_port_and_token(self, port, token):
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
        self.subscribed_events.clear()
        await self.ws.close()

    # 发送订阅消息
    async def subscribe(self, lcu_event: str):
        await self.ws.send_json([5, lcu_event])
        self.subscribed_events.add(lcu_event)

    # 发送取消订阅消息
    async def unsubscribe(self, lcu_event: str):
        await self.ws.send_json([6, lcu_event])
        self.subscribed_events.discard(lcu_event)

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


class Websocket2Lcu:
    def __init__(self, port=None, token=None, w2front: Websocket2Front = None) -> None:
        self.w2front = w2front
        self.port = port
        self.token = token
        self.ws = WebsocketManager(port=port, token=token)
        self.events = Events()
        self.all_events = self.events.all_events
        self.event_loop_task = None
        self.auto_connect_task = None
        self.on_port_token_update = None
        # 最后设置 is_connected，这样前面的属性都已经初始化完成
        self.is_connected = False

    def __setattr__(self, name, value):
        # 先设置属性
        super().__setattr__(name, value)
        
        # 如果是 is_connected 属性变化且有 w2front，则使用 w2front.sync_data 发送
        if name == 'is_connected' and hasattr(self, 'w2front') and self.w2front:
            self.w2front.sync_data.lcu_connected = value

    # 更新port和token,以及ws的port和token
    def update_port_and_token(self, port, token):
        self.port, self.token = port, token
        self.ws.update_port_and_token(port, token)

    # 连接Websocket
    async def connect(self):
        print("Websocket2Lcu 正在连接")
        await self.ws.connect()
        self.is_connected = True
        print("Websocket2Lcu 连接成功")

    async def start(self):
        # 连接
        await self.connect()
        # 订阅
        for event in self.all_events:
            await self.ws.subscribe(event)
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
                call_back_functions = self.events.match_event(json_data)
                if call_back_functions:
                    # 分离异步和同步函数
                    async_funcs = []
                    sync_funcs = []
                    for func in call_back_functions:
                        if asyncio.iscoroutinefunction(func):
                            async_funcs.append(func)
                        else:
                            sync_funcs.append(func)
                    
                    # 使用任务队列执行异步函数
                    if async_funcs:
                        # 创建所有任务
                        tasks = []
                        for func in async_funcs:
                            task = asyncio.create_task(func(json_data))
                            tasks.append(task)
                    
                    # 顺序执行同步函数
                    loop = asyncio.get_event_loop()
                    for func in sync_funcs:
                        await loop.run_in_executor(None, func, json_data)
                        
            except json.JSONDecodeError:
                print("接收到的消息无法解析为JSON:", msg)

    # 结束
    async def close(self):

        # 取消事件循环任务
        if self.event_loop_task is not None:
            self.event_loop_task.cancel()
            try:
                await self.event_loop_task
                print("事件循环任务已取消")
            except asyncio.CancelledError:
                print("事件循环任务已取消")
            except Exception as e:
                print(f"事件循环任务取消失败: {e}")

        await self.ws.close()
        self.is_connected = False
        print("WebSocket 连接已关闭")

    async def start_auto_connect(self, on_port_token_update=None):
        """开始自动连接检测"""
        self.on_port_token_update = on_port_token_update
        if self.auto_connect_task is None:
            self.auto_connect_task = asyncio.create_task(self._auto_connect_loop())

    async def _auto_connect_loop(self):
        """自动连接循环"""
        while True:
            try:
                # 如果已连接，等待连接断开
                while self.is_connected:
                    await asyncio.sleep(1)
                
                # 未连接时，尝试获取新的连接信息
                port, token = get_port_and_token_by_tasklist()
                if port and token:
                    try:
                        # 如果有回调函数，先更新app.state
                        if self.on_port_token_update:
                            await self.on_port_token_update(port, token)
                        self.update_port_and_token(port, token)
                        await self.start()
                    except Exception as e:
                        print(f"自动连接失败: {e}")
                        await asyncio.sleep(5)  # 连接失败后等待5秒再试
                else:
                    await asyncio.sleep(5)  # 未检测到客户端时等待5秒再试
                    
            except Exception as e:
                print(f"自动连接循环发生错误: {e}")
                await asyncio.sleep(5)


class GameflowPhaseEvent:
    # 事件列表
    self_event:list = []
    lobby:list = []
    none:list = []
    match_making:list = []
    ready_check:list = []
    champ_select:list = []
    game_start:list = []
    end_of_game:list = []
    def match_event(self, json_data):
        if json_data[2]['data'] == 'Lobby':
            return self.lobby
        if json_data[2]['data'] == 'None':
            return self.none
        if json_data[2]['data'] == 'Matchmaking':
            return self.match_making
        if json_data[2]['data'] == 'ReadyCheck':
            return self.ready_check
        if json_data[2]['data'] == 'ChampSelect':
            return self.champ_select
        if json_data[2]['data'] == 'GameStart':
            return self.game_start
        if json_data[2]['data'] == 'InProgress':
            return []
        if json_data[2]['data'] == 'WaitingForStats':
            return []
        if json_data[2]['data'] == 'PreEndOfGame':
            return []
        if json_data[2]['data'] == 'EndOfGame':
            return self.end_of_game
        return []

class ChampSelectSessionEvent:
    self_event:list = []
    def match_event(self, json_data):
        return []

class Events:
    def __init__(self):
        self.gameflow_phase_event = GameflowPhaseEvent()
        self.champ_select_session_event = ChampSelectSessionEvent()
        self.all_events = [
            "OnJsonApiEvent_lol-gameflow_v1_gameflow-phase",
            "OnJsonApiEvent_lol-champ-select_v1_session",
        ]

    def match_event(self, json_data) -> list:
        # 根据 json_data 的内容匹配并执行相应的事件
        if json_data[1] == 'OnJsonApiEvent_lol-gameflow_v1_gameflow-phase':
            return self.gameflow_phase_event.match_event(json_data) + self.gameflow_phase_event.self_event 
        if json_data[1] == 'OnJsonApiEvent_lol-champ-select_v1_session':
            return self.champ_select_session_event.match_event(json_data) + self.champ_select_session_event.self_event
        return []

    # 自定义对应事件关系
    def on_gameflow_phase(self, callback_functions:list):
        self.gameflow_phase_event.self_event = callback_functions

    def on_gameflow_phase_lobby(self, callback_functions:list):
        self.gameflow_phase_event.lobby = callback_functions

    def on_gameflow_phase_none(self, callback_functions:list):
        self.gameflow_phase_event.none = callback_functions

    def on_gameflow_phase_match_making(self, callback_functions:list):
        self.gameflow_phase_event.match_making = callback_functions

    def on_gameflow_phase_ready_check(self, callback_functions:list):
        self.gameflow_phase_event.ready_check = callback_functions
    
    def on_gameflow_phase_champ_select(self, callback_functions:list):
        self.gameflow_phase_event.champ_select = callback_functions
    
    def on_gameflow_phase_game_start(self, callback_functions:list):
        self.gameflow_phase_event.game_start = callback_functions

    def on_gameflow_phase_end_of_game(self, callback_functions:list):
        self.gameflow_phase_event.end_of_game = callback_functions


    def on_champ_select_session(self, callback_functions:list):
        self.champ_select_session_event.self_event = callback_functions



# 测试用的同步回调函数
def on_gameflow_phase_lobby_sync(json_data):
    print("同步函数: 进入组队界面")


# 测试用的异步回调函数
async def on_gameflow_phase_none_async(json_data):
    print("异步函数: 进入大厅")


async def on_gameflow_phase_match_making(json_data):
    print("进入匹配界面")


async def main_w2l():
    w2lcu = Websocket2Lcu()
    w2lcu.update_port_and_token(port=59578, token="TXgXXPK77dTA_bpQAVC4-A")

    await w2lcu.start()

    # 可以同时使用同步和异步回调函数
    w2lcu.events.on_gameflow_phase_lobby(on_gameflow_phase_lobby_sync)  # 同步函数
    w2lcu.events.on_gameflow_phase_none(on_gameflow_phase_none_async)  # 异步函数
    w2lcu.events.on_gameflow_phase_match_making(on_gameflow_phase_match_making)  # 异步函数

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
