# -*- coding: utf-8 -*-
# @Time    : 2024/11/6 22:48
# @Author  : GZA
# @File    : _lcu_http.py
import asyncio
import base64
import re
from typing import Optional

from . import _lcu_manager as lcu
from ..response_parser.http_response.http_response_parser import Response2Info, CurrentSummonerOutput


class Http2Lcu:
    def __init__(self, port=None, token=None):
        self.http: Optional[lcu.Http] = None
        self.loop = asyncio.get_event_loop()
        self.id2info: Optional[dict] = None
        self.champion_id_list: Optional[list] = None

        self.update_port_and_token(port, token)

    def update_port_and_token(self, port, token):
        """更新port和token"""
        if port is not None and token is not None:
            self.http = lcu.Http(port=port, token=token)
        else:
            try:
                port, token = lcu.get_port_and_token()
                self.http = lcu.Http(port=port, token=token)
            except Exception as e:
                print(f"自动获取端口失败:{e}")
                self.http = None

    # Get something
    # 基本信息
    async def get_game_client_directory(self):
        """获取游戏安装路径"""
        response_data = await self.http.request("GET", "/data-store/v1/install-dir")
        return response_data.data
    
    async def get_current_summoner(self) -> CurrentSummonerOutput:
        """获取召唤师基本信息"""
        response_data = await self.http.request("GET", "/lol-summoner/v1/current-summoner")
        current_summoner = Response2Info.current_summoner(response_data)
        return current_summoner

    async def get_match_history(self, puuid: str, beg_index: int = 0, end_index: int = 4):
        """获取对局历史"""
        params = {"begIndex": beg_index, "endIndex": end_index}
        response_data = await self.http.request("GET", f"/lol-match-history/v1/products/lol/{puuid}/matches", params=params)
        ...
        return response_data.data

    async def get_game_detail(self, game_id: int):
        """获取游戏详细信息"""
        response_data = await self.http.request("GET", f"/lol-match-history/v1/games/{game_id}")
        return response_data.data

    # 获取游戏资源文件的方法

    async def get_profile_icon(self, icon_id: int):
        """获取召唤师头像"""
        response_data = await self.http.request("GET", f"/lol-game-data/assets/v1/profile-icons/{icon_id}.jpg")
        return response_data.data

    async def get_champion_icon(self, champion_id: int):
        """获取英雄图标"""
        response_data = await self.http.request("GET", f"/lol-game-data/assets/v1/champion-icons/{champion_id}.png")
        return response_data.data

    async def get_item_icon(self, item_id: int):
        """获取物品图标"""
        if self.id2info is None:
            await self.get_all_id2info()

        # 装备栏为空时(item_id==0),获取装备栏占位图标
        if item_id == 0:
            response_data = await self.http.request("GET", r"/lol-game-data/assets/ASSETS/Items/Icons2D/gp_ui_placeholder.png")
            return response_data.data

        path = self.id2info["items"][item_id]["icon"]
        response_data = await self.http.request("GET", path)
        return response_data.data

    async def get_spell_icon(self, spell_id: int):
        """获取召唤师技能图标"""
        if self.id2info is None:
            await self.get_all_id2info()

        path = self.id2info["spells"][spell_id]["icon"]
        response_data = await self.http.request("GET", path)
        return response_data.data

    async def get_rune_icon(self, rune_id: int):
        """获取符文图标"""
        if self.id2info is None:
            await self.get_all_id2info()

        path = ''
        try:
            path = self.id2info["runes"][rune_id]['icon']
        except:
            for item in self.id2info["perks"]['styles']:
                if item['id'] == rune_id:
                    path = item['iconPath']

        response_data = await self.http.request("GET", path)
        return response_data.data

    async def get_augment_icon(self, augment_id: int):
        """获取强化符文图标"""
        if self.id2info is None:
            await self.get_all_id2info()

        path = self.id2info["augments"][augment_id]["icon"]
        response_data = await self.http.request("GET", path)
        return response_data.data

    async def get_champion_splash(self, skin_id: int, is_centered: bool = True):
        """获取英雄原画
        Args:
            skin_id: 皮肤ID
            is_centered: 是否居中,True为居中(如BP界面),False为未居中
        """
        if self.id2info is None:
            await self.get_all_id2info()

        skin_info = self.id2info["skins"][skin_id]
        path = skin_info["splashPath"] if is_centered else skin_info["uncenteredSplashPath"]

        response_data = await self.http.request("GET", path)
        return response_data.data

    async def get_champion_name_by_id(self, champion_id: int):
        if self.id2info is None:
            await self.get_all_id2info()
        return self.id2info["champions"][champion_id]['name']

    async def get_augment_name_by_id(self, augment_id: int):
        if self.id2info is None:
            await self.get_all_id2info()
        return self.id2info["augments"][augment_id]['name']

    # Do something
    async def accept_matchmaking(self):
        """接受匹配"""
        response_data = await self.http.request("POST", "/lol-matchmaking/v1/ready-check/accept")
        ...
        return response_data.data

    async def decline_matchmaking(self):
        """拒绝匹配"""
        response_data = await self.http.request("POST", "/lol-matchmaking/v1/ready-check/decline")
        ...
        return response_data.data

    async def select_champion(self, action_id: int, champion_id: int, completed: bool = None):
        """选择英雄
        Args:
            action_id: 操作ID
            champion_id: 英雄ID
            completed: 是否锁定英雄，None为不锁定，True为锁定
        """
        data = {"championId": champion_id, "type": "pick"}
        if completed is not None:
            data["completed"] = completed

        response_data = await self.http.request("PATCH", f"/lol-champ-select/v1/session/actions/{action_id}", data=data)
        return response_data.data

    """符文页操作"""
    async def get_current_rune_page(self):
        """获取当前符文页"""
        response_data = await self.http.request("GET", "/lol-perks/v1/currentpage")
        return response_data.data

    async def delete_current_rune_page(self):
        """删除当前符文页"""
        current_rune_page = await self.get_current_rune_page()

        # 无符文页
        if current_rune_page is None:
            return None

        # 当前符文页不可删除
        if not current_rune_page['isDeletable']:
            return None

        response_data = await self.http.request("DELETE", f"/lol-perks/v1/pages/{current_rune_page['id']}")
        res = response_data.data
        return res

    async def create_rune_page(self, name, primaryId, secondaryId, perks):
        """创建符文页"""
        # 构建符文页的数据
        body = {
            "name": name,
            "primaryStyleId": primaryId,
            "subStyleId": secondaryId,
            "selectedPerkIds": perks,
            "current": True
        }

        response_data = await self.http.request("POST", "/lol-perks/v1/pages", data=body)
        return response_data.data

    """装备页操作"""
    async def get_current_item_page(self, summoner_id=None):
        """获取装备页"""
        if summoner_id is None:
            current_summoner = await self.get_current_summoner()
            summoner_id = current_summoner.summoner_id
        response_data = await self.http.request("GET", f"/lol-item-sets/v1/item-sets/{summoner_id}/sets")
        return response_data.data

    # Todo: 以下需要测试

    async def accept_trade(self, trade_id: int):
        """同意交换英雄"""
        response_data = await self.http.request("POST", f"/lol-champ-select/v1/session/trades/{trade_id}/accept")
        return response_data.data

    async def bench_swap(self, champion_id: int):
        """备战席交换英雄"""
        response_data = await self.http.request("POST", f"/lol-champ-select/v1/session/bench/swap/{champion_id}")
        return response_data.data

    async def get_current_champion(self):
        """获取当前选择的英雄"""
        response_data = await self.http.request("GET", "/lol-champ-select/v1/current-champion")
        return response_data.data

    async def reroll(self):
        """摇骰子(重新随机英雄)"""
        response_data = await self.http.request("POST", "/lol-champ-select/v1/session/my-selection/reroll")
        return response_data.data

    async def ban_champion(self, action_id: int, champion_id: int, completed: bool = None):
        """禁用英雄
        Args:
            action_id: 操作ID
            champion_id: 英雄ID
            completed: 是否锁定禁用，None为不锁定，True为锁定
        """
        data = {"championId": champion_id, "type": "ban"}
        if completed is not None:
            data["completed"] = completed

        response_data = await self.http.request("PATCH", f"/lol-champ-select/v1/session/actions/{action_id}", data=data)
        return response_data.data

    async def get_skin_carousel(self):
        """获取可用的皮肤列表"""
        response_data = await self.http.request("GET", "/lol-champ-select/v1/skin-carousel-skins")
        return response_data.data

    async def select_config(self, skin_id: int, spell1_id: int = None, spell2_id: int = None, ward_skin_id: int = None):
        """选择皮肤和召唤师技能
        Args:
            skin_id: 皮肤ID
            spell1_id: 第一个召唤师技能ID (例如: 4-点燃)
            spell2_id: 第二个召唤师技能ID (例如: 12-闪现)
            ward_skin_id: 守卫皮肤ID (默认-1)
        """
        data = {"selectedSkinId": skin_id}

        if spell1_id is not None:
            data["spell1Id"] = spell1_id
        if spell2_id is not None:
            data["spell2Id"] = spell2_id
        if ward_skin_id is not None:
            data["wardSkinId"] = ward_skin_id

        response_data = await self.http.request("PATCH", "/lol-champ-select/v1/session/my-selection", data=data)
        return response_data.data

    ...

    async def get_all_id2info(self):
        """获取游戏基础数据(items/spells/runes等)"""
        # 获取各类数据
        items_json = await self.http.request("GET", "/lol-game-data/assets/v1/items.json")
        spells_json = await self.http.request("GET", "/lol-game-data/assets/v1/summoner-spells.json")
        runes_json = await self.http.request("GET", "/lol-game-data/assets/v1/perks.json")
        perks_json = await self.http.request("GET", "/lol-game-data/assets/v1/perkstyles.json")
        queues_json = await self.http.request("GET", "/lol-game-queues/v1/queues")
        champions_json = await self.http.request("GET", "/lol-game-data/assets/v1/champion-summary.json")
        skins_json = await self.http.request("GET", "/lol-game-data/assets/v1/skins.json")
        augments_json = await self.http.request("GET", "/lol-game-data/assets/v1/cherry-augments.json")
        maps_json = await self.http.request("GET", "/lol-game-data/assets/v1/maps.json")

        # 获取对应关系
        items_id2info = {
            item["id"]: {
                "icon": item["iconPath"],
                'name': item['name'],
                'desc': item['description']
            } for item in items_json.data
        }

        spells_id2info = {
            item["id"]: {
                "icon": item["iconPath"],
                'name': item['name'],
                'desc': item['description']
            } for item in spells_json.data[:-3]  # 去掉最后3个测试用的召唤师技能
        }

        runes_id2info = {
            item["id"]: {
                "icon": item["iconPath"],
                'name': item['name'],
                'desc': item['longDesc']
            } for item in runes_json.data
        }

        # 队列信息
        queues_id2info = {
            item["id"]: {
                "mapId": item["mapId"],
                "name": item["name"]
            } for item in queues_json.data
        }

        # 英雄基本信息
        self.champion_id_list = [item["id"] for item in champions_json.data][1:]
        champions_id2info = {
            item["id"]: {
                "name": item["name"],
                "alias": item["alias"],
                "squarePortraitPath": item["squarePortraitPath"]
            } for item in champions_json.data
        }

        # 皮肤信息(包含名人堂皮肤的augments信息)
        skins_info = {}
        skin_augments = {}
        for item in skins_json.data.values():
            champion_id = item["id"] // 1000

            if 'questSkinInfo' in item:
                for tier in item['questSkinInfo']['tiers']:
                    skins_info[tier["id"]] = {
                        "name": tier["name"],
                        "championId": champion_id,
                        'splashPath': tier['splashPath'],
                        'uncenteredSplashPath': tier['uncenteredSplashPath']
                    }

                    if 'skinAugments' in tier and 'augments' in tier['skinAugments']:
                        content_id = tier['skinAugments']['augments'][0]['contentId']
                        skin_augments[tier['id']] = content_id
            else:
                skins_info[item["id"]] = {
                    "name": item["name"],
                    "championId": champion_id,
                    'splashPath': item['splashPath'],
                    'uncenteredSplashPath': item['uncenteredSplashPath']
                }

                if 'skinAugments' in item and 'augments' in item['skinAugments']:
                    content_id = item['skinAugments']['augments'][0]['contentId']
                    skin_augments[item['id']] = content_id

        # 强化符文信息
        augments_id2info = {
            item['id']: {
                'name': item['nameTRA'],
                'rarity': item['rarity'],  # 新增: 稀有度
                'icon': item['augmentSmallIconPath']
            } for item in augments_json.data
        }

        # 地图信息
        maps_id2info = {
            item["id"]: {
                "name": item["name"],
                "description": item["description"],
                "mapStringId": item["mapStringId"]
            } for item in maps_json.data
        }

        id2info = {
            "items": items_id2info,
            "spells": spells_id2info,
            "runes": runes_id2info,
            "queues": queues_id2info,
            "champions": champions_id2info,
            "skins": skins_info,
            "skin_augments": skin_augments,
            "augments": augments_id2info,
            "perks": perks_json.data,  # 符文样式保持原始数据结构
            "maps": maps_id2info  # 新增地图信息
        }
        self.id2info = id2info

        return id2info

# if __name__ == '__main__':
#     lcu_port, lcu_token = lcu.get_port_and_token()
#     print(f"{lcu_port=}, {lcu_token=}")
#     lcu_http = Http2Lcu(lcu_port, lcu_token)
#     current_summoner = lcu_http.get_current_summoner()
#     print(f"{current_summoner=}")
