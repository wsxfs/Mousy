from fastapi import APIRouter, WebSocket
import json
from server_app.services import Websocket2Front

router = APIRouter()

@router.websocket("/test")
async def websocket_endpoint(websocket: WebSocket):
    app = websocket.app
    w2front: Websocket2Front = app.state.w2front
    await w2front.connect(websocket)
    try:
        # 连接后立即发送当前的 sync_data 状态
        sync_data = {
            "type": "sync_data",
            "data": {
                "my_team_puuid_list": w2front.sync_data.my_team_puuid_list,
                "their_team_puuid_list": w2front.sync_data.their_team_puuid_list,
                "current_champion": w2front.sync_data.current_champion,
                "bench_champions": w2front.sync_data.bench_champions,
                "gameflow_phase": w2front.sync_data.gameflow_phase,
                "swap_champion_button": w2front.sync_data.swap_champion_button,
                "selected_champion_id": w2front.sync_data.selected_champion_id,
                "summoner_id": w2front.sync_data.summoner_id,
                "lcu_connected": w2front.sync_data.lcu_connected,
            }
        }
        await websocket.send_json(sync_data)
        
        while True:
            # 保持连接活跃
            receive_text = await websocket.receive_text()
            data_json = json.loads(receive_text)
            data_message = data_json["message"]
            print("接收到消息：", data_message)
            await w2front.broadcast(f"接收到消息：{data_message}")
    except Exception as e:
        print("连接断开")
        print(e)
        await w2front.disconnect(websocket)