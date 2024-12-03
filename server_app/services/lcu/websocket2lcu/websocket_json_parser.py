# -*- coding: utf-8 -*-
# @Time    : 2024/11/12 3:20
# @Author  : GZA
# @File    : websocket_json_parser.py

import json
from pydantic import BaseModel

from .websocket_json_examples import ChampSelectJson, GameFlowPhaseJson


class JsonParser:
    """
    用于解析WebSocket JSON消息的基类。
    """

    def __init__(self, json_data: dict):
        self.data = json_data['data']
        self.eventType = json_data['eventType']
        self.uri = json_data['uri']


class GameFlowPhaseJsonParser(JsonParser):
    def __init__(self, json_data: dict):
        super().__init__(json_data)
        self.client_status = self.get_client_status()

    def get_client_status(self):
        return self.data


...  # Todo 其他json解析
