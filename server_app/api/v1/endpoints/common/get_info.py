from fastapi import APIRouter, Request
from typing import Dict

from server_app.new_services.lcu import Websocket2Lcu

from server_app.new_services.lcu import Http2Lcu

router = APIRouter()


@router.get("/map_id2name")
async def get_map_id2name(request: Request) -> Dict[int, str]:
    """获取地图ID与名称的对应关系
    
    Returns:
        Dict[int, str]: 地图ID与名称的对应字典,如 {11: "召唤师峡谷", 12: "嚎哭深渊"}
    """
    w2lcu: Websocket2Lcu = request.app.state.w2lcu
    h2lcu: Http2Lcu = request.app.state.h2lcu

    if h2lcu.id2info is None:
        await h2lcu.get_all_id2info()

    maps_info = h2lcu.id2info["maps"]
    return {map_id: info["name"] for map_id, info in maps_info.items()}


@router.get("/champions_info")
async def get_champions_info(request: Request) -> Dict[int, Dict]:
    """获取所有英雄信息
    
    Returns:
        Dict[int, Dict]: 英雄ID与信息的对应字典,如 
        {
            1: {
                "name": "黑暗之女",
                "alias": "Annie",
                "title": "安妮",
                // ... 其他英雄信息
            }
        }
    """
    h2lcu: Http2Lcu = request.app.state.h2lcu

    if h2lcu.id2info is None:
        await h2lcu.get_all_id2info()

    return h2lcu.id2info["champions"]
