# -*- coding: utf-8 -*-
# @Time    : 2024/11/16 13:56
# @Author  : GZA
# @File    : perks.py.py
from pathlib import Path
import time

from fastapi import APIRouter, Request, Form, Body
from typing import List, Optional, Any, Literal
from pydantic import BaseModel
from fastapi import HTTPException

from server_app.lcu.lcu_mine import Http2Lcu
from server_app.services.item_set_manager import ItemSetManager
from server_app.opgg.opgg import Opgg

router = APIRouter()


class PerksInput(BaseModel):
    name: str
    primary_style_id: int  # 主系符文ID
    sub_style_id: int  # 副系符文ID
    selected_perk_ids: List[int]  # 选择的符文ID列表


@router.post("/apply_perks")
async def apply_perks(request: Request, perks: PerksInput):
    """应用符文页

    Args:
        perks: 包含符文页配置的数据

    Returns:
        dict: 包含操作结果的响应
    """
    try:
        h2lcu = request.app.state.h2lcu

        # 1. 删除当前符文页
        await h2lcu.delete_current_rune_page()

        # 2. 创建新的符文页
        result = await h2lcu.create_rune_page(
            name=perks.name,
            primaryId=perks.primary_style_id,
            secondaryId=perks.sub_style_id,
            perks=perks.selected_perk_ids
        )

        return {
            "success": True,
            "message": "符文页应用成功",
            "data": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"应用符文页失败: {str(e)}")


class ItemInfo(BaseModel):
    icons: List[int]
    winRate: str
    pickRate: str


class ItemSetContent(BaseModel):
    startItems: List[ItemInfo]
    boots: List[ItemInfo]
    coreItems: List[ItemInfo]
    lastItems: List[int]


class ItemSetInput(BaseModel):
    title: str
    source: str
    associatedChampions: List[int]
    associatedMaps: List[int]
    items: ItemSetContent


def convert_to_item_set_json(item_set: ItemSetInput) -> dict:
    """将ItemSetInput转换为游戏可识别的物品套装JSON格式
    
    Args:
        item_set: 输入的物品套装数据
        
    Returns:
        dict: 转换后的JSON数据结构
    """
    # 添加时间戳以确保uid唯一
    timestamp = int(time.time())
    
    output_json = {
        "associatedChampions": item_set.associatedChampions,
        "associatedMaps": item_set.associatedMaps,
        "mode": "any",
        "map": "any",
        "sortrank": 0,
        "type": "global",
        "uid": f"Mousy_{item_set.source}_{item_set.associatedChampions[0] if item_set.associatedChampions else 'global'}_{timestamp}",
        "title": item_set.title,
        "blocks": []
    }
    line = "—" * 15

    # 添加起始装备
    for idx, info in enumerate(item_set.items.startItems):
        block_type = f"出门装 (胜率{info.winRate}% 选用{info.pickRate}%)"
        if idx == 0:
            block_type += line
        start_block = {
            "type": block_type,
            "items": [{"id": str(item_id), "count": 1} 
                     for item_id in info.icons]
        }
        output_json["blocks"].append(start_block)

    # 添加鞋子
    for idx, info in enumerate(item_set.items.boots):
        block_type = f"鞋子 (胜率{info.winRate}% 选用{info.pickRate}%)"
        if idx == 0:
            block_type += line
        boots_block = {
            "type": block_type,
            "items": [{"id": str(item_id), "count": 1}
                     for item_id in info.icons]
        }
        output_json["blocks"].append(boots_block)

    # 添加核心装备
    for idx, info in enumerate(item_set.items.coreItems):
        block_type = f"核心装 (胜率{info.winRate}% 选用{info.pickRate}%)"
        if idx == 0:
            block_type += line
        core_block = {
            "type": block_type,
            "items": [{"id": str(item_id), "count": 1}
                     for item_id in info.icons]
        }
        output_json["blocks"].append(core_block)

    # 添加可选装备
    if item_set.items.lastItems:
        last_block = {
            "type": "可选装备" + line,
            "items": [{"id": str(item_id), "count": 1}
                     for item_id in item_set.items.lastItems]
        }
        output_json["blocks"].append(last_block)

    return output_json


@router.post("/apply_items")
async def apply_items(request: Request, item_set: ItemSetInput):
    """应用出装页

    Args:
        item_set: 出装配置数据，包含以下字段：
            - title: 出装方案标题
            - source: 出装方案来源
            - associatedChampions: 关联英雄ID列表
            - associatedMaps: 关联地图ID列表
            - items: 出装内容，包含：
                - startItems: 起始装备列表
                - boots: 鞋子列表
                - coreItems: 核心装备列表
                - lastItems: 最后装备ID列表

    Returns:
        dict: 包含操作结果的响应
    """
    h2lcu: Http2Lcu = request.app.state.h2lcu
    item_set_manager: ItemSetManager = request.app.state.item_set_manager


    # 转换数据格式
    output_json = convert_to_item_set_json(item_set)
    
    # 保存文件
    item_set_manager.save_item2global(output_json, f"Mousy_{item_set.source}_{item_set.associatedChampions[0] if item_set.associatedChampions else 'global'}.json")

    return {
        "success": True,
        "message": "出装方案保存成功"
    }


