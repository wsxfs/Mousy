# -*- coding: utf-8 -*-
# @Time    : 2024/11/13 4:32
# @Author  : GZA
# @File    : get_resource.py

from fastapi import APIRouter, Request
from fastapi.responses import Response
from typing import Optional, Dict, List
from pydantic import BaseModel, Field

from server_app.services.game_resource_getter.game_resource_getter import GameResourceGetter

router = APIRouter()


@router.get("/profile-icon/{icon_id}")
async def get_profile_icon(request: Request, icon_id: int):
    """获取召唤师头像"""
    image_data = await request.app.state.game_resource_getter.get_profile_icon(icon_id)
    return Response(content=image_data, media_type="image/jpeg")


@router.get("/champion-icon/{champion_id}")
async def get_champion_icon(request: Request, champion_id: int):
    """获取英雄图标"""
    image_data = await request.app.state.game_resource_getter.get_champion_icon(champion_id)
    return Response(content=image_data, media_type="image/png")


@router.get("/item-icon/{item_id}")
async def get_item_icon(request: Request, item_id: int):
    """获取物品图标"""
    image_data = await request.app.state.game_resource_getter.get_item_icon(item_id)
    return Response(content=image_data, media_type="image/png")


@router.get("/spell-icon/{spell_id}")
async def get_spell_icon(request: Request, spell_id: int):
    """获取召唤师技能图标"""
    image_data = await request.app.state.game_resource_getter.get_spell_icon(spell_id)
    return Response(content=image_data, media_type="image/png")


@router.get("/rune-icon/{rune_id}")
async def get_rune_icon(request: Request, rune_id: int):
    """获取符文图标"""
    image_data = await request.app.state.game_resource_getter.get_rune_icon(rune_id)
    return Response(content=image_data, media_type="image/png")


@router.get("/augment-icon/{augment_id}")
async def get_augment_icon(request: Request, augment_id: int):
    """获取强化符文图标"""
    image_data = await request.app.state.game_resource_getter.get_augment_icon(augment_id)
    return Response(content=image_data, media_type="image/png")


@router.get("/champion-splash/{skin_id}")
async def get_champion_splash(request: Request, skin_id: int, is_centered: Optional[bool] = True):
    """获取英雄原画
    
    Args:
        skin_id: 皮肤ID
        is_centered: 是否居中,默认为True(如BP界面),False为未居中
    """
    image_data = await request.app.state.game_resource_getter.get_champion_splash(skin_id, is_centered)
    return Response(content=image_data, media_type="image/jpeg")


class ResourceRequest(BaseModel):
    profile_icons: Optional[List[int]] = Field(default=None, description="召唤师头像ID列表")
    champion_icons: Optional[List[int]] = Field(default=None, description="英雄图标ID列表")
    item_icons: Optional[List[int]] = Field(default=None, description="物品图标ID列表")
    spell_icons: Optional[List[int]] = Field(default=None, description="召唤师技能图标ID列表")
    rune_icons: Optional[List[int]] = Field(default=None, description="符文图标ID列表")
    augment_icons: Optional[List[int]] = Field(default=None, description="强化符文图标ID列表")
    champion_splashes: Optional[List[dict]] = Field(default=None, description="英雄原画请求列表,格式:[{'skin_id':1, 'is_centered':true}]")


class ResourceResponse(BaseModel):
    profile_icons: Optional[Dict[int, str]] = Field(default=None, description="召唤师头像base64字典")
    champion_icons: Optional[Dict[int, str]] = Field(default=None, description="英雄图标base64字典")
    item_icons: Optional[Dict[int, str]] = Field(default=None, description="物品图标base64字典") 
    spell_icons: Optional[Dict[int, str]] = Field(default=None, description="召唤师技能图标base64字典")
    rune_icons: Optional[Dict[int, str]] = Field(default=None, description="符文图标base64字典")
    augment_icons: Optional[Dict[int, str]] = Field(default=None, description="强化符文图标base64字典")
    champion_splashes: Optional[Dict[str, str]] = Field(default=None, description="英雄原画base64字典,key格式:'skin_id_is_centered'")


@router.post("/batch_get_resources")
async def batch_get_resources(request: Request, resource_request: ResourceRequest) -> ResourceResponse:
    """批量获取游戏资源
    
    Args:
        resource_request: 资源请求对象,包含各类资源ID列表
        
    Returns:
        ResourceResponse: 资源响应对象,包含各类资源的base64编码字典
    """
    response = ResourceResponse()
    getter: GameResourceGetter = request.app.state.game_resource_getter
    
    # 获取召唤师头像
    if resource_request.profile_icons:
        response.profile_icons = {icon_id: await getter.get_profile_icon(icon_id) for icon_id in resource_request.profile_icons}
    
    # 获取英雄图标
    if resource_request.champion_icons:
        response.champion_icons = {icon_id: await getter.get_champion_icon(icon_id) for icon_id in resource_request.champion_icons}
    
    # 获取物品图标
    if resource_request.item_icons:
        response.item_icons = {icon_id: await getter.get_item_icon(icon_id) for icon_id in resource_request.item_icons}
    
    # 获取召唤师技能图标
    if resource_request.spell_icons:
        response.spell_icons = {icon_id: await getter.get_spell_icon(icon_id) for icon_id in resource_request.spell_icons}
    
    # 获取符文图标
    if resource_request.rune_icons:
        response.rune_icons = {icon_id: await getter.get_rune_icon(icon_id) for icon_id in resource_request.rune_icons}
    
    # 获取强化符文图标
    if resource_request.augment_icons:
        response.augment_icons = {icon_id: await getter.get_augment_icon(icon_id) for icon_id in resource_request.augment_icons}
    
    # 获取英雄原画
    if resource_request.champion_splashes:
        response.champion_splashes = {}
        for splash in resource_request.champion_splashes:
            skin_id = splash['skin_id']
            is_centered = splash.get('is_centered', True)  # 默认为True
            image_data = await getter.get_champion_splash(skin_id, is_centered)
            key = f"{skin_id}_{is_centered}"
            response.champion_splashes[key] = image_data
    
    return response
