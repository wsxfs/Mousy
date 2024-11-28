<template>
  <div class="match-history-container">
    <el-tabs v-model="activeTab" type="card" @tab-remove="removeTab">
      <!-- 对局列表标签页 -->
      <el-tab-pane name="match-list" :closable="false">
        <template #label>
          <el-icon><List /></el-icon>
        </template>
        
        <div class="content-wrapper">
          <!-- 筛选条件 -->
          <div class="filter-section">
            <el-card>
              <template #header>
                <div class="filter-header">
                  <div class="filter-header-left">
                    <span>筛选条件</span>
                    <el-button
                      :loading="loading"
                      link
                      type="primary"
                      @click="fetchMatchHistory"
                    >
                      <el-icon><Refresh /></el-icon>
                      刷新战绩
                    </el-button>
                  </div>
                  <el-button 
                    v-if="hasActiveFilters"
                    link
                    type="primary"
                    @click="clearFilters"
                  >
                    清除筛选
                  </el-button>
                </div>
              </template>
              
              <div class="filter-content">
                <div class="filter-groups-wrapper">
                  <div class="filter-group" v-if="Object.keys(availableGameModes).length">
                    <div class="filter-label">游戏模式:</div>
                    <div class="checkbox-wrapper">
                      <el-checkbox-group v-model="selectedGameModes">
                        <el-checkbox 
                          v-for="(name, mode) in availableGameModes" 
                          :key="mode" 
                          :label="mode"
                          class="filter-checkbox"
                        >
                          {{ name }}
                        </el-checkbox>
                      </el-checkbox-group>
                    </div>
                  </div>
                  
                  <div class="filter-group" v-if="Object.keys(availableMapIds).length">
                    <div class="filter-label">地图:</div>
                    <div class="checkbox-wrapper">
                      <el-checkbox-group v-model="selectedMapIds">
                        <el-checkbox 
                          v-for="(name, id) in availableMapIds" 
                          :key="id" 
                          :label="Number(id)"
                          class="filter-checkbox"
                        >
                          {{ name }}
                        </el-checkbox>
                      </el-checkbox-group>
                    </div>
                  </div>
                </div>
              </div>
            </el-card>
          </div>

          <!-- 数据统计 -->
          <div class="stats-section">
            <el-card>
              <div class="stats-grid">
                <div class="stat-item">
                  <div class="stat-value">{{ filteredMatches.length }}</div>
                  <div class="stat-label">筛选对局数</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ winRate }}%</div>
                  <div class="stat-label">胜率</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ avgKDA }}</div>
                  <div class="stat-label">平均KDA</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ avgDuration }}</div>
                  <div class="stat-label">平均时长</div>
                </div>
              </div>
            </el-card>
          </div>

          <!-- 对局列表 -->
          <match-history-list
            :matches="filteredMatches"
            :loading="loading"
            @match-click="handleMatchClick"
          />
        </div>
      </el-tab-pane>

      <!-- 动态对局详情标签页 -->
      <el-tab-pane
        v-for="item in matchTabs"
        :key="item.name"
        :label="item.title"
        :name="item.name"
        :closable="true"
      >
        <template v-if="item.gameId">
          <match-detail 
            :game-id="item.gameId"
            @back="handleBack"
            @player-click="handlePlayerClick"
          />
        </template>
        <template v-else-if="item.puuid">
          <player-match-history
            :puuid="item.puuid"
            :player-name="item.title"
            @match-click="handleMatchClick"
          />
        </template>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import MatchHistoryList from './MatchHistoryList.vue'
import { Refresh, List } from '@element-plus/icons-vue'
import MatchDetail from './MatchDetail.vue'
import type { Game, MatchTab, GameModeMap } from './match'
import PlayerMatchHistory from './PlayerMatchHistory.vue'

// 基础状态
const matches = ref<Game[]>([])
const loading = ref(false)
const activeTab = ref('match-list')
const matchTabs = ref<MatchTab[]>([])

