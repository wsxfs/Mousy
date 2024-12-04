# -*- coding: utf-8 -*-
# @Time    : 2024/12/4 1:15
# @Author  : GZA
# @File    : user_config_handler.py

import asyncio
from typing import Optional

from server_app.services.lcu import Http2Lcu, Websocket2Lcu
from .user_config import UserConfig


class UserConfigHandler:
    selected_champion_id: Optional[int] = None
    summoner_id: Optional[int] = None
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

    async def _handle_champ_select_session_changed(self, json_data):
        print("选人阶段改变")   

        # 获取当前玩家的英雄ID
        localPlayerCellId = json_data[2]['data']['localPlayerCellId']
        myTeam_list = json_data[2]['data']['myTeam']
        current_champion_id = None
        for player in myTeam_list:
            if player['cellId'] == localPlayerCellId:
                current_champion_id = player['championId']
                break
        print(f"当前玩家英雄ID: {current_champion_id}")

        # 获取备用席英雄ID
        bench_champions = json_data[2]['data']['benchChampions']
        bench_champion_ids = [champion['championId'] for champion in bench_champions]
        print(f"备用席英雄ID: {bench_champion_ids}")

        # 创建可选英雄池（当前英雄 + 备用席英雄）
        available_champion_ids = bench_champion_ids + [current_champion_id]
        print(f"可选英雄池: {available_champion_ids}")

        # 获取配置的优先级列表
        pydantic_settings = self.user_config.get_pydantic_settings()
        aram_auto_pick_champion_ids = pydantic_settings.aram_auto_pick_champions
        print(f"配置的优先级列表: {aram_auto_pick_champion_ids}")
        
        # 在可选英雄池中找到优先级最高的英雄
        best_champion_id = None
        for champion_id in aram_auto_pick_champion_ids:
            if champion_id in available_champion_ids:
                best_champion_id = champion_id
                break
        
        # 如果找到目标英雄且不是当前英雄，则进行交换
        if best_champion_id and best_champion_id != current_champion_id:
            print(f"找到最优英雄ID: {best_champion_id}")
            self.selected_champion_id = best_champion_id
            await self.h2lcu.bench_swap(self.selected_champion_id)
        else:
            print("当前英雄已经是最优选择")
    
    async def bench_swap(self, champion_id: int=None):
        if champion_id:
            await self.h2lcu.bench_swap(champion_id)
        else:
            await self.h2lcu.bench_swap(self.selected_champion_id)

