# -*- coding: utf-8 -*-
# @Time    : 2024/11/13 4:30
# @Author  : GZA
# @File    : __init__.py.py

from fastapi import APIRouter
from . import get_resource, get_info, common_control

router = APIRouter()
router.include_router(get_resource.router, prefix="/game_resource", tags=["获取游戏资源"])
# Todo 修改game_resource为game_info
router.include_router(get_info.router, prefix="/game_resource", tags=["获取游戏信息"])
router.include_router(common_control.router, prefix="/common_control", tags=["通用控制接口"])
