# -*- coding: utf-8 -*-
# @Time    : 2024/11/9 2:24
# @Author  : GZA
# @File    : user_config.py
import json
import os
from pydantic import BaseModel, Field
from typing import List, Dict
import sys
import appdirs
from pathlib import Path

# 定义基础数据模型
class ChampionSettings(BaseModel):
    enabled: bool = False
    delay: float = 0.0
    champions: List[int] = []

class PositionChampions(BaseModel):
    top: List[int] = []
    jungle: List[int] = []
    middle: List[int] = []
    bottom: List[int] = []
    support: List[int] = []

    def get_champions_by_pos(self, pos_name):
        if pos_name == "top":
            return self.top
        elif pos_name == "jungle":
            return self.jungle
        elif pos_name == "middle":
            return self.middle
        elif pos_name == "bottom":
            return self.bottom
        elif pos_name in ("support", "utility"):
            return self.support
        else:
            return []


class RankedPickBanSettings(BaseModel):
    enabled: bool = False
    delay: float = 0.0
    champions: PositionChampions = PositionChampions()

class RankedSettings(BaseModel):
    pick: RankedPickBanSettings = RankedPickBanSettings()
    ban: RankedPickBanSettings = RankedPickBanSettings()

class NormalSettings(BaseModel):
    pick: ChampionSettings = ChampionSettings()
    ban: ChampionSettings = ChampionSettings()

class AramSettings(BaseModel):
    pick: ChampionSettings = ChampionSettings()

# 添加布局设置模型
class LayoutSettings(BaseModel):
    card_order: List[str] = ["ranked", "normal"]

# 主设置模型
class SettingsModel(BaseModel):
    # 基础设置
    auto_accept: bool = False
    auto_accept_swap_position: bool = False
    auto_accept_swap_champion: bool = False
    show_game_summary: bool = True

    # 布局设置
    layout: LayoutSettings = LayoutSettings()

    # 游戏模式设置
    ranked: RankedSettings = RankedSettings()
    normal: NormalSettings = NormalSettings()
    aram: AramSettings = AramSettings()

class UserConfig:
    def __init__(self, config_filename='user_config.json'):
        """初始化用户配置管理器
        
        Args:
            config_filename: 配置文件名称
        """
        # 获取系统标准配置目录
        app_name = "Mousy"  # 使用你的应用名称
        app_author = "Mousy"  # 使用你的开发者/组织名称
        
        # 获取系统配置目录
        config_dir = Path(appdirs.user_config_dir(app_name, app_author))
        
        # 确保配置目录存在
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # 设置配置文件完整路径
        self.config_file = config_dir / config_filename
        self.settings = {}
        self.load_settings()

    def load_settings(self):
        """从 JSON 配置文件加载设置。"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.settings = json.load(f)
        else:
            # 使用 SettingsModel 的默认值创建新的设置
            default_settings = SettingsModel()
            self.settings = default_settings.model_dump()
            self.save_settings()

    def save_settings(self):
        """将当前设置保存到 JSON 配置文件。"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=4)

    def get_setting(self, key):
        """获取指定键的设置值。"""
        return self.settings.get(key)

    def set_setting(self, key, value):
        """设置指定键的值并保存到配置文件。"""
        self.settings[key] = value
        self.save_settings()

    def update_settings(self, new_settings):
        """批量更新设置。"""
        self.settings = new_settings.model_dump()
        self.save_settings()

    def reset_settings(self):
        """重置设置为默认值。"""
        default_settings = SettingsModel()
        self.settings = default_settings.model_dump()
        self.save_settings()
    
    def get_pydantic_settings(self):
        """获取 Pydantic 模型格式的设置。"""
        return SettingsModel(**self.settings)
