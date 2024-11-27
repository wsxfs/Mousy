<template>
  <div class="match-detail">
    <!-- 返回按钮 -->
    <div class="header-controls">
      <el-button 
        type="primary" 
        size="small" 
        @click="$emit('back')"
        :icon="ArrowLeft">
        返回列表
      </el-button>
    </div>

    <!-- 加载状态 -->
    <div v-loading="loading" class="detail-content">
      <template v-if="gameDetail">
        <!-- 对局基本信息 -->
        <div class="match-summary">
          <div class="game-info">
            <div class="mode">{{ getGameMode(gameDetail.gameMode) }}</div>
            <div class="time">{{ formatDate(gameDetail.gameCreation) }}</div>
            <div class="duration">时长: {{ formatDuration(gameDetail.gameDuration) }}</div>
          </div>
        </div>

        <!-- 队伍对比数据 -->
        <div class="teams-comparison">
          <div class="team" :class="{ 'win': gameDetail.teams[0].win === 'Win' }">
            <div class="team-stats">
              <div class="stat">
                <span class="label">击杀</span>
                <span class="value">{{ getTeamKills(100) }}</span>
              </div>
              <div class="stat">
                <span class="label">防御塔</span>
                <span class="value">{{ gameDetail.teams[0].towerKills }}</span>
              </div>
              <div class="stat">
                <span class="label">经济</span>
                <span class="value">{{ getTeamGold(100) }}</span>
              </div>
            </div>
          </div>
          <div class="vs">VS</div>
          <div class="team" :class="{ 'win': gameDetail.teams[1].win === 'Win' }">
            <div class="team-stats">
              <div class="stat">
                <span class="label">击杀</span>
                <span class="value">{{ getTeamKills(200) }}</span>
              </div>
              <div class="stat">
                <span class="label">防御塔</span>
                <span class="value">{{ gameDetail.teams[1].towerKills }}</span>
              </div>
              <div class="stat">
                <span class="label">经济</span>
                <span class="value">{{ getTeamGold(200) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 玩家详细数据 -->
        <div class="teams-detail">
          <!-- 蓝队数据 -->
          <div class="team-table">
            <div class="team-label" :class="{ 'win': gameDetail.teams[0].win === 'Win' }">
              蓝队 {{ gameDetail.teams[0].win === 'Win' ? '(获胜)' : '(失败)' }}
            </div>
            <el-table :data="getTeamPlayers(100)" size="small">
              <el-table-column label="玩家" min-width="200">
                <template #default="scope">
                  <div class="player-info">
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

          <!-- 红队数据 -->
          <div class="team-table">
            <div class="team-label" :class="{ 'win': gameDetail.teams[1].win === 'Win' }">
              红队 {{ gameDetail.teams[1].win === 'Win' ? '(获胜)' : '(失败)' }}
            </div>
            <el-table :data="getTeamPlayers(200)" size="small">
              <el-table-column label="玩家" min-width="200">
                <template #default="scope">
                  <div class="player-info">
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
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ArrowLeft } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import axios from 'axios'

const props = defineProps<{
  gameId: number
}>()

defineEmits<{
  'back': []
}>()

const loading = ref(false)
const gameDetail = ref<any>(null)

// 添加资源响应类型
interface ResourceResponse {
  champion_icons?: Record<string | number, string>
  spell_icons?: Record<string | number, string>
  item_icons?: Record<string | number, string>
}

// 添加资源状态
const gameResources = ref<ResourceResponse>({})

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
  return gameDetail.value.participants
    .filter((p: any) => p.teamId === teamId)
    .reduce((sum: number, p: any) => sum + p.stats.kills, 0)
}

const getTeamGold = (teamId: number) => {
  return gameDetail.value.participants
    .filter((p: any) => p.teamId === teamId)
    .reduce((sum: number, p: any) => sum + p.stats.goldEarned, 0)
}

const getTeamPlayers = (teamId: number) => {
  return gameDetail.value.participants.filter((p: any) => p.teamId === teamId)
}

const getPlayerName = (participantId: number) => {
  const identity = gameDetail.value.participantIdentities.find(
    (p: any) => p.participantId === participantId
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
    // 调试
    console.log('resourceRequest:', resourceRequest)
    console.log('gameResources.value:', gameResources.value)
  } catch (error) {
    console.error('加载游戏资源失败:', error)
    ElMessage.error('加载游戏资源失败')
  }
}

onMounted(() => {
  fetchGameDetail()
})
</script>

<style scoped>
.match-detail {
  padding: 20px;
}

.header-controls {
  margin-bottom: 20px;
}

.match-summary {
  background: var(--el-bg-color-overlay);
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.game-info {
  display: flex;
  gap: 20px;
  align-items: center;
}

.teams-comparison {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  background: var(--el-bg-color-overlay);
  padding: 20px;
  border-radius: 8px;
}

.team {
  flex: 1;
  padding: 20px;
  border-radius: 8px;
}

.team.win {
  background: rgba(var(--el-color-primary-rgb), 0.1);
}

.vs {
  font-size: 24px;
  font-weight: bold;
  margin: 0 20px;
}

.team-stats {
  display: flex;
  justify-content: space-around;
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.label {
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.value {
  font-size: 18px;
  font-weight: bold;
}

.player-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.champion-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
}

.spell-icon {
  width: 20px;
  height: 20px;
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
  width: 30px;
  height: 30px;
  border-radius: 4px;
}

.empty-item {
  width: 30px;
  height: 30px;
  background: var(--el-border-color-lighter);
  border-radius: 4px;
}

.teams-detail {
  background: var(--el-bg-color-overlay);
  padding: 20px;
  border-radius: 8px;
}

.team-table {
  margin-bottom: 20px;
}

.team-label {
  padding: 10px;
  font-size: 16px;
  font-weight: bold;
  background: var(--el-fill-color-light);
  border-radius: 4px;
  margin-bottom: 10px;
}

.team-label.win {
  background: rgba(var(--el-color-primary-rgb), 0.1);
  color: var(--el-color-primary);
}

.team-table:last-child {
  margin-bottom: 0;
}

@media (max-width: 768px) {
  .teams-comparison {
    flex-direction: column;
    gap: 20px;
  }

  .vs {
    margin: 10px 0;
  }
}
</style>
