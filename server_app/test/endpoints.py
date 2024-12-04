# -*- coding: utf-8 -*-
# @Time    : 2024/11/7 0:01
# @Author  : GZA
# @File    : _endpoints.py

from typing import Tuple, Dict
from pydantic import BaseModel


class WebsocketEndpoint(BaseModel):
    event: str
    uri: str
    event_types: Tuple[str, ...]


class WebsocketEndpoints(BaseModel):
    SummonerProfile: WebsocketEndpoint
    GameFlowPhase: WebsocketEndpoint
    ChampSelect: WebsocketEndpoint
    SGPToken: WebsocketEndpoint


websocket_endpoints_dict = {
    # # 所有信息
    # "OnJsonApiEvent": {
    #     "event": "OnJsonApiEvent",
    #     "uri": '/lol-chat/v1/me',
    #     "event_types": ("Update",)
    # },

    # 召唤师个人资料改变
    "SummonerProfile": {
        "event": 'OnJsonApiEvent_lol-summoner_v1_current-summoner',
        "uri": '/lol-summoner/v1/current-summoner',
        "event_types": ('Update',)
    },

    # 游戏流程阶段改变
    "GameFlowPhase": {
        "event": 'OnJsonApiEvent_lol-gameflow_v1_gameflow-phase',
        "uri": '/lol-gameflow/v1/gameflow-phase',
        "event_types": ('Update',)
    },

    # 英雄选择
    "ChampSelect": {
        "event": 'OnJsonApiEvent_lol-champ-select_v1_session',
        "uri": '/lol-champ-select/v1/session',
        "event_types": ('Update',)
    },

    # SGPToken
    "SGPToken": {
        "event": 'OnJsonApiEvent_entitlements_v1_token',
        "uri": '/entitlements/v1/token',
        "event_types": ('Update',)
    }

}

# 可以这样验证现有的字典
websocket_endpoints = WebsocketEndpoints(**websocket_endpoints_dict)
