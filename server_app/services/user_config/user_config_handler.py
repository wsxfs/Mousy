# -*- coding: utf-8 -*-
# @Time    : 2024/12/4 1:15
# @Author  : GZA
# @File    : user_config_handler.py

import asyncio
from typing import Optional

from server_app.services.lcu import Http2Lcu, Websocket2Lcu
from server_app.services.front import Websocket2Front
from .user_config import UserConfig
from pydantic import BaseModel
from typing import List, Dict

class GameState(BaseModel):
    gameflow_phase: str
    champ_select_session: Dict


class UserConfigHandler:
    selected_champion_id: Optional[int] = None
    summoner_id: Optional[int] = None
    swap_champion_button: bool = True
    def __init__(self, user_config: UserConfig, h2lcu: Http2Lcu, w2lcu: Websocket2Lcu, w2front: Websocket2Front):
        """初始化用户配置处理器
        
        Args:
            user_config: 用户配置实例
            h2lcu: HTTP客户端实例
            w2lcu: WebSocket客户端实例
            w2front: 前端WebSocket客户端实例
        """
        self.user_config = user_config
        self.h2lcu = h2lcu
        self.w2lcu = w2lcu
        self.w2front = w2front
        self._register_events()
        self.all_events = [
            "OnJsonApiEvent_lol-gameflow_v1_gameflow-phase",
            "OnJsonApiEvent_lol-champ-select_v1_session",
        ]
        self.game_state = GameState(gameflow_phase="None", champ_select_session=dict())
    
    def _register_events(self):
        # 匹配事件
        self.w2lcu.events.on_gameflow_phase_none([self._handle_gameflow_phase_none])  # 大厅
        self.w2lcu.events.on_gameflow_phase_lobby([self._handle_gameflow_phase_lobby])  # 组队中
        self.w2lcu.events.on_gameflow_phase_match_making([self._handle_match_making])  # 匹配中
        self.w2lcu.events.on_gameflow_phase_ready_check([self._handle_gameflow_phase_ready_check])  # 确认对局
        self.w2lcu.events.on_gameflow_phase_champ_select([self._handle_gameflow_phase_champ_select])  # 选择英雄阶段
        self.w2lcu.events.on_gameflow_phase_game_start([self._handle_gameflow_phase_game_start])  # 游戏开始
        self.w2lcu.events.on_champ_select_session([self._handle_champ_select_session])  # 选人阶段改变
        
        
    
    
    async def _handle_gameflow_phase_none(self, json_data):
        print("进入大厅状态")
        print(json_data)
        await self.w2front.broadcast_event("gameflow_phase", "none")

    async def _handle_gameflow_phase_lobby(self, json_data):
        print("进入组队中状态")
        print(json_data)
        await self.w2front.broadcast_event("gameflow_phase", "lobby")
    
    async def _handle_match_making(self, json_data):
        print("进入匹配状态")
        print(json_data)
        await self.w2front.broadcast_event("gameflow_phase", "match_making")

    async def _handle_gameflow_phase_ready_check(self, json_data):
        print("进入确认对局状态")
        print(json_data)
        if self.user_config.settings['auto_accept']:
            await self.h2lcu.accept_matchmaking()  # 接受匹配
        await self.w2front.broadcast_event("gameflow_phase", "ready_check")

    async def _handle_gameflow_phase_champ_select(self, json_data):
        print("进入选择英雄状态")
        print(json_data)
        self.swap_champion_button = True
        await self.w2front.broadcast_event("gameflow_phase", "champ_select")
        champ_select_state = await self.h2lcu.get_champ_select_state()
        current_champion_id = await self._get_current_champion_id_by_data(champ_select_state)
        await asyncio.sleep(0.3)
        await self.w2front.broadcast_event("champ_select_changed", f"current_champion={current_champion_id},bench_champions={[]}")
    
    async def _handle_gameflow_phase_game_start(self, json_data):
        print("进入游戏开始状态")
        print(json_data)
        await self.w2front.broadcast_event("gameflow_phase", "game_start")



    async def _handle_champ_select_session(self, json_data):
        print("触发事件: 选人阶段改变")

        # 获取当前玩家的英雄ID
        current_champion_id = await self._get_current_champion_id_by_data(json_data[2]['data'])
        print(f"\t当前玩家英雄ID: {current_champion_id}")

        # 获取备用席英雄ID
        bench_champions = json_data[2]['data']['benchChampions']
        bench_champion_ids = [champion['championId'] for champion in bench_champions]
        print(f"\t备用席英雄ID: {bench_champion_ids}")

        # 发送选人阶段改变事件信息：当前玩家的英雄ID和备用席英雄ID
        await self.w2front.broadcast_event("champ_select_changed", f"current_champion={current_champion_id},bench_champions={bench_champion_ids}")

        if not self.swap_champion_button:
            return

        # 获取 Pydantic 设置
        pydantic_settings = self.user_config.get_pydantic_settings()
        aram_auto_pick_enabled = pydantic_settings.aram_auto_pick_enabled  # 是否启用ARAM自动选择功能
        aram_auto_pick_delay = pydantic_settings.aram_auto_pick_delay  # 延迟时间
        aram_auto_pick_champion_ids = pydantic_settings.aram_auto_pick_champions  # 优先级列表

        print(f"用户设置如下:")
        print(f"\tARAM自动选择功能: {aram_auto_pick_enabled}")
        print(f"\tARAM自动选择延迟: {aram_auto_pick_delay} 秒")
        print(f"\tARAM自动选择优先级: {aram_auto_pick_champion_ids}")

        # 检查是否启用了ARAM自动选择功能
        if not pydantic_settings.aram_auto_pick_enabled:
            print("\tARAM自动选择功能未启用")
            return

        print("通过json_data获取到的信息如下:")

        

        # 创建可选英雄池（当前英雄 + 备用席英雄）
        available_champion_ids = bench_champion_ids + [current_champion_id]
        print(f"\t可选英雄池: {available_champion_ids}")

        # 在可选英雄池中找到优先级最高的英雄
        best_champion_id = None
        for champion_id in aram_auto_pick_champion_ids:
            if champion_id in available_champion_ids:
                best_champion_id = champion_id
                break
        
        self.selected_champion_id = best_champion_id

        print(f"\t分析得出的最优英雄ID: {best_champion_id}")

        print(f"结论如下:")

        if best_champion_id is None:
            print("\t无可选英雄")
            return

        if best_champion_id == current_champion_id:
            print("\t当前英雄已经是最优选择")
            return
        
        print("\t需要交换英雄")
        
        # 等待延迟时间后发送交换请求
        print(f"\t等待 {aram_auto_pick_delay} 秒后发送交换请求")
        if aram_auto_pick_delay > 0:
            await asyncio.sleep(aram_auto_pick_delay)
        
        # 延迟后再次检查
        if not self.swap_champion_button:
            return
        
        await self.h2lcu.bench_swap(best_champion_id)
    
    async def _get_current_champion_id_by_data(self, data):
        # 获取当前玩家的英雄ID
        localPlayerCellId = data['localPlayerCellId']
        myTeam_list = data['myTeam']
        for player in myTeam_list:
            if player['cellId'] == localPlayerCellId:
                return player['championId']
        return None


    # async def _send_requests_periodically(self, best_champion_id):
    #     start_time = asyncio.get_event_loop().time()
    #     await self.h2lcu.bench_swap(best_champion_id)
    #     print(f"2s后开始发送请求")
    #     while True:
    #         current_time = asyncio.get_event_loop().time()
    #         elapsed_time = current_time - start_time
    #         if elapsed_time > 3.5:
    #             break
    #         if 2 <= elapsed_time <= 3.5:
    #             print(f"尝试交换到最优英雄ID: {best_champion_id}")
    #             await self.h2lcu.bench_swap(best_champion_id)
    #         await asyncio.sleep(0.1)  # 每0.1秒发送一次请求
    #     print("停止发送请求")

    async def bench_swap(self, champion_id: int=None):
        if champion_id:
            await self.h2lcu.bench_swap(champion_id)
        else:
            await self.h2lcu.bench_swap(self.selected_champion_id)

