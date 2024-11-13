<template>
    <div class="match-history">
      <!-- 筛选器部分 -->
      <div class="filter-section">
        <div class="filter-group">
          <el-select v-model="gameType" placeholder="游戏类型" class="filter-select">
            <el-option label="全部" value="all" />
            <el-option label="匹配赛" value="normal" />
            <el-option label="排位赛" value="ranked" />
          </el-select>
          
          <el-select v-model="timeRange" placeholder="时间范围" class="filter-select">
            <el-option label="全部时间" value="all" />
            <el-option label="最近一周" value="week" />
            <el-option label="最近一月" value="month" />
          </el-select>
        </div>
      </div>
  
      <!-- 对局列表 -->
      <div class="match-list" v-loading="loading">
        <div v-for="game in matches" :key="game.gameCreation" 
             class="match-item" 
             :class="getGameResult(game, game.participantIdentities[0].participantId)">
          <!-- 基本信息 -->
          <div class="match-info">
            <div class="game-mode-time">
              <span class="game-type">{{ game.gameMode }}</span>
              <span class="game-time">{{ formatDate(game.gameCreation) }}</span>
            </div>
            <div class="game-duration">时长: {{ formatDuration(game.gameDuration) }}</div>
            <div class="game-result" :class="getGameResult(game, game.participantIdentities[0].participantId)">
              {{ getGameResult(game, game.participantIdentities[0].participantId) === 'victory' ? '胜利' : '失败' }}
            </div>
          </div>
  
          <!-- 英雄信息 -->
          <div class="champion-info">
            <img :src="getResourceUrl('champion_icons', game.participants[0].championId)" 
                 :alt="String(game.participants[0].championId)" 
                 class="champion-icon">
            <div class="summoner-spells">
              <img :src="getResourceUrl('spell_icons', game.participants[0].spell1Id)" 
                   :alt="String(game.participants[0].spell1Id)">
              <img :src="getResourceUrl('spell_icons', game.participants[0].spell2Id)" 
                   :alt="String(game.participants[0].spell2Id)">
            </div>
          </div>
  
          <!-- 数据统计 -->
          <div class="stats">
            <div class="kda">
              <span>{{ game.participants[0].stats.kills }}/{{ game.participants[0].stats.deaths }}/{{ game.participants[0].stats.assists }}</span>
              <span class="kda-ratio">
                {{ ((game.participants[0].stats.kills + game.participants[0].stats.assists) / 
                    Math.max(1, game.participants[0].stats.deaths)).toFixed(2) }} KDA
              </span>
            </div>
            <div class="other-stats">
              <span>补刀 {{ game.participants[0].stats.totalMinionsKilled }}</span>
              <span>金钱 {{ game.participants[0].stats.goldEarned }}</span>
            </div>
          </div>
  
          <!-- 装备栏 -->
          <div class="items">
            <template v-for="i in 7" :key="i">
              <img v-if="game.participants[0].stats[`item${i-1}` as keyof PlayerStats]"
                   :src="getResourceUrl('item_icons', Number(game.participants[0].stats[`item${i-1}` as keyof PlayerStats]))"
                   :alt="String(game.participants[0].stats[`item${i-1}` as keyof PlayerStats])">
              <div v-else class="empty-item"></div>
            </template>
          </div>
        </div>
      </div>
  
      <!-- 分页器 -->
      <div class="pagination">
        <el-pagination
          :current-page="currentPage"
          @current-change="handleCurrentChange"
          :page-size="pageSize"
          :total="totalMatches"
          layout="prev, pager, next"
        />
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, onMounted, watch } from 'vue'
  import axios from 'axios'
  import { ElMessage } from 'element-plus'
  
  // 定义接口
  interface PlayerStats {
    assists: number
    deaths: number
    kills: number
    goldEarned: number
    totalMinionsKilled: number
    win: boolean
    item0: number
    item1: number
    item2: number
    item3: number
    item4: number
    item5: number
    item6: number
    champLevel: number
  }
  
  interface Player {
    gameName: string
    tagLine: string
    profileIcon: number
  }
  
  interface Participant {
    championId: number
    participantId: number
    spell1Id: number
    spell2Id: number
    stats: PlayerStats
    teamId: number
  }
  
  interface ParticipantIdentity {
    participantId: number
    player: Player
  }
  
  interface Team {
    teamId: number
    win: string
  }
  
  interface Game {
    gameCreation: number
    gameDuration: number
    gameMode: string
    gameType: string
    participants: Participant[]
    participantIdentities: ParticipantIdentity[]
    teams: Team[]
  }
  
  interface MatchHistoryResponse {
    accountId: number
    games: {
      gameCount: number
      games: Game[]
    }
  }
  
  interface ResourceRequest {
    profile_icons?: number[]
    champion_icons?: number[]
    item_icons?: number[]
    spell_icons?: number[]
    rune_icons?: number[]
    augment_icons?: number[]
    champion_splashes?: Array<{skin_id: number, is_centered: boolean}>
  }
  
  interface ResourceResponse {
    profile_icons?: Record<number, string>
    champion_icons?: Record<number, string>
    item_icons?: Record<number, string>
    spell_icons?: Record<number, string>
    rune_icons?: Record<number, string>
    augment_icons?: Record<number, string>
    champion_splashes?: Record<string, string>
  }
  
  // 状态定义
  const gameType = ref('all')
  const timeRange = ref('all')
  const currentPage = ref(1)
  const pageSize = ref(10)
  const totalMatches = ref(0)
  const matches = ref<Game[]>([])
  const loading = ref(false)
  const gameResources = ref<ResourceResponse>({})
  
  // 添加分页处理函数
  const handleCurrentChange = (val: number) => {
    currentPage.value = val;
  }
  
  // 获取对局历史
  const fetchMatchHistory = async () => {
    try {
      loading.value = true
      const startIndex = (currentPage.value - 1) * pageSize.value
      const endIndex = startIndex + pageSize.value - 1
      
      // 使用 URLSearchParams 构建请求数据
      const params = new URLSearchParams();
      params.append('beg_index', startIndex.toString());
      params.append('end_index', endIndex.toString());
      
      const response = await axios.post<MatchHistoryResponse>(
        '/api/match_history/get_match_history',
        params,
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        }
      )
      
      if (response.data?.games?.games) {
        matches.value = response.data.games.games;
        totalMatches.value = response.data.games.gameCount;
        // 加载游戏资源
        await loadGameResources(matches.value)
      } else {
        matches.value = [];
        totalMatches.value = 0;
      }
    } catch (error) {
      ElMessage.error('获取对局历史失败')
      console.error('获取对局历史失败:', error)
    } finally {
      loading.value = false
    }
  }
  
  // 监听分页变化
  watch(currentPage, () => {
    fetchMatchHistory()
  })
  
  // 格式化时间
  const formatDate = (timestamp: number): string => {
    const date = new Date(timestamp)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
  
  // 格式化时长
  const formatDuration = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}分${remainingSeconds}秒`
  }
  
  // 获取游戏结果
  const getGameResult = (game: Game, participantId: number): 'victory' | 'defeat' => {
    const participant = game.participants.find(p => p.participantId === participantId)
    if (!participant) return 'defeat'
    const team = game.teams.find(t => t.teamId === participant.teamId)
    return team?.win === 'Win' ? 'victory' : 'defeat'
  }
  
  // 资源加载函数
  const loadGameResources = async (games: Game[]) => {
    try {
      const resourceRequest: ResourceRequest = {
        champion_icons: [],
        spell_icons: [],
        item_icons: []
      }
      
      // 收集所需资源ID
      games.forEach(game => {
        const participant = game.participants[0]
        
        // 收集英雄图标
        if (!resourceRequest.champion_icons?.includes(participant.championId)) {
          resourceRequest.champion_icons?.push(participant.championId)
        }
        
        // 收集召唤师技能图标
        if (!resourceRequest.spell_icons?.includes(participant.spell1Id)) {
          resourceRequest.spell_icons?.push(participant.spell1Id)
        }
        if (!resourceRequest.spell_icons?.includes(participant.spell2Id)) {
          resourceRequest.spell_icons?.push(participant.spell2Id)
        }
        
        // 收集装备图标
        for (let i = 0; i < 7; i++) {
          const itemId = Number(participant.stats[`item${i}` as keyof PlayerStats])
          if (itemId !== 0 && !resourceRequest.item_icons?.includes(itemId)) {
            resourceRequest.item_icons?.push(itemId)
          }
        }
      })
      
      // 请求资源
      const response = await axios.post<ResourceResponse>(
        '/api/common/game_resource/batch_get_resources',
        resourceRequest
      )
      
      gameResources.value = response.data
    } catch (error) {
      console.error('加载游戏资源失败:', error)
      ElMessage.error('加载游戏资源失败')
    }
  }
  
  // 修改图片加载方式
  const getResourceUrl = (
    type: keyof Omit<ResourceResponse, 'champion_splashes'>, 
    id: number | string
  ): string => {
    const resources = gameResources.value[type] as Record<string | number, string>;
    if (resources?.[id]) {
        return `data:image/png;base64,${resources[id]}`
    }
    return '/placeholder.png'
  }
  
  onMounted(() => {
    fetchMatchHistory()
  })
  </script>
  
  <style scoped>
  .match-history {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    background-color: var(--el-bg-color);
    min-height: 100%;
  }
  
  .filter-section {
    background: white;
    padding: 16px;
    border-radius: 8px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
    margin-bottom: 20px;
  }
  
  .filter-group {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
  }
  
  .filter-select {
    min-width: 160px;
  }
  
  .match-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  
  .match-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px;
    gap: 20px;
    min-height: 120px;
    background: white;
    border-radius: 8px;
    border: 1px solid var(--el-border-color-lighter);
    transition: all 0.2s ease;
  }
  
  .match-item:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  }
  
  .match-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  
  .game-mode-time {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  .game-type {
    font-size: 14px;
    font-weight: 600;
    color: var(--el-color-primary);
    background: var(--el-color-primary-light-9);
    padding: 2px 8px;
    border-radius: 4px;
  }
  
  .game-time {
    font-size: 13px;
    color: var(--el-text-color-secondary);
  }
  
  .game-duration {
    color: var(--el-text-color-regular);
    font-size: 0.9em;
    margin: 4px 0;
  }
  
  .game-result {
    font-weight: 600;
    padding: 4px 12px;
    border-radius: 4px;
    display: inline-block;
    width: fit-content;
  }
  
  .victory .game-result {
    background-color: var(--el-color-success-light-9);
    color: var(--el-color-success);
  }
  
  .defeat .game-result {
    background-color: var(--el-color-danger-light-9);
    color: var(--el-color-danger);
  }
  
  .champion-info {
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 100px;
  }
  
  .champion-icon {
    width: 56px;
    height: 56px;
    border-radius: 50%;
    border: 3px solid var(--el-border-color-light);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s ease;
  }
  
  .champion-icon:hover {
    transform: scale(1.1);
  }
  
  .summoner-spells {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  
  .summoner-spells img {
    width: 28px;
    height: 28px;
    border-radius: 4px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
  
  .stats {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  
  .kda {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  .kda span:first-child {
    font-size: 16px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }
  
  .kda-ratio {
    font-size: 13px;
    color: var(--el-text-color-secondary);
    background: var(--el-fill-color-light);
    padding: 1px 6px;
    border-radius: 3px;
  }
  
  .other-stats {
    display: flex;
    gap: 16px;
    font-size: 13px;
  }
  
  .other-stats span {
    display: flex;
    align-items: center;
    color: var(--el-text-color-regular);
  }
  
  .items {
    display: grid;
    grid-template-columns: repeat(7, 32px);
    gap: 4px;
    align-items: center;
    justify-content: center;
    min-height: 40px;
  }
  
  .items img, .empty-item {
    width: 32px;
    height: 32px;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .empty-item {
    background: var(--el-fill-color-lighter);
    border: 2px dashed var(--el-border-color-lighter);
  }
  
  .pagination {
    margin-top: 24px;
    padding: 16px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  }
  
  @media (max-width: 768px) {
    .match-item {
      flex-direction: column;
      align-items: flex-start;
      padding: 12px;
    }
  
    .game-mode-time {
      width: 100%;
      justify-content: space-between;
    }
  
    .stats {
      width: 100%;
      flex-direction: row;
      justify-content: space-between;
      align-items: center;
    }
  
    .items {
      width: 100%;
      justify-content: center;
    }
  }
  </style>