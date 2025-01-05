# -*- coding: utf-8 -*-
# @Time    : 2024/11/9 2:07
# @Author  : GZA
# @File    : user_settings.py
from fastapi import APIRouter, Request, Form, Body
from typing import Optional, List
from pydantic import BaseModel
from typing import Annotated
from server_app.services.user_config.user_config_handler import UserConfigHandler
from server_app.services.user_config.user_config import SettingsModel


router = APIRouter()


@router.get("/get", name="获取设置")
async def get_settings(request: Request):
    return request.app.state.user_config.settings


@router.post("/add", name="添加设置")
async def update_settings(request: Request, key: str, value: str):
    request.app.state.user_config.set_setting(key, value)
    return {"message": "Settings updated"}


@router.post("/update_all", name="更新所有设置")
async def update_all_settings(request: Request, new_settings: SettingsModel):
    """批量更新设置。"""
    request.app.state.user_config.update_settings(new_settings)
    return {"message": "All settings updated"}
