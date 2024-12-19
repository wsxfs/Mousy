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

class SyncFrontData:
    current_puuid: Optional[str] = None
    my_team_puuid_list: Optional[List[str]] = None
    their_team_puuid_list: Optional[List[str]] = None
    current_champion: Optional[int] = None
    bench_champions: Optional[List[int]] = None
    gameflow_phase: Optional[str] = None
    swap_champion_button: Optional[bool] = None
    selected_champion_id: Optional[int] = None
    summoner_id: Optional[int] = None

    def __init__(self, w2front: Websocket2Front, current_puuid: Optional[str] = None):
        self.w2front = w2front
        self.current_puuid = current_puuid

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        # 执行异步方法
        asyncio.create_task(self.async_set_value(name, value))

    async def async_set_value(self, name, new_value):
        if self.w2front and new_value is not None:
            # 将消息格式改为标准 JSON 格式
            message = {
                "type": "attribute_change",
                "data": {
                    "attribute": name,
                    "value": new_value
                }
            }
            await self.w2front.broadcast_event("attribute_change", message)

class GameState(BaseModel):
    gameflow_phase: Optional[str] = None
    champ_select_session: Optional[Dict] = None


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
        self.game_state = GameState()  # 储存websocket2lcu的事件数据
        self.sync_front_data = SyncFrontData(self.w2front)  # 储存前端同步数据

    
    def _register_events(self):
        # 匹配事件
        self.w2lcu.events.on_gameflow_phase([self._handle_gameflow_phase])  # 游戏状态改变总事件
        self.w2lcu.events.on_gameflow_phase_none([self._handle_gameflow_phase_none])  # 大厅
        self.w2lcu.events.on_gameflow_phase_lobby([self._handle_gameflow_phase_lobby])  # 组队中
        self.w2lcu.events.on_gameflow_phase_match_making([self._handle_match_making])  # 匹配中
        self.w2lcu.events.on_gameflow_phase_ready_check([self._handle_gameflow_phase_ready_check])  # 确认对局
        self.w2lcu.events.on_gameflow_phase_champ_select([self._handle_gameflow_phase_champ_select])  # 选择英雄阶段
        self.w2lcu.events.on_gameflow_phase_game_start([self._handle_gameflow_phase_game_start])  # 游戏开始
        self.w2lcu.events.on_champ_select_session([self._handle_champ_select_session])  # 选人阶段改变
        
        
    async def _handle_gameflow_phase(self, json_data):
        print("触发事件: 游戏状态改变")
        self.game_state.gameflow_phase = json_data[2]['data']
        
        # 退出选人阶段时，清空选人阶段数据
        if json_data[2]['data'] != "ChampSelect":  
            self.game_state.champ_select_session = None
            # await self.w2front.broadcast_event("gameflow_phase_exit", "champ_select_exit")

    async def _handle_gameflow_phase_none(self, json_data):
        print("进入大厅状态")
        # await self.w2front.broadcast_event("gameflow_phase", "none")
        self.sync_front_data.gameflow_phase = "none"


    async def _handle_gameflow_phase_lobby(self, json_data):
        print("进入组队中状态")
        # await self.w2front.broadcast_event("gameflow_phase", "lobby")
        self.sync_front_data.gameflow_phase = "lobby"

    async def _handle_match_making(self, json_data):
        print("进入匹配状态")
        # await self.w2front.broadcast_event("gameflow_phase", "match_making")
        self.sync_front_data.gameflow_phase = "match_making"

    async def _handle_gameflow_phase_ready_check(self, json_data):
        print("进入确认对局状态")
        self.sync_front_data.gameflow_phase = "ready_check"
        if self.user_config.settings['auto_accept']:
            await self.h2lcu.accept_matchmaking()  # 接受匹配
        # await self.w2front.broadcast_event("gameflow_phase", "ready_check")

    async def _handle_gameflow_phase_champ_select(self, json_data):
        print("进入选择英雄状态")
        self.sync_front_data.gameflow_phase = "champ_select"
        self.swap_champion_button = True
        # await self.w2front.broadcast_event("gameflow_phase", "champ_select")

        # 等待选择英雄阶段数据
        while self.game_state.champ_select_session is None:
            await asyncio.sleep(0.1)

        # 获取双方队伍的puuid(目前只能获取到队友的puuid)
        my_team_puuid_list, their_team_puuid_list = await self._get_puuids_by_champ_select_session(self.game_state.champ_select_session)
        self.sync_front_data.my_team_puuid_list = my_team_puuid_list
        self.sync_front_data.their_team_puuid_list = their_team_puuid_list

        # 获取当前玩家的英雄ID
        champ_select_state = await self.h2lcu.get_champ_select_state()
        current_champion_id = await self._get_current_champion_id_by_data(champ_select_state)

        await asyncio.sleep(0.3)
        self.sync_front_data.current_champion = current_champion_id
        self.sync_front_data.bench_champions = []
        # await self.w2front.broadcast_event("champ_select_changed", f"current_champion={current_champion_id},bench_champions={[]}")
    
    async def _handle_gameflow_phase_game_start(self, json_data):
        print("进入游戏开始状态")
        self.sync_front_data.gameflow_phase = "game_start"
        # 获取当前puuid
        if self.sync_front_data.current_puuid is None: 
            current_summoner = await self.h2lcu.get_current_summoner()
            self.sync_front_data.current_puuid = current_summoner.puuid
        my_team_puuid_list, their_team_puuid_list = await self._get_puuids_by_gameflow_session(json_data[2]['data'], self.sync_front_data.current_puuid)
        self.sync_front_data.my_team_puuid_list = my_team_puuid_list
        self.sync_front_data.their_team_puuid_list = their_team_puuid_list



    async def _handle_champ_select_session(self, json_data):
        print("触发事件: 选人阶段改变")
        self.game_state.champ_select_session = json_data[2]['data']

        # 获取当前玩家的英雄ID
        current_champion_id = await self._get_current_champion_id_by_data(json_data[2]['data'])
        print(f"\t当前玩家英雄ID: {current_champion_id}")

        # 获取备用席英雄ID
        bench_champions = json_data[2]['data']['benchChampions']
        bench_champion_ids = [champion['championId'] for champion in bench_champions]
        print(f"\t备用席英雄ID: {bench_champion_ids}")

        # 发送选人阶段改变事件信息：当前玩家的英雄ID和备用席英雄ID
        self.sync_front_data.current_champion = current_champion_id
        self.sync_front_data.bench_champions = bench_champion_ids

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
        for player in data['gameData']['teamOne']:
            team_one_puuid_list.append(player['puuid'])
        for player in data['gameData']['teamTwo']:
            team_two_puuid_list.append(player['puuid'])
        if current_puuid in team_one_puuid_list:
            return team_one_puuid_list, team_two_puuid_list
        else:
            return team_two_puuid_list, team_one_puuid_list

    async def bench_swap(self, champion_id: int=None):
        if champion_id:
            await self.h2lcu.bench_swap(champion_id)
        else:
            await self.h2lcu.bench_swap(self.selected_champion_id)

