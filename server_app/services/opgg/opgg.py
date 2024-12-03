# -*- coding: utf-8 -*-
# @Time    : 2024/11/15 3:20
# @Author  : GZA
# @File    : opgg.py


import aiohttp
from async_lru import alru_cache


from server_app.services.lcu import Http2Lcu
from server_app.services.game_resource_getter import GameResourceGetter

TAG = "opgg"


class Opgg:
    """
    Opgg类用于与OPGG API进行交互，获取英雄联盟游戏数据。
    """

    def __init__(self, lcu_port, lcu_token):
        """
        初始化Opgg对象，设置会话为None。
        """
        self.session = None
        self.h2lcu = Http2Lcu(lcu_port, lcu_token)
        self.game_resource_getter = GameResourceGetter(self.h2lcu)
        self.getChampionNameById = self.h2lcu.get_champion_name_by_id
        self.getChampionIcon = self.game_resource_getter.get_champion_icon
        self.getSummonerSpellIcon = self.game_resource_getter.get_spell_icon
        self.getItemIcon = self.game_resource_getter.get_item_icon
        self.getRuneIcon = self.game_resource_getter.get_rune_icon
        self.getAugmentIcon = self.game_resource_getter.get_augment_icon
        self.getAugmentsName = self.h2lcu.get_augment_name_by_id

    async def start(self):
        """
        启动会话，连接到OPGG API的基础URL。
        """
        self.session = aiohttp.ClientSession("https://lol-api-champion.op.gg")

    async def update_port_and_token(self, port, token):
        self.h2lcu.update_port_and_token(port, token)

    async def close(self):
        """
        关闭会话，释放资源。
        """
        if self.session:
            await self.session.close()

    @alru_cache(maxsize=512)
    async def __fetchTierList(self, region, mode, tier):
        """
        从OPGG API获取分区列表数据。

        :param region: 区域代码，例如'kr'、'na'等。
        :param mode: 游戏模式，例如'ranked'、'normal'等。
        :param tier: 阶段，例如'platinum'、'diamond'等。
        :return: JSON格式的分区列表数据。
        """
        url = f"/api/{region}/champions/{mode}"
        params = {"tier": tier}

        return await self.__get(url, params)

    @alru_cache(maxsize=512)
    async def __fetchChampionBuild(self, region, mode, championId, position, tier):
        """
        从OPGG API获取特定英雄的构建数据。

        :param region: 区域代码，例如'kr'、'na'等。
        :param mode: 游戏模式，例如'ranked'、'aram'等。
        :param championId: 英雄ID。
        :param position: 英雄位置，例如'top'、'jungle'等。
        :param tier: 段位，例如'platinum'、'diamond'等。
        :return: JSON格式的英雄构建数据。
        """
        if mode != 'arena':
            url = f"/api/{region}/champions/{mode}/{championId}/{position}"
        else:
            url = f"/api/{region}/champions/{mode}/{championId}"

        params = {"tier": tier}

        return await self.__get(url, params)

    @alru_cache(maxsize=512)
    async def getChampionBuild(self, region, mode, championId, position, tier):
        """
        获取特定英雄的构建数据，并进行解析。

        :param region: 区域代码，例如'kr'、'na'等。
        :param mode: 游戏模式，例如'ranked'、'aram'等。
        :param championId: 英雄ID。
        :param position: 英雄位置，例如'top'、'jungle'等。
        :param tier: 阶段，例如'platinum'、'diamond'等。
        :return: 解析后的英雄构建数据，包括数据、版本、模式。
        """
        positions = await self.getChampionPositions(region, championId, tier)
        if position not in positions and mode == 'ranked':
            position = positions[0]

        raw = await self.__fetchChampionBuild(region, mode, championId, position, tier)

        if mode != 'arena':
            res = await OpggDataParser.parseOtherChampionBuild(raw, position, self.getChampionNameById, self.getChampionIcon, self.getSummonerSpellIcon, self.getItemIcon, self.getRuneIcon)
        else:
            res = await OpggDataParser.parseArenaChampionBuild(raw, self.getChampionNameById, self.getChampionIcon, self.getSummonerSpellIcon, self.getItemIcon, self.getRuneIcon, self.getAugmentIcon, self.getAugmentsName)

        return {
            'data': res,
            'version': raw['meta']['version'],
            'mode': mode,
        }

    @alru_cache(maxsize=512)
    async def getTierList(self, region, mode, tier):
        """
        获取特定区域、模式和阶段的分区列表数据，并进行解析。

        :param region: 区域代码，例如'kr'、'na'等。
        :param mode: 游戏模式，例如'ranked'、'normal'等。
        :param tier: 阶段，例如'platinum'、'diamond'等。
        :return: 解析后的分区列表数据，包括数据和版本。
        """
        raw = await self.__fetchTierList(region, mode, tier)

        version = raw['meta']['version']

        if mode == 'ranked':
            res = await OpggDataParser.parseRankedTierList(raw, self.getChampionNameById, self.getChampionIcon)
        else:
            res = await OpggDataParser.parseOtherTierList(raw, self.getChampionNameById, self.getChampionIcon)

        return {
            'data': res,
            'version': version
        }

    @alru_cache(maxsize=512)
    async def getChampionPositions(self, region, championId, tier):
        """
        获取特定英雄在特定区域和阶段的所有可能位置。

        :param region: 区域代码，例如'kr'、'na'等。
        :param championId: 英雄ID。
        :param tier: 阶段，例如'platinum'、'diamond'等。
        :return: 英雄可能的位置列表。
        """
        # 这个调用因为有 cache，所以还是挺快的
        data = await self.__fetchTierList(region, "ranked", tier)

        for item in data['data']:
            if item['id'] == championId:
                return [p['name'] for p in item['positions']]

        return []

    @alru_cache(maxsize=512)
    async def getAllChampionPositions(self, region, tier):
        """
        获取所有英雄在特定区域和阶段的所有可能位置。

        :param region: 区域代码，例如'kr'、'na'等。
        :param tier: 阶段，例如'platinum'、'diamond'等。
        :return: 字典，键为英雄ID，值为该英雄可能的位置列表。
        """
        data = await self.__fetchTierList(region, "ranked", tier)
        result = {}
        
        for item in data['data']:
            champion_id = item['id']
            positions = [p['name'] for p in item['positions']]
            result[champion_id] = positions
            
        return result

    async def __get(self, url, params=None):
        """
        发送GET请求到OPGG API，获取数据。

        :param url: 请求的URL。
        :param params: 请求的参数。
        :return: JSON格式的响应数据。
        """
        res = await self.session.get(url, params=params, ssl=False, proxy=None)
        return await res.json()


