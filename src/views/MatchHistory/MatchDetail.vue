<template>
  <div class="match-detail">
    <!-- 头部控制栏 -->
    <div class="header-controls">
      <div class="header-left">
        <el-button 
          type="primary" 
          size="small" 
          @click="$emit('back')"
          :icon="ArrowLeft">
          返回我的主页
        </el-button>
      </div>
      <div class="header-right">
        <div class="game-meta">
          <span>{{ getGameMode(gameDetail?.gameMode || '') }}</span>
          <span>{{ formatDate(gameDetail?.gameCreation || 0) }}</span>
          <span>时长: {{ formatDuration(gameDetail?.gameDuration || 0) }}</span>
        </div>
        <el-button 
          type="primary" 
          size="small" 
          @click="handleAnalyze"
          :icon="DataAnalysis">
          对局分析
        </el-button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-loading="loading" class="detail-content">
      <template v-if="gameDetail">
        <!-- 蓝方数据 -->
        <div class="team-section">
          <div class="team-summary" :class="{ 'win': gameDetail.teams[0].win === 'Win' }">
            <div class="summary-content">
              <div class="team-label">
                <span class="team-name">蓝方</span>
                <span class="result-tag" :class="{ 'win': gameDetail.teams[0].win === 'Win' }">
                  {{ gameDetail.teams[0].win === 'Win' ? '胜利' : '失败' }}
                </span>
              </div>
              <div class="team-stats">
                <div class="stat">
                  <img src="./icon/kill.svg" class="stat-icon" alt="击杀">
                  <span class="value">{{ getTeamKills(100) }}</span>
                </div>
                <div class="stat">
                  <img src="./icon/tower.svg" class="stat-icon" alt="防御塔">
                  <span class="value">{{ gameDetail.teams[0].towerKills }}</span>
                </div>
                <div class="stat">
                  <img src="./icon/money.svg" class="stat-icon" alt="经济">
                  <span class="value">{{ formatNumber(getTeamGold(100)) }}</span>
                </div>
              </div>
            </div>
          </div>

          <el-table :data="getTeamPlayers(100)" size="small" :header-cell-style="{ padding: '4px 0' }"
            :cell-style="{ padding: '4px 0' }">
            <el-table-column label="玩家" min-width="200">
              <template #default="scope">
                <div class="player-info" @click="handlePlayerClick(scope.row.participantId)">
                  <img :src="getResourceUrl('champion_icons', scope.row.championId)" class="champion-icon">
                  <div class="player-name">
                    <div>{{ getPlayerName(scope.row.participantId) }}</div>
                    <div class="summoner-spells">
                      <img :src="getResourceUrl('spell_icons', scope.row.spell1Id)" class="spell-icon">
                      <img :src="getResourceUrl('spell_icons', scope.row.spell2Id)" class="spell-icon">
                    </div>
                  </div>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="stats.kills" label="击杀" width="60" align="center" />
            <el-table-column prop="stats.deaths" label="死亡" width="60" align="center" />
            <el-table-column prop="stats.assists" label="助攻" width="60" align="center" />
            <el-table-column label="装备" min-width="200">
              <template #default="scope">
                <div class="items-list">
                  <template v-for="i in 6" :key="i">
                    <img 
                      v-if="scope.row.stats[`item${i-1}`]"
                      :src="getResourceUrl('item_icons', scope.row.stats[`item${i-1}`])"
                      class="item-icon"
                    >
                    <div v-else class="empty-item" />
                  </template>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="输出" align="center" min-width="120">
              <template #default="scope">
                {{ formatNumber(scope.row.stats.totalDamageDealtToChampions) }}
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 红方数据 -->
        <div class="team-section">
          <div class="team-summary" :class="{ 'win': gameDetail.teams[1].win === 'Win' }">
            <div class="summary-content">
              <div class="team-label">
                <span class="team-name">红方</span>
                <span class="result-tag" :class="{ 'win': gameDetail.teams[1].win === 'Win' }">
                  {{ gameDetail.teams[1].win === 'Win' ? '胜利' : '失败' }}
                </span>
              </div>
              <div class="team-stats">
                <div class="stat">
                  <img src="./icon/kill.svg" class="stat-icon" alt="击杀">
                  <span class="value">{{ getTeamKills(200) }}</span>
                </div>
                <div class="stat">
                  <img src="./icon/tower.svg" class="stat-icon" alt="防御塔">
                  <span class="value">{{ gameDetail.teams[1].towerKills }}</span>
                </div>
                <div class="stat">
                  <img src="./icon/money.svg" class="stat-icon" alt="经济">
                  <span class="value">{{ formatNumber(getTeamGold(200)) }}</span>
                </div>
              </div>
            </div>
          </div>

          <el-table :data="getTeamPlayers(200)" size="small" :header-cell-style="{ padding: '4px 0' }"
            :cell-style="{ padding: '4px 0' }">
            <el-table-column label="玩家" min-width="200">
              <template #default="scope">
                <div class="player-info" @click="handlePlayerClick(scope.row.participantId)">
                  <img :src="getResourceUrl('champion_icons', scope.row.championId)" class="champion-icon">
                  <div class="player-name">
                    <div>{{ getPlayerName(scope.row.participantId) }}</div>
                    <div class="summoner-spells">
                      <img :src="getResourceUrl('spell_icons', scope.row.spell1Id)" class="spell-icon">
                      <img :src="getResourceUrl('spell_icons', scope.row.spell2Id)" class="spell-icon">
                    </div>
                  </div>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="stats.kills" label="击杀" width="60" align="center" />
            <el-table-column prop="stats.deaths" label="死亡" width="60" align="center" />
            <el-table-column prop="stats.assists" label="助攻" width="60" align="center" />
            <el-table-column label="装备" min-width="200">
              <template #default="scope">
                <div class="items-list">
                  <template v-for="i in 6" :key="i">
                    <img 
                      v-if="scope.row.stats[`item${i-1}`]"
                      :src="getResourceUrl('item_icons', scope.row.stats[`item${i-1}`])"
                      class="item-icon"
                    >
                    <div v-else class="empty-item" />
                  </template>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="输出" align="center" min-width="120">
              <template #default="scope">
                {{ formatNumber(scope.row.stats.totalDamageDealtToChampions) }}
              </template>
            </el-table-column>
          </el-table>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ArrowLeft, DataAnalysis } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import axios from 'axios'
