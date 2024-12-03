# -*- coding: utf-8 -*-
# @Time    : 2024/11/13 0:22
# @Author  : GZA
# @File    : game_resource_getter.py
import base64
import os
import aiofiles
import asyncio

from server_app.new_services.lcu import Http2Lcu


class GameResourceGetter:
    def __init__(self, http2lcu: Http2Lcu, resource_base_path="../../resource/game"):
        """初始化游戏资源管理器
        
        Args:
            http2lcu: LCU HTTP客户端实例
            resource_base_path: 资源文件基础路径
        """
        self.http2lcu = http2lcu
        self.base_path = resource_base_path

        # 创建资源文件夹
        self.folders = {
            "profile_icons": f"{resource_base_path}/profile_icons",
            "champion_icons": f"{resource_base_path}/champion_icons",
            "item_icons": f"{resource_base_path}/item_icons",
            "spell_icons": f"{resource_base_path}/spell_icons",
            "rune_icons": f"{resource_base_path}/rune_icons",
            "augment_icons": f"{resource_base_path}/augment_icons",
            "champion_splashes": f"{resource_base_path}/champion_splashes"
        }

        # 创建所需文件夹
        for folder in self.folders.values():
            os.makedirs(folder, exist_ok=True)

    async def get_profile_icon(self, icon_id: int) -> bytes:
        """获取召唤师头像"""
        file_path = f"{self.folders['profile_icons']}/{icon_id}.jpg"
        
        if os.path.exists(file_path):
            # 读取本地文件
            profile_icon = await self._read_image(file_path)
            return profile_icon

        # 下载并保存文件
        profile_icon = await self.http2lcu.get_profile_icon(icon_id)
        await self._save_image(profile_icon, file_path)
        return profile_icon

    async def get_champion_icon(self, champion_id: int) -> str:
        """获取英雄图标"""
        file_path = f"{self.folders['champion_icons']}/{champion_id}.png"

        if os.path.exists(file_path):
            champion_icon = await self._read_image(file_path)
        else:
            champion_icon = await self.http2lcu.get_champion_icon(champion_id)
            await self._save_image(champion_icon, file_path)
        result = base64.b64encode(champion_icon).decode()
        return result

    async def get_item_icon(self, item_id: int) -> str:
        """获取物品图标"""
        file_path = f"{self.folders['item_icons']}/{item_id}.png"

        if os.path.exists(file_path):
            item_icon = await self._read_image(file_path)
        else:
            item_icon = await self.http2lcu.get_item_icon(item_id)
            await self._save_image(item_icon, file_path)
        result = base64.b64encode(item_icon).decode()
        return result

    async def get_spell_icon(self, spell_id: int) -> str:
        """获取召唤师技能图标"""
        file_path = f"{self.folders['spell_icons']}/{spell_id}.png"

        if os.path.exists(file_path):
            spell_icon = await self._read_image(file_path)
        else:
            spell_icon = await self.http2lcu.get_spell_icon(spell_id)
            await self._save_image(spell_icon, file_path)
        result = base64.b64encode(spell_icon).decode()
        return result

    async def get_rune_icon(self, rune_id: int) -> str:
        """获取符文图标"""
        file_path = f"{self.folders['rune_icons']}/{rune_id}.png"

        if os.path.exists(file_path):
            rune_icon = await self._read_image(file_path)
        else:
            rune_icon = await self.http2lcu.get_rune_icon(rune_id)
            await self._save_image(rune_icon, file_path)
        result = base64.b64encode(rune_icon).decode()
        return result

    async def get_augment_icon(self, augment_id: int) -> str:
        """获取强化符文图标"""
        file_path = f"{self.folders['augment_icons']}/{augment_id}.png"

        if os.path.exists(file_path):
            augment_icon = await self._read_image(file_path)
        else:
            augment_icon = await self.http2lcu.get_augment_icon(augment_id)
            await self._save_image(augment_icon, file_path)
        result = base64.b64encode(augment_icon).decode()
        return result

    async def get_champion_splash(self, skin_id: int, is_centered: bool = True) -> str:
        """获取英雄原画"""
        file_suffix = "centered" if is_centered else "uncentered"
        file_path = f"{self.folders['champion_splashes']}/{skin_id}_{file_suffix}.jpg"

        if os.path.exists(file_path):
            champion_splash = await self._read_image(file_path)
        else:
            champion_splash = await self.http2lcu.get_champion_splash(skin_id, is_centered)
            await self._save_image(champion_splash, file_path)
        result = base64.b64encode(champion_splash).decode()
        return result

    @staticmethod
    async def _save_image(image_data: bytes, file_path: str):
        """保存图片文件"""
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(image_data)
    
    @staticmethod
    async def _read_image(file_path: str) -> bytes:
        """读取图片文件"""
        async with aiofiles.open(file_path, 'rb') as f:
            return await f.read()


if __name__ == '__main__':
    http2lcu = Http2Lcu()
    game_resource_getter = GameResourceGetter(http2lcu)
    asyncio.gather(game_resource_getter.get_profile_icon(1),
                   game_resource_getter.get_champion_icon(1),
                   game_resource_getter.get_item_icon(1001),
                   game_resource_getter.get_spell_icon(1),
                   game_resource_getter.get_rune_icon(8369),
                   game_resource_getter.get_augment_icon(1),
                   game_resource_getter.get_champion_splash(1000))