class OpggDataParser:

    @staticmethod
    async def parseRankedTierList(data, getChampionNameById, getChampionIcon):
        '''
        召唤师峡谷模式下的原始梯队数据，是所有英雄所有位置一起返回的

        在此函数内按照分路位置将它们分开
        '''

        data = data['data']
        res = {p: []
               for p in ['TOP', 'JUNGLE', 'MID', 'ADC', 'SUPPORT']}

        for item in data:
            championId = item['id']
            name = await getChampionNameById(championId)
            icon_id = championId

            for p in item['positions']:
                position = p['name']

                stats = p['stats']
                tier = stats['tier_data']

                counters = [{
                    'championId': c['champion_id'],
                    'icon': c['champion_id']
                } for c in p['counters']]

                res[position].append({
                    'championId': championId,
                    'name': name,
                    'icon': icon_id,
                    'winRate': stats.get('win_rate'),
                    'pickRate': stats.get('pick_rate'),
                    'banRate': stats.get('ban_rate'),
                    'kda': stats.get('kda'),
                    'tier': tier.get('tier'),
                    'rank': tier.get('rank'),
                    'position': position,
                    'counters': counters,
                })

        # 排名 / 梯队是乱的，所以排个序
        for tier in res.values():
            tier.sort(key=lambda x: x['rank'])

        return res

    @staticmethod
    async def parseOtherTierList(data, getChampionNameById, getChampionIcon):
        '''
        处理其他模式下的原始梯队数据
        '''

        data = data['data']
        res = []

        for item in data:
            stats = item['average_stats']

            if stats == None:
                continue

            if stats.get('rank') == None:
                continue

            championId = item['id']
            name = await getChampionNameById(championId)
            icon_id = championId

            res.append({
                'championId': championId,
                'name': name,
                'icon': icon_id,
                'winRate': stats.get('win_rate'),
                'pickRate': stats.get('pick_rate'),
                'banRate': stats.get('ban_rate'),
                'kda': stats.get('kda'),
                'tier': stats.get('tier'),
                'rank': stats.get('rank'),
                "position": None,
                'counters': [],
            })

        return sorted(res, key=lambda x: x['rank'])

    @staticmethod
    async def parseOtherChampionBuild(data, position, getChampionNameById, getChampionIcon, getSummonerSpellIcon, getItemIcon, getRuneIcon):
        data = data['data']

        summary = data['summary']
        championId = summary['id']
        icon_id = championId
        name = await getChampionNameById(championId)

        if position != 'none':
            for p in summary['positions']:
                if p['name'] == position:
                    stats: dict = p['stats']
                    break

            winRate = stats.get('win_rate')
            pickRate = stats.get('pick_rate')
            banRate = stats.get('ban_rate')
            kda = stats.get('kda')

            tierData: dict = stats['tier_data']
            tier = tierData.get("tier")
            rank = tierData.get("rank")

        else:
            stats = summary['average_stats']
            winRate = stats.get('win_rate')
            pickRate = stats.get('pick_rate')
            banRate = stats.get('ban_rate')
            kda = stats.get('kda')
            tier = stats.get("tier")
            rank = stats.get("rank")

        summonerSpells = []
        for s in data['summoner_spells']:
            icon_ids = s['ids']

            summonerSpells.append({
                'ids': s['ids'],
                'icons': icon_ids,
                'win': s['win'],
                'play': s['play'],
                'pickRate': s['pick_rate']
            })

        skills = {
            "masteries": data['skill_masteries'][0]['ids'],
            "order": data['skills'][0]['order'],
            'play': data['skills'][0]['play'],
            'win': data['skills'][0]['win'],
            'pickRate': data['skills'][0]['pick_rate']
        }

        boots = []
        for i in data['boots'][:3]:
            icon_ids = i['ids']
            boots.append({
                "icons": icon_ids,
                "play": i['play'],
                "win": i['win'],
                'pickRate': i['pick_rate']
            })

        startItems = []
        for i in data['starter_items'][:3]:
            icon_ids = i['ids']  # item_id
            startItems.append({
                "icons": icon_ids,
                "play": i['play'],
                "win": i['win'],
                'pickRate': i['pick_rate']
            })

        coreItems = []
        for i in data['core_items'][:5]:
            icon_ids = i['ids']  # item_id
            coreItems.append({
                "icons": icon_ids,
                "play": i['play'],
                "win": i['win'],
                'pickRate': i['pick_rate']
            })

        lastItems = []
        for i in data['last_items'][:16]:
            lastItems.append(i['ids'][0])  # item_id

        strongAgainst = []
        weakAgainst = []

        for c in data['counters']:
            winRate = c['win'] / c['play']
            arr = strongAgainst if winRate >= 0.5 else weakAgainst

            arr.append({
                'championId': (id := c['champion_id']),
                'name': await getChampionNameById(id),
                'icon': id,  # champion_id
                'play': c['play'],
                'win': c['win'],
                'winRate': winRate
            })

        strongAgainst.sort(key=lambda x: -x['winRate'])
        weakAgainst.sort(key=lambda x: x['winRate'])

        perks = [{
            'primaryId': (mainId := perk['primary_page_id']),
            "primaryIcon": mainId,  # rune_id
            'secondaryId': (subId := perk['secondary_page_id']),
            "secondaryIcon": subId,  # rune_id
            'perks': (perkIds := perk['primary_rune_ids'] + perk['secondary_rune_ids'] + perk['stat_mod_ids']),
            "icons": perkIds,  # rune_id
            'play': perk['play'],
            'win': perk['win'],
            'pickRate': perk['pick_rate'],
        } for perk in data['runes']
        ]


        return {
            "summary": {
                'name': name,
                'championId': championId,
                'icon': icon_id,
                'position': position,
                'winRate': winRate,
                'pickRate': pickRate,
                'banRate': banRate,
                'kda': kda,
                'tier': tier,
                'rank': rank
            },
            "summonerSpells": summonerSpells,
            "championSkills": skills,
            "items": {
                "boots": boots,
                "startItems": startItems,
                "coreItems": coreItems,
                "lastItems": lastItems,
            },
            "counters": {
                "strongAgainst": strongAgainst,
                "weakAgainst": weakAgainst,
            },
            "perks": perks,
        }

    @staticmethod
    async def parseArenaChampionBuild(data, getChampionNameById, getChampionIcon, getSummonerSpellIcon, getItemIcon, getRuneIcon, getAugmentIcon, getAugmentsName):
        data = data['data']

        summary = data['summary']
        championId = summary['id']
        name = await getChampionNameById(championId)
        icon_id = championId

        stats = summary['average_stats']
        play = stats['play']
        winRate = stats['win'] / play
        firstRate = stats['first_place'] / play
        averagePlace = stats['total_place'] / play
        pickRate = stats['pick_rate']
        banRate = stats['ban_rate']
        tier = stats['tier']

        skills = {
            "masteries": data['skill_masteries'][0]['ids'],
            "order": data['skills'][0]['order'],
            'play': data['skills'][0]['play'],
            'win': data['skills'][0]['win'],
            'pickRate': data['skills'][0]['pick_rate']
        }

        boots = []
        for i in data['boots'][:3]:
            icon_ids = i['ids']  # item_id
            boots.append({
                "icons": icon_ids,
                "play": i['play'],
                "win": i['win'],
                'pickRate': i['pick_rate'],
                "averatePlace": i['total_place'] / i['play'],
                "firstRate": i['first_place'] / i['play']
            })

        startItems = []
        for i in data['starter_items'][:3]:
            icon_ids = i['ids']
            startItems.append({
                "icons": icon_ids,
                "play": i['play'],
                "win": i['win'],
                'pickRate': i['pick_rate'],
                "averatePlace": i['total_place'] / i['play'],
                "firstRate": i['first_place'] / i['play']
            })

        coreItems = []
        for i in data['core_items'][:5]:
            icon_ids = i['ids']
            coreItems.append({
                "icons": icon_ids,
                "play": i['play'],
                "win": i['win'],
                'pickRate': i['pick_rate'],
                "averatePlace": i['total_place'] / i['play'],
                "firstRate": i['first_place'] / i['play']
            })

        lastItems = []
        for i in data['last_items'][:16]:
            lastItems.append(i['ids'][0])

        augments = []
        for item in data['augment_group']:
            arr = [{
                "id": (augId := aug['id']),
                "icon": augId,
                "name": await getAugmentsName(augId),
                "win": aug['win'],
                'play': aug['play'],
                "totalPlace": aug['total_place'],
                "firstPlace": aug['first_place'],
                'pickRate': aug['pick_rate']
            } for aug in item['augments']]

            augments.append(arr)

        synergies = [{
            "championId": (chId := syn['champion_id']),
            'icon': chId,
            "name": await getChampionNameById(chId),
            "win": syn['win'],
            'play': syn['play'],
            "totalPlace": syn['total_place'],
            "firstPlace": syn['first_place'],
            'pickRate': syn['pick_rate']
        } for syn in data['synergies']]

        return {
            "summary": {
                "name": name,
                "icon": icon_id,
                "championId": championId,
                "play": play,
                "winRate": winRate,
                "firstRate": firstRate,
                "averagePlace": averagePlace,
                "pickRate": pickRate,
                "banRate": banRate,
                "tier": tier,
                "position": "none"
            },
            "championSkills": skills,
            "items": {
                "boots": boots,
                "startItems": startItems,
                "coreItems": coreItems,
                "lastItems": lastItems,
            },
            "augments": augments,
            "synergies": synergies,
        }





# test
async def main():
    """
    测试 Opgg 类的主要功能
    """
    from server_app.services.lcu import get_port_and_token
    port, token = get_port_and_token()
    opgg = Opgg(port, token)
    # 初始化并启动 OPGG 客户端
    await opgg.start()

    # 测试获取英雄梯队数据
    tier_data = await opgg.getTierList(
        region="kr",  # 韩服数据
        mode="ranked",  # 排位模式
        tier="platinum_plus"  # 白金以上段位
    )
    print("梯队数据示例：")
    print(f"版本: {tier_data['version']}")
    print(f"中路前三英雄: {tier_data['data']['MID'][:3]}\n")

    # 测试获取具体英雄数据（以亚索为例，ID=157）
    build_data = await opgg.getChampionBuild(
        region="kr",
        mode="ranked",
        championId=157,  # 亚索
        position="MID",
        tier="platinum_plus"
    )
    print("亚索中单数据示例：")
    print(f"版本: {build_data['version']}")
    print(f"胜率: {build_data['data']['summary']['winRate']}")
    print(f"选取率: {build_data['data']['summary']['pickRate']}")
    print(f"技能加点顺序: {build_data['data']['championSkills']['order']}\n")

    # 关闭会话
    await opgg.close()


if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
