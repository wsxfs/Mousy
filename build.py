# -*- coding: utf-8 -*-
# @Time    : 2024/10/31 23:28
# @Author  : GZA
# @File    : build.py
# 一个打包脚本

import subprocess
import os
import shutil


def build():
    output_dir = "resources/server"
    
    # 如果输出目录存在，先删除它
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    
    # 确保 resources 目录存在
    os.makedirs("resources", exist_ok=True)
    
    # 打包命令配置
    command = [
        "pyinstaller",
        # "--onefile",  # 打包成单个可执行文件
        "--windowed",  # 在打包 GUI 应用程序时不显示控制台窗口
        "--name", "server",  # 可执行文件的名称
        "--distpath", "resources",  # 直接指定输出目录为 resources
        "--noconfirm",  # 禁用确认提示
        # "--hidden-import", "appdirs",  # 添加这行
        "server_app/main.py"  # 入口文件
    ]

    # 执行打包命令
    subprocess.run(command)


if __name__ == "__main__":
    build()
