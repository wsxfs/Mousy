# -*- coding: utf-8 -*-
# @Time    : 2025/6/22 22:00
# @Author  : GZA
# @File    : unclaimed_rewards.py

from typing import List, Optional
from fastapi import APIRouter, Request
from pydantic import BaseModel

from server_app.services.lcu.http2lcu.http2lcu_response_parser import UnclaimedReward

router = APIRouter()


class UnclaimedRewardsResponse(BaseModel):
    """未领取奖励响应模型"""
    success: bool
    message: str
    data: Optional[List[UnclaimedReward]] = None


class BatchClaimRequestItem(BaseModel):
    grantId: str
    rewardGroupId: str
    rewardIds: list[str]
    maxSelectionsAllowed: int

class BatchClaimResponseItem(BaseModel):
    grantId: str
    rewardGroupId: str
    selected: list[str]
    result: dict
    success: bool
    message: str

class BatchClaimResponse(BaseModel):
    results: list[BatchClaimResponseItem]


@router.get("/get_unclaimed_rewards", name="获取未领取的奖励信息", response_model=UnclaimedRewardsResponse)
async def get_unclaimed_rewards(request: Request):
    """
    获取当前账号未领取的奖励信息
    
    Returns:
        UnclaimedRewardsResponse: 包含未领取奖励列表的响应
    """
    try:
        h2lcu = request.app.state.h2lcu
        
        # 检查LCU连接状态
        if not request.app.state.w2lcu.is_connected:
            return UnclaimedRewardsResponse(
                success=False,
                message="LCU未连接，请先连接游戏客户端"
            )
        
        # 获取未领取的奖励
        rewards_data = await h2lcu.get_unclaimed_rewards()
        
        if rewards_data is None:
            return UnclaimedRewardsResponse(
                success=True,
                message="暂无未领取的奖励",
                data=[]
            )
        
        # 使用Pydantic模型验证数据，并只保留未领取（PENDING_SELECTION）
        validated_rewards = []
        for reward in rewards_data:
            if reward.get('info', {}).get('status') == 'PENDING_SELECTION':
                validated_reward = UnclaimedReward(**reward)
                validated_rewards.append(validated_reward)
        
        return UnclaimedRewardsResponse(
            success=True,
            message=f"您有 {len(validated_rewards)} 个奖励未领取",
            data=validated_rewards
        )
        
    except Exception as e:
        return UnclaimedRewardsResponse(
            success=False,
            message=f"获取未领取奖励失败: {str(e)}"
        )

@router.post("/batch_claim_rewards", name="批量领取奖励", response_model=BatchClaimResponse)
async def batch_claim_rewards(request: Request, items: List[BatchClaimRequestItem]):
    """
    批量领取奖励，每组rewardIds分批，每批maxSelectionsAllowed个领取，最后一批不足maxSelectionsAllowed也领取
    """
    h2lcu = request.app.state.h2lcu
    results = []
    for item in items:
        reward_ids = item.rewardIds
        batch_size = item.maxSelectionsAllowed
        total = len(reward_ids)
        for i in range(0, total, batch_size):
            selections = reward_ids[i:i+batch_size]
            try:
                result = await h2lcu.select_reward(item.grantId, item.rewardGroupId, selections)
                results.append(BatchClaimResponseItem(
                    grantId=item.grantId,
                    rewardGroupId=item.rewardGroupId,
                    selected=selections,
                    result=result,
                    success=True,
                    message=f"领取成功: {selections}"
                ))
            except Exception as e:
                results.append(BatchClaimResponseItem(
                    grantId=item.grantId,
                    rewardGroupId=item.rewardGroupId,
                    selected=selections,
                    result={},
                    success=False,
                    message=str(e)
                ))
    return BatchClaimResponse(results=results) 