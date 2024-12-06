# -*- coding: utf-8 -*-
# @Time    : 2024/11/12 3:20
# @Author  : GZA
# @File    : http_response_parser.py

import json
from typing import Union

from PIL import Image
from io import BytesIO

import httpx
from pydantic import BaseModel


class ResponseParser:
    """
    用于解析WebSocket JSON消息的基类。
    """
    content_type: str
    data: Union[dict, bytes]

    def __init__(self, response: httpx.Response):
        self.content_type = response.headers.get('Content-Type')

        if not response.is_success:
            self.data = None
            return

        if self.content_type == 'application/json':
            if response.content == b'':
                self.data = None
                return
            self.data = response.json()
            return
        if self.content_type == 'image/jpeg' or self.content_type == 'image/png':
            self.data = response.content
            return

    def img_show(self):
        if self.content_type == 'image/jpeg' or self.content_type == 'image/png':
            img = Image.open(BytesIO(self.data))
            img.show()
            return
        print("非图片类型")
        return

    def img_save(self, path):
        if self.content_type == 'image/jpeg':
            with open(path, 'wb') as file:
                file.write(self.data)
            return
        print("非图片类型")
        return


class CurrentSummonerInput(BaseModel):
    accountId: int
    displayName: str
    gameName: str
    internalName: str
    nameChangeFlag: bool
    percentCompleteForNextLevel: int
    privacy: str
    profileIconId: int
    puuid: str
    rerollPoints: dict
    summonerId: int
    summonerLevel: int
    tagLine: str
    unnamed: bool
    xpSinceLastLevel: int
    xpUntilNextLevel: int


class CurrentSummonerOutput(BaseModel):
    game_name: str
    puuid: str
    accountId: int
    summoner_id: int
    tag_line: str
    summoner_level: int
    xp_since_last_level: int
    xp_until_next_level: int
    profileIconId: int


class Response2Info:
    @staticmethod
    def current_summoner(response_parser: ResponseParser) -> CurrentSummonerOutput:
        input_data = response_parser.data
        current_summoner_input = CurrentSummonerInput(**input_data)
        return CurrentSummonerOutput(
            game_name=current_summoner_input.gameName,
            puuid=current_summoner_input.puuid,
            accountId=current_summoner_input.accountId,
            summoner_id=current_summoner_input.summonerId,
            tag_line=current_summoner_input.tagLine,
            summoner_level=current_summoner_input.summonerLevel,
            xp_since_last_level=current_summoner_input.xpSinceLastLevel,
            xp_until_next_level=current_summoner_input.xpUntilNextLevel,
            profileIconId=current_summoner_input.profileIconId
        )