import type { 
  Game, 
  ResourceResponse, 
  Participant, 
  ParticipantIdentity 
} from './match'
import { useRouter } from 'vue-router'

const props = defineProps<{
  gameId: number
}>()

// 定义 emit
const emit = defineEmits<{
  (e: 'back'): void
  (e: 'player-click', puuid: string, playerName: string): void
}>()

const loading = ref(false)
const gameDetail = ref<Game | null>(null)
const gameResources = ref<ResourceResponse>({})
const router = useRouter()

// 工具函数
const formatDate = (timestamp: number) => {
  return dayjs(timestamp).format('YYYY-MM-DD HH:mm:ss')
}

const formatDuration = (seconds: number) => {
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
}

const formatNumber = (num: number) => {
  return num.toLocaleString()
}

const getGameMode = (mode: string) => {
  const modes: Record<string, string> = {
    'CLASSIC': '经典模式',
    'ARAM': '极地大乱斗',
    'URF': '无限火力'
  }
  return modes[mode] || mode
}

const getTeamKills = (teamId: number) => {
  if (!gameDetail.value) return 0
  
  return gameDetail.value.participants
    .filter((p: Participant) => p.teamId === teamId)
    .reduce((sum: number, p: Participant) => sum + p.stats.kills, 0)
}

const getTeamGold = (teamId: number) => {
  if (!gameDetail.value) return 0
  
  return gameDetail.value.participants
    .filter((p: Participant) => p.teamId === teamId)
    .reduce((sum: number, p: Participant) => sum + p.stats.goldEarned, 0)
}

const getTeamPlayers = (teamId: number) => {
  if (!gameDetail.value) return []
  
  return gameDetail.value.participants.filter((p: Participant) => p.teamId === teamId)
}

const getPlayerName = (participantId: number) => {
  if (!gameDetail.value) return '未知玩家'
  
  const identity = gameDetail.value.participantIdentities.find(
    (p: ParticipantIdentity) => p.participantId === participantId
  )
  return identity?.player?.gameName || '未知玩家'
}

// 获取资源URL的方法（参考自ChampionRanking）
const getResourceUrl = (type: keyof ResourceResponse, id: number): string => {
  const resources = gameResources.value[type]
  if (resources?.[id]) {
    return `data:image/png;base64,${resources[id]}`
  }
  return '/placeholder.png'
}

// 获取对局详情
const fetchGameDetail = async () => {
  try {
    loading.value = true
    const params = new URLSearchParams()
    params.append('game_id', props.gameId.toString())
    

    const response = await axios.post(
      '/api/match_history/get_game_detail',
      params,
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }
    )
    // 调试
    console.log('params:', params)

    
    
    gameDetail.value = response.data
    // 加载游戏资源
    await loadGameResources()
  } catch (error) {
    console.error('获取对局详情失败:', error)
    ElMessage.error('获取对局详情失败')
  } finally {
    loading.value = false
  }
}

