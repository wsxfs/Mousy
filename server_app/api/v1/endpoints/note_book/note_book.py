from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from server_app.services.notebook_config import NoteBookModel, NoteRecord, NoteBookConfig
from server_app.services.lcu.http2lcu.http2lcu import Http2Lcu
from typing import List
from datetime import datetime


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


@router.get("/get_settings")
async def get_settings(request: Request):
    """获取笔记本设置"""
    return request.app.state.notebook_config.settings

@router.post("/update_all")
async def update_all_settings(request: Request, new_settings: NoteBookModel):
    """批量更新设置"""
    notebook_config: NoteBookConfig = request.app.state.notebook_config
    try:
        notebook_config.update_settings(new_settings)
        return {"message": "Settings updated successfully"}
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"message": f"Failed to update settings: {str(e)}"}
        )

@router.post("/blacklist/add")
async def add_to_blacklist(request: Request, record: NoteRecord):
    """添加记录到黑名单"""
    notebook_config: NoteBookConfig = request.app.state.notebook_config
    try:
        notebook_config.add_to_blacklist(record)
        return {"message": "Record added to blacklist"}
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"message": f"Failed to add record: {str(e)}"}
        )

@router.post("/whitelist/add")
async def add_to_whitelist(request: Request, record: NoteRecord):
    """添加记录到白名单"""
    notebook_config: NoteBookConfig = request.app.state.notebook_config
    try:
        notebook_config.add_to_whitelist(record)
        return {"message": "Record added to whitelist"}
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"message": f"Failed to add record: {str(e)}"}
        )

@router.post("/blacklist/remove")
async def remove_from_blacklist(request: Request, summoner_id: str):
    """从黑名单中删除记录"""
    notebook_config: NoteBookConfig = request.app.state.notebook_config
    try:
        notebook_config.remove_from_blacklist(summoner_id)
        return {"message": "Record removed from blacklist"}
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"message": f"Failed to remove record: {str(e)}"}
        )

@router.post("/whitelist/remove")
async def remove_from_whitelist(request: Request, summoner_id: str):
    """从白名单中删除记录"""
    notebook_config: NoteBookConfig = request.app.state.notebook_config
    try:
        notebook_config.remove_from_whitelist(summoner_id)
        return {"message": "Record removed from whitelist"}
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"message": f"Failed to remove record: {str(e)}"}
        )
