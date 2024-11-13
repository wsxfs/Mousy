<template>
  <div class="match-history-container">
    <div class="content-wrapper">
      <div class="filter-section">
        <el-card>
          <template #header>
            <div class="filter-header">筛选条件</div>
          </template>
          
          <div class="filter-content">
            <div class="filter-groups-wrapper">
              <!-- 游戏模式筛选 -->
              <div class="filter-group" v-if="Object.keys(availableGameModes).length">
                <div class="filter-label">游戏模式：</div>
                <el-checkbox-group v-model="selectedGameModes">
                  <el-checkbox 
                    v-for="(name, mode) in availableGameModes" 
                    :key="mode" 
                    :label="mode"
                  >
                    {{ name }}
                  </el-checkbox>
                </el-checkbox-group>
              </div>
              
              <!-- 地图筛选 -->
              <div class="filter-group" v-if="Object.keys(availableMapIds).length">
                <div class="filter-label">地图：</div>
                <el-checkbox-group v-model="selectedMapIds">
                  <el-checkbox 
                    v-for="(name, id) in availableMapIds" 
                    :key="id" 
                    :label="Number(id)"
                  >
                    {{ name }}
                  </el-checkbox>
                </el-checkbox-group>
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <match-history-list
        :matches="filteredMatches"
        :loading="loading"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import MatchHistoryList from '../components/MatchHistoryList.vue'

// 添加 Game 接口定义
interface Game {
  id?: number;
  gameCreation: number;
  gameDuration: number;
  gameMode: string;
  mapId: number;
  participants: any[];
  participantIdentities: any[];
  teams: any[];
}

// 基础状态
const matches = ref<Game[]>([])
const loading = ref(false)

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
const availableGameModes = computed(() => {
  const modes = new Set(matches.value.map(match => match.gameMode))
  const availableModes: Record<string, string> = {}
  modes.forEach(mode => {
    if (gameModes.value[mode]) {
      availableModes[mode] = gameModes.value[mode]
    }
  })
  return availableModes
})

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
  max-width: 1000px;
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
  font-weight: bold;
}

.filter-content {
  width: 100%;
}

.filter-groups-wrapper {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  width: 100%;
}

.filter-group {
  display: flex;
  gap: 12px;
  align-items: center;
  min-width: 200px;
  flex: 1;
}

.filter-label {
  white-space: nowrap;
  color: var(--el-text-color-regular);
  min-width: 80px;
  line-height: 32px;
  height: 32px;
  display: flex;
  align-items: center;
}

:deep(.el-checkbox-group) {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  flex: 1;
  align-items: center;
}

:deep(.el-checkbox) {
  margin-right: 0;
  margin-bottom: 0;
  height: 32px;
  display: flex;
  align-items: center;
}
</style>