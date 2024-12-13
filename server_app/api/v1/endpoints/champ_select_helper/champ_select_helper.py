from fastapi import APIRouter, Request
from server_app.services.user_config.user_config_handler import UserConfigHandler
router = APIRouter()


@router.get("/swap_champion_off", name="关闭自动换人")
async def swap_champion_off(request: Request):
    user_config_handler: UserConfigHandler = request.app.state.user_config_handler
    user_config_handler.swap_champion_button = False
    return {"success": True, "message": "已锁定英雄"}

@router.get("/swap_champion_on", name="开启自动换人")
async def swap_champion_on(request: Request):
    user_config_handler: UserConfigHandler = request.app.state.user_config_handler
    user_config_handler.swap_champion_button = True
    return {"success": True, "message": "已解锁英雄"}



