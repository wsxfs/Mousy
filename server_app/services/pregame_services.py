# -*- coding: utf-8 -*-
# @Time    : 2024/11/8 0:52
# @Author  : GZA
# @File    : pregame_services.py

import asyncio
import time

from server_app.lcu.lcu_mine import Http2Lcu
from server_app.lcu.lcu_mine import Websocket2Lcu


class LcuServices:
    def __init__(self):
        self.h2lcu = Http2Lcu()

    async def accept_matchmaking(self, ):
        """接受匹配"""
        await self.h2lcu.accept_matchmaking()

    async def decline_matchmaking(self, ):
        """拒绝匹配"""
        # try:
        await self.h2lcu.decline_matchmaking()
        # except Exception as e:
        #     print("接受匹配出错:")
        #     print(e)
        # else:
        #     print("接受匹配成功")


# # Initialize Websocket2Lcu
# w2lcu = Websocket2Lcu(port=1234, token='your_token_here')

# @w2lcu.on["SummonerProfile"]
# async def on_summoner_profile(event):
#     print("Summoner Profile Updated:", event['data'])

# @w2lcu.on["GameFlowPhase"]
# async def on_game_flow_phase(event):
#     print("Game Flow Phase Changed:", event['data'])

# @w2lcu.on["ChampSelect"]
# async def on_champ_select(event):
#     print("Champ Select Updated:", event['data'])

# @w2lcu.on["SGPToken"]
# async def on_sgp_token(event):
#     print("SGP Token Updated:", event['data'])

# async def main():
#     await w2lcu.start()
#     print("WebSocket started")

#     # Simulate running for 10 seconds
#     await asyncio.sleep(10)

#     # Unsubscribe from GameFlowPhase
#     w2lcu.on.unsubscribe(on_game_flow_phase)
#     print("Unsubscribed from GameFlowPhase")

#     # Run for another 10 seconds
#     await asyncio.sleep(10)

#     # Close WebSocket
#     await w2lcu.close()
#     print("WebSocket closed")


# if __name__ == '__main__':
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(main())
#     loop.stop()
