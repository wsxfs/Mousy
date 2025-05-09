# -*- coding: utf-8 -*-
# @Time    : 2024/12/3 22:10
# @Author  : GZA
# @File    : get_port_and_token.py
import re
import psutil
import subprocess

# 旧的获取方法
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


# 更新后的获取方法, 通过tasklist工具获取pid, 再通过psutil根据pid查询,速度快
def get_port_and_token_by_tasklist():
    tasklist = get_tasklist()
    pids = get_game_pids(tasklist)

    if not pids:
        return None, None
    
    port, token, _ = get_port_token_server_by_pid(pids[0])
    return port, token
        

def get_tasklist():
    for path in ['tasklist', 'C:/Windows/System32/tasklist.exe']:
        try:
            cmd = f'{path} /FI "imagename eq LeagueClientUx.exe" /NH'
            _ = subprocess.check_output(cmd, shell=True)
            return path
        except:
            pass

    return None

def get_game_pids(tasklist):
    try:
        processes = subprocess.check_output(
            f'{tasklist} /FI "imagename eq LeagueClientUx.exe" /NH',
            shell=True,
            stderr=subprocess.STDOUT
        )
    except subprocess.CalledProcessError as e:
        print(
            'an error occurred when calling tasklist command, '
            f'original output: {e.output.decode()}'
        )
        raise e

    pids = []

    if not b'LeagueClientUx.exe' in processes:
        return pids

    arr = processes.split()

    for i, s in enumerate(arr):
        if s == b'LeagueClientUx.exe':
            pids.append(int(arr[i + 1]))

    return pids

def get_port_token_server_by_pid(pid):
    port, token, server = None, None, None

    process = psutil.Process(pid)
    cmdline = process.cmdline()

    for cmd in cmdline:

        p = cmd.find("--app-port=")
        if p != -1:
            port = cmd[11:]

        p = cmd.find("--remoting-auth-token=")
        if p != -1:
            token = cmd[22:]

        p = cmd.find("--rso_platform_id=")
        if p != -1:
            server = cmd[18:]

        if port and token and server:
            break

    return port, token, server

if __name__ == '__main__':
    # port, token = get_port_and_token()
    port, token = get_port_and_token_by_tasklist()
    print(port, token)
