<template>
  <div class="analysis-content" v-loading="loading">
    <template v-if="playersHistory">
      <el-table 
        :data="playersHistory" 
        class="history-table"
        :show-header="false"
        :row-class-name="getRowClassName">
        <!-- 玩家信息列 -->
        <el-table-column 
          label="" 
          width="100" 
          fixed="left"
          header-align="center">
          <template #default="scope">
            <div class="player-info">
              <div 
                class="team-indicator" 
                :class="scope.row.teamId === 100 ? 'blue' : 'red'" />
              <el-tooltip 
                :content="'点击复制: ' + scope.row.playerName"
                placement="top">
                <div 
                  class="player-name clickable"
                  @click="copyPlayerName(scope.row.playerName)">
                  {{ getDisplayName(scope.row.playerName) }}
                </div>
              </el-tooltip>
            </div>
          </template>
        </el-table-column>

        <!-- 动态生成最近20场对局列 -->
        <el-table-column 
          v-for="index in 20" 
          :key="index"
          :label="`G${index}`"
          width="80"  
          align="center">
          <template #default="scope">
            <el-tooltip 
              v-if="scope.row.matches[index - 1]"
              :content="`KDA: ${scope.row.matches[index - 1].kills}/${scope.row.matches[index - 1].deaths}/${scope.row.matches[index - 1].assists}`"
              placement="top">
              <div 
                class="match-cell"
                :class="{ 
                  'victory': scope.row.matches[index - 1].win,
                  'defeat': !scope.row.matches[index - 1].win
                }"
                @click="handleMatchClick(scope.row.matches[index - 1])">
                <img 
                  :src="getResourceUrl('champion_icons', scope.row.matches[index - 1].championId)"
                  class="champion-icon"
                  :alt="scope.row.matches[index - 1].championId">
                <div class="match-stats">
                  {{ scope.row.matches[index - 1].kills }}/
                  {{ scope.row.matches[index - 1].deaths }}/
                  {{ scope.row.matches[index - 1].assists }}
                </div>
              </div>
            </el-tooltip>
            <div v-else class="match-cell empty">
              -
            </div>
          </template>
        </el-table-column>
      </el-table>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'
import type { ResourceResponse } from '../../MatchHistory/match'
import { ElMessage } from 'element-plus'
import { useWebSocketStore } from '../../../stores/websocket'
import { useRouter } from 'vue-router'

const props = defineProps<{
  myTeamPuuids: string[]
  theirTeamPuuids: string[]
}>()

interface MatchData {
  championId: number
  win: boolean
  kills: number
  deaths: number
  assists: number
  gameId: string
}

interface PlayerHistory {
  playerName: string
  teamId: number
  matches: MatchData[]
}

const wsStore = useWebSocketStore()
const loading = ref(false)
const playersHistory = ref<PlayerHistory[]>([])
const gameResources = ref<ResourceResponse>({})
const isCurrentGame = ref(false)
const router = useRouter()

// 获取资源URL的工具函数
const getResourceUrl = (type: keyof ResourceResponse, id: number): string => {
  const resources = gameResources.value[type]
  if (resources?.[id]) {
    return `data:image/png;base64,${resources[id]}`
  }
  return '/placeholder.png'
}

// 加载游戏资源
const loadGameResources = async (championIds: number[]) => {
  try {
    const resourceRequest = {
      champion_icons: Array.from(new Set(championIds))
    }

    const response = await axios.post<ResourceResponse>(
      '/api/common/game_resource/batch_get_resources',
      resourceRequest
    )

    gameResources.value = response.data
  } catch (error) {
    console.error('加载游戏资源失败:', error)
  }
}

// 检查是否为当前对局
const checkIfCurrentGame = () => {
  const currentMyTeam = wsStore.syncFrontData.my_team_puuid_list || []
  const currentTheirTeam = wsStore.syncFrontData.their_team_puuid_list || []
  
  return props.myTeamPuuids.every(puuid => currentMyTeam.includes(puuid)) &&
         props.theirTeamPuuids.every(puuid => currentTheirTeam.includes(puuid))
}

// 监听战绩数据变化
watch(
  [
    () => wsStore.syncFrontData.my_team_match_history,
    () => wsStore.syncFrontData.their_team_match_history
  ],
  async ([newMyTeamHistory, newTheirTeamHistory]) => {
    // 只有当是当前对局时才使用 WebSocket 数据
    if (isCurrentGame.value && (newMyTeamHistory || newTheirTeamHistory)) {
      await transformMatchHistories(newMyTeamHistory, newTheirTeamHistory)
    }
  },
  { immediate: true, deep: true }
)

// 获取战绩数据
const fetchAnalysisData = async () => {
  loading.value = true
  try {
    // 检查是否为当前对局
    isCurrentGame.value = checkIfCurrentGame()
    
    if (isCurrentGame.value) {
      // 使用 WebSocket 数据
      await transformMatchHistories(
        wsStore.syncFrontData.my_team_match_history,
        wsStore.syncFrontData.their_team_match_history
      )
    } else {
      // 从后端获取数据
      const params = new URLSearchParams()
      const allPuuids = [...props.myTeamPuuids, ...props.theirTeamPuuids]
      allPuuids.forEach(puuid => {
        params.append('puuid_list', puuid)
      })
      params.append('beg_index', '0')
      params.append('end_index', '10')
      
      const response = await axios.post(
        '/api/match_history/get_batch_match_history',
        params,
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        }
      )

      console.log("查询战绩数据response:", response.data)
      // 转换数据格式
      const myTeamHistory: Record<string, any> = {}
      const theirTeamHistory: Record<string, any> = {}
      
      props.myTeamPuuids.forEach(puuid => {
        myTeamHistory[puuid] = response.data[puuid]
      })
      
      props.theirTeamPuuids.forEach(puuid => {
        theirTeamHistory[puuid] = response.data[puuid]
      })
      
      await transformMatchHistories(myTeamHistory, theirTeamHistory)
      console.log("转换后的战绩数据:", playersHistory.value)
    }
  } catch (error) {
    console.error('获取战绩数据失败:', error)
    ElMessage.error('获取战绩数据失败')
  } finally {
    loading.value = false
  }
}

