from pathlib import Path
import json
import time
from typing import List, Optional

from server_app.services.lcu import Http2Lcu
class ItemSetManager:
    def __init__(self, h2lcu: Http2Lcu):
        """初始化ItemSetManager

        Args:
            h2lcu: Http2Lcu实例
        """
        self.h2lcu = h2lcu
    
    async def update_h2lcu(self):
        """更新Http2Lcu实例"""
        if self.h2lcu.http.port is None or self.h2lcu.http.token is None:
            print("port或token未知")
            return
        await self.get_all_path_by_h2lcu()
    
    async def get_all_path_by_h2lcu(self):
        """根据Http2Lcu实例获取所有路径"""
        game_client_directory = await self.h2lcu.get_game_client_directory()
        self.game_client_path = Path(game_client_directory)
        self.config_path = self.game_client_path.parent / "Game" / "Config"
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

    def delete_mousy_items(self, champion_name: str) -> None:
        """删除指定英雄文件夹中以Mousy开头的推荐出装文件
        
        Args:
            champion_name: 英雄名称
        """
        champion_path = self.champions_path / champion_name / "Recommended"
        if champion_path.exists():
            for file in champion_path.glob("Mousy*.json"):
                file.unlink()  # 删除文件