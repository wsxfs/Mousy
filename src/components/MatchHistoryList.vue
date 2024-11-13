<template>
  <div class="match-history">
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
            <img :src="getResourceUrl('item_icons', Number(game.participants[0].stats[`item${i-1}` as keyof PlayerStats]))"
                 :alt="String(game.participants[0].stats[`item${i-1}` as keyof PlayerStats])">
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

// 接口定义
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
}

interface Team {
  teamId: number
  win: string
}

interface Game {
  gameCreation: number
  gameDuration: number
  gameMode: string
  participants: Participant[]
  participantIdentities: ParticipantIdentity[]
  teams: Team[]
}

interface ResourceResponse {
  champion_icons?: Record<number, string>
  item_icons?: Record<number, string>
  spell_icons?: Record<number, string>
}

// Props 定义
const props = defineProps<{
  matches: Game[]
  loading?: boolean
}>()

// 状态
const gameResources = ref<ResourceResponse>({})

// 工具函数
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

const formatDuration = (seconds: number): string => {
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  return `${minutes}分${remainingSeconds}秒`
}

const getGameResult = (game: Game, participantId: number): 'victory' | 'defeat' => {
  const participant = game.participants.find(p => p.participantId === participantId)
  if (!participant) return 'defeat'
  const team = game.teams.find(t => t.teamId === participant.teamId)
  return team?.win === 'Win' ? 'victory' : 'defeat'
}

const getResourceUrl = (
  type: keyof ResourceResponse, 
  id: number | string
): string => {
  const resources = gameResources.value[type] as Record<string | number, string>
  if (resources?.[id]) {
    return `data:image/png;base64,${resources[id]}`
  }
  return '/placeholder.png'
}

// 资源加载
const loadGameResources = async (games: Game[]) => {
  try {
    const resourceRequest = {
      champion_icons: [] as number[],
      spell_icons: [] as number[],
      item_icons: [] as number[]
    }
    
    games.forEach(game => {
      const participant = game.participants[0]
      
      if (!resourceRequest.champion_icons.includes(participant.championId)) {
        resourceRequest.champion_icons.push(participant.championId)
      }
      
      [participant.spell1Id, participant.spell2Id].forEach(spellId => {
        if (!resourceRequest.spell_icons.includes(spellId)) {
          resourceRequest.spell_icons.push(spellId)
        }
      })
      
      for (let i = 0; i < 7; i++) {
        const itemId = participant.stats[`item${i}` as keyof PlayerStats]
        if (typeof itemId === 'number') {
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

// 监听 matches 变化
watch(() => props.matches, (newMatches) => {
  if (newMatches.length > 0) {
    loadGameResources(newMatches)
  }
}, { immediate: true })
</script>

<style scoped>
.match-history {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  background-color: var(--el-bg-color);
  min-height: 100%;
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
  flex: 0.8;
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
  flex: 0.6;
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
  gap: 3px;
  align-items: center;
  justify-content: center;
  min-height: 40px;
}

.items img {
  width: 32px;
  height: 32px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style> 