# -*- coding: utf-8 -*-
# @Time    : 2024/12/4 1:15
# @Author  : GZA
# @File    : notebook_config.py

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json
import os
from pathlib import Path
import appdirs

class NoteRecord(BaseModel):
    """笔记记录数据模型"""
    summoner_id: str
    game_name: str
    champion_id: Optional[int] = None
    timestamp: float = datetime.now().timestamp()
    reason: Optional[str] = None
    details: Optional[str] = None
    game_id: Optional[str] = None
    region: Optional[str] = None
    puuid: Optional[str] = None

class NoteBookModel(BaseModel):
    """笔记本主数据模型"""
    blacklist: List[NoteRecord] = []
    whitelist: List[NoteRecord] = []

class NoteBookConfig:
    def __init__(self, config_filename='notebook_config.json'):
        """初始化笔记本配置管理器
        
        Args:
            config_filename: 配置文件名称
        """
        # 获取系统标准配置目录
        app_name = "Mousy"
        app_author = "Mousy"
        
        # 获取系统配置目录
        config_dir = Path(appdirs.user_config_dir(app_name, app_author))
        
        # 确保配置目录存在
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # 设置配置文件完整路径
        self.config_file = config_dir / config_filename
        self.settings = {}
        self.load_settings()

    def load_settings(self):
        """从 JSON 配置文件加载设置"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.settings = json.load(f)
        else:
            # 使用默认值创建新的设置
            default_settings = NoteBookModel()
            self.settings = default_settings.model_dump()
            self.save_settings()

    def save_settings(self):
        """将当前设置保存到 JSON 配置文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=4)

    def update_settings(self, new_settings: NoteBookModel):
        """批量更新设置"""
        self.settings = new_settings.model_dump()
        self.save_settings()

    def get_pydantic_settings(self):
        """获取 Pydantic 模型格式的设置"""
        return NoteBookModel(**self.settings)

    def add_to_blacklist(self, record: NoteRecord):
        """添加记录到黑名单"""
        self.settings['blacklist'].append(record.model_dump())
        self.save_settings()

    def add_to_whitelist(self, record: NoteRecord):
        """添加记录到白名单"""
        self.settings['whitelist'].append(record.model_dump())
        self.save_settings()

    def remove_from_blacklist(self, summoner_id: str):
        """从黑名单移除记录"""
        self.settings['blacklist'] = [
            record for record in self.settings['blacklist'] 
            if record['summoner_id'] != summoner_id
        ]
        self.save_settings()

    def remove_from_whitelist(self, summoner_id: str):
        """从白名单移除记录"""
        self.settings['whitelist'] = [
            record for record in self.settings['whitelist'] 
            if record['summoner_id'] != summoner_id
        ]
        self.save_settings() 