const loadGameResources = async () => {
  try {
    if (!gameDetail.value) return

    const resourceRequest = {
      champion_icons: [] as number[],
      spell_icons: [] as number[],
      item_icons: [] as number[]
    }

    // 收集所有需要的资源ID
    gameDetail.value.participants.forEach((participant: any) => {
      // 英雄图标
      if (!resourceRequest.champion_icons.includes(participant.championId)) {
        resourceRequest.champion_icons.push(participant.championId)
      }
      
      // 召唤师技能图标
      if (!resourceRequest.spell_icons.includes(participant.spell1Id)) {
        resourceRequest.spell_icons.push(participant.spell1Id)
      }
      if (!resourceRequest.spell_icons.includes(participant.spell2Id)) {
        resourceRequest.spell_icons.push(participant.spell2Id)
      }

      // 装备图标
      for (let i = 0; i < 6; i++) {
        const itemId = participant.stats[`item${i}`]
        if (itemId && !resourceRequest.item_icons.includes(itemId)) {
          resourceRequest.item_icons.push(itemId)
        }
      }
    })

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

const handlePlayerClick = (participantId: number): void => {
  if (!gameDetail.value) return
  
  const identity = gameDetail.value.participantIdentities.find(
    (p: ParticipantIdentity) => p.participantId === participantId
  )
  if (identity?.player?.puuid) {
    emit('player-click', identity.player.puuid, identity.player.gameName)
  }
}

// 添加分析处理函数
const handleAnalyze = () => {
  if (!gameDetail.value) return
  
  const blueTeamPuuids = gameDetail.value.participantIdentities
    .filter(p => {
      const participant = gameDetail.value?.participants.find(
        part => part.participantId === p.participantId
      )
      return participant?.teamId === 100
    })
    .map(p => p?.player?.puuid)
    .filter(Boolean)

  const redTeamPuuids = gameDetail.value.participantIdentities
    .filter(p => {
      const participant = gameDetail.value?.participants.find(
        part => part.participantId === p.participantId
      )
      return participant?.teamId === 200
    })
    .map(p => p?.player?.puuid)
    .filter(Boolean)

  router.push({
    name: 'GameAnalysis',
    query: {
      createTab: 'true',
      gameId: props.gameId.toString(),
      blueTeam: blueTeamPuuids.join(','),
      redTeam: redTeamPuuids.join(',')
    }
  })
}

onMounted(() => {
  fetchGameDetail()
})
</script>

<style scoped>
.detail-content {
  max-width: 1000px;
  margin: 0 auto;
  width: 100%;
}

.match-detail {
  padding: 0px;
}

.header-controls {
  max-width: 1000px;
  margin: 0 auto 8px;
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--el-bg-color-overlay);
  padding: 2px 12px;
  border-radius: 8px;
}

.header-left {
  flex-shrink: 0;
}

.header-right {
  flex-grow: 1;
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  align-items: center;
}

.game-meta {
  display: flex;
  gap: 12px;
  color: var(--el-text-color-regular);
  font-size: 13px;
}

.team-section {
  background: var(--el-bg-color-overlay);
  padding: 8px;
  border-radius: 8px;
  margin-bottom: 8px;
}

.team-summary {
  padding: 4px 12px;
  margin-bottom: 4px;
  background: var(--el-fill-color-light);
  border: 1px solid var(--el-border-color-lighter);
}

.team-summary.win {
  background: var(--el-color-success-light-9);
  border: 1px solid var(--el-color-success-light-7);
}

.summary-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.team-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.team-stats {
  display: flex;
  gap: 16px;
}

.team-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  margin: 0;
}

.team-name {
  font-weight: bold;
}

.result-tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: normal;
  background-color: var(--el-color-danger-light-9);
  color: var(--el-color-danger);
  border: 1px solid var(--el-color-danger-light-7);
}

.result-tag.win {
  background-color: var(--el-color-success-light-9);
  color: var(--el-color-success);
  border: 1px solid var(--el-color-success-light-7);
}

.player-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.player-info:hover {
  opacity: 0.8;
}

.champion-icon {
  width: 28px;
  height: 28px;
  border-radius: 50%;
}

.spell-icon {
  width: 16px;
  height: 16px;
  border-radius: 4px;
}

.summoner-spells {
  display: flex;
  gap: 4px;
}

.items-list {
  display: flex;
  gap: 4px;
}

.item-icon {
  width: 24px;
  height: 24px;
  border-radius: 4px;
}

.empty-item {
  width: 24px;
  height: 24px;
  background: var(--el-border-color-lighter);
  border-radius: 4px;
}

@media (max-width: 768px) {
  .header-controls {
    flex-direction: column;
    gap: 4px;
    align-items: flex-start;
  }
  
  .header-right {
    width: 100%;
    justify-content: flex-start;
  }
  
  .game-meta {
    flex-wrap: wrap;
    gap: 6px 12px;
  }
}

:deep(.el-table) {
  --el-table-header-bg-color: transparent;
  --el-table-row-hover-bg-color: var(--el-fill-color-light);
}

:deep(.el-table__header) {
  margin-bottom: 0;
}

:deep(.el-table__body) td {
  border-bottom: none;
}

.match-info {
  display: none;
}

.stat-icon {
  width: 20px;
  height: 20px;
  vertical-align: middle;
}

.stat {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
