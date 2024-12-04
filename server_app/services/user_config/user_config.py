# -*- coding: utf-8 -*-
# @Time    : 2024/11/9 2:24
# @Author  : GZA
# @File    : user_config.py
import json
import os


class UserConfig:
    def __init__(self, config_file='user_config.json'):
        self.config_file = config_file
        self.settings = {}
        self.load_settings()

    def load_settings(self):
        """从 JSON 配置文件加载设置。"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.settings = json.load(f)
        else:
            # 如果配置文件不存在，使用默认设置并创建配置文件
            self.settings = {
                "auto_accept": False,
                "auto_pick_champions": None,
                "auto_ban_champions": None,
                "auto_accept_swap_position": False,
                "auto_accept_swap_champion": False,
                "aram_auto_pick_champions": None,
            }
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
        self.settings.update(new_settings)
        self.save_settings()

    def reset_settings(self):
        """重置设置为默认值。"""
        self.settings = {
            'auto_accept': False,
            'auto_pick_champions': None,
            'auto_ban_champions': None,
            'auto_accept_swap_position': False,
            'auto_accept_swap_champion': False,
            'aram_auto_pick_champions': None,
        }
        self.save_settings()
