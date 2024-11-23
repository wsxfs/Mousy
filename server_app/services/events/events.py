# -*- coding: utf-8 -*-
# @Time    : 2024/11/10 23:23
# @Author  : GZA
# @File    : events.py

import asyncio

from server_app.lcu.lcu_mine import Websocket2Lcu
from server_app.lcu.lcu_mine import Http2Lcu
from server_app.lcu.response_parser.websocket_response.websocket_json_parser import GameFlowPhaseJsonParser


# 自动接受对局事件
def get_event_auto_accept_match(h2lcu, user_config):
    async def auto_accept_match(event):
        print(f"{event['data']=}")
        print(f"{user_config.settings['auto_accept']=}")
        if event["data"] == "ReadyCheck" and user_config.settings["auto_accept"]:
            await h2lcu.accept_matchmaking()
            print("接受匹配")

    return auto_accept_match


def get_all_events(h2lcu: Http2Lcu, user_config):
    async def auto_accept_match(event):
        """自动接受对局事件"""
        # 解析json数据
        json_dict = GameFlowPhaseJsonParser(event)
        client_status = json_dict.client_status
        if client_status == "ReadyCheck" and user_config.settings["auto_accept"]:
            await h2lcu.accept_matchmaking()
            print("接受匹配")

    async def auto_decline_match(event):
        """自动拒绝对局事件"""
        # print(f"{event['data']=}")
        # print(f"{user_config.settings['auto_accept']=}")
        if event["data"] == "ReadyCheck" and user_config.settings["auto_accept"]:
            await h2lcu.decline_matchmaking()
            print("拒绝匹配")

    async def champ_select(event):
        """英雄选择阶段执行"""
        # 获取事件数据
        data = event['data']

        # 获取本地玩家的 cellId
        localPlayerCellId = data['localPlayerCellId']

        # 检查是否轮到玩家选择
        is_selecting, action_id = await get_if_selecting(data, localPlayerCellId)

        if is_selecting:
            # 从配置中获取要选择的英雄ID列表
            champion_ids = user_config.settings['auto_pick_champions']
            if champion_ids:
                # 获取已选择的英雄列表
                selected_champions = set()
                for team in [data['myTeam'], data['theirTeam']]:
                    for player in team:
                        if player['championId'] > 0:  # 0表示未选择
                            selected_champions.add(str(player['championId']))

                # 尝试选择未被选择的英雄 TODO: 需要测试
                for champion_id in champion_ids:
                    if champion_id not in selected_champions:
                        try:
                            # 先尝试选择英雄且锁定
                            await h2lcu.select_champion(action_id, int(champion_id), completed=True)
                            print(f"自动选择英雄: {champion_id}")
                            break
                        except Exception as e:
                            print(f"选择英雄 {champion_id} 失败: {e}")
                            continue

        # 检查是否有换位请求  TODO: 需要测试
        if user_config.settings['auto_accept_swap_position']:
            for trade in data.get('trades', []):
                if trade['state'] == 'RECEIVED':
                    await h2lcu.accept_trade(trade['id'])
                    print("自动接受换位请求")

    async def get_if_selecting(data, localPlayerCellId):
        """判断当前是否轮到玩家选择英雄"""
        # 遍历所有action组
        for actionGroup in reversed(data['actions']):
            for action in actionGroup:
                # 检查是否是当前玩家的选择回合且未完成
                if (action["actorCellId"] == localPlayerCellId
                        and action['type'] == "pick"
                        and not action['completed']):
                    return True, action['id']
        return False, None

    class AllEvents:
        event_auto_accept_match = auto_accept_match
        event_auto_decline_match = auto_decline_match

        event_champ_select = champ_select

    return AllEvents
