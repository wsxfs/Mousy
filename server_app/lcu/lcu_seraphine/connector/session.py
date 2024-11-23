# -*- coding: utf-8 -*-
# @Time    : 2024/11/7 19:35
# @Author  : GZA
# @File    : session.py.py

"""
session.py - 会话管理模块。
负责与英雄联盟客户端的 HTTPS 会话初始化和维护。
"""

import aiohttp
import psutil
import re


class SessionManager:
    def __init__(self):
        """初始化会话管理器"""
        self.port = None
        self.token = None
        self.base_url = None
        self.session = None

    def initialize(self):
        """
        获取客户端的端口和认证令牌，初始化会话。
        """
        self.port, self.token = self.get_port_and_token()
        self.base_url = f"https://127.0.0.1:{self.port}"
        self.session = aiohttp.ClientSession(
            base_url=self.base_url,
            auth=aiohttp.BasicAuth("riot", self.token),
            connector=aiohttp.TCPConnector(ssl=False)
        )

    async def close(self):
        """关闭 HTTPS 会话"""
        if self.session:
            await self.session.close()

    def get_port_and_token(self):
        """
        使用 psutil 获取 LeagueClientUx 进程的端口和 token。
        """
        for process in psutil.process_iter(['name', 'cmdline']):
            if process.info['name'] == "LeagueClientUx.exe":
                # 从命令行参数中解析端口和 token
                cmdline = " ".join(process.info['cmdline'])
                port_match = re.search(r"--app-port=([0-9]*)", cmdline)
                token_match = re.search(r"--remoting-auth-token=([\w-]*)", cmdline)

                if port_match and token_match:
                    port = port_match.group(1)
                    token = token_match.group(1)
                    return port, token
        raise Exception("无法找到 LeagueClientUx 进程或解析端口和 token 失败")
