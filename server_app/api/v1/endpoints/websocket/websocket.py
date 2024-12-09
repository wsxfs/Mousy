from fastapi import APIRouter, WebSocket
from server_app.services.front.websocket2front.websocket2front import Websocket2Front

router = APIRouter()
w2front = Websocket2Front()

@router.websocket("/test")
async def websocket_endpoint(websocket: WebSocket):
    await w2front.connect(websocket)
    try:
        while True:
            # 保持连接活跃
            data = await websocket.receive_text()
            print("接收到消息：", data)
            await w2front.broadcast({"type": "message", "content": data})
    except Exception:
        await w2front.disconnect(websocket)