# -*- coding: utf-8 -*-
# @Time    : 2024/11/12 17:42
# @Author  : GZA
# @File    : match_history.py
from typing import Annotated, Optional, List
from fastapi import APIRouter, Request, Form
from pydantic import BaseModel

from server_app.services.lcu import Websocket2Lcu
from server_app.services.lcu import Http2Lcu

router = APIRouter()


class MatchHistoryResponseInput(BaseModel):
    puuid: Optional[str] = None  # 可选
    beg_index: int
    end_index: int

class SummonerInfoResponseInput(BaseModel):
    puuid: Optional[str] = None  # 可选


@router.post("/get_match_history", name="获取召唤师的比赛记录")
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
    # game_id = match_history['games']['games'][0]['gameId']
    # 8003456682
    return match_history

class BatchMatchHistoryInput(BaseModel):
    puuid_list: List[str]
    beg_index: int = 0
    end_index: int = 4

# 添加缓存装饰器
async def _get_cached_match_history(puuid: str, beg_index: int, end_index: int, h2lcu: Http2Lcu):
    """带缓存的获取战绩函数"""
    match_history = await h2lcu.get_match_history(
        puuid=puuid,
        beg_index=beg_index,
        end_index=end_index
    )
    return match_history

@router.post("/get_batch_match_history", name="批量获取多个召唤师的比赛记录")
async def get_batch_match_history(
    request: Request,
    puuid_list: Annotated[List[str], Form()],
    beg_index: Annotated[int, Form()] = 0,
    end_index: Annotated[int, Form()] = 4,
):
    """批量获取多个召唤师的历史战绩"""
    h2lcu: Http2Lcu = request.app.state.h2lcu
    
    result = {}
    for puuid in puuid_list:
        try:
            match_history = await _get_cached_match_history(
                puuid,
                beg_index,
                end_index,
                h2lcu
            )
            result[puuid] = match_history
        except Exception as e:
            print(f"获取玩家{puuid}战绩失败: {e}")
            result[puuid] = None
        
    return result



@router.post("/get_game_detail", name="获取指定游戏ID的详细信息")
async def get_game_detail(game_id: Annotated[int, Form()], request: Request):
    """获取指定游戏ID的详细信息"""
    h2lcu: Http2Lcu = request.app.state.h2lcu
    game_detail = await h2lcu.get_game_detail(game_id=game_id)
    return game_detail


@router.post("/get_summoner_info", name="获取召唤师信息")
async def get_summoner_info(form: Annotated[SummonerInfoResponseInput, Form()], request: Request):
    """获取召唤师信息"""
    h2lcu: Http2Lcu = request.app.state.h2lcu
    
    puuid = form.puuid
    
    # 如果puuid为空，则获取当前召唤师的信息
    if not puuid:
        current_summoner = await h2lcu.get_current_summoner()
        return current_summoner
        
    # 否则根据puuid获取召唤师信息
    summoner_info = await h2lcu.get_summoner_by_puuid(puuid)
    return summoner_info
