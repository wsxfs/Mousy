from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from server_app.services.lcu import Http2Lcu

router = APIRouter()

@router.get("/get_game_detail_when_end_of_game")
async def get_game_detail_when_end_of_game(request: Request):
    """获取游戏结束时的游戏详情"""
    h2lcu: Http2Lcu = request.app.state.h2lcu
    game_detail = await h2lcu.get_end_of_game_stats()
    
    if game_detail:
        # 遍历所有队伍的玩家
        for team in game_detail['teams']:
            for player in team['players']:
                # 获取玩家的puuid
                puuid = player.get('puuid')
                if puuid:
                    # 获取玩家详细信息
                    summoner_info = await h2lcu.get_summoner_by_puuid(puuid)
                    # 添加game_name字段
                    player['game_name'] = f"{summoner_info.game_name}#{summoner_info.tag_line}"
                else:
                    # 如果puuid为空，添加空字符串
                    player['game_name'] = ""

    return game_detail

@router.get("/get_platformId_by_puuid")
async def get_platformId_by_puuid(request: Request, puuid: str):
    """根据puuid获取平台ID"""
    h2lcu: Http2Lcu = request.app.state.h2lcu
    platform_id = await h2lcu.get_platformId_by_puuid(puuid)
    return platform_id
