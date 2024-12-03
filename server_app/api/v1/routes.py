# -*- coding: utf-8 -*-
# @Time    : 2024/11/9 2:04
# @Author  : GZA
# @File    : routes.py
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from server_app.new_services.game_resource_getter.game_resource_getter import GameResourceGetter
from server_app.new_services.item_set_manager.item_set_manager import ItemSetManager
from server_app.new_services.user_config.user_config import UserConfig
from server_app.new_services.opgg.opgg import Opgg
from server_app.new_services.lcu import Http2Lcu, Websocket2Lcu, get_port_and_token

from .endpoints import user_settings, hello_world, match_history, match_data
from .endpoints.common import router as common_router


async def app_state_init():
    # 计算port和token
    lcu_port, lcu_token = get_port_and_token()
    # 生成实例
    user_config = UserConfig()
    h2lcu = Http2Lcu(lcu_port, lcu_token)
    w2lcu = Websocket2Lcu(lcu_port, lcu_token)
    opgg = Opgg(lcu_port, lcu_token)
    await opgg.start()
    game_resource_getter = GameResourceGetter(h2lcu, r'resources/game')

    game_client_path = Path(await h2lcu.get_game_client_directory())
    item_set_manager = ItemSetManager(game_client_path)

    id2info = await h2lcu.get_all_id2info()

    # 绑定实例到app的state中
    app.state.user_config = user_config
    app.state.get_port_and_token = get_port_and_token
    app.state.port = lcu_port
    app.state.token = lcu_token
    app.state.h2lcu = h2lcu
    app.state.w2lcu = w2lcu
    app.state.opgg = opgg
    app.state.id2info = id2info
    app.state.game_resource_getter = game_resource_getter
    app.state.game_client_path = game_client_path
    app.state.item_set_manager = item_set_manager


async def app_state_update(port, token):
    app.state.port = port
    app.state.token = token
    app.state.h2lcu.update_port_and_token(port, token)
    app.state.w2lcu.update_port_and_token(port, token)
    app.state.id2info = await app.state.h2lcu.get_all_id2info()
    app.state.game_resource_getter = GameResourceGetter(app.state.h2lcu, r'resources/game')


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
    # current_item_page = await h2lcu.get_current_item_page()
    # champion_build = await app.state.opgg.getChampionBuild('kr', 'ranked', 1, 'top', 'platinum')
    # body = {'associatedChampions': [133], 'associatedMaps': [11], 'blocks': [{'hideIfSummonerSpell': '', 'items': [{'count': 1, 'id': '1055'}, {'count': 1, 'id': '2003'}, {'count': 1, 'id': '3340'}], 'showIfSummonerSpell': '', 'type': '出门装'}, {'hideIfSummonerSpell': '', 'items': [{'count': 1, 'id': '6672'}], 'showIfSummonerSpell': '', 'type': '核心装备'}, {'hideIfSummonerSpell': '', 'items': [{'count': 1, 'id': '3111'}, {'count': 1, 'id': '1029'}, {'count': 1, 'id': '1006'}], 'showIfSummonerSpell': '', 'type': '多面手1'}, {'hideIfSummonerSpell': '', 'items': [{'count': 1, 'id': '3010'}, {'count': 1, 'id': '1029'}, {'count': 1, 'id': '1006'}, {'count': 1, 'id': '2022'}], 'showIfSummonerSpell': '', 'type': '多面手2'}, {'hideIfSummonerSpell': '', 'items': [{'count': 1, 'id': '3111'}, {'count': 1, 'id': '6672'}, {'count': 1, 'id': '3091'}, {'count': 1, 'id': '3143'}, {'count': 1, 'id': '2504'}, {'count': 1, 'id': '3153'}], 'showIfSummonerSpell': '', 'type': '新的区块'}, {'hideIfSummonerSpell': '', 'items': [{'count': 1, 'id': '3010'}, {'count': 1, 'id': '6672'}, {'count': 1, 'id': '3091'}, {'count': 1, 'id': '2504'}, {'count': 1, 'id': '3110'}, {'count': 1, 'id': '3181'}], 'showIfSummonerSpell': '', 'type': '新的区块'}], 'map': 'any', 'mode': 'any', 'preferredItemSlots': [], 'sortrank': 0, 'startedFrom': 'blank', 'title': '多面手11', 'type': 'custom', 'uid': 'cacccb30-316d-11ef-9069-1d4e6a1890bd'}
    #
    # post_response = await h2lcu.update_item_pages(body)
    #
    # print(post_response)



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
app.include_router(common_router, prefix="/api/common", tags=["Common"])
app.include_router(match_data.router, prefix="/api/match_data", tags=["Match Data"])

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
