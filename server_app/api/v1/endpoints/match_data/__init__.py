# -*- coding: utf-8 -*-
# @Time    : 2024/11/16 13:55
# @Author  : GZA
# @File    : __init__.py

from fastapi import APIRouter
from . import champion_ranking, perks_and_items

router = APIRouter()
router.include_router(champion_ranking.router, prefix="/champion_ranking_data", tags=["英雄排名数据"])
router.include_router(perks_and_items.router, prefix="/perks_and_items", tags=["应用符文或出装"])