// 添加游戏模式映射
const availableGameModes = computed(() => {
  const modes = new Set(matches.value.map(match => match.gameMode))
  const availableModes: GameModeMap = {}
  modes.forEach(mode => {
    if (gameModes.value[mode]) {
      availableModes[mode] = gameModes.value[mode]
    }
  })
  return availableModes
})

// 添加筛选相关的状态
const selectedGameModes = ref<string[]>([])
const selectedMapIds = ref<number[]>([])
const mapNames = ref<Record<number, string>>({})
const gameModes = ref<Record<string, string>>({
  'CLASSIC': '经典模式',
  'ARAM': '大乱斗',
  'URF': '无限火力',
  'ARURF': '随机无限火力',
  'ONEFORALL': '克隆大作战',
  'PRACTICETOOL': '训练模式',
  'NEXUSBLITZ': '闪电战',
  'TFT': '云顶之弈',
  'ULTBOOK': '终极魔典',
  'TUTORIAL': '新手教程'
})

// 计算实际存在的游戏模式和地图
const availableMapIds = computed(() => {
  const maps = new Set(matches.value.map(match => match.mapId))
  const availableMaps: Record<number, string> = {}
  maps.forEach(mapId => {
    if (mapNames.value[mapId]) {
      availableMaps[mapId] = mapNames.value[mapId]
    }
  })
  return availableMaps
})

// 获取地图名称
const loadMapNames = async () => {
  try {
    const response = await axios.get<Record<number, string>>('/api/common/game_resource/map_id2name')
    mapNames.value = response.data
  } catch (error) {
    ElMessage.error('加载地图名称失败')
    console.error('加载地图名称失败:', error)
  }
}

// 计算筛选后的对局列表
const filteredMatches = computed(() => {
  return matches.value.filter(match => {
    const gameModeMatch = selectedGameModes.value.length === 0 || 
                         selectedGameModes.value.includes(match.gameMode)
    const mapMatch = selectedMapIds.value.length === 0 || 
                    selectedMapIds.value.includes(match.mapId)
    return gameModeMatch && mapMatch
  })
})

console.log("filteredMatches:", filteredMatches)

// 获取对局历史
const fetchMatchHistory = async () => {
  try {
    loading.value = true
    const params = new URLSearchParams()
    params.append('beg_index', '0')
    params.append('end_index', '19')

    const response = await axios.post(
      '/api/match_history/get_match_history',
      params,
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }
    )
    
    if (response.data?.games?.games) {
      matches.value = response.data.games.games
    }
  } catch (error) {
    ElMessage.error('获取对局历史失败')
    console.error('获取对局历史失败:', error)
  } finally {
    loading.value = false
  }
}

// 添加清除筛选功能
const hasActiveFilters = computed(() => {
  return selectedGameModes.value.length > 0 || selectedMapIds.value.length > 0
})

const clearFilters = () => {
  selectedGameModes.value = []
  selectedMapIds.value = []
}

// 添加统计数据计算
const winRate = computed(() => {
  if (!filteredMatches.value.length) return 0
  const wins = filteredMatches.value.filter(match => 
    match.participants[0]?.stats?.win).length
  return ((wins / filteredMatches.value.length) * 100).toFixed(1)
})

const avgKDA = computed(() => {
  if (!filteredMatches.value.length) return '0.00'
  const kdas = filteredMatches.value.map(match => {
    const stats = match.participants[0]?.stats
    if (!stats) return 0
    const deaths = stats.deaths || 1
    return ((stats.kills + stats.assists) / deaths)
  })
  const avg = kdas.reduce((a, b) => a + b, 0) / kdas.length
  return avg.toFixed(2)
})

const avgDuration = computed(() => {
  if (!filteredMatches.value.length) return '0:00'
  const avg = filteredMatches.value.reduce((acc, match) => 
    acc + match.gameDuration, 0) / filteredMatches.value.length
  const minutes = Math.floor(avg / 60)
  const seconds = Math.floor(avg % 60)
  return `${minutes}:${seconds.toString().padStart(2, '0')}`
})

