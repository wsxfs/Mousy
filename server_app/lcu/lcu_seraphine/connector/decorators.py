# -*- coding: utf-8 -*-
# @Time    : 2024/11/7 19:35
# @Author  : GZA
# @File    : decorators.py.py


"""
decorators.py - 通用装饰器模块。
提供重试机制、LCU状态检查等功能。
"""

import asyncio
import inspect
from functools import wraps
from asyncio import CancelledError

def retry(retries=3, delay=1, exceptions=(Exception,)):
    """
    为指定函数添加重试机制。

    Args:
        retries (int): 最大重试次数。
        delay (int): 每次重试之间的延迟时间（秒）。
        exceptions (tuple): 需要捕获并重试的异常类型。

    Returns:
        function: 装饰后的函数。
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(retries):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt < retries - 1:
                        await asyncio.sleep(delay)
                    else:
                        raise e
        return wrapper
    return decorator

def need_lcu():
    """
    检查 LCU 会话是否已初始化。
    如果未初始化，抛出 ReferenceError。

    Returns:
        function: 装饰后的函数。
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            instance = args[0]
            if not hasattr(instance, "session") or instance.session is None:
                raise ReferenceError("LCU session is not initialized.")
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def log_call(tag="DEBUG"):
    """
    打印函数调用日志，用于调试和跟踪。

    Args:
        tag (str): 日志标记。

    Returns:
        function: 装饰后的函数。
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            func_name = func.__name__
            param_info = inspect.signature(func).bind(*args, **kwargs).arguments
            print(f"[{tag}] Calling {func_name} with {param_info}")
            result = await func(*args, **kwargs)
            print(f"[{tag}] {func_name} returned {result}")
            return result
        return wrapper
    return decorator
