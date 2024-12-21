<template>
  <div class="drawer-analysis">
    <div v-loading="loading" class="analysis-content">
      <template v-if="playersHistory">
        <el-table 
          :data="playersHistory" 
          class="history-table"
          :show-header="false"
          size="small"
          :row-class-name="getRowClassName">
          <!-- 玩家信息列 -->
          <el-table-column 
            label="" 
            width="80" 
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

          <!-- 最近10场对局 -->
          <el-table-column 
            v-for="index in 10" 
            :key="index"
            :label="`G${index}`"
            width="60"
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
                  }">
                  <img 
                    :src="getResourceUrl('champion_icons', scope.row.matches[index - 1].championId)"
                    class="champion-icon"
                    :alt="scope.row.matches[index - 1].championId">
                  <div class="match-stats">
                    {{ scope.row.matches[index - 1].kills }}/{{ scope.row.matches[index - 1].deaths }}/{{ scope.row.matches[index - 1].assists }}
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
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
    const theirTeam = wsStore.syncFrontData.their_team_puuid_list || []
    
    if (myTeam.length === 0 && theirTeam.length === 0) {
      playersHistory.value = []
      return
    }

    const allPuuids = [...myTeam, ...theirTeam]
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
            teamId: wsStore.syncFrontData.my_team_puuid_list?.includes(puuid) ? 100 : 200,
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
          teamId: wsStore.syncFrontData.my_team_puuid_list?.includes(puuid) ? 100 : 200,
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
  padding: 2px;
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
}

.team-blue {
  background-color: rgba(var(--el-color-primary-rgb), 0.1);
}

.team-red {
  background-color: rgba(var(--el-color-danger-rgb), 0.1);
}

:deep(.el-table .cell) {
  padding: 4px !important;
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
</style> 