class AllChampionsItemsInput(BaseModel):
    """所有英雄出装方案的输入模型"""
    region: Literal['global', 'kr', 'na', 'euw']  # 限制可用的服务器选项
    mode: Literal['ranked', 'aram']  # 限制可用的游戏模式
    tier: str  # 段位 (如 'platinum_plus')
    position: Literal['ALL', 'TOP', 'JUNGLE', 'MID', 'ADC', 'SUPPORT']  # 限制可用的位置

def champion_build_2_items_json(champion_build: dict) -> dict:
    """将champion_build转换为游戏可识别的物品套装JSON格式
    
    Args:
        champion_build: 从OPGG获取的英雄出装数据
        
    Returns:
        dict: 转换后的JSON数据结构
    """
    # 获取基础信息
    champion_data = champion_build['data']
    summary = champion_data['summary']
    items = champion_data['items']
    
    timestamp = int(time.time())
    
    output_json = {
        "associatedChampions": [summary['championId']],
        "associatedMaps": [11],  # 召唤师峡谷
        "mode": "any",
        "map": "any",
        "sortrank": 0,
        "type": "global",
        "uid": f"Mousy_OPGG_{summary['championId']}_{timestamp}",
        "title": f"{summary['name']}的出装方案(Best Wishes From Mousy🐹)",
        "blocks": []
    }
    
    line = "———————————————"
    
    # 添加起始装备
    for idx, item in enumerate(items['startItems']):
        win_rate = round(item['win'] / item['play'] * 100, 1)
        pick_rate = round(item['pickRate'] * 100, 1)
        
        block_type = f"出门装 (胜率{win_rate}% 选用{pick_rate}%)"
        if idx == 0:
            block_type += line
            
        block = {
            "type": block_type,
            "items": [{"id": str(icon), "count": 1} for icon in item['icons']]
        }
        output_json["blocks"].append(block)
    
    # 添加鞋子
    for idx, boot in enumerate(items['boots']):
        win_rate = round(boot['win'] / boot['play'] * 100, 1)
        pick_rate = round(boot['pickRate'] * 100, 1)
        
        block_type = f"鞋子 (胜率{win_rate}% 选用{pick_rate}%)"
        if idx == 0:
            block_type += line
            
        block = {
            "type": block_type,
            "items": [{"id": str(icon), "count": 1} for icon in boot['icons']]
        }
        output_json["blocks"].append(block)
    
    # 添加核心装备
    for idx, core in enumerate(items['coreItems']):
        win_rate = round(core['win'] / core['play'] * 100, 1)
        pick_rate = round(core['pickRate'] * 100, 1)
        
        block_type = f"核心装 (胜率{win_rate}% 选用{pick_rate}%)"
        if idx == 0:
            block_type += line
            
        block = {
            "type": block_type,
            "items": [{"id": str(icon), "count": 1} for icon in core['icons']]
        }
        output_json["blocks"].append(block)
    
    # 添加可选装备
    if items.get('lastItems'):
        block = {
            "type": "可选装备" + line,
            "items": [{"id": str(item_id), "count": 1} 
                     for item_id in items['lastItems']]
        }
        output_json["blocks"].append(block)
    
    return output_json

@router.post("/apply_all_champions_items")
async def apply_all_champions_items(
    request: Request,
    data: AllChampionsItemsInput = Body(...)  # 使用 Body 显式指定这是请求体
):
    """应用所有英雄的出装方案"""
    try:
        h2lcu: Http2Lcu = request.app.state.h2lcu
        item_set_manager: ItemSetManager = request.app.state.item_set_manager
        opgg: Opgg = request.app.state.opgg
        id2info: dict = request.app.state.id2info
        
        champion_id_list = h2lcu.champion_id_list
        
        # 应用所有英雄的出装方案
        for champion_id in champion_id_list:
            champion_build = await opgg.getChampionBuild(data.region, data.mode, champion_id, data.position, data.tier)
            items_json = champion_build_2_items_json(champion_build)
            champion_name = id2info['champions'][champion_id]['alias']
            
            item_set_manager.save_item2champions(items_json, champion_name, f"Mousy_OPGG_{data.region}_{data.mode}_{data.tier}_{data.position}")

        return {
            "success": True,
            "message": "所有英雄出装方案应用成功",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"应用所有英雄出装方案失败: {str(e)}")


