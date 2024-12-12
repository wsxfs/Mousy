from fastapi import APIRouter, Request
from server_app.services.user_config.user_config_handler import UserConfigHandler

router = APIRouter()

@router.post("/bench_swap", name="交换候选席英雄")
async def bench_swap(request: Request, champion_id: int = None):
    user_config_handler: UserConfigHandler = request.app.state.user_config_handler
    await user_config_handler.bench_swap(champion_id)
    return {"message": "交换候选席英雄成功"}