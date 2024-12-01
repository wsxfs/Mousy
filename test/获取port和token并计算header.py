# -*- coding: utf-8 -*-
# @Time    : 2024/11/4 7:07
# @Author  : GZA
# @File    : 查找客户端.py
import base64
import psutil


def get_lcu_info():
    for process in psutil.process_iter(['name', 'cmdline']):
        if process.info['name'] == 'LeagueClientUx.exe':
            cmdline = process.info['cmdline']
            # 提取端口和认证令牌
            port = None
            token = None
            install_path = None
            for arg in cmdline:
                if '--app-port=' in arg:
                    port = arg.split('=')[1]
                elif '--remoting-auth-token=' in arg:
                    token = arg.split('=')[1]
                elif '--install-directory=' in arg:
                    install_path = arg.split('=')[1]

            # 检查是否找到了所需信息
            if port and token and install_path:
                return {
                    'port': port,
                    'token': token,
                    'install_path': install_path
                }

    print("未找到运行中的 LeagueClientUx.exe 进程，请确认客户端已启动。")
    return None


def get_headers(token):
    auth = base64.b64encode(f"riot:{token}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth}",
        "Accept": "application/json"
    }
    return headers


if __name__ == '__main__':
    lcu_info = get_lcu_info()
    port = lcu_info['port']
    token = lcu_info['token']
    headers = get_headers(token)
    print(f"{port=}{token=} {headers=}")
