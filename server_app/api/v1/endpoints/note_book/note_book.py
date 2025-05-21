from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from server_app.services.notebook_config import NoteBookModel, NoteRecord, NoteBookConfig
from server_app.services.lcu.http2lcu.http2lcu import Http2Lcu
from typing import List, Union, Optional
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

@router.post("/get_puuids_by_name_tag")
async def get_puuids_by_name_tag(request: Request, name_tag: Union[str, List[str]]):
    """根据name#tagLine获取puuid
    
    Args:
        name_tag: 可以是单个name#tagLine字符串，也可以是name#tagLine列表
                例如: "name1#tag1" 或 ["name1#tag1", "name2#tag2"]
        
    Returns:
        Union[str, List[str]]: 如果输入是字符串，返回单个puuid；如果输入是列表，返回puuid列表
    """
    h2lcu: Http2Lcu = request.app.state.h2lcu
    
    # 将单个字符串转换为列表处理
    is_single = isinstance(name_tag, str)
    name_tag_list = [name_tag] if is_single else name_tag
    
    summoners = await h2lcu.get_summoners_by_name_tag(name_tag_list)
    puuid_list = [summoner["puuid"] for summoner in summoners]
    
    # 如果输入是单个字符串，返回单个puuid
    return puuid_list[0] if is_single else puuid_list

@router.post("/get_name_tag_by_puuid")
async def get_name_tag_by_puuid(request: Request, puuid: Union[str, List[str]]):
    """根据puuid获取name#tagLine
    
    Args:
        puuid: 可以是单个puuid字符串，也可以是puuid列表
        
    Returns:
        Union[str, List[str]]: 如果输入是字符串，返回单个name#tagLine；如果输入是列表，返回name#tagLine列表
    """
    h2lcu: Http2Lcu = request.app.state.h2lcu
    
    # 将单个字符串转换为列表处理
    is_single = isinstance(puuid, str)
    puuid_list = [puuid] if is_single else puuid
    
    # 获取所有召唤师信息
    result = []
    for p in puuid_list:
        summoner = await h2lcu.get_summoner_by_puuid(p)
        if summoner:
            name_tag = f"{summoner.game_name}#{summoner.tag_line}"
            result.append(name_tag)
        else:
            result.append(None)  # 如果找不到召唤师，返回None
    
    # 如果输入是单个字符串，返回单个结果
    return result[0] if is_single else result

@router.post("/blacklist/smart_add")
async def smart_add_to_blacklist(request: Request, record: NoteRecord):
    """智能添加记录到黑名单
    如果只提供name#tagLine，会自动补全puuid
    如果只提供puuid，会自动补全name#tagLine
    """
    h2lcu: Http2Lcu = request.app.state.h2lcu
    notebook_config: NoteBookConfig = request.app.state.notebook_config
    
    try:
        # 补全缺失信息
        complete_record = await complete_record_info(h2lcu, record)
        if complete_record is None:
            return JSONResponse(
                status_code=400,
                content={"message": "Failed to find summoner information"}
            )
            
        # 添加到黑名单
        notebook_config.add_to_blacklist(complete_record)
        return {
            "message": "Record added to blacklist",
            "record": complete_record
        }
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"message": f"Failed to add record: {str(e)}"}
        )

@router.post("/whitelist/smart_add")
async def smart_add_to_whitelist(request: Request, record: NoteRecord):
    """智能添加记录到白名单
    如果只提供name#tagLine，会自动补全puuid
    如果只提供puuid，会自动补全name#tagLine
    """
    h2lcu: Http2Lcu = request.app.state.h2lcu
    notebook_config: NoteBookConfig = request.app.state.notebook_config
    
    try:
        # 补全缺失信息
        complete_record = await complete_record_info(h2lcu, record)
        if complete_record is None:
            return JSONResponse(
                status_code=400,
                content={"message": "Failed to find summoner information"}
            )
            
        # 添加到白名单
        notebook_config.add_to_whitelist(complete_record)
        return {
            "message": "Record added to whitelist",
            "record": complete_record
        }
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"message": f"Failed to add record: {str(e)}"}
        )

async def complete_record_info(h2lcu: Http2Lcu, record: NoteRecord) -> Optional[NoteRecord]:
    """补全记录中缺失的信息
    
    Args:
        h2lcu: Http2Lcu实例
        record: 需要补全的记录
        
    Returns:
        Optional[NoteRecord]: 补全后的记录，如果无法补全则返回None
    """
    try:
        # 如果有game_name和summoner_id但没有puuid，尝试获取puuid
        if record.game_name and record.summoner_id and not record.puuid:
            name_tag = f"{record.game_name}#{record.summoner_id}"
            puuid = await h2lcu.get_summoners_by_name_tag(name_tag)
            if puuid:
                record.puuid = puuid
            else:
                return None
                
        # 如果只有puuid，尝试获取game_name和summoner_id
        elif record.puuid and (not record.game_name or not record.summoner_id):
            name_tag = await h2lcu.get_name_tag_by_puuid(record.puuid)
            if name_tag:
                game_name, tag = name_tag.split('#')
                record.game_name = game_name
                record.summoner_id = tag
            else:
                return None
                
        return record
    except Exception:
        return None
