# -*- coding: utf-8 -*-
# @Time    : 2024/11/16 13:56
# @Author  : GZA
# @File    : perks_and_items.py
import time
import asyncio

from fastapi import APIRouter, Request, Body
from typing import List, Literal
from pydantic import BaseModel
from fastapi import HTTPException

from server_app.services.lcu import Http2Lcu
from server_app.services.item_set_manager.item_set_manager import ItemSetManager
from server_app.services.opgg.opgg import Opgg

router = APIRouter()

# 在文件开头定义所有映射字典
MAPS = {
    'position': {
        'TOP': '上路',
        'JUNGLE': '打野',
        'MID': '中路',
        'ADC': '下路',
        'SUPPORT': '辅助',
        'none': '无分路'
    },
    'region': {
        'global': '全球',
        'kr': '韩服',
        'euw': '欧服',
        'na': '美服'
    },
    'tier': {
        'all': '全部',
        'bronze': '青铜',
        'silver': '白银',
        'gold': '黄金',
        'platinum': '铂金',
        'diamond': '钻石',
        'master': '大师',
        'grandmaster': '宗师',
        'challenger': '王者',
        'gold_plus': '黄金以上',
        'platinum_plus': '铂金以上',
        'diamond_plus': '钻石以上',
        'master_plus': '大师以上'
    },
    'mode': {
        'ranked': '单双排位',
        'aram': '极地大乱斗'
    }
}


"""应用符文页接口"""
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

"""应用出装页接口"""  # TODO: 存在bug，鱼鞋、魔宗等装备无法识别，需要进一步优化
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


def create_title(champion_name: str, position: str, region: str, tier: str, mode: str) -> str:
    """生成统一格式的标题"""
    position_text = f" - {MAPS['position'].get(position, position)}" if mode != 'aram' else ''
    return (f"Mousy&OPGG - {champion_name}{position_text} - "
            f"{MAPS['region'].get(region, region)} - "
            f"{MAPS['tier'].get(tier, tier)} - "
            f"{MAPS['mode'].get(mode, mode)}")

def create_block(items: List[int], block_type: str, win_rate: float = None, pick_rate: float = None, is_first: bool = False) -> dict:
    """生成统一格式的物品块"""
    line = "———————————————"
    if win_rate is not None and pick_rate is not None:
        block_type = f"{block_type} (胜率{win_rate}% 选用{pick_rate}%)"
    if is_first:
        block_type += line
        
    return {
        "type": block_type,
        "items": [{"id": str(item_id), "count": 1} for item_id in items]
    }

def convert_to_item_set_json(item_set: ItemSetInput) -> dict:
    """简化后的转换函数"""
    timestamp = int(time.time())
    
    output_json = {
        "associatedChampions": item_set.associatedChampions,
        "associatedMaps": item_set.associatedMaps,
        "mode": "any",
        "map": "any",
        "sortrank": 0,
        "type": "global",
        "uid": f"Mousy_{item_set.source}_{item_set.associatedChampions[0] if item_set.associatedChampions else 'global'}_{timestamp}",
        "blocks": []
    }

    # 添加各类物品块
    for idx, info in enumerate(item_set.items.startItems):
        output_json["blocks"].append(
            create_block(info.icons, "出门装", float(info.winRate.rstrip('%')), float(info.pickRate.rstrip('%')), idx == 0)
        )
    
    # 添加鞋子
    for idx, info in enumerate(item_set.items.boots):
        output_json["blocks"].append(
            create_block(info.icons, "鞋子", float(info.winRate.rstrip('%')), float(info.pickRate.rstrip('%')), idx == 0)
        )
    
    # 添加核心装备
    for idx, info in enumerate(item_set.items.coreItems):
        output_json["blocks"].append(
            create_block(info.icons, "核心装", float(info.winRate.rstrip('%')), float(info.pickRate.rstrip('%')), idx == 0)
        )
    
    # 添加可选装备
    if item_set.items.lastItems:
        output_json["blocks"].append(
            create_block(item_set.items.lastItems, "可选装备", is_first=True)
        )

    return output_json

