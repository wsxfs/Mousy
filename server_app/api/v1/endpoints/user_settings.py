# -*- coding: utf-8 -*-
# @Time    : 2024/11/9 2:07
# @Author  : GZA
# @File    : user_settings.py
from fastapi import APIRouter, Request, Form, Body
from typing import Optional, List
from pydantic import BaseModel
from typing import Annotated


class UserConfigInput(BaseModel):
    """用户配置输入。"""
    auto_accept: Optional[bool] = None
    auto_pick_champions: Optional[List[str]] = None
    auto_ban_champions: Optional[List[str]] = None
    auto_accept_swap_position: Optional[bool] = None
    auto_accept_swap_champion: Optional[bool] = None


router = APIRouter()


@router.get("/get")
async def get_settings(request: Request):
    return request.app.state.user_config.settings


@router.post("/add")
async def update_settings(request: Request, key: str, value: str):
    request.app.state.user_config.set_setting(key, value)
    return {"message": "Settings updated"}


@router.post("/update_all")
async def update_all_settings(request: Request, new_settings: UserConfigInput):
    """批量更新设置。"""
    request.app.state.user_config.update_settings(new_settings)
    return {"message": "All settings updated"}