// 转换战绩数据
const transformMatchHistories = async (
  myTeamHistory: Record<string, any> | null,
  theirTeamHistory: Record<string, any> | null
) => {
  console.log("转换战绩数据myTeamHistory:", myTeamHistory)
  console.log("转换战绩数据theirTeamHistory:", theirTeamHistory)
  const allPlayers: PlayerHistory[] = []
  const championIds: number[] = []

  // 处理我方战绩
  if (myTeamHistory) {
    for (const puuid of props.myTeamPuuids) {
      const history = myTeamHistory[puuid]
      if (history?.games?.games) {
        // 获取游戏名称和标签
        const player = history.games.games[0]?.participantIdentities[0]?.player
        const playerName = player ? 
          `${player.gameName || ''}${player.tagLine ? '#' + player.tagLine : ''}` : 
          puuid
        const matches = history.games.games.map((game: any) => {
          const championId = game.participants[0].championId
          championIds.push(championId)
          return {
            championId,
            win: game.participants[0].stats.win,
            kills: game.participants[0].stats.kills,
            deaths: game.participants[0].stats.deaths,
            assists: game.participants[0].stats.assists,
            gameId: game.gameId
          }
        })
        allPlayers.push({
          playerName,
          teamId: 100,
          matches
        })
      }
    }
  }

  // 处理敌方战绩
  if (theirTeamHistory) {
    for (const puuid of props.theirTeamPuuids) {
      const history = theirTeamHistory[puuid]
      if (history?.games?.games) {
        const player = history.games.games[0]?.participantIdentities[0]?.player
        const playerName = player ? 
          `${player.gameName || ''}${player.tagLine ? '#' + player.tagLine : ''}` : 
          puuid
        const matches = history.games.games.map((game: any) => {
          const championId = game.participants[0].championId
          championIds.push(championId)
          return {
            championId: game.participants[0].championId,
            win: game.participants[0].stats.win,
            kills: game.participants[0].stats.kills,
            deaths: game.participants[0].stats.deaths,
            assists: game.participants[0].stats.assists,
            gameId: game.gameId
          }
        })
        allPlayers.push({
          playerName,
          teamId: 200,
          matches
        })
      }
    }
  }

  playersHistory.value = allPlayers
  await loadGameResources(championIds)
}

// 工具函数
const getRowClassName = ({ row }: { row: PlayerHistory }) => {
  return row.teamId === 100 ? 'team-blue' : 'team-red'
}

const getDisplayName = (fullName: string): string => {
  return fullName.split('#')[0]
}

const copyPlayerName = async (fullName: string) => {
  try {
    await navigator.clipboard.writeText(fullName)
    ElMessage.success('玩家名称已复制到剪贴板')
  } catch (err) {
    console.error('复制失败:', err)
    ElMessage.error('复制失败')
  }
}

// 处理对局点击
const handleMatchClick = (match: MatchData) => {
  // 获取对局ID
  const gameId = match.gameId
  if (gameId) {
    // 使用 router 跳转到对局详情页，并替换当前历史记录
    router.push({
      path: '/match-history',
      query: { gameId }
    })
  }
}

onMounted(() => {
  fetchAnalysisData()
})

// 暴露方法给父组件
defineExpose({
  fetchAnalysisData
})
</script>

<style scoped>
.analysis-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header-controls {
  flex-shrink: 0;
}

.history-table {
  flex: 1;
  overflow: auto;
  width: 100%;
  border-spacing: 0;
  border-collapse: collapse;
}

.player-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.team-indicator {
  width: 4px;
  height: 20px;
  border-radius: 2px;
}

.team-indicator.blue {
  background-color: var(--el-color-primary);
}

.team-indicator.red {
  background-color: var(--el-color-danger);
}

.match-cell {
  padding: 1px 2px;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0px;
  margin: 0;
}

.match-cell.victory {
  background-color: rgba(var(--el-color-success-rgb), 0.1);
  border: 1px solid var(--el-color-success-light-5);
}

.match-cell.defeat {
  background-color: rgba(var(--el-color-danger-rgb), 0.1);
  border: 1px solid var(--el-color-danger-light-5);
}

.match-cell.empty {
  color: var(--el-text-color-secondary);
}

.champion-icon {
  width: 40px;
  height: 40px;
  border-radius: 20px;
  border: 1px solid var(--el-border-color);
  margin-bottom: 1px;
}

.match-stats {
  font-size: 11px;
  color: var(--el-text-color-regular);
  margin-top: 0;
  line-height: 1;
}

.team-blue {
  background-color: rgba(var(--el-color-primary-rgb), 0.1);
}

.team-red {
  background-color: rgba(var(--el-color-danger-rgb), 0.1);
}

:deep(.el-table .cell) {
  padding: 0 2px !important;
  line-height: 1.2;
}

:deep(.el-table td) {
  padding: 4px 0;
}

.player-name.clickable {
  cursor: pointer;
  &:hover {
    color: var(--el-color-primary);
  }
}

:deep(.el-table__row) {
  height: 44px;
}

:deep(.el-table__header-wrapper) {
  display: none;
}
</style> 