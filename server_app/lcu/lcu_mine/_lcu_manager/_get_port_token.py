# -*- coding: utf-8 -*-
# @Time    : 2024/11/6 23:43
# @Author  : GZA
# @File    : _get_port_token.py
import re

import psutil


def get_port_and_token():
    """
    使用 psutil 获取 LeagueClientUx 进程的端口和 token
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
    print("无法找到 LeagueClientUx 进程或解析端口和 token 失败")
    return None, None


# if __name__ == '__main__':
#     port, token = get_port_and_token()
#     print(port, token)
