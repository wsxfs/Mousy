# -*- coding: utf-8 -*-
# @Time    : 2024/11/16 13:56
# @Author  : GZA
# @File    : perks.py.py
from pathlib import Path
import time
import asyncio
from itertools import islice

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
    title: str                      # 英雄名称
    source: str                     # 服务器
    tier: str                       # 段位
    mode: str                       # 游戏模式
    position: str                   # 位置
    associatedChampions: List[int]  # 关联英雄ID列表
    associatedMaps: List[int]      # 关联地图ID列表
    items: ItemSetContent          # 出装内容


def convert_to_item_set_json(item_set: ItemSetInput) -> dict:
    """将ItemSetInput转换为游戏可识别的物品套装JSON格式
    
    Args:
        item_set: 输入的物品套装数据
        
    Returns:
        dict: 转换后的JSON数据结构
    """
    # 添加区域、段位和模式的中文映射
    region_map = {
        'global': '全球',
        'kr': '韩服',
        'euw': '欧服',
        'na': '美服'
    }
    
    tier_map = {
        'all': '全部',
        'bronze': '青铜',
        'silver': '白银',
        'gold': '黄金',
        'gold_plus': '黄金及以上',
        'platinum': '铂金',
        'platinum_plus': '铂金及以上',
        'diamond': '钻石',
        'diamond_plus': '钻石及以上',
        'master': '大师',
        'master_plus': '大师及以上',
        'grandmaster': '宗师',
        'challenger': '王者'
    }
    
    mode_map = {
        'ranked': '单双排位',
        'aram': '极地大乱斗'
    }

    position_map = {
        'TOP': '上路',
        'JUNGLE': '打野',
        'MID': '中路',
        'ADC': '下路',
        'SUPPORT': '辅助',
        'none': '无分路'
    }

    timestamp = int(time.time())
    
    # 构建标题
    title_parts = [
        f"Mousy&OPGG - {item_set.title}",
        f"服务器: {region_map.get(item_set.source, item_set.source)}",
        f"段位: {tier_map.get(item_set.tier, item_set.tier)}",
        f"模式: {mode_map.get(item_set.mode, item_set.mode)}"
    ]
    
    # 只在非极地大乱斗模式下添加位置信息
    if item_set.mode != 'aram':
        title_parts.append(f"位置: {position_map.get(item_set.position, item_set.position)}")
    
    output_json = {
        "associatedChampions": item_set.associatedChampions,
        "associatedMaps": item_set.associatedMaps,
        "mode": "any",
        "map": "any",
        "sortrank": 0,
        "type": "global",
        "uid": f"Mousy_{item_set.source}_{item_set.associatedChampions[0] if item_set.associatedChampions else 'global'}_{timestamp}",
        "title": " - ".join(title_parts),
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

# 中英文映射
position_map = {
    'TOP': '上路',
    'JUNGLE': '打野',
    'MID': '中路',
    'ADC': '下路',
    'SUPPORT': '辅助',
    'none': '无分路'
}
region_map = {
    'global': '全球',
    'kr': '韩服',
    'euw': '欧服',
    'na': '美服'
}

tier_map = {
    'all': '全部',
    'bronze': '青铜',
    'silver': '白银',
    'gold': '黄金',
    'gold_plus': '黄金及以上',
    'platinum': '铂金',
    'platinum_plus': '铂金及以上',
    'diamond': '钻石',
    'diamond_plus': '钻石及以上',
    'master': '大师',
    'master_plus': '大师及以上',
    'grandmaster': '宗师',
    'challenger': '王者'
}

mode_map = {
    'ranked': '单双排位',
    'aram': '极地大乱斗'
}

@router.post("/apply_items")
async def apply_items(request: Request, item_set: ItemSetInput):
    """应用出装页到指定英雄的推荐位置"""
    h2lcu: Http2Lcu = request.app.state.h2lcu
    item_set_manager: ItemSetManager = request.app.state.item_set_manager

    # 添加区域、段位和模式的中文映射
    region_map = {
        'global': '全球',
        'kr': '韩服',
        'euw': '欧服',
        'na': '美服'
    }
    
    tier_map = {
        'all': '全部',
        'bronze': '青铜',
        'silver': '白银',
        'gold': '黄金',
        'gold_plus': '黄金及以上',
        'platinum': '铂金',
        'platinum_plus': '铂金及以上',
        'diamond': '钻石',
        'diamond_plus': '钻石及以上',
        'master': '大师',
        'master_plus': '大师及以上',
        'grandmaster': '宗师',
        'challenger': '王者'
    }
    
    mode_map = {
        'ranked': '单双排位',
        'aram': '极地大乱斗'
    }

    champion_name_zh = request.app.state.id2info['champions'][item_set.associatedChampions[0]]['name']
    champion_name_en = request.app.state.id2info['champions'][item_set.associatedChampions[0]]['alias']
    
    # 转换数据格式
    output_json = convert_to_item_set_json(item_set)
    
    # 修改 title 添加位置信息
    position_text = f" - {position_map.get(item_set.position, item_set.position)}" if item_set.mode != 'aram' else ''
    output_json['title'] = f"Mousy&OPGG - {champion_name_zh}{position_text} - {region_map.get(item_set.source, item_set.source)} - {tier_map.get(item_set.tier, item_set.tier)} - {mode_map.get(item_set.mode, item_set.mode)}"

    # 保存文件到指定英雄的推荐位置
    item_set_manager.save_item2champions(output_json, champion_name_en, f"Mousy_{item_set.source}_{champion_name_en}")

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

def champion_build_2_items_json(champion_build: dict, champion_name_zh: str, position: str, region: str, mode: str, tier: str) -> dict:
    """将champion_build转换为游戏可识别的物品套装JSON格式
    
    Args:
        champion_build: 从OPGG获取的英雄出装数据
        champion_name: 英雄名称
        region: 服务器
        mode: 游戏模式
        tier: 段位
        
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
        "title": f"Mousy&OPGG - {champion_name_zh}{position}的出装方案 - 服务器: {region} - 段位: {tier} - 模式: {mode}",
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
    
    # 添加位置映射

    
    # 修改 title 添加位置信息
    position_text = f" - {position_map.get(position, position)}" if mode != 'aram' else ''
    output_json['title'] = f"Mousy&OPGG - {champion_name_zh}{position_text} - {region_map.get(region, region)} - {tier_map.get(tier, tier)} - {mode_map.get(mode, mode)}"
    
    return output_json

# 添加一个全局变量来跟踪进度
apply_items_progress = {
    "total": 0,
    "current": 0,
    "is_running": False
}

@router.get("/get_apply_items_progress")
async def get_apply_items_progress():
    """获取应用装备的进度"""
    return {
        "total": apply_items_progress["total"],
        "current": apply_items_progress["current"],
        "is_running": apply_items_progress["is_running"]
    }

@router.post("/apply_all_champions_items")
async def apply_all_champions_items(request: Request, data: AllChampionsItemsInput = Body(...)):
    """应用所有英雄的出装方案"""
    try:
        h2lcu: Http2Lcu = request.app.state.h2lcu
        item_set_manager: ItemSetManager = request.app.state.item_set_manager
        opgg: Opgg = request.app.state.opgg
        id2info: dict = request.app.state.id2info
        
        # 重置并初始化进度
        global apply_items_progress
        apply_items_progress["total"] = len(h2lcu.champion_id_list)
        apply_items_progress["current"] = 0
        apply_items_progress["is_running"] = True

        

        # 获取所有英雄位置信息
        all_champion_positions = await opgg.getAllChampionPositions(data.region, data.tier)
        
        async def process_champion(champion_id, positions):
            champion_builds = []
            for position in positions:
                try:
                    build = await opgg.getChampionBuild(
                        data.region, data.mode, champion_id, position, data.tier
                    )
                    if build:
                        items_json = champion_build_2_items_json(
                            build, 
                            id2info['champions'][champion_id]['name'],
                            position,
                            data.region, data.mode, data.tier
                        )
                        champion_name_zh = id2info['champions'][champion_id]['name']
                        # 修改 title 添加位置信息
                        position_text = f" - {position_map.get(position, position)}" if data.mode != 'aram' else ''
                        items_json['title'] = f"Mousy&OPGG - {champion_name_zh}{position_text} - {region_map.get(data.region, data.region)} - {tier_map.get(data.tier, data.tier)} - {mode_map.get(data.mode, data.mode)}"
                        champion_builds.append((items_json, position))
                except Exception as e:
                    print(f"获取英雄 {champion_id} 位置 {position} 出装失败: {str(e)}")
                    continue
            
            # 更新进度
            apply_items_progress["current"] += 1
            
            return champion_id, champion_builds

        # 分批处理，每批处理 65 个英雄
        BATCH_SIZE = 65
        champion_id_list = h2lcu.champion_id_list
        
        try:
            for i in range(0, len(champion_id_list), BATCH_SIZE):
                batch = champion_id_list[i:i + BATCH_SIZE]
                tasks = [
                    process_champion(champion_id, all_champion_positions[champion_id])
                    for champion_id in batch
                ]
                
                # 并发执行当前批次的任务
                results = await asyncio.gather(*tasks)
                
                # 批量保存文件
                for champion_id, builds in results:
                    if builds:
                        champion_name = id2info['champions'][champion_id]['alias']
                        for items_json, position in builds:
                            item_set_manager.save_item2champions(
                                items_json,
                                champion_name,
                                f"Mousy_OPGG_{champion_name}_{data.region}_{data.mode}_{data.tier}_{position}"
                            )
        finally:
            # 完成后重置状态
            apply_items_progress["is_running"] = False

        return {
            "success": True,
            "message": "所有英雄出装方案应用成功",
        }

    except Exception as e:
        # 发生错误时也要重置状态
        apply_items_progress["is_running"] = False
        raise HTTPException(status_code=500, detail=f"应用所有英雄出装方案失败: {str(e)}")

@router.post("/reset_all_champions_items")
async def reset_all_champions_items(request: Request):
    """恢复所有英雄的出装方案"""
    try:
        h2lcu: Http2Lcu = request.app.state.h2lcu
        item_set_manager: ItemSetManager = request.app.state.item_set_manager
        
        # 删除所有以Mousy开头的推荐出装文件
        champion_id_list = h2lcu.champion_id_list
        for champion_id in champion_id_list:
            champion_name = request.app.state.id2info['champions'][champion_id]['alias']
            item_set_manager.delete_mousy_items(champion_name)

        return {
            "success": True,
            "message": "所有英雄出装方案已恢复默认"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"恢复出装方案失败: {str(e)}")