example_data = {
    "gameClient": {
        "observerServerIp": "hn1-k8s-sc.lol.qq.com",
        "observerServerPort": 8080,
        "running": True,
        "serverIp": "gpp-hn1-1.lol.qq.com",
        "serverPort": 10500,
        "visible": False
    },
    "gameData": {
        "gameId": 9600727127,
        "gameName": "",
        "isCustomGame": False,
        "password": "",
        "playerChampionSelections": [
            {
                "championId": 59,
                "selectedSkinIndex": 4,
                "spell1Id": 4,
                "spell2Id": 32,
                "summonerInternalName": "l命中不注定l"
            },
            {
                "championId": 40,
                "selectedSkinIndex": 0,
                "spell1Id": 6,
                "spell2Id": 4,
                "summonerInternalName": "落生K"
            },
            {
                "championId": 67,
                "selectedSkinIndex": 0,
                "spell1Id": 6,
                "spell2Id": 4,
                "summonerInternalName": "Gaosgc"
            },
            {
                "championId": 268,
                "selectedSkinIndex": 0,
                "spell1Id": 4,
                "spell2Id": 21,
                "summonerInternalName": "杨杨天硕"
            },
            {
                "championId": 110,
                "selectedSkinIndex": 7,
                "spell1Id": 4,
                "spell2Id": 7,
                "summonerInternalName": "二十余五"
            },
            {
                "championId": 30,
                "selectedSkinIndex": 0,
                "spell1Id": 32,
                "spell2Id": 4,
                "summonerInternalName": "北风向东刮"
            },
            {
                "championId": 875,
                "selectedSkinIndex": 0,
                "spell1Id": 4,
                "spell2Id": 32,
                "summonerInternalName": "灬袖手天下睨苍生"
            },
            {
                "championId": 32,
                "selectedSkinIndex": 0,
                "spell1Id": 4,
                "spell2Id": 32,
                "summonerInternalName": "山鬼写下的情书"
            },
            {
                "championId": 112,
                "selectedSkinIndex": 0,
                "spell1Id": 4,
                "spell2Id": 6,
                "summonerInternalName": "睡個覺"
            },
            {
                "championId": 99,
                "selectedSkinIndex": 0,
                "spell1Id": 4,
                "spell2Id": 3,
                "summonerInternalName": "淡淡姐的小跟班"
            }
        ],
        "queue": {
            "allowablePremadeSizes": [
                1,
                2,
                3,
                4,
                5
            ],
            "areFreeChampionsAllowed": True,
            "assetMutator": "MapSkin_HA_Crepe",
            "category": "PvP",
            "championsRequiredToPlay": 16,
            "description": "极地大乱斗",
            "detailedDescription": "",
            "gameMode": "ARAM",
            "gameTypeConfig": {
                "advancedLearningQuests": False,
                "allowTrades": True,
                "banMode": "SkipBanStrategy",
                "banTimerDuration": 0,
                "battleBoost": True,
                "crossTeamChampionPool": False,
                "deathMatch": False,
                "doNotRemove": False,
                "duplicatePick": False,
                "exclusivePick": True,
                "id": 21,
                "learningQuests": False,
                "mainPickTimerDuration": 0,
                "maxAllowableBans": 0,
                "name": "GAME_CFG_TEAM_BUILDER_RANDOM",
                "onboardCoopBeginner": False,
                "pickMode": "AllRandomPickStrategy",
                "postPickTimerDuration": 33,
                "reroll": False,
                "teamChampionPool": False
            },
            "id": 450,
            "isRanked": False,
            "isTeamBuilderManaged": True,
            "lastToggledOffTime": 0,
            "lastToggledOnTime": 0,
            "mapId": 12,
            "maximumParticipantListSize": 5,
            "minLevel": 6,
            "minimumParticipantListSize": 1,
            "name": "极地大乱斗",
            "numPlayersPerTeam": 5,
            "queueAvailability": "Available",
            "queueRewards": {
                "isChampionPointsEnabled": True,
                "isIpEnabled": True,
                "isXpEnabled": True,
                "partySizeIpRewards": []
            },
            "removalFromGameAllowed": False,
            "removalFromGameDelayMinutes": 0,
            "shortName": "极地大乱斗",
            "showPositionSelector": False,
            "spectatorEnabled": True,
            "type": "ARAM_UNRANKED_5x5"
        },
        "spectatorsAllowed": False,
        "teamOne": [
            {
                "championId": 110,
                "lastSelectedSkinIndex": 0,
                "profileIconId": 15,
                "puuid": "ce4ecce9-d1d5-5474-99a3-1eedf6112e10",
                "selectedPosition": "NONE",
                "selectedRole": "NONE.NONE.NONE.UNSELECTED",
                "summonerId": 2672909359033952,
                "summonerInternalName": "二十余五",
                "summonerName": "二十余五",
                "teamOwner": False,
                "teamParticipantId": 4
            },
            {
                "championId": 40,
                "lastSelectedSkinIndex": 0,
                "profileIconId": 5526,
                "puuid": "5eaf9e59-b607-55f0-af3a-cb3e8987282b",
                "selectedPosition": "NONE",
                "selectedRole": "NONE.NONE.NONE.UNSELECTED",
                "summonerId": 2453407998471008,
                "summonerInternalName": "落生K",
                "summonerName": "落生K",
                "teamOwner": False,
                "teamParticipantId": 2
            },
            {
                "championId": 268,
                "lastSelectedSkinIndex": 0,
                "profileIconId": 3543,
                "puuid": "5a5ebfd4-bc54-5e11-8ec4-21e876db41b9",
                "selectedPosition": "NONE",
                "selectedRole": "NONE.NONE.NONE.UNSELECTED",
                "summonerId": 2794652091967808,
                "summonerInternalName": "杨杨天硕",
                "summonerName": "杨杨天硕",
                "teamOwner": False,
                "teamParticipantId": 4
            },
            {
                "championId": 59,
                "lastSelectedSkinIndex": 0,
                "profileIconId": 6709,
                "puuid": "dc23fd04-5e73-5a24-b6da-3d53264b77fc",
                "selectedPosition": "NONE",
                "selectedRole": "NONE.NONE.NONE.UNSELECTED",
                "summonerId": 4135580109,
                "summonerInternalName": "l命中不注定l",
                "summonerName": "l命中不注定l",
                "teamOwner": False,
                "teamParticipantId": 1
            },
            {
                "championId": 67,
                "lastSelectedSkinIndex": 0,
                "profileIconId": 5,
                "puuid": "5f2ceb4a-c8e7-5318-8549-40ecb459ce48",
                "selectedPosition": "NONE",
                "selectedRole": "NONE.NONE.NONE.UNSELECTED",
                "summonerId": 2228982599836544,
                "summonerInternalName": "Gaosgc",
                "summonerName": "Gaosgc",
                "teamOwner": False,
                "teamParticipantId": 3
            }
        ],
        "teamTwo": [
            {
                "championId": 30,
                "lastSelectedSkinIndex": 0,
                "profileIconId": 5414,
                "puuid": "76d32a2e-e1c2-5718-9ce7-7de543bf34fa",
                "selectedPosition": "NONE",
                "selectedRole": "NONE.NONE.NONE.UNSELECTED",
                "summonerId": 2526773063643456,
                "summonerInternalName": "北风向东刮",
                "summonerName": "北风向东刮",
                "teamOwner": False,
                "teamParticipantId": 5
            },
            {
                "championId": 112,
                "lastSelectedSkinIndex": 0,
                "profileIconId": 6459,
                "puuid": "06c2a9ab-21d3-5ee0-9997-e049fca40e9b",
                "selectedPosition": "NONE",
                "selectedRole": "NONE.NONE.NONE.UNSELECTED",
                "summonerId": 4119444620,
                "summonerInternalName": "睡個覺",
                "summonerName": "睡個覺",
                "teamOwner": False,
                "teamParticipantId": 8
            },
            {
                "championId": 99,
                "lastSelectedSkinIndex": 0,
                "profileIconId": 3543,
                "puuid": "001917db-b5c5-5753-84ca-9fd3baaf722a",
                "selectedPosition": "NONE",
                "selectedRole": "NONE.NONE.NONE.UNSELECTED",
                "summonerId": 3038843940866816,
                "summonerInternalName": "淡淡姐的小跟班",
                "summonerName": "淡淡姐的小跟班",
                "teamOwner": False,
                "teamParticipantId": 9
            },
            {
                "championId": 875,
                "lastSelectedSkinIndex": 0,
                "profileIconId": 3886,
                "puuid": "66d40cb0-d8ff-5e43-aa45-08a4d07c3341",
                "selectedPosition": "NONE",
                "selectedRole": "NONE.NONE.NONE.UNSELECTED",
                "summonerId": 4118326333,
                "summonerInternalName": "灬袖手天下睨苍生",
                "summonerName": "灬袖手天下睨苍生",
                "teamOwner": False,
                "teamParticipantId": 6
            },
            {
                "championId": 32,
                "lastSelectedSkinIndex": 0,
                "profileIconId": 3543,
                "puuid": "37f1314f-3076-5d8a-878d-1959b88c093f",
                "selectedPosition": "NONE",
                "selectedRole": "NONE.NONE.NONE.UNSELECTED",
                "summonerId": 3015529932336096,
                "summonerInternalName": "山鬼写下的情书",
                "summonerName": "山鬼写下的情书",
                "teamOwner": False,
                "teamParticipantId": 7
            }
        ]
    },
    "gameDodge": {
        "dodgeIds": [],
        "phase": "None",
        "state": "Invalid"
    },
    "map": {
        "assets": {
            "champ-select-background-sound": "lol-game-data/assets/content/src/LeagueClient/GameModeAssets/Crepe/sound/music-cs-allrandom-bridgeofprogress.ogg",
            "champ-select-banphase-background-sound": "lol-game-data/assets/content/src/LeagueClient/GameModeAssets/Crepe/sound/music-cs-allrandom-banphase-howlingabyss.ogg",
            "champ-select-flyout-background": "lol-game-data/assets/content/src/LeagueClient/GameModeAssets/Crepe/img/champ-select-flyout-background.png",
            "game-select-icon-active": "lol-game-data/assets/content/src/LeagueClient/GameModeAssets/Crepe/img/game-select-icon-active.png",
            "game-select-icon-active-video": "lol-game-data/assets/content/src/LeagueClient/GameModeAssets/Crepe/video/game-select-icon-active.webm",
            "game-select-icon-default": "lol-game-data/assets/content/src/LeagueClient/GameModeAssets/Crepe/img/game-select-icon-default.png",
            "game-select-icon-disabled": "lol-game-data/assets/content/src/LeagueClient/GameModeAssets/Crepe/img/game-select-icon-disabled.png",
            "game-select-icon-hover": "lol-game-data/assets/content/src/LeagueClient/GameModeAssets/Crepe/img/game-select-icon-hover.png",
            "game-select-icon-intro-video": "lol-game-data/assets/content/src/LeagueClient/GameModeAssets/Crepe/video/game-select-icon-intro.webm",
            "gameflow-background": "lol-game-data/assets/content/src/LeagueClient/GameModeAssets/Crepe/img/gameflow-background.jpg",
            "gameflow-background-dark": "lol-game-data/assets/content/src/LeagueClient/GameModeAssets/Crepe/img/gameflow-background-dark.jpg",
            "gameselect-button-hover-sound": "lol-game-data/assets/content/src/LeagueClient/GameModeAssets/Shared/sound/sfx-gameselect-button-hover.ogg",
            "icon-defeat": "lol-game-data/assets/content/src/LeagueClient/GameModeAssets/Crepe/img/icon-defeat.png",
            "icon-defeat-v2": "lol-game-data/assets/content/src/LeagueClient/GameModeAssets/Crepe/img/icon-defeat-v2.png",
            "icon-defeat-video": "lol-game-data/assets/content/src/LeagueClient/GameModeAssets/Crepe/video/icon-defeat.webm",
            "icon-empty": "lol-game-data/assets/content/src/LeagueClient/GameModeAssets/Crepe/img/icon-empty.png",
            "icon-hover": "lol-game-data/assets/content/src/LeagueClient/GameModeAssets/Crepe/img/icon-hover.png",
            "icon-leaver": "lol-game-data/assets/content/src/LeagueClient/GameModeAssets/Crepe/img/icon-leaver.png",
            "icon-leaver-v2": "lol-game-data/assets/content/src/LeagueClient/GameModeAssets/Crepe/img/icon-leaver-v2.png",
            "icon-loss-forgiven-v2": "lol-game-data/assets/content/src/LeagueClient/GameModeAssets/Crepe/img/icon-loss-forgiven-v2.png",
            "icon-v2": "lol-game-data/assets/content/src/LeagueClient/GameModeAssets/Crepe/img/icon-v2.png",
            "icon-victory": "lol-game-data/assets/content/src/LeagueClient/GameModeAssets/Crepe/img/icon-victory.png",
            "icon-victory-video": "lol-game-data/assets/content/src/LeagueClient/GameModeAssets/Crepe/video/icon-victory.webm",
            "music-inqueue-loop-sound": "lol-game-data/assets/content/src/LeagueClient/GameModeAssets/Crepe/sound/music-inqueue-loop-bridgeofprogress.ogg",
            "parties-background": "lol-game-data/assets/content/src/LeagueClient/GameModeAssets/Crepe/img/parties-background.jpg",
            "postgame-ambience-loop-sound": "lol-game-data/assets/content/src/LeagueClient/GameModeAssets/Crepe/sound/sfx-ambience-loop-bridgeofprogress.ogg",
            "ready-check-background": "lol-game-data/assets/content/src/LeagueClient/GameModeAssets/Crepe/img/ready-check-background.png",
            "ready-check-background-sound": "lol-game-data/assets/content/src/LeagueClient/GameModeAssets/Crepe/sound/sfx-readycheck-bridgeofprogress.ogg",
            "sfx-ambience-pregame-loop-sound": "lol-game-data/assets/content/src/LeagueClient/GameModeAssets/Crepe/sound/sfx-ambience-loop-bridgeofprogress.ogg",
            "social-icon-leaver": "lol-game-data/assets/content/src/LeagueClient/GameModeAssets/Crepe/img/social-icon-leaver.png",
            "social-icon-victory": "lol-game-data/assets/content/src/LeagueClient/GameModeAssets/Crepe/img/social-icon-victory.png"
        },
        "categorizedContentBundles": {},
        "description": "嚎哭深渊是一个无底裂隙，位于弗雷尔卓德最为寒冷、最为残酷的部分。传说在很久以前，一场宏大的战役就发生在横跨这道天堑的一座狭窄桥梁上。没有人记得谁在此战斗，为何而战斗，但有传言说，如果你仔细聆听风声的话，仍然可以听见那些葬身于深渊之中的败亡者们在嚎哭不停。",
        "gameMode": "ARAM",
        "gameModeName": "极地大乱斗",
        "gameModeShortName": "极地大乱斗",
        "gameMutator": "MapSkin_HA_Crepe",
        "id": 12,
        "isRGM": False,
        "mapStringId": "HA",
        "name": "进步之桥",
        "perPositionDisallowedSummonerSpells": {},
        "perPositionRequiredSummonerSpells": {},
        "platformId": "",
        "platformName": "",
        "properties": {
            "suppressRunesMasteriesPerks": False
        }
    },
    "phase": "InProgress"
}
