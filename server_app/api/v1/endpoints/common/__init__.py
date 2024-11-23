# -*- coding: utf-8 -*-
# @Time    : 2024/11/13 4:30
# @Author  : GZA
# @File    : __init__.py.py

from fastapi import APIRouter
from . import get_resource, get_info

router = APIRouter()
router.include_router(get_resource.router, prefix="/game_resource", tags=["游戏资源"])
router.include_router(get_info.router, prefix="/game_resource", tags=["游戏信息"])
