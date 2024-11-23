# -*- coding: utf-8 -*-
# @Time    : 2024/11/7 13:00
# @Author  : GZA
# @File    : __init__.py.py
import time
from ._lcu_manager import get_port_and_token
from ._port_token import lcu_port, lcu_token
from ._lcu_http import Http2Lcu
from ._lcu_websocket import Websocket2Lcu

# __all__ = ['lcu_port', 'lcu_token', 'h2lcu', 'w2lcu']
# __all__ = ['lcu_port']
h2lcu = Http2Lcu(lcu_port, lcu_token)
w2lcu = Websocket2Lcu(lcu_port, lcu_token)


# if __name__ == '__main__':
#     current_summoner = h2lcu.get_current_summoner()
#     print(current_summoner)
#
#     @w2lcu.on["GameFlowPhase"]
#     def on_json_api_event(even):
#         print("data: ", even['data'])
#
#
#     w2lcu.start()
#
#     time.sleep(50)
