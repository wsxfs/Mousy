# -*- coding: utf-8 -*-
# @Time    : 2024/11/11 2:43
# @Author  : GZA
# @File    : hello_world.py
import asyncio
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Request
from server_app.services.lcu import Websocket2Lcu
from server_app.services.lcu import Http2Lcu
from typing import List
router = APIRouter()


class LcuStatusResponse(BaseModel):
    is_connected: bool
    game_name: Optional[str] = None
    tag_line: Optional[str] = None


@router.get("/get_fastapi_status", name="获取FastAPI状态")
async def get_fastapi_status():
    return {"message": "Hello from FastAPI server!!"}


@router.get("/get_lcu_status", name="获取w2lcu状态", response_model=LcuStatusResponse)
async def get_lcu_status(request: Request):
    w2lcu: Websocket2Lcu = request.app.state.w2lcu
    h2lcu: Http2Lcu = request.app.state.h2lcu
    if w2lcu.is_connected:
        current_summoner = await h2lcu.get_current_summoner()
        game_name = current_summoner.game_name
        tag_line = current_summoner.tag_line
        return LcuStatusResponse(
            is_connected=True,
            game_name=game_name,
            tag_line=tag_line
        )
    else:
        return LcuStatusResponse(is_connected=False)


@router.get("/disconnect_lcu", name="断开w2lcu连接")
async def disconnect_lcu(request: Request):
    w2lcu: Websocket2Lcu = request.app.state.w2lcu
    h2lcu: Http2Lcu = request.app.state.h2lcu

    if not w2lcu.is_connected:
        response = await get_lcu_status(request)
        return response

    await w2lcu.close()
    response = await get_lcu_status(request)
    return response


@router.get("/connect_lcu", name="连接w2lcu")
async def connect_lcu(request: Request):
    w2lcu: Websocket2Lcu = request.app.state.w2lcu
    h2lcu: Http2Lcu = request.app.state.h2lcu
    all_events: List[str] = request.app.state.all_events

    # 如果已经连接，则返回当前状态
    if w2lcu.is_connected:
        return await get_lcu_status(request)

    # 验证port和token
    try:
        await h2lcu.get_current_summoner()
    except Exception:
        port, token = request.app.state.get_port_and_token()
        # 更新port和token
        await request.app.state.app_state_update(port, token)

    await w2lcu.start(all_events)
    await asyncio.sleep(0.5)
    return await get_lcu_status(request)

class GameModeResponse(BaseModel):
    game_mode: Optional[str]

@router.get("/get_game_mode", name="获取游戏模式(在选择英雄时)", response_model=GameModeResponse)
async def get_game_mode(request: Request):
    h2lcu: Http2Lcu = request.app.state.h2lcu
    game_mode = await h2lcu.get_game_mode()
    return GameModeResponse(game_mode=game_mode)
