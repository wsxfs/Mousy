# -*- coding: utf-8 -*-
# @Time    : 2024/11/6 23:34
# @Author  : GZA
# @File    : _lcu_websocket.py

import asyncio
import json

import aiohttp

# import _lcu_manager as lcu
import _endpoints


class WebsocketManager:
    session: aiohttp.ClientSession
    ws: aiohttp.ClientWebSocketResponse

    def __init__(self, port, token):
        self.port = port
        self.token = token

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

        # 发送订阅消息
        await self.ws.send_json([5, "OnJsonApiEvent_lol-gameflow_v1_gameflow-phase"])

        # 循环接收WebSocket返回
        while True:
            msg = await self.ws.receive()
            msg_type = msg.type
            msg_data = msg.data
            msg_extra = msg.extra

            if msg_type != aiohttp.WSMsgType.TEXT:
                if msg.type == aiohttp.WSMsgType.CLOSED:
                    print("WebSocket 连接被关闭")
                    break

            if msg_data == '':
                continue

            print(f'接收到的msg_data:{msg_data}')


class Websocket2Lcu:
    # 映射事件名称到对应的 URI 和事件类型
    event_map = _endpoints.websocket_endpoints_dict

    def __init__(self, port, token):
        self.port = port
        self.token = token

        self.events = []
        self.subscribes = []

        self.on = EventHandler(self)
        self.task = None
        self.session = None
        self.ws = None

        self.is_connected = False
        self.on_close = None

    def update_port_and_token(self, port=None, token=None):
        """更新port和token"""
        # 如果传入port和token, 则更新
        if port is not None and token is not None:
            self.port, self.token = port, token
            return port, token

        # 如果对象中没有 port 和 token, 则尝试获取
        if self.port is None or self.token is None:
            new_port, new_token = lcu.get_port_and_token()
            self.port, self.token = new_port, new_token
            return new_port, new_token
        return self.port, self.token

    async def run_ws(self):
        self.session = aiohttp.ClientSession(
            auth=aiohttp.BasicAuth('riot', self.token),
            headers={
                'Content-type': 'application/json',
                'Accept': 'application/json'
            }
        )
        address = f'wss://127.0.0.1:{self.port}/'

        try:  # 尝试建立 WebSocket 连接
            self.ws = await self.session.ws_connect(address, ssl=False)
            self.is_connected = True
            print("WebSocket 连接已建立")
        except Exception as e:
            self.is_connected = False
            print(f"WebSocket 连接失败: {str(e)}")
            return

        # 订阅事件
        for event in self.events:
            await self.ws.send_json([5, event])

        while True:
            msg = await self.ws.receive()

            if msg.type == aiohttp.WSMsgType.TEXT and msg.data != '':
                data = json.loads(msg.data)[2]
                self.match_uri(data)
            elif msg.type == aiohttp.WSMsgType.CLOSED:
                print("WebSocket 连接被关闭")
                break

        await self.session.close()
        self.is_connected = False
        await self._trigger_on_close()

    async def _trigger_on_close(self):
        """触发用户定义的关闭回调函数"""
        if callable(self.on_close):
            await self.on_close()  # 确保回调是异步的

    def match_uri(self, data):
        for s in self.subscribes:
            # 匹配 URI 和事件类型
            if (data.get('uri') == s['uri'] and data.get('eventType') in s['type']):
                asyncio.create_task(s['callable'](data))

    async def start(self):
        """启动 WebSocket 连接。"""
        if self.port is None or self.token is None:
            print("未获取port或token，无法启动 WebSocket 连接。")
            return False

        if self.task is not None and not self.task.done():
            print("WebSocket 连接已存在，请等待连接关闭后再尝试启动。")
            return False

        self.task = asyncio.create_task(self.run_ws())
        return True

    async def close(self):
        if self.task is not None:
            self.task.cancel()
            await self.session.close()
            self.is_connected = False
            await self._trigger_on_close()

    async def subscribe(self, event_key, func):
        """订阅一个事件并关联到一个回调函数。"""
        event_info = self.event_map.get(event_key)
        if event_info:
            event = event_info['event']
            uri = event_info['uri']
            event_type = event_info['event_types']

            # 添加事件到订阅列表
            if event not in self.events:
                self.events.append(event)
                # 如果 WebSocket 已连接，发送订阅消息
                if self.ws is not None and not self.ws.closed:
                    await self.ws.send_json([5, event])

            # 添加订阅信息
            self.subscribes.append({
                'event': event,
                'uri': uri,
                'type': event_type,
                'callable': func
            })
        else:
            raise ValueError(f"Unknown event name: {event_key}")

    async def unsubscribe(self, func):
        """取消订阅之前订阅的函数。"""
        # 查找与函数关联的订阅
        subs_to_remove = [s for s in self.subscribes if s['callable'] == func]
        if not subs_to_remove:
            raise ValueError("Function not found in subscriptions")

        # 移除订阅
        for s in subs_to_remove:
            self.subscribes.remove(s)

        # 重建事件列表
        old_events = set(self.events)
        self.events = list(set(s['event'] for s in self.subscribes))

        # 确定已移除的事件
        events_removed = old_events - set(self.events)

        # 如果 WebSocket 正在运行，发送取消订阅消息
        if self.ws is not None and not self.ws.closed:
            for event in events_removed:
                await self.ws.send_json([6, event])


class EventHandler:
    def __init__(self, parent):
        self.parent = parent  # 引用 Websocket2Lcu 实例

    def __getitem__(self, key):
        def decorator(func):
            # 使用 event_map 获取 event、uri 和 type
            event_info = self.parent.event_map.get(key)
            if event_info:
                event = event_info['event']
                uri = event_info['uri']
                event_type = event_info['event_types']

                # 添加事件到订阅列表
                if event not in self.parent.events:
                    self.parent.events.append(event)

                # 存储订阅详细信息
                self.parent.subscribes.append({
                    'event': event,
                    'uri': uri,
                    'type': event_type,
                    'callable': func
                })
            else:
                raise ValueError(f"Unknown event name: {key}")
            return func

        return decorator

async def main():
    ws = WebsocketManager(port=51967, token="2T4HmwxwCAvUCq1N7ywAvw")
    await ws.connect()

if __name__ == '__main__':
    asyncio.run(main())
