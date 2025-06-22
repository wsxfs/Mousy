# -*- coding: utf-8 -*-
# @Time    : 2024/12/3 22:00
# @Author  : GZA
# @File    : __init__.py

from . import unclaimed_rewards

# 创建主路由
from fastapi import APIRouter

router = APIRouter()

# 包含子路由
router.include_router(unclaimed_rewards.router, tags=["Unclaimed Rewards"]) 