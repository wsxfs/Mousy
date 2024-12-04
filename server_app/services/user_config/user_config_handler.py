# -*- coding: utf-8 -*-
# @Time    : 2024/12/4 1:15
# @Author  : GZA
# @File    : user_config_handler.py

import asyncio
from typing import Optional

from server_app.services.lcu import Http2Lcu, Websocket2Lcu
from .user_config import UserConfig


class UserConfigHandler:
    def __init__(self, user_config: UserConfig, h2lcu: Http2Lcu, w2lcu: Websocket2Lcu):
        """初始化用户配置处理器
        
        Args:
            user_config: 用户配置实例
            h2lcu: HTTP客户端实例
            w2lcu: WebSocket客户端实例
        """
        self.user_config = user_config
        self.h2lcu = h2lcu
        self.w2lcu = w2lcu
        self._register_events()
        self.all_events = [
            "OnJsonApiEvent_lol-gameflow_v1_gameflow-phase",
            "OnJsonApiEvent_lol-champ-select_v1_session",
        ]
    
    def _register_events(self):
        # 匹配事件
        self.w2lcu.events.on_gameflow_phase_match_making(self._handle_match_making)
        self.w2lcu.events.on_gameflow_phase_none(self._handle_gameflow_phase_none)
        self.w2lcu.events.on_gameflow_phase_ready_check(self._handle_gameflow_phase_ready_check)  # 确认对局
        self.w2lcu.events.on_champ_select_session_changed(self._handle_champ_select_session_changed)  # 选人阶段改变
        
    async def _handle_match_making(self, json_data):
        print("进入匹配状态")
        print(json_data)
    
    async def _handle_gameflow_phase_none(self, json_data):
        print("进入大厅状态")
        print(json_data)

    async def _handle_gameflow_phase_ready_check(self, json_data):
        print("进入确认对局状态")
        print(json_data)
        if self.user_config.settings['auto_accept']:
            await self.h2lcu.accept_matchmaking()  # 接受匹配
        # await self.h2lcu.decline_matchmaking()  # 拒绝匹配

    async def _handle_champ_select_session_changed(self, json_data):
        print("选人阶段改变")
        print(json_data)
