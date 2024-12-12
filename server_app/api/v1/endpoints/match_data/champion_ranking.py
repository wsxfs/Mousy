# -*- coding: utf-8 -*-
# @Time    : 2024/11/15 4:46
# @Author  : GZA
# @File    : champion_ranking.py

from fastapi import APIRouter, Request, Form
from pydantic import BaseModel, Field
from typing import Annotated
from server_app.services.opgg.opgg import Opgg

router = APIRouter()


class TierListInput(BaseModel):
    """获取英雄梯队数据的输入模型"""
    region: str = Field(default="kr", description="服务器地区，如'kr'、'na'等")
    mode: str = Field(default="ranked", description="游戏模式，如'ranked'、'normal'等")
    tier: str = Field(default="platinum_plus", description="段位，如'platinum_plus'、'diamond_plus'等")


class ChampionBuildInput(BaseModel):
    """获取英雄构建数据的输入模型"""
    champion_id: int = Field(default=1,  description="英雄ID")
    region: str = Field(default="kr", description="服务器地区，如'kr'、'na'等")
    mode: str = Field(default="ranked", description="游戏模式，如'ranked'、'normal'等")
    position: str = Field(default="TOP", description="位置，如'TOP'、'JUNGLE'等")
    tier: str = Field(default="platinum_plus", description="段位，如'platinum_plus'、'diamond_plus'等")


class ChampionPositionsInput(BaseModel):
    """获取英雄位置数据的输入模型"""
    champion_id: int = Field(default=1, description="英雄ID")
    region: str = Field(default="kr", description="服务器地区，如'kr'、'na'等")
    tier: str = Field(default="platinum_plus", description="段位，如'platinum_plus'、'diamond_plus'等")


@router.post("/tier_list", name="获取英雄梯队数据")
async def get_tier_list(
        request: Request,
        form: Annotated[TierListInput, Form()]
):
    """
    获取英雄梯队数据
    
    Args:
        form: 包含region、mode和tier参数的表单数据
        
    Returns:
        包含英雄梯队数据的字典
    """
    opgg: Opgg = request.app.state.opgg
    tier_list = await opgg.getTierList(
        region=form.region,
        mode=form.mode,
        tier=form.tier
    )
    return tier_list


@router.post("/champion_build", name="获取英雄构建数据")
async def get_champion_build(
        request: Request,
        form: Annotated[ChampionBuildInput, Form()]
):
    """
    获取特定英雄的构建数据
    
    Args:
        form: 包含champion_id、region、mode、position和tier参数的表单数据
        
    Returns:
        包含英雄构建数据的字典
    """
    opgg: Opgg = request.app.state.opgg
    champion_build = await opgg.getChampionBuild(
        region=form.region,
        mode=form.mode,
        championId=form.champion_id,
        position=form.position,
        tier=form.tier
    )
    return champion_build


@router.post("/champion_positions", name="获取英雄可用位置")
async def get_champion_positions(
        request: Request,
        form: Annotated[ChampionPositionsInput, Form()]
):
    """
    获取特定英雄的所有可用位置
    
    Args:
        form: 包含champion_id、region和tier参数的表单数据
        
    Returns:
        包含英雄可用位置的列表
    """
    opgg = request.app.state.opgg
    return await opgg.getChampionPositions(
        region=form.region,
        championId=form.champion_id,
        tier=form.tier
    )
