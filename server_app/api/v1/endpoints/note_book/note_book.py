from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from server_app.services.lcu import Http2Lcu

router = APIRouter()

@router.get("/get_game_detail_when_end_of_game")
async def get_game_detail_when_end_of_game(request: Request):
    """获取游戏结束时的游戏详情"""
    h2lcu: Http2Lcu = request.app.state.h2lcu
    game_detail = await h2lcu.get_game_detail_when_end_of_game()
    return game_detail
