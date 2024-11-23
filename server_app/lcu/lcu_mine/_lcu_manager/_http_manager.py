# -*- coding: utf-8 -*-
# @Time    : 2024/11/5 20:07
# @Author  : GZA
# @File    : http_requests.py

import base64
import httpx
import asyncio
from typing import Optional, Dict, Any

from ._get_port_token import get_port_and_token
from ...response_parser.http_response.http_response_parser import ResponseParser


class Http:
    def __init__(self, port=None, token=None):
        self.port = None
        self.token = None
        self.base_url = None
        self.headers = None
        self.client: httpx.AsyncClient = None
        self._initialize_connection(port, token)

    def _initialize_connection(self, port=None, token=None):
        """
        初始化连接，设置端口、token 和请求头
        """

        if port is None or token is None:
            # 获取端口和 token
            self.port, self.token = get_port_and_token()
        else:
            self.port, self.token = port, token

        # 设置 base_url 和 headers
        self.base_url = f"https://127.0.0.1:{self.port}"
        auth = base64.b64encode(f"riot:{self.token}".encode()).decode()
        self.headers = {
            "Authorization": f"Basic {auth}",
            "Accept": "application/json"
        }

        # 初始化 httpx 异步客户端
        self.client = httpx.AsyncClient(headers=self.headers, verify=False)

    async def request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None,
                      data: Optional[Dict[str, Any]] = None) -> ResponseParser:
        """
        异步通用请求方法，用于调用 LCU API

        :param method: HTTP 请求方法（GET、POST、PUT、DELETE）
        :param endpoint: API 端点（例如 /lol-summoner/v1/current-summoner）
        :param params: URL 参数
        :param data: 请求体数据
        :return: 返回 API 响应的 JSON 数据
        """
        url = f"{self.base_url}{endpoint}"

        # 选择请求方法并执行异步请求
        try:
            response = await self.client.request(
                method=method,
                url=url,
                params=params,
                json=data
            )

            response = ResponseParser(response)
            return response
        except httpx.RequestError as e:
            print(f"请求出现错误：{e}")

    async def close(self):
        """关闭异步客户端连接"""
        await self.client.aclose()

# async def get_current_summoner(lcu_connection):
#     current_summoner = await lcu_connection.request("GET", "/lol-summoner/v1/current-summoner")
#     return current_summoner
#
#
# async def main():
#     lcu_connection = Http()
#     current_summoner = await get_current_summoner(lcu_connection)
#     print("当前召唤师信息：", current_summoner)
#     await lcu_connection.close()


# if __name__ == '__main__':
#     asyncio.run(main())
