# -*- coding: utf-8 -*-
# @Time    : 2024/11/16 13:55
# @Author  : GZA
# @File    : __init__.py

from fastapi import APIRouter
from . import match_data, perks

router = APIRouter()
router.include_router(match_data.router, prefix="/match_data", tags=["英雄数据"])
router.include_router(perks.router, prefix="/match_data", tags=["应用符文或出装"])
