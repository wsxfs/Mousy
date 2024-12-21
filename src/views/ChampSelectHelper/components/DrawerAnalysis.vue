<template>
  <div class="drawer-analysis">
    <div v-loading="loading" class="analysis-content">
      <template v-if="playersHistory">
        <el-table 
          :data="transformedMatchData" 
          class="history-table"
          size="small">
          <!-- 对局序号列 -->
          <el-table-column 
            label="对局"
            width="50"
            fixed="left"
            align="center">
            <template #default="scope">
              G{{ scope.row.gameIndex }}
            </template>
          </el-table-column>

          <!-- 玩家列 -->
          <el-table-column 
            v-for="player in playersHistory" 
            :key="player.playerName"
            :label="getDisplayName(player.playerName)"
            :class-name="player.teamId === 100 ? 'team-blue' : 'team-red'"
            width="66"
            align="center">
            
            <!-- 玩家名称（列头） -->
            <template #header>
              <div class="player-header">
                <div 
                  class="team-indicator" 
                  :class="player.teamId === 100 ? 'blue' : 'red'" />
                <el-tooltip 
                  :content="'点击复制: ' + player.playerName"
                  placement="top">
                  <div 
                    class="player-name clickable"
                    @click="copyPlayerName(player.playerName)">
                    {{ getDisplayName(player.playerName) }}
                  </div>
                </el-tooltip>
              </div>
            </template>

            <!-- 动态生成最近20场对局列 -->
            <template #default="scope">
              <template v-if="scope.row.playerMatches[player.playerName]">
                <div 
                  class="match-cell"
                  :class="{ 
                    'victory': scope.row.playerMatches[player.playerName].win,
                    'defeat': !scope.row.playerMatches[player.playerName].win
                  }">
                  <img 
                    :src="getResourceUrl('champion_icons', scope.row.playerMatches[player.playerName].championId)"
                    class="champion-icon"
                    :alt="scope.row.playerMatches[player.playerName].championId">
                  <div class="match-stats">
                    {{ scope.row.playerMatches[player.playerName].kills }}/
                    {{ scope.row.playerMatches[player.playerName].deaths }}/
                    {{ scope.row.playerMatches[player.playerName].assists }}
                  </div>
                </div>
              </template>
              <div v-else class="match-cell empty">
                -
              </div>
            </template>
          </el-table-column>
        </el-table>

        <!-- 添加查看更多按钮 -->
        <div class="view-more">
          <el-button 
            type="primary" 
            size="small"
            @click="handleViewDetailedAnalysis">
            查看更多对局
          </el-button>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useWebSocketStore } from '../../../stores/websocket'

const wsStore = useWebSocketStore()

interface MatchData {
  championId: number
  win: boolean
  kills: number
  deaths: number
  assists: number
}

interface PlayerHistory {
  playerName: string
  teamId: number
  matches: MatchData[]
}

const loading = ref(true)
const playersHistory = ref<PlayerHistory[]>([])
const gameResources = ref<Record<string, Record<number, string>>>({})

const getResourceUrl = (type: string, id: number): string => {
  const resources = gameResources.value[type]
  if (resources?.[id]) {
    return `data:image/png;base64,${resources[id]}`
  }
  return '/placeholder.png'
}

const loadGameResources = async (championIds: number[]) => {
  try {
    const resourceRequest = {
      champion_icons: Array.from(new Set(championIds))
    }

    const response = await axios.post(
      '/api/common/game_resource/batch_get_resources',
      resourceRequest
    )

    gameResources.value = response.data
  } catch (error) {
    console.error('加载游戏资源失败:', error)
  }
}

watch(
  () => [
    wsStore.syncFrontData.my_team_puuid_list,
    wsStore.syncFrontData.their_team_puuid_list
  ],
  async ([newMyTeam, newTheirTeam], [oldMyTeam, oldTheirTeam]) => {
    const oldPuuids = [...(oldMyTeam || []), ...(oldTheirTeam || [])]
    const newPuuids = [...(newMyTeam || []), ...(newTheirTeam || [])]
    
    if (JSON.stringify(oldPuuids) !== JSON.stringify(newPuuids)) {
      await fetchAnalysisData()
    }
  },
  { deep: true }
)

