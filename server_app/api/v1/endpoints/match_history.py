# -*- coding: utf-8 -*-
# @Time    : 2024/11/12 17:42
# @Author  : GZA
# @File    : match_history.py
from typing import Annotated, Optional
from fastapi import APIRouter, Request, Form
from pydantic import BaseModel

from server_app.lcu.lcu_mine import Websocket2Lcu, Http2Lcu

router = APIRouter()


class MatchHistoryResponseInput(BaseModel):
    puuid: Optional[str] = None  # 可选
    beg_index: int
    end_index: int


@router.post("/get_match_history")
async def get_match_history(form: Annotated[MatchHistoryResponseInput, Form()], request: Request):
    """指定puuid获取召唤师的近期比赛记录,若不指定puuid,默认为当前召唤师"""
    h2lcu: Http2Lcu = request.app.state.h2lcu

    puuid = form.puuid
    beg_index = form.beg_index
    end_index = form.end_index

    # 如果puuid为空，则获取当前召唤师的puuid
    if puuid is None:
        current_summoner = await h2lcu.get_current_summoner()
        puuid = current_summoner.puuid

    match_history = await h2lcu.get_match_history(puuid=puuid, beg_index=beg_index, end_index=end_index)
    return match_history