// 处理对局点击
const handleMatchClick = (gameId: number) => {
  const tabName = `match-${gameId}`
  
  if (!matchTabs.value.find(tab => tab.name === tabName)) {
    matchTabs.value.push({
      title: `对局 ${gameId}`,
      name: tabName,
      gameId: gameId
    })
  }
  
  activeTab.value = tabName
}

// 移除标签页
const removeTab = (tabName: string) => {
  const tabs = matchTabs.value
  let activeName = activeTab.value
  
  if (activeName === tabName) {
    tabs.forEach((tab, index) => {
      if (tab.name === tabName) {
        const nextTab = tabs[index + 1] || tabs[index - 1]
        if (nextTab) {
          activeName = nextTab.name
        } else {
          activeName = 'match-list'
        }
      }
    })
  }
  
  activeTab.value = activeName
  matchTabs.value = tabs.filter(tab => tab.name !== tabName)
}

// 返回列表
const handleBack = () => {
  activeTab.value = 'match-list'
}

// 添加处理玩家点击的函数
const handlePlayerClick = (puuid: string, playerName: string) => {
  const tabName = `player-${puuid}`
  
  // 如果标签页已存在，直接切换
  if (matchTabs.value.find(tab => tab.name === tabName)) {
    activeTab.value = tabName
    return
  }
  
  // 添加新标签页
  matchTabs.value.push({
    title: playerName,
    name: tabName,
    puuid
  })
  activeTab.value = tabName
  
  // 获取该玩家的对局历史
  fetchPlayerMatchHistory(puuid)
}

// 添加获取玩家对局历史的函数
const fetchPlayerMatchHistory = async (puuid: string) => {
  try {
    loading.value = true
    const params = new URLSearchParams()
    params.append('puuid', puuid)
    params.append('beg_index', '0')
    params.append('end_index', '19')

    const response = await axios.post(
      '/api/match_history/get_match_history',
      params,
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }
    )
    
    if (response.data?.games?.games) {
      matches.value = response.data.games.games
    }
  } catch (error) {
    ElMessage.error('获取对局历史失败')
    console.error('获取对局历史失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchMatchHistory()
  loadMapNames()
})
</script>

<style scoped>
.match-history-container {
  width: 100%;
  min-height: 100vh;
  background-color: var(--el-bg-color-page);
}

.content-wrapper {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.filter-section {
  width: 100%;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
}

.filter-content {
  padding: 4px 0;
}

.filter-groups-wrapper {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  gap: 16px 32px;
}

.filter-group {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 12px;
  min-width: 200px;
  flex: 1;
}

.filter-label {
  font-size: 15px;
  color: var(--el-text-color-primary);
  font-weight: 700;
  white-space: nowrap;
  letter-spacing: 0.5px;
}

.checkbox-wrapper {
  padding-left: 0;
  flex: 1;
}

:deep(.el-checkbox-group) {
  display: flex;
  flex-wrap: wrap;
  gap: 16px 24px;
}

.filter-checkbox {
  margin-right: 0 !important;
  margin-bottom: 0 !important;
}

:deep(.filter-checkbox .el-checkbox__label) {
  font-size: 13px;
  font-weight: 400;
  color: var(--el-text-color-secondary);
  opacity: 0.85;
}

@media screen and (max-width: 768px) {
  .filter-groups-wrapper {
    flex-direction: column;
    gap: 24px;
  }
  
  .filter-group {
    flex-direction: column;
    align-items: flex-start;
    min-width: unset;
    gap: 8px;
  }
  
  .checkbox-wrapper {
    width: 100%;
  }
  
  :deep(.el-checkbox-group) {
    gap: 12px 16px;
  }
  
  .filter-checkbox {
    min-width: calc(50% - 8px);
  }
}

.stats-section {
  width: 100%;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  padding: 8px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: var(--el-color-primary);
}

.stat-label {
  font-size: 14px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}

@media screen and (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }
}

.filter-header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

:deep(.el-icon) {
  margin-right: 4px;
}
</style>