const fetchAnalysisData = async () => {
  try {
    loading.value = true
    const myTeam = wsStore.syncFrontData.my_team_puuid_list || []
    
    if (myTeam.length === 0) {
      playersHistory.value = []
      return
    }

    const allPuuids = myTeam
    const formData = new FormData()
    allPuuids.forEach(puuid => {
      formData.append('puuid_list', puuid)
    })
    formData.append('beg_index', '0')
    formData.append('end_index', '10')

    const response = await axios.post('/api/match_history/get_batch_match_history', formData)
    
    const playerHistoryData = await Promise.all(
      allPuuids.map(async (puuid) => {
        const matchHistory = response.data[puuid]
        if (!matchHistory?.games?.games?.length) {
          return {
            playerName: '未知玩家',
            teamId: 100,
            matches: []
          }
        }

        const games = matchHistory.games.games
        const matches = games.map((game: any) => {
          const participant = game.participants.find(
            (p: any) => game.participantIdentities.find(
              (pi: any) => pi.player.puuid === puuid
            )?.participantId === p.participantId
          )

          return {
            championId: participant.championId,
            win: participant.stats.win,
            kills: participant.stats.kills,
            deaths: participant.stats.deaths,
            assists: participant.stats.assists
          }
        })

        const playerIdentity = games[0]?.participantIdentities.find(
          (pi: any) => pi.player.puuid === puuid
        )

        return {
          playerName: `${playerIdentity?.player.gameName}#${playerIdentity?.player.tagLine}`,
          teamId: 100,
          matches
        }
      })
    )

    playersHistory.value = playerHistoryData

    const championIds = playersHistory.value.flatMap(player => 
      player.matches.map(match => match.championId)
    )
    
    await loadGameResources(championIds)
  } catch (error) {
    console.error('获取对局分析数据失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchAnalysisData()
})

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

const transformedMatchData = computed(() => {
  if (!playersHistory.value?.length) return []
  
  const maxGames = 10
  const transformedData = []

  for (let i = 0; i < maxGames; i++) {
    const gameData = {
      gameIndex: i + 1,
      playerMatches: {} as Record<string, MatchData>
    }

    playersHistory.value.forEach(player => {
      if (player.matches[i]) {
        gameData.playerMatches[player.playerName] = player.matches[i]
      }
    })

    transformedData.push(gameData)
  }

  return transformedData
})

const handleViewDetailedAnalysis = () => {
  window.electron.ipcRenderer.send('open-main-window', {
    route: '/game-analysis',
    focusWindow: true
  })
}
</script>

<style scoped>
.drawer-analysis {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.analysis-content {
  flex: 1;
  overflow: auto;
}

.history-table {
  width: 100%;
  font-size: 12px;
}

.player-info {
  display: flex;
  align-items: center;
  gap: 6px;
}

.team-indicator {
  width: 3px;
  height: 16px;
  border-radius: 2px;
}

.team-indicator.blue {
  background-color: var(--el-color-primary);
}

.team-indicator.red {
  background-color: var(--el-color-danger);
}

.match-cell {
  padding: 1px;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1px;
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
  width: 24px;
  height: 24px;
  border-radius: 12px;
  border: 1px solid var(--el-border-color);
}

.match-stats {
  font-size: 10px;
  color: var(--el-text-color-regular);
  margin: -5px 0; /* 添加负的上下边距来缩短间距 */
}

.team-blue {
  background-color: rgba(var(--el-color-primary-rgb), 0.1);
}

.team-red {
  background-color: rgba(var(--el-color-danger-rgb), 0.1);
}

:deep(.el-table .cell) {
  padding: 1px !important;
}

.player-name.clickable {
  cursor: pointer;
  font-size: 12px;
  &:hover {
    color: var(--el-color-primary);
  }
}

:deep(.el-table__row) {
  height: 36px;
}

.player-header {
  display: flex;
  align-items: center;
  gap: 6px;
  justify-content: center;
}

:deep(.team-blue) {
  background-color: rgba(var(--el-color-primary-rgb), 0.1);
}

:deep(.team-red) {
  background-color: rgba(var(--el-color-danger-rgb), 0.1);
}

.view-more {
  padding: 5px;
  display: flex;
  justify-content: center;
  margin-top: 0px;
}
</style> 