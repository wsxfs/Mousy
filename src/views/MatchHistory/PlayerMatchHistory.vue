<template>
    <div class="player-match-history">
      <div class="header">
        <div class="header-content">
          <div class="header-title-group">
            <el-button 
              v-if="playerName !== '我'"
              type="primary" 
              size="small" 
              @click="$emit('back')"
              :icon="ArrowLeft"
            >
              返回我的主页
            </el-button>
          </div>
        </div>
      </div>
      
      <div class="content-wrapper">
        <!-- 用户信息卡片 -->
        <el-affix :offset="0" @change="handleAffixChange">
          <div class="user-info-section">
            <el-card>
              <div class="user-info" :class="{ 'affixed': isAffixed }">
                <div class="user-avatar-wrapper">
                  <el-progress
                    type="dashboard"
                    :percentage="levelProgress"
                    :width="90"
                    :stroke-width="3"
                    class="level-progress"
                  />
                  <div class="user-avatar">
                    <el-image 
                      :src="profileIconUrl"
                      :alt="summoner.game_name"
                      class="avatar-image"
                    >
                      <template #error>
                        <div class="image-error">
                          <el-icon><Picture /></el-icon>
                        </div>
                      </template>
                    </el-image>
                  </div>
                  <div class="level-badge">{{ summoner.summoner_level }}</div>
                </div>
                <div class="user-details">
                  <div class="name-tag-group">
                    <div class="user-name">{{ summoner.game_name }}</div>
                    <div class="user-tag">#{{ summoner.tag_line }}</div>
                    <el-button 
                      link
                      type="primary"
                      size="small"
                      @click="copyGameId"
                    >
                      <el-icon><CopyDocument /></el-icon>
                    </el-button>
                  </div>
                </div>
                
                <!-- 添加回到顶部按钮 -->
                <div v-if="isAffixed" class="back-to-top">
                  <el-button
                    circle
                    type="primary"
                    @click="window.scrollTo({ top: 0, behavior: 'smooth' })"
                  >
                    <el-icon><ArrowUp /></el-icon>
                  </el-button>
                </div>
              </div>
            </el-card>
          </div>
        </el-affix>

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
                    @click="fetchPlayerMatchHistory"
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
        
        <match-history-list
          :matches="filteredMatches"
          :loading="loading"
          @match-click="handleMatchClick"
        />
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, onMounted, computed, watch } from 'vue'
  import axios from 'axios'
  import { ElMessage } from 'element-plus'
  import MatchHistoryList from './MatchHistoryList.vue'
  import type { Game } from './match'
  import { Refresh, ArrowLeft, Picture, CopyDocument, ArrowUp } from '@element-plus/icons-vue'
  
  const props = defineProps<{
    puuid: string
    playerName: string
  }>()
  
  const emit = defineEmits<{
    (e: 'match-click', gameId: number): void
    (e: 'back'): void
  }>()
  
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
  
  // 计算属性
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
  
  const filteredMatches = computed(() => {
    return matches.value.filter(match => {
      const gameModeMatch = selectedGameModes.value.length === 0 || 
                           selectedGameModes.value.includes(match.gameMode)
      const mapMatch = selectedMapIds.value.length === 0 || 
                      selectedMapIds.value.includes(match.mapId)
      return gameModeMatch && mapMatch
    })
  })
  
  const hasActiveFilters = computed(() => {
    return selectedGameModes.value.length > 0 || selectedMapIds.value.length > 0
  })
  
  // 统计数据计算
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
  
  // 清除筛选
  const clearFilters = () => {
    selectedGameModes.value = []
    selectedMapIds.value = []
  }
  
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
  
  const fetchPlayerMatchHistory = async () => {
    try {
      loading.value = true
      const params = new URLSearchParams()
      
      if (props.puuid) {
        params.append('puuid', props.puuid)
      }
      
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
      } else {
        matches.value = []
        ElMessage.warning('没有找到对局记录')
      }
    } catch (error) {
      ElMessage.error('获取对局历史失败')
      console.error('获取对局历史失败:', error)
    } finally {
      loading.value = false
    }
  }
  
  const handleMatchClick = (gameId: number) => {
    emit('match-click', gameId)
  }
  
  // 添加召唤师信息接口
  interface Summoner {
    game_name: string
    puuid: string
    accountId: number
    summoner_id: number
    tag_line: string
    summoner_level: number
    xp_since_last_level: number
    xp_until_next_level: number
    profileIconId: number
  }
  
  // 添加召唤师信息状态
  const summoner = ref<Summoner>({
    game_name: '',
    puuid: '',
    accountId: 0,
    summoner_id: 0,
    tag_line: '',
    summoner_level: 0,
    xp_since_last_level: 0,
    xp_until_next_level: 0,
    profileIconId: 1
  })
  
  // 添加头像URL的计算属性
  const profileIconUrl = ref('')
  
  // 修改获取头像的方法
  const fetchProfileIcon = async () => {
    try {
      const response = await axios.get(
        `/api/common/game_resource/profile-icon/${summoner.value.profileIconId}`,
        { responseType: 'text' }
      )
      // 将base64数据转换为URL
      profileIconUrl.value = `data:image/jpeg;base64,${response.data}`
    } catch (error) {
      console.error('获取头像失败:', error)
    }
  }
  
  // 监听profileIconId的变化
  watch(() => summoner.value.profileIconId, (newId) => {
    if (newId) {
      fetchProfileIcon()
    }
  })
  
  // 在获取召唤师信息后获取头像
  const fetchSummonerInfo = async () => {
    try {
      const params = new URLSearchParams()
      if (props.puuid) {
        params.append('puuid', props.puuid)
      }
      
      const response = await axios.post(
        '/api/match_history/get_summoner_info',
        params,
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        }
      )
      
      if (response.data) {
        summoner.value = response.data
        // 获取到召唤师信息后立即获取头像
        fetchProfileIcon()
      }
    } catch (error) {
      ElMessage.error('获取召唤师信息失败')
      console.error('获取召唤师信息失败:', error)
    }
  }
  
  // 添加经验值进度计算
  const levelProgress = computed(() => {
    const total = summoner.value.xp_until_next_level
    const current = summoner.value.xp_since_last_level
    if (total === 0) return 0
    return Math.round((current / total) * 100)
  })
  
  // 添加复制功能
  const copyGameId = () => {
    const gameId = `${summoner.value.game_name}#${summoner.value.tag_line}`
    navigator.clipboard.writeText(gameId)
      .then(() => {
        ElMessage.success('游戏ID已复制到剪贴板')
      })
      .catch(() => {
        ElMessage.error('复制失败')
      })
  }
  
  // 在其他 ref 导入后添加
  const isAffixed = ref(false)
  
  // 添加处理固钉状态变化的方法
  const handleAffixChange = (value: boolean) => {
    isAffixed.value = value
  }
  
  onMounted(() => {
    fetchSummonerInfo()
    fetchPlayerMatchHistory()
    loadMapNames()
  })
  </script>
  
  <style scoped>
  .player-match-history {
    padding: 12px;
  }
  
  .header {
    margin-bottom: 12px;
  }
  
  .header-content {
    max-width: 800px;
    margin: 0 auto;
    width: 100%;
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
  }
  
  .header h3 {
    margin: 0;
    color: var(--el-text-color-primary);
  }
  
  .content-wrapper {
    max-width: 800px;
    margin: 0 auto;
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 12px;
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
    padding: 2px 0;
  }
  
  .filter-groups-wrapper {
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    gap: 12px 24px;
  }
  
  .filter-group {
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: 8px;
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
  
  .stats-section {
    margin: 8px 0;
  }
  
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
  }
  
  .stat-item {
    text-align: center;
    padding: 12px;
    border-radius: 8px;
    background: var(--el-bg-color-overlay);
    transition: all 0.2s;
    border: 1px solid var(--el-border-color-lighter);
  }
  
  .stat-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  }
  
  .stat-value {
    font-size: 24px;
    font-weight: 700;
    color: var(--el-color-primary);
    margin-bottom: 4px;
    line-height: 1;
  }
  
  .stat-label {
    font-size: 13px;
    color: var(--el-text-color-secondary);
  }
  
  .filter-header-left {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  
  :deep(.el-icon) {
    margin-right: 4px;
  }
  
  /* 响应式样式 */
  @media screen and (max-width: 768px) {
    .filter-groups-wrapper {
      flex-direction: column;
      gap: 16px;
    }
    
    .filter-group {
      flex-direction: column;
      align-items: flex-start;
      min-width: unset;
      gap: 6px;
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
    
    .stats-grid {
      grid-template-columns: repeat(2, 1fr);
      gap: 8px;
    }
    
    .stat-item {
      padding: 8px;
    }
    
    .stat-value {
      font-size: 20px;
    }
  }
  
  .header-title-group {
    display: flex;
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  /* 添加用户信息卡片样式 */
  .user-info-section {
    margin-bottom: 12px;
  }
  
  .user-info {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 4px;
    justify-content: center;
    transition: all 0.3s ease;
  }
  
  /* 添加固钉状态的样式 */
  .user-info.affixed {
    justify-content: flex-start;
    padding-left: 24px;
    position: relative;
  }
  
  .user-avatar-wrapper {
    position: relative;
    width: 90px;
    height: 90px;
    display: flex;
    justify-content: center;
    align-items: center;
  }
  
  .level-progress {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
  }
  
  .user-avatar {
    position: relative;
    width: 80px;
    height: 80px;
    z-index: 1;
  }
  
  .avatar-image {
    width: 100%;
    height: 100%;
    border-radius: 50%;
    object-fit: cover;
  }
  
  .level-badge {
    position: absolute;
    bottom: -8px;
    left: 50%;
    transform: translateX(-50%);
    background: var(--el-color-primary);
    color: white;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: bold;
    z-index: 2;
  }
  
  :deep(.el-progress__text) {
    display: none;
  }
  
  :deep(.el-progress-dashboard) {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
  }
  
  .user-details {
    display: flex;
    flex-direction: column;
    gap: 4px;
    align-items: center;
  }
  
  .name-tag-group {
    display: flex;
    align-items: center;
    gap: 16px;
    justify-content: center;
  }
  
  .user-name {
    font-size: 24px;
    font-weight: bold;
    color: var(--el-text-color-primary);
  }
  
  .user-tag {
    font-size: 20px;
    color: var(--el-text-color-secondary);
  }
  
  .image-error {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    height: 100%;
    background: var(--el-fill-color-light);
    color: var(--el-text-color-secondary);
  }
  
  /* 响应式调整 */
  @media screen and (max-width: 768px) {
    .user-info {
      padding: 12px;
      flex-direction: column;
      gap: 12px;
    }
    
    .user-avatar-wrapper {
      width: 70px;
      height: 70px;
    }
    
    .user-avatar {
      width: 60px;
      height: 60px;
    }
    
    .level-badge {
      font-size: 10px;
      padding: 1px 6px;
    }
    
    .user-name {
      font-size: 20px;
    }
    
    .user-tag {
      font-size: 12px;
    }
  }
  
  .name-tag-group {
    display: flex;
    align-items: center;
    gap: 16px;
  }
  
  :deep(.el-button) {
    padding: 0;
    height: auto;
  }
  
  :deep(.el-icon) {
    font-size: 16px;
  }
  
  /* 响应式调整 */
  @media screen and (max-width: 768px) {
    :deep(.el-icon) {
      font-size: 14px;
    }
  }
  
  /* 添加回到顶部按钮样式 */
  .back-to-top {
    position: absolute;
    right: 24px;
    top: 50%;
    transform: translateY(-50%);
    opacity: 0;
    transition: opacity 0.3s ease;
  }
  
  .user-info.affixed .back-to-top {
    opacity: 1;
  }
  
  /* 响应式调整 */
  @media screen and (max-width: 768px) {
    .user-info.affixed {
      padding-left: 12px;
    }
    
    .back-to-top {
      right: 12px;
    }
    
    .user-info.affixed {
      flex-direction: row;
    }
  }
  </style>