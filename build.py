# -*- coding: utf-8 -*-
# @Time    : 2024/10/31 23:28
# @Author  : GZA
# @File    : build.py
# 一个打包脚本

import subprocess
import os
import shutil


def build():
    # 清理上一次的打包文件
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")

    # 打包命令配置
    command = [
        "pyinstaller",
        # "--onefile",  # 打包成单个可执行文件
        "--windowed",  # 在打包 GUI 应用程序时不显示控制台窗口
        "--name", "server",  # 可执行文件的名称
        "--distpath", "resources",  # 直接指定输出目录为 resources
        "server_app/main.py"  # 入口文件
    ]

    # 执行打包命令
    subprocess.run(command)


if __name__ == "__main__":
    build()
