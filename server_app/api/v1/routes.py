# -*- coding: utf-8 -*-
# @Time    : 2024/11/9 2:04
# @Author  : GZA
# @File    : routes.py
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from server_app.services import GameResourceGetter, ItemSetManager, UserConfig, UserConfigHandler, Opgg, Http2Lcu, Websocket2Lcu, Websocket2Front
from server_app.services import get_port_and_token_by_tasklist
from server_app.services.notebook_config import NoteBookConfig

from .endpoints import user_settings, hello_world, match_history, match_data, websocket, common, champ_select_helper, note_book


async def app_state_init():
    # 获取port和token
    lcu_port, lcu_token = get_port_and_token_by_tasklist()
    # 生成实例
    user_config = UserConfig()
    w2front = Websocket2Front()
    h2lcu = Http2Lcu(lcu_port, lcu_token)
    w2lcu = Websocket2Lcu(lcu_port, lcu_token, w2front)
    
    # 启动自动连接检测
    await w2lcu.start_auto_connect(on_port_token_update=app_state_update)
    
    user_config_handler = UserConfigHandler(user_config, h2lcu, w2lcu, w2front)
    all_events = w2lcu.all_events
    
    game_resource_getter = GameResourceGetter(h2lcu, r'resources/game')
    opgg = Opgg(h2lcu, game_resource_getter)
    await opgg.start()

    item_set_manager = ItemSetManager(h2lcu)
    await item_set_manager.update_h2lcu()

    id2info = await h2lcu.get_all_id2info()

    # 初始化笔记本配置
    notebook_config = NoteBookConfig()

    # 绑定实例到app的state中
    app.state.user_config = user_config
    app.state.get_port_and_token = get_port_and_token_by_tasklist
    app.state.port = lcu_port
    app.state.token = lcu_token
    app.state.h2lcu = h2lcu
    app.state.w2lcu = w2lcu
    app.state.w2front = w2front
    app.state.user_config_handler = user_config_handler
    app.state.all_events = all_events
    app.state.opgg = opgg
    app.state.id2info = id2info
    app.state.game_resource_getter = game_resource_getter
    app.state.item_set_manager = item_set_manager
    app.state.notebook_config = notebook_config

async def app_state_update(port, token):  # Todo:OPGG可能需要更新
    app.state.port = port
    app.state.token = token
    app.state.h2lcu.update_port_and_token(port, token)
    app.state.w2lcu.update_port_and_token(port, token)
    app.state.id2info = await app.state.h2lcu.get_all_id2info()
    app.state.game_resource_getter = GameResourceGetter(app.state.h2lcu, r'resources/game')
    await app.state.item_set_manager.update_h2lcu()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI的生命周期函数"""
    app.state.app_state_init = app_state_init
    app.state.app_state_update = app_state_update
    try:
        await app_state_init()
    except Exception as e:
        print("初始化失败: ", e)


    # # test
    # game_mode = await app.state.h2lcu.get_game_mode()
    # print(f"{game_mode=}")



    yield  # 服务运行期间
    # 这里可以添加清理代码


app = FastAPI(lifespan=lifespan)

# 配置允许的跨域源（origin）
origins = [
    "http://localhost:5173",  # 允许从 localhost:5173 访问
]

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 允许指定来源
    allow_credentials=True,  # 是否允许携带凭证（如 Cookies）
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
)

# 注册路由
app.include_router(user_settings.router, prefix="/api/user_settings", tags=["User Settings"])
app.include_router(hello_world.router, prefix="/api/hello_world", tags=["Hello World"])
app.include_router(match_history.router, prefix="/api/match_history", tags=["Match History"])
app.include_router(common.router, prefix="/api/common", tags=["Common"])
app.include_router(match_data.router, prefix="/api/match_data", tags=["Match Data"])
app.include_router(websocket.router, prefix="/api/websocket", tags=["Websocket"])
app.include_router(champ_select_helper.router, prefix="/api/champ_select_helper", tags=["Champ Select Helper"])
app.include_router(note_book.router, prefix="/api/note_book", tags=["Note Book"])

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
