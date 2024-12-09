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