@router.post("/apply_items")
async def apply_items(request: Request, item_set: ItemSetInput):
    """应用出装页到指定英雄的推荐位置"""
    h2lcu: Http2Lcu = request.app.state.h2lcu
    item_set_manager: ItemSetManager = request.app.state.item_set_manager

    champion_name_zh = request.app.state.id2info['champions'][item_set.associatedChampions[0]]['name']
    champion_name_en = request.app.state.id2info['champions'][item_set.associatedChampions[0]]['alias']
    
    # 转换数据格式
    output_json = convert_to_item_set_json(item_set)
    
    # 修改 title 添加位置信息
    position_text = f" - {MAPS['position'].get(item_set.position, item_set.position)}" if item_set.mode != 'aram' else ''
    output_json['title'] = f"Mousy&OPGG - {champion_name_zh}{position_text} - {MAPS['region'].get(item_set.source, item_set.source)} - {MAPS['tier'].get(item_set.tier, item_set.tier)} - {MAPS['mode'].get(item_set.mode, item_set.mode)}"

    # 修改文件命名格式,与 get_apply_items_progress 保持一致
    file_name = f"Mousy_OPGG_{champion_name_en}_{item_set.source}_{item_set.mode}_{item_set.tier}_{item_set.position}"
    
    # 保存文件到指定英雄的推荐位置
    item_set_manager.save_item2champions(output_json, champion_name_en, file_name)

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
    """将champion_build转换为游戏可识别的物品套装JSON格式"""
    # 获取基础信息
    champion_data = champion_build['data']
    summary = champion_data['summary']
    items = champion_data['items']
    
    timestamp = int(time.time())
    
    output_json = {
        "associatedChampions": [summary['championId']],
        "associatedMaps": [11, 12],  # 召唤师峡谷和极地大乱斗
        "mode": "any",
        "map": "any",
        "sortrank": 0,
        "type": "global",
        "uid": f"Mousy_OPGG_{summary['championId']}_{timestamp}",
        "blocks": []
    }
    
    line = "———————————————"
    
    # 添加起始装备
    if items.get('startItems'):
        for idx, item in enumerate(items['startItems']):
            win_rate = round(item['win'] / item['play'] * 100, 1) if item['play'] > 0 else 0
            pick_rate = round(item['pickRate'] * 100, 1)
            
            block = create_block(
                item['icons'],
                "出门装",
                win_rate,
                pick_rate,
                idx == 0
            )
            output_json["blocks"].append(block)
    
    # 添加鞋子
    if items.get('boots'):
        for idx, boot in enumerate(items['boots']):
            win_rate = round(boot['win'] / boot['play'] * 100, 1) if boot['play'] > 0 else 0
            pick_rate = round(boot['pickRate'] * 100, 1)
            
            block = create_block(
                boot['icons'],
                "鞋子",
                win_rate,
                pick_rate,
                idx == 0
            )
            output_json["blocks"].append(block)
    
    # 添加核心装备
    if items.get('coreItems'):
        for idx, core in enumerate(items['coreItems']):
            win_rate = round(core['win'] / core['play'] * 100, 1) if core['play'] > 0 else 0
            pick_rate = round(core['pickRate'] * 100, 1)
            
            block = create_block(
                core['icons'],
                "核心装",
                win_rate,
                pick_rate,
                idx == 0
            )
            output_json["blocks"].append(block)
    
    # 添加可选装备
    if items.get('lastItems'):
        block = create_block(
            items['lastItems'],
            "可选装备",
            is_first=True
        )
        output_json["blocks"].append(block)
    
    # 设置标题
    output_json['title'] = create_title(
        champion_name_zh,
        position,
        region,
        tier,
        mode
    )
    
    return output_json

# 修改进度跟踪的全局变量
apply_items_progress = {
    "total": 0,
    "current": 0,
    "is_running": False,
    "last_update": 0  # 添加最后更新时间戳
}

@router.get("/get_apply_items_progress")
async def get_apply_items_progress():
    """获取应用装备的进度"""
    global apply_items_progress
    
    # 添加超时检查：如果超过5秒没有更新，认为进程已经停止
    if apply_items_progress["is_running"]:
        if time.time() - apply_items_progress.get("last_update", 0) > 5:
            apply_items_progress["is_running"] = False
    
    return {
        "total": apply_items_progress["total"],
        "current": apply_items_progress["current"],
        "is_running": apply_items_progress["is_running"]
    }

@router.post("/apply_all_ranked_items")
async def apply_all_ranked_items(request: Request, data: AllChampionsItemsInput = Body(...)):
    """批量应用所有英雄的单双排出装方案"""
    try:
        services = request.app.state
        h2lcu: Http2Lcu = services.h2lcu
        item_set_manager: ItemSetManager = services.item_set_manager
        opgg: Opgg = services.opgg
        
        # 获取所有英雄的位置信息
        champion_positions = await opgg.getAllChampionPositions(data.region, data.tier)
        
        # 初始化进度
        total_tasks = sum(len(positions) for positions in champion_positions.values())
        global apply_items_progress
        apply_items_progress.update({
            "total": total_tasks,
            "current": 0,
            "is_running": True,
            "last_update": time.time()
        })
        
        async def process_champion_position(champion_id: int, position: str) -> tuple[int, str, dict]:
            try:
                champion_name_zh = services.id2info['champions'][champion_id]['name']
                champion_name_en = services.id2info['champions'][champion_id]['alias']
                
                build = await services.opgg.getChampionBuild(
                    data.region, data.mode, champion_id, position, data.tier
                )
                
                if build and build.get('data'):
                    items_json = champion_build_2_items_json(
                        build,
                        champion_name_zh,
                        position,
                        data.region,
                        data.mode,
                        data.tier
                    )
                    
                    # 生成文件名
                    file_name = f"Mousy_OPGG_{champion_name_en}_{data.region}_{data.mode}_{data.tier}_{position}"
                    
                    # 保存出装方案
                    item_set_manager.save_item2champions(items_json, champion_name_en, file_name)
                    
                    # 更新进度和时间戳
                    apply_items_progress["current"] += 1
                    apply_items_progress["last_update"] = time.time()
                    
                    return champion_id, position, items_json
                
            except Exception as e:
                print(f"处理英雄 {champion_id} 的位置 {position} 失败: {str(e)}")
                apply_items_progress["current"] += 1
                apply_items_progress["last_update"] = time.time()
                return champion_id, position, None

        # 使用信号量限制并发数量
        sem = asyncio.Semaphore(5)
        
        async def process_with_semaphore(champion_id: int, position: str):
            async with sem:
                return await process_champion_position(champion_id, position)

        # 创建所有任务
        tasks = []
        for champion_id, positions in champion_positions.items():
            for position in positions:
                tasks.append(process_with_semaphore(champion_id, position))
        
        # 并发处理所有英雄的所有位置
        results = await asyncio.gather(*tasks)
        
        # 统计处理结果
        success_count = sum(1 for _, _, items_json in results if items_json is not None)
        total_count = len(results)
        
        # 确保在完成时正确设置状态
        apply_items_progress.update({
            "is_running": False,
            "current": apply_items_progress["total"]
        })
        
        return {
            "success": True,
            "message": f"批量应用出装成功，共处理 {total_count} 个英雄位置组合，成功 {success_count} 个",
            "data": {
                "total": total_count,
                "success": success_count
            }
        }

    except Exception as e:
        # 确保在发生错误时也设置正确的状态
        apply_items_progress["is_running"] = False
        raise HTTPException(status_code=500, detail=f"批量应用出装失败: {str(e)}")

@router.post("/apply_all_aram_items")
async def apply_all_aram_items(request: Request, data: AllChampionsItemsInput = Body(...)):
    """批量应用所有英雄的极地大乱斗出装方案"""
    try:
        services = request.app.state
        h2lcu: Http2Lcu = services.h2lcu
        item_set_manager: ItemSetManager = services.item_set_manager
        opgg: Opgg = services.opgg
        
        # 获取所有英雄ID列表
        champion_id_list = h2lcu.champion_id_list
        
        # 初始化进度
        total_tasks = len(champion_id_list)
        global apply_items_progress
        apply_items_progress.update({
            "total": total_tasks,
            "current": 0,
            "is_running": True,
            "last_update": time.time()
        })
        
        async def process_champion(champion_id: int) -> tuple[int, dict]:
            try:
                champion_name_zh = services.id2info['champions'][champion_id]['name']
                champion_name_en = services.id2info['champions'][champion_id]['alias']
                
                build = await services.opgg.getChampionBuild(
                    data.region, 'aram', champion_id, 'none', data.tier
                )
                
                if build and build.get('data'):
                    items_json = champion_build_2_items_json(
                        build,
                        champion_name_zh,
                        'none',
                        data.region,
                        'aram',
                        data.tier
                    )
                    
                    # 生成文件名
                    file_name = f"Mousy_OPGG_{champion_name_en}_{data.region}_aram_{data.tier}_none"
                    
                    # 保存出装方案
                    item_set_manager.save_item2champions(items_json, champion_name_en, file_name)
                    
                    # 更新进度和时间戳
                    apply_items_progress["current"] += 1
                    apply_items_progress["last_update"] = time.time()
                    
                    return champion_id, items_json
                
            except Exception as e:
                print(f"处理英雄 {champion_id} 失败: {str(e)}")
                apply_items_progress["current"] += 1
                apply_items_progress["last_update"] = time.time()
                return champion_id, None

        # 使用信号量限制并发数量
        sem = asyncio.Semaphore(5)
        
        async def process_with_semaphore(champion_id: int):
            async with sem:
                return await process_champion(champion_id)

        # 创建所有任务
        tasks = [process_with_semaphore(champion_id) for champion_id in champion_id_list]
        
        # 并发处理所有英雄
        results = await asyncio.gather(*tasks)
        
        # 统计处理结果
        success_count = sum(1 for _, items_json in results if items_json is not None)
        total_count = len(results)
        
        # 确保在完成时正确设置状态
        apply_items_progress.update({
            "is_running": False,
            "current": apply_items_progress["total"]
        })
        
        return {
            "success": True,
            "message": f"批量应用大乱斗出装成功，共处理 {total_count} 个英雄，成功 {success_count} 个",
            "data": {
                "total": total_count,
                "success": success_count
            }
        }

    except Exception as e:
        # 确保在发生错误时也设置正确的状态
        apply_items_progress["is_running"] = False
        raise HTTPException(status_code=500, detail=f"批量应用大乱斗出装失败: {str(e)}")

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
