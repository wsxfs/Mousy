# -*- coding: utf-8 -*-
# @Time    : 2024/12/4 1:15
# @Author  : GZA
# @File    : user_config_handler.py

import asyncio
from typing import Optional

from server_app.services.lcu import Http2Lcu, Websocket2Lcu
from server_app.services.front import Websocket2Front
from .user_config import UserConfig, SettingsModel
from pydantic import BaseModel
from typing import List, Dict

class GameState(BaseModel):
    gameflow_phase: Optional[str] = None
    champ_select_session: Optional[Dict] = None

class AutoBPSetting(BaseModel):
    enabled: bool = False
    delay: float = 0
    champions: List[int] = []


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
        self.game_state = GameState()  # 储存websocket2lcu的事件数据
        self.sync_front_data = self.w2front.sync_data

        self.done_action_ids = []
        self.if_done_primary_selection = False
        self.game_mode = None

    
    def _register_events(self):
        # 匹配事件
        self.w2lcu.events.on_gameflow_phase([self._handle_gameflow_phase])  # 游戏状态改变总事件
        self.w2lcu.events.on_gameflow_phase_none([self._handle_gameflow_phase_none])  # 大厅
        self.w2lcu.events.on_gameflow_phase_lobby([self._handle_gameflow_phase_lobby])  # 组队中
        self.w2lcu.events.on_gameflow_phase_match_making([self._handle_match_making])  # 匹配中
        self.w2lcu.events.on_gameflow_phase_ready_check([self._handle_gameflow_phase_ready_check])  # 确认对局
        self.w2lcu.events.on_gameflow_phase_champ_select([self._handle_gameflow_phase_champ_select])  # 选择英雄阶段
        self.w2lcu.events.on_gameflow_phase_game_start([self._handle_gameflow_phase_game_start])  # 游戏开始
        self.w2lcu.events.on_gameflow_phase_end_of_game([self._handle_gameflow_phase_end_of_game])  # 游戏结束

        self.w2lcu.events.on_champ_select_session([self._handle_champ_select_session])  # 选人阶段改变
        
        
    async def _handle_gameflow_phase(self, json_data):
        print("触发事件: 游戏状态改变")
        print(f"改变后的游戏状态: {json_data[2]['data']}")

        # 退出选人阶段时，清空选人阶段数据
        if json_data[2]['data'] != "ChampSelect":  
            self.game_state.champ_select_session = None
            self.done_action_ids = []
            self.if_done_primary_selection = False
            self.game_mode = None

    async def _handle_gameflow_phase_none(self, json_data):
        print("进入大厅状态")
        self.sync_front_data.gameflow_phase = "none"


    async def _handle_gameflow_phase_lobby(self, json_data):
        print("进入组队中状态")
        self.sync_front_data.gameflow_phase = "lobby"

    async def _handle_match_making(self, json_data):
        print("进入匹配状态")
        self.sync_front_data.gameflow_phase = "match_making"

    async def _handle_gameflow_phase_ready_check(self, json_data):
        print("进入确认对局状态")
        self.sync_front_data.gameflow_phase = "ready_check"
        if self.user_config.settings['auto_accept']:
            await self.h2lcu.accept_matchmaking()  # 接受匹配

    async def _handle_gameflow_phase_champ_select(self, json_data):
        print("进入选择英雄状态")
        self.sync_front_data.gameflow_phase = "champ_select"
        self.swap_champion_button = True

        # 等待选择英雄阶段数据
        while self.game_state.champ_select_session is None:
            await asyncio.sleep(0.1)

        # 获取双方队伍的puuid
        my_team_puuid_list, their_team_puuid_list = await self._get_puuids_by_champ_select_session(self.game_state.champ_select_session)
        self.sync_front_data.my_team_puuid_list = my_team_puuid_list
        self.sync_front_data.their_team_puuid_list = their_team_puuid_list

        # 获取当前玩家的英雄ID
        champ_select_state = await self.h2lcu.get_champ_select_state()
        current_champion_id = await self._get_current_champion_id_by_data(champ_select_state)

        # 获取战绩数据
        await self._fetch_team_match_histories()

        self.sync_front_data.current_champion = current_champion_id
        self.sync_front_data.bench_champions = []

    async def _fetch_team_match_histories(self):
        """获取队伍成员的战绩数据"""
        my_team_history = {}
        their_team_history = {}
        
        # 获取我方战绩
        if self.sync_front_data.my_team_puuid_list:
            for puuid in self.sync_front_data.my_team_puuid_list:
                try:
                    match_history = await self.h2lcu.get_match_history(
                        puuid=puuid,
                        beg_index=0,
                        end_index=10  # 获取最近10场比赛
                    )
                    my_team_history[puuid] = match_history
                except Exception as e:
                    print(f"获取玩家{puuid}战绩失败: {e}")
                    my_team_history[puuid] = None

        # 获取敌方战绩
        if self.sync_front_data.their_team_puuid_list:
            for puuid in self.sync_front_data.their_team_puuid_list:
                try:
                    match_history = await self.h2lcu.get_match_history(
                        puuid=puuid,
                        beg_index=0,
                        end_index=10
                    )
                    their_team_history[puuid] = match_history
                except Exception as e:
                    print(f"获取玩家{puuid}战绩失败: {e}")
                    their_team_history[puuid] = None

        # 更新前端数据
        self.sync_front_data.my_team_match_history = my_team_history
        self.sync_front_data.their_team_match_history = their_team_history
        print(f"获取到的我方战绩数据: {self.sync_front_data.my_team_match_history}")
        print(f"获取到的敌方战绩数据: {self.sync_front_data.their_team_match_history}")

    async def _handle_gameflow_phase_game_start(self, json_data):
        print("进入游戏开始状态")
        self.sync_front_data.gameflow_phase = "game_start"
        # 获取当前puuid
        if self.sync_front_data.current_puuid is None: 
            current_summoner = await self.h2lcu.get_current_summoner()
            self.sync_front_data.current_puuid = current_summoner.puuid
        print(f"进入游戏开始状态时当前puuid: {self.sync_front_data.current_puuid}")
        data = await self.h2lcu.get_game_state_detail()
        
        # 等待游戏状态达到游戏开始阶段
        while data is None:
            await asyncio.sleep(0.1)
            data = await self.h2lcu.get_game_state_detail()
            
        print("进入函数_get_puuids_by_gameflow_session")
        my_team_puuid_list, their_team_puuid_list = await self._get_puuids_by_gameflow_session(data, self.sync_front_data.current_puuid)
        print(f"当前队伍的puuid: {my_team_puuid_list}")
        print(f"敌方队伍的puuid: {their_team_puuid_list}")
        self.sync_front_data.my_team_puuid_list = my_team_puuid_list
        self.sync_front_data.their_team_puuid_list = their_team_puuid_list
        
        # 获取战绩数据
        await self._fetch_team_match_histories()

    async def _handle_gameflow_phase_end_of_game(self, json_data):
        print("进入游戏结束状态")
        self.sync_front_data.gameflow_phase = "end_of_game"

    async def _handle_champ_select_session(self, json_data):
        print("触发事件: 选人阶段改变")

        # 如果事件类型为Delete，则不处理
        if json_data[2]['eventType'] == "Delete":
            return
        
        self.game_state.champ_select_session = json_data[2]['data']  # 储存选人阶段数据(双方puuid)

        # 获取游戏模式
        if self.game_mode is None:
            self.game_mode = await self.h2lcu.get_game_mode()
        
        """根据json_data获取信息"""
        # 获取当前玩家的英雄ID
        current_champion_id = await self._get_current_champion_id_by_data(json_data[2]['data'])
        # 是否存在备用席
        benchEnabled = json_data[2]['data']['benchEnabled']
        # 获取备用席英雄ID
        bench_champions = json_data[2]['data']['benchChampions']
        bench_champion_ids = [champion['championId'] for champion in bench_champions]
        # 发送选人阶段改变事件信息：当前玩家的英雄ID和备用席英雄ID
        self.sync_front_data.current_champion = current_champion_id
        self.sync_front_data.bench_champions = bench_champion_ids
        # 获取当前选择英雄流程
        champ_select_phase = json_data[2]['data']['timer']['phase']  # ['PLANNING', 'BAN_PICK', 'FINALIZATION']
        # 获取当前玩家cellId
        localPlayerCellId = json_data[2]['data']['localPlayerCellId']
        # 获取cell、position
        local_player_cell = None
        local_player_position = None
        for player in json_data[2]['data']['myTeam']:
            if player['cellId'] == localPlayerCellId:
                local_player_cell = player['cellId']
                local_player_position = player['assignedPosition']
                break

        # 获取所有actions
        actions = json_data[2]['data']['actions']
        # 获取所有BP信息、当前玩家pick id、当前玩家正在进行的操作
        Ban_actions = []
        Pick_actions = []
        current_pick_id = None
        current_doing_actions = []
        for action_group in actions:
            for action in action_group:
                # 获取所有BP信息
                if action['type'] == 'ban':
                    Ban_actions.append(action)
                elif action['type'] == 'pick':
                    Pick_actions.append(action)
                
                # 获取当前玩家pick id
                if action['actorCellId'] == localPlayerCellId and action['type'] == 'pick':
                    current_pick_id = action['id']

                # 获取当前玩家正在进行的操作
                if action['actorCellId'] == localPlayerCellId and action['isInProgress'] == True:
                    current_doing_actions.append(action)
        
        # 获取所有已完成的action中的BP英雄以及队友预选的英雄
        BP_champion_ids = []
        teammates_primary_selection_champion_ids = []
        for action in Ban_actions:
            if action['completed']:
                BP_champion_ids.append(action['championId'])
        for action in Pick_actions:
            if action['completed']:
                BP_champion_ids.append(action['championId'])
            if action['isAllyAction'] and not action['completed'] and action['championId'] != 0:
                teammates_primary_selection_champion_ids.append(action['championId'])
        print(f"已完成的BP英雄ID: {BP_champion_ids}")
        print(f"队友预选的英雄ID: {teammates_primary_selection_champion_ids}")

        """根据游戏模式提取用户配置信息"""
        pydantic_settings: SettingsModel = self.user_config.get_pydantic_settings()

        auto_pick_enabled = False  # 自动选择开关
        auto_pick_champion_ids = []  # 自动选择英雄列表
        auto_pick_delay = 0  # 自动选择延迟

        auto_ban_enabled = False  # 自动禁用开关
        auto_ban_champion_ids = []  # 自动禁用英雄列表
        auto_ban_delay = 0  # 自动禁用延迟

        if self.game_mode == 'ARAM':
            # pick
            auto_pick_enabled = pydantic_settings.aram.pick.enabled
            auto_pick_delay = pydantic_settings.aram.pick.delay
            auto_pick_champion_ids = pydantic_settings.aram.pick.champions
        elif self.game_mode in ['CLASSIC', 'PRACTICETOOL']:
            if local_player_position:
                # 排位
                auto_pick_enabled = pydantic_settings.ranked.pick.enabled
                auto_pick_delay = pydantic_settings.ranked.pick.delay
                auto_pick_champion_ids = pydantic_settings.ranked.pick.champions.get_champions_by_pos(local_player_position)
                auto_ban_enabled = pydantic_settings.ranked.ban.enabled
                auto_ban_delay = pydantic_settings.ranked.ban.delay
                auto_ban_champion_ids = pydantic_settings.ranked.ban.champions.get_champions_by_pos(local_player_position)
            else:
                # 非排位
                # pick
                auto_pick_enabled = pydantic_settings.normal.pick.enabled
                auto_pick_delay = pydantic_settings.normal.pick.delay
                auto_pick_champion_ids = pydantic_settings.normal.pick.champions
                # # ban
                # auto_ban_enabled = pydantic_settings.normal.ban.enabled
                # auto_ban_delay = pydantic_settings.normal.ban.delay
                # auto_ban_champion_ids = pydantic_settings.normal.ban.champions
        
        auto_ban_setting = AutoBPSetting(enabled=auto_ban_enabled, delay=auto_ban_delay, champions=auto_ban_champion_ids)
        auto_pick_setting = AutoBPSetting(enabled=auto_pick_enabled, delay=auto_pick_delay, champions=auto_pick_champion_ids)

        

        """根据配置信息和选人阶段信息执行操作"""
        # 预选英雄
        if not self.if_done_primary_selection and  auto_pick_enabled and auto_pick_champion_ids:
            await self._do_primary_selection(auto_pick_setting, current_pick_id)
        
        # BP操作
        if champ_select_phase == 'BAN_PICK':
            await self._do_bp(auto_ban_setting, auto_pick_setting, BP_champion_ids, teammates_primary_selection_champion_ids, current_doing_actions)
        
        # 候选席操作
        if benchEnabled and auto_pick_enabled and self.swap_champion_button and auto_pick_champion_ids:
            await self._do_bench_swap(bench_champion_ids, current_champion_id, auto_pick_setting)
    
    async def _do_primary_selection(self, auto_pick_setting, current_pick_id):
        """预选英雄"""
        # 解构配置
        auto_pick_enabled = auto_pick_setting.enabled
        auto_pick_champion_ids = auto_pick_setting.champions
        auto_pick_delay = auto_pick_setting.delay

        # 预选英雄
        await self.h2lcu.pick_champion(current_pick_id, auto_pick_champion_ids[0], completed=False)
        self.if_done_primary_selection = True
        print(f"预选英雄完成")


    async def _do_bp(self, auto_ban_setting, auto_pick_setting, BP_champion_ids, teammates_primary_selection_champion_ids, current_doing_actions):
        """执行BP操作"""
        # 解构配置
        auto_ban_enabled = auto_ban_setting.enabled
        auto_ban_champion_ids = auto_ban_setting.champions
        auto_ban_delay = auto_ban_setting.delay

        auto_pick_enabled = auto_pick_setting.enabled
        auto_pick_champion_ids = auto_pick_setting.champions
        auto_pick_delay = auto_pick_setting.delay

        # 计算当前玩家需要禁用的首选英雄
        ban_champion_id = None
        if auto_ban_enabled and auto_ban_champion_ids:
            for champion_id in auto_ban_champion_ids:
                if champion_id not in BP_champion_ids and champion_id not in teammates_primary_selection_champion_ids:
                    ban_champion_id = champion_id
                    break
        
        # 计算当前玩家需要选择的首选英雄
        pick_champion_id = None
        if auto_pick_enabled and auto_pick_champion_ids:
            for champion_id in auto_pick_champion_ids:
                if champion_id not in BP_champion_ids:
                    pick_champion_id = champion_id
                    break
        
        print(f"当前玩家需要禁用的首选英雄ID: {ban_champion_id}")
        print(f"当前玩家需要选择的首选英雄ID: {pick_champion_id}")

        if current_doing_actions:
            action = current_doing_actions[0]
            if action['id'] not in self.done_action_ids:

                # 执行BP操作
                if action['type'] == 'ban' and ban_champion_id is not None:
                    if auto_ban_delay > 0:
                        await asyncio.sleep(auto_ban_delay)
                    await self.h2lcu.ban_champion(action['id'], ban_champion_id, completed=True)
                elif action['type'] == 'pick' and pick_champion_id is not None:
                    if auto_pick_delay > 0:
                        await asyncio.sleep(auto_pick_delay)
                    await self.h2lcu.pick_champion(action['id'], pick_champion_id, completed=True)

                # 记录执行过的action
                self.done_action_ids.append(action['id'])

    async def _do_bench_swap(self, bench_champion_ids, current_champion_id, auto_pick_setting):
        """执行交换英雄操作"""
        # 解构配置
        auto_pick_enabled = auto_pick_setting.enabled
        auto_pick_champion_ids = auto_pick_setting.champions
        auto_pick_delay = auto_pick_setting.delay

        # 创建可选英雄池（当前英雄 + 备用席英雄）
        available_champion_ids = bench_champion_ids + [current_champion_id]
        print(f"\t可选英雄池: {available_champion_ids}")

        # 在可选英雄池中找到优先级最高的英雄
        best_champion_id = None
        for champion_id in auto_pick_champion_ids:
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
        print(f"\t等待 {auto_pick_delay} 秒后发送交换请求")
        if auto_pick_delay > 0:
            await asyncio.sleep(auto_pick_delay)
        
        # 延迟后再次检查
        if not self.swap_champion_button:
            return
        
        await self.h2lcu.bench_swap(best_champion_id)
        
    
    # async def _handle_champ_select_session_bench(self, json_data):
    #     print("触发事件: 选人阶段改变(bench)")

    #     # 获取当前玩家的英雄ID
    #     current_champion_id = await self._get_current_champion_id_by_data(json_data[2]['data'])
    #     print(f"\t当前玩家英雄ID: {current_champion_id}")

    #     # 获取备用席英雄ID
    #     bench_champions = json_data[2]['data']['benchChampions']
    #     bench_champion_ids = [champion['championId'] for champion in bench_champions]
    #     print(f"\t备用席英雄ID: {bench_champion_ids}")

    #     # 发送选人阶段改变事件信息：当前玩家的英雄ID和备用席英雄ID
    #     self.sync_front_data.current_champion = current_champion_id
    #     self.sync_front_data.bench_champions = bench_champion_ids

    #     if not self.swap_champion_button:
    #         return

    #     # 获取 Pydantic 设置
    #     pydantic_settings = self.user_config.get_pydantic_settings()
    #     aram_auto_pick_enabled = pydantic_settings.aram_auto_pick_enabled  # 是否启用ARAM自动选择功能
    #     aram_auto_pick_delay = pydantic_settings.aram_auto_pick_delay  # 延迟时间
    #     aram_auto_pick_champion_ids = pydantic_settings.aram_auto_pick_champions  # 优先级列表

    #     print(f"用户设置如下:")
    #     print(f"\tARAM自动选择功能: {aram_auto_pick_enabled}")
    #     print(f"\tARAM自动选择延迟: {aram_auto_pick_delay} 秒")
    #     print(f"\tARAM自动选择优先级: {aram_auto_pick_champion_ids}")

    #     # 检查是否启用了ARAM自动选择功能
    #     if not pydantic_settings.aram_auto_pick_enabled:
    #         print("\tARAM自动选择功能未启用")
    #         return

    #     print("通过json_data获取到的信息如下:")


    #     # 创建可选英雄池（当前英雄 + 备用席英雄）
    #     available_champion_ids = bench_champion_ids + [current_champion_id]
    #     print(f"\t可选英雄池: {available_champion_ids}")

    #     # 在可选英雄池中找到优先级最高的英雄
    #     best_champion_id = None
    #     for champion_id in aram_auto_pick_champion_ids:
    #         if champion_id in available_champion_ids:
    #             best_champion_id = champion_id
    #             break
        
    #     self.selected_champion_id = best_champion_id

    #     print(f"\t分析得出的最优英雄ID: {best_champion_id}")

    #     print(f"结论如下:")

    #     if best_champion_id is None:
    #         print("\t无可选英雄")
    #         return

    #     if best_champion_id == current_champion_id:
    #         print("\t当前英雄已经是最优选择")
    #         return
        
    #     print("\t需要交换英雄")
        
    #     # 等待延迟时间后发送交换请求
    #     print(f"\t等待 {aram_auto_pick_delay} 秒后发送交换请求")
    #     if aram_auto_pick_delay > 0:
    #         await asyncio.sleep(aram_auto_pick_delay)
        
    #     # 延迟后再次检查
    #     if not self.swap_champion_button:
    #         return
        
    #     await self.h2lcu.bench_swap(best_champion_id)
    
    # async def _handle_champ_select_session_bp(self, json_data):
    #     print("触发事件: 选人阶段改变(bp)")
    #     """获取用户配置信息"""
    #     pydantic_settings = self.user_config.get_pydantic_settings()
    #     auto_pick_champions = pydantic_settings.auto_pick_champions   # 自动选择英雄列表
    #     auto_ban_champions = pydantic_settings.auto_ban_champions  # 自动禁用英雄列表

    #     """获取json_data信息"""
    #     # 获取当前阶段
    #     phase = json_data[2]['data']['timer']['phase']
    #     # 获取当前玩家cellId
    #     localPlayerCellId = json_data[2]['data']['localPlayerCellId']
    #     # 获取所有actions
    #     actions = json_data[2]['data']['actions']
    #     # 获取所有BP信息、当前玩家pick id、当前玩家正在进行的操作
    #     Ban_actions = []
    #     Pick_actions = []
    #     current_pick_id = None
    #     current_doing_actions = []
    #     for action_group in actions:
    #         for action in action_group:
    #             # 获取所有BP信息
    #             if action['type'] == 'ban':
    #                 Ban_actions.append(action)
    #             elif action['type'] == 'pick':
    #                 Pick_actions.append(action)
                
    #             # 获取当前玩家pick id
    #             if action['actorCellId'] == localPlayerCellId and action['type'] == 'pick':
    #                 current_pick_id = action['id']


    #             # 获取当前玩家正在进行的操作
    #             if action['actorCellId'] == localPlayerCellId and action['isInProgress'] == True:
    #                 current_doing_actions.append(action)
        
    #     # 获取所有已完成的action中的Ban英雄和除了当前玩家以外的Pick英雄
    #     BP_champion_ids = []
    #     for action in Ban_actions:
    #         if action['completed']:
    #             BP_champion_ids.append(action['championId'])
    #     for action in Pick_actions:
    #         if action['completed'] and action['actorCellId'] != localPlayerCellId:
    #             BP_champion_ids.append(action['championId'])
    #     print(f"除了当前玩家以外所有的BP英雄ID: {BP_champion_ids}")

    #     # 验证current_actions数量
    #     if len(current_doing_actions) != 1:
    #         print(f"当前玩家正在进行的操作数量为{len(current_doing_actions)}")


    #     """分析信息"""
    #     # 计算当前玩家需要选择和禁用的首选英雄
    #     ban_champion_id = None
    #     for champion_id in auto_ban_champions:
    #         if champion_id not in BP_champion_ids:
    #             ban_champion_id = champion_id
    #             break
    #     pick_champion_id = None
    #     for champion_id in auto_pick_champions:
    #         if champion_id not in BP_champion_ids:
    #             pick_champion_id = champion_id
    #             break
        
    #     print(f"当前玩家需要禁用的首选英雄ID: {ban_champion_id}")
    #     print(f"当前玩家需要选择的首选英雄ID: {pick_champion_id}")
                    
        
    #     """执行操作"""
    #     if phase == 'PLANNING' and not self.if_done_primary_selection and pick_champion_id is not None:
    #         # 预选英雄
    #         await self.h2lcu.pick_champion(current_pick_id, pick_champion_id, completed=False)
    #         self.if_done_primary_selection = True
    #         print(f"预选英雄完成")
    #         return
                
    #     if phase == 'BAN_PICK':
    #         # 执行BP操作
    #         for action in current_doing_actions:  # 一般只有一个或0个
    #             if action['id'] not in self.done_action_ids:
    #                 if action['type'] == 'ban' and ban_champion_id is not None:
    #                     await self.h2lcu.ban_champion(action['id'], ban_champion_id, completed=True)
    #                     self.done_action_ids.append(action['id'])
    #                 elif action['type'] == 'pick' and pick_champion_id is not None:
    #                     await self.h2lcu.pick_champion(action['id'], pick_champion_id, completed=True)
    #                     self.done_action_ids.append(action['id'])
    #         return


    
    async def _get_current_champion_id_by_data(self, data):
        # 获取当前玩家的英雄ID
        localPlayerCellId = data['localPlayerCellId']
        myTeam_list = data['myTeam']
        for player in myTeam_list:
            if player['cellId'] == localPlayerCellId:
                return player['championId']
        return None
    
    async def _get_puuids_by_champ_select_session(self, data):
        # 获取双方队伍的puuid
        my_team_puuid_list = []
        their_team_puuid_list = []
        for player in data['myTeam']:
            my_team_puuid_list.append(player['puuid'])
        for player in data['theirTeam']:
            their_team_puuid_list.append(player['puuid'])
        return my_team_puuid_list, their_team_puuid_list
    
    async def _get_puuids_by_gameflow_session(self, data, current_puuid):
        # 获取双方队伍的puuid
        team_one_puuid_list = []
        team_two_puuid_list = []

        team_one = data['gameData']['teamOne']
        team_two = data['gameData']['teamTwo']

        # 获取队伍1的puuid
        if team_one:  # 队伍1不为空
            for player in team_one:
                if 'puuid' in player:  # 确保player包含puuid,防止因人机而导致报错
                    team_one_puuid_list.append(player['puuid'])
            
        # 获取队伍2的puuid
        if team_two:  # 队伍2不为空
            for player in team_two:
                if 'puuid' in player:  # 确保player包含puuid,防止因人机而导致报错
                    team_two_puuid_list.append(player['puuid'])
            
        print(f"team_one_puuid_list: {team_one_puuid_list}")
        print(f"team_two_puuid_list: {team_two_puuid_list}")
        print(f"current_puuid in team_one_puuid_list: {current_puuid in team_one_puuid_list}")
        if current_puuid in team_one_puuid_list:
            print("当前玩家在队伍1")
            print(f"返回值: {team_one_puuid_list}, {team_two_puuid_list}")
            return team_one_puuid_list, team_two_puuid_list
        else:
            print("当前玩家在队伍2")
            print(f"返回值: {team_two_puuid_list}, {team_one_puuid_list}")
            return team_two_puuid_list, team_one_puuid_list

    async def bench_swap(self, champion_id: int=None):
        if champion_id:
            await self.h2lcu.bench_swap(champion_id)
        else:
            await self.h2lcu.bench_swap(self.selected_champion_id)
