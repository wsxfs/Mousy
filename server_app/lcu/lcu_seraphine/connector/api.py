# -*- coding: utf-8 -*-
# @Time    : 2024/11/7 19:35
# @Author  : GZA
# @File    : api.py.py


"""
api.py - API 调用模块。
封装对英雄联盟客户端和服务器 API 的 HTTPS 调用。
"""

import aiohttp
from .decorators import retry, need_lcu


class ApiClient:
    def __init__(self, session_manager):
        """
        初始化 API 客户端。

        Args:
            session_manager (SessionManager): 会话管理器，用于提供 HTTPS 会话。
        """
        self.session_manager = session_manager
        self.session = session_manager.session

    @retry()
    @need_lcu()
    async def get(self, path: str, params=None):
        """
        发送 GET 请求。

        Args:
            path (str): API 路径。
            params (dict, optional): 请求参数。

        Returns:
            dict: 响应数据。
        """
        async with self.session.get(path, params=params) as response:
            return await self._process_response(response)

    @retry()
    @need_lcu()
    async def post(self, path: str, data=None):
        """
        发送 POST 请求。

        Args:
            path (str): API 路径。
            data (dict, optional): 请求体。

        Returns:
            dict: 响应数据。
        """
        async with self.session.post(path, json=data) as response:
            return await self._process_response(response)

    @retry()
    @need_lcu()
    async def put(self, path: str, data=None):
        """
        发送 PUT 请求。

        Args:
            path (str): API 路径。
            data (dict, optional): 请求体。

        Returns:
            dict: 响应数据。
        """
        async with self.session.put(path, json=data) as response:
            return await self._process_response(response)

    @retry()
    @need_lcu()
    async def delete(self, path: str):
        """
        发送 DELETE 请求。

        Args:
            path (str): API 路径。

        Returns:
            dict: 响应数据。
        """
        async with self.session.delete(path) as response:
            return await self._process_response(response)

    @retry()
    @need_lcu()
    async def patch(self, path: str, data=None):
        """
        发送 PATCH 请求。

        Args:
            path (str): API 路径。
            data (dict, optional): 请求体。

        Returns:
            dict: 响应数据。
        """
        async with self.session.patch(path, json=data) as response:
            return await self._process_response(response)

    async def _process_response(self, response):
        """
        处理 HTTP 响应，解析 JSON 数据并检查状态码。

        Args:
            response (aiohttp.ClientResponse): HTTP 响应对象。

        Returns:
            dict: 解析后的 JSON 数据。

        Raises:
            Exception: 当响应状态码非 2xx 时抛出异常。
        """
        if response.status >= 400:
            error_text = await response.text()
            raise Exception(f"API Error {response.status}: {error_text}")

        return await response.json()
