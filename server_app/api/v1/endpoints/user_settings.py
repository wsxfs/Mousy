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


@router.post("/reset_close_preference", name="重置关闭偏好设置")
async def reset_close_preference(request: Request):
    """重置关闭偏好设置。"""
    request.app.state.user_config.clear_close_preference()
    return {"message": "Close preference reset successfully"}


@router.post("/update_close_preference", name="更新关闭偏好设置")
async def update_close_preference(request: Request, settings: dict):
    """更新关闭偏好设置。"""
    if "closePreference" in settings:
        close_pref = settings["closePreference"]
        request.app.state.user_config.set_close_preference(
            action=close_pref.get("action", ""),
            remember_choice=close_pref.get("rememberChoice", False)
        )
        return {"message": "Close preference updated successfully"}
    return {"message": "No close preference provided", "success": False}


@router.get("/get_close_preference", name="获取关闭偏好设置")
async def get_close_preference(request: Request):
    """获取关闭偏好设置。"""
    close_pref = request.app.state.user_config.get_close_preference()
    if close_pref:
        return close_pref
    return {"action": "", "rememberChoice": False}
