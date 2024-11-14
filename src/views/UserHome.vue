<template>
  <div class="user-home">
    <!-- 基本信息卡片 -->
    <el-card class="profile-card">
      <div class="profile-header">
        <div class="profile-avatar">
          <el-avatar 
            :size="80" 
            :src="userInfo.profileIconUrl" 
            class="avatar"
          />
          <span class="level">{{ userInfo.summonerLevel }}</span>
        </div>
        <div class="profile-info">
          <h2>{{ userInfo.gameName }}</h2>
          <p class="tagline">#{{ userInfo.tagLine }}</p>
          <div class="rank-info" v-if="userInfo.rank">
            <img :src="getRankIcon(userInfo.rank.tier)" class="rank-icon">
            <span>{{ userInfo.rank.tier }} {{ userInfo.rank.rank }}</span>
            <span class="lp">{{ userInfo.rank.leaguePoints }} LP</span>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 数据统计卡片 -->
    <el-card class="stats-card">
      <template #header>
        <div class="card-header">
          <span>近期数据统计</span>
          <el-select v-model="selectedQueue" placeholder="选择游戏模式">
            <el-option
              v-for="queue in queueTypes"
              :key="queue.id"
              :label="queue.name"
              :value="queue.id"
            />
          </el-select>
        </div>
      </template>
      
      <div class="stats-grid">
        <div class="stat-item">
          <div class="stat-value">{{ stats.totalGames }}</div>
          <div class="stat-label">总场次</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ stats.winRate }}%</div>
          <div class="stat-label">胜率</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ stats.avgKDA }}</div>
          <div class="stat-label">平均KDA</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ stats.avgCS }}</div>
          <div class="stat-label">场均补刀</div>
        </div>
      </div>

      <!-- 常用英雄统计 -->
      <div class="champions-stats">
        <h3>常用英雄</h3>
        <div class="champion-list">
          <div v-for="champion in stats.topChampions" 
               :key="champion.id" 
               class="champion-item">
            <img :src="champion.iconUrl" :alt="champion.name">
            <div class="champion-info">
              <div class="champion-name">{{ champion.name }}</div>
              <div class="champion-stats">
                <span>{{ champion.winRate }}% 胜率</span>
                <span>{{ champion.kda }} KDA</span>
                <span>{{ champion.games }}场</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

// 接口定义
interface UserRank {
  tier: string
  rank: string
  leaguePoints: number
}

interface UserInfo {
  gameName: string
  tagLine: string
  summonerLevel: number
  profileIconUrl: string
  rank?: UserRank
}

interface ChampionStats {
  id: number
  name: string
  iconUrl: string
  winRate: number
  kda: number
  games: number
}

interface Stats {
  totalGames: number
  winRate: number
  avgKDA: number
  avgCS: number
  topChampions: ChampionStats[]
}

interface QueueType {
  id: number
  name: string
}

// 状态定义
const userInfo = ref<UserInfo>({
  gameName: '',
  tagLine: '',
  summonerLevel: 0,
  profileIconUrl: ''
})

const stats = ref<Stats>({
  totalGames: 0,
  winRate: 0,
  avgKDA: 0,
  avgCS: 0,
  topChampions: []
})

const selectedQueue = ref(420) // 默认选择排位模式

const queueTypes = ref<QueueType[]>([
  { id: 420, name: '单双排位' },
  { id: 440, name: '灵活组排' },
  { id: 450, name: '大乱斗' },
  { id: 400, name: '匹配模式' }
])

// 获取段位图标
const getRankIcon = (tier: string): string => {
  return `/rank-icons/${tier.toLowerCase()}.png`
}

// 获取用户信息
const fetchUserInfo = async () => {
  try {
    const response = await axios.get('/api/user/info')
    userInfo.value = response.data
  } catch (error) {
    ElMessage.error('获取用户信息失败')
    console.error('获取用户信息失败:', error)
  }
}

// 获取数据统计
const fetchStats = async () => {
  try {
    const response = await axios.get(`/api/user/stats`, {
      params: {
        queue_id: selectedQueue.value
      }
    })
    stats.value = response.data
  } catch (error) {
    ElMessage.error('获取数据统计失败')
    console.error('获取数据统计失败:', error)
  }
}

// 监听游戏模式变化
watch(selectedQueue, () => {
  fetchStats()
})

onMounted(() => {
  fetchUserInfo()
  fetchStats()
})
</script>

<style scoped>
.user-home {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.profile-card {
  background: white;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 20px;
}

.profile-avatar {
  position: relative;
}

.avatar {
  border: 3px solid var(--el-color-primary);
}

.level {
  position: absolute;
  bottom: -5px;
  right: -5px;
  background: var(--el-color-primary);
  color: white;
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 12px;
}

.profile-info h2 {
  margin: 0;
  font-size: 24px;
}

.tagline {
  color: var(--el-text-color-secondary);
  margin: 4px 0;
}

.rank-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
}

.rank-icon {
  width: 24px;
  height: 24px;
}

.lp {
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 30px;
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

.champions-stats {
  margin-top: 20px;
}

.champion-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.champion-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
  border-radius: 8px;
  background: var(--el-fill-color-light);
}

.champion-item img {
  width: 48px;
  height: 48px;
  border-radius: 50%;
}

.champion-info {
  flex: 1;
}

.champion-name {
  font-weight: 500;
}

.champion-stats {
  display: flex;
  gap: 12px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .champion-stats {
    flex-direction: column;
    gap: 4px;
  }
}
</style>