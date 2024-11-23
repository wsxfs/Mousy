from pathlib import Path
import json
import time
from typing import List, Optional

class ItemSetManager:
    def __init__(self, game_client_path: Path):
        """初始化ItemSetManager
        
        Args:
            game_client_path: 游戏客户端路径
        """
        self.game_client_path = game_client_path
        self.config_path = game_client_path.parent / "Game" / "Config"
        self.champions_path = self.config_path / "Champions"
        self.global_recommended_path = self.config_path / "Global" / "Recommended"

    def save_item2global(self, item_set_data: dict, filename: str) -> Path:
        """保存出装方案到全局推荐位置
        
        Args:
            item_set_data: 出装方案数据
            filename: 文件名
            
        Returns:
            Path: 保存文件的路径
        """
        if not self.global_recommended_path.exists():
            self.global_recommended_path.mkdir(parents=True, exist_ok=True)
            
        output_file = self.global_recommended_path / filename
        return self.save_item2file(item_set_data, output_file)

    def save_item2champions(self, item_set_data: dict, champion_name: str, filename: str) -> Path:
        """保存出装方案到指定英雄的推荐位置
        
        Args:
            item_set_data: 出装方案数据
            champion_name: 英雄名称
            filename: 文件名
            
        Returns:
            Path: 保存文件的路径
        """
        champion_path = self.champions_path / champion_name / "Recommended"
        if not champion_path.exists():
            champion_path.mkdir(parents=True, exist_ok=True)
            
        output_file = champion_path / f"{filename}.json"
        return self.save_item2file(item_set_data, output_file)

    def save_item2file(self, item_set_data: dict, output_file: Path) -> Path:
        """保存出装方案到文件
        
        Args:
            item_set_data: 出装方案数据
            output_file:
            
        Returns:
            Path: 保存文件的路径
        """
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(item_set_data, f, ensure_ascii=False, indent=2)
            
        return output_file