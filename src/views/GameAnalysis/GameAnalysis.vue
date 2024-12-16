<template>
    <div class="game-analysis">
      <div class="header-controls">
        <el-button 
          type="primary" 
          size="small" 
          @click="$emit('back')"
          :icon="ArrowLeft">
          返回对局详情
        </el-button>
      </div>
  
      <!-- 加载状态 -->
      <div v-loading="loading" class="analysis-content">
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
              width="90"
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
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, onMounted, watch } from 'vue'
  import { ArrowLeft } from '@element-plus/icons-vue'
  import axios from 'axios'
  import type { ResourceResponse } from '../MatchHistory/match'
  import { useWebSocketStore } from '../../stores/websocket'
  import { ElMessage } from 'element-plus'
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
    teamId: number  // 100 for blue, 200 for red
    matches: MatchData[]
  }
  
//   const props = defineProps<{
//     gameId: number
//   }>()
  
  const loading = ref(true)
  const playersHistory = ref<PlayerHistory[]>([])
  const gameResources = ref<ResourceResponse>({})
  
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
  
  // 监听队伍成员变化
  watch(
    () => [
      wsStore.syncFrontData.my_team_puuid_list,
      wsStore.syncFrontData.their_team_puuid_list
    ],
    async ([newMyTeam, newTheirTeam], [oldMyTeam, oldTheirTeam]) => {
      // 检查是否有实际变化
      const oldPuuids = [...(oldMyTeam || []), ...(oldTheirTeam || [])]
      const newPuuids = [...(newMyTeam || []), ...(newTheirTeam || [])]
      
      if (JSON.stringify(oldPuuids) !== JSON.stringify(newPuuids)) {
        console.log('队伍成员发生变化，重新获取数据')
        await fetchAnalysisData()
      }
    },
    { deep: true }
  )
  
  // 获取对局成分分析数据
  const fetchAnalysisData = async () => {
    try {
      loading.value = true
      const myTeam = wsStore.syncFrontData.my_team_puuid_list || []
      const theirTeam = wsStore.syncFrontData.their_team_puuid_list || []
      
      // 如果两个队伍都没有数据，则清空显示并返回
      if (myTeam.length === 0 && theirTeam.length === 0) {
        playersHistory.value = []
        return
      }

      const allPuuids = [...myTeam, ...theirTeam]
      console.log("当前队伍成员:", allPuuids)

      // 获取所有玩家的最近20场对局
      const playerHistoryPromises = allPuuids.map(async (puuid) => {
        try {
          const formData = new FormData()
          formData.append('puuid', puuid)
          formData.append('beg_index', '0')
          formData.append('end_index', '20')

          const response = await axios.post('/api/match_history/get_match_history', formData)
          const games = response.data.games.games

          // 处理每场比赛的数据
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
          console.log("matches:", matches)

          // 获取玩家名称
          const playerIdentity = games[0]?.participantIdentities.find(
            (pi: any) => pi.player.puuid === puuid
          )
          console.log("playerIdentity:", playerIdentity)

          return {
            playerName: `${playerIdentity?.player.gameName}#${playerIdentity?.player.tagLine}`,
            teamId: wsStore.syncFrontData.my_team_puuid_list?.includes(puuid) ? 100 : 200,
            matches
          }
        } catch (error) {
          console.error(`获取玩家 ${puuid} 的对局历史失败:`, error)
          return {
            playerName: '未知玩家',
            teamId: wsStore.syncFrontData.my_team_puuid_list?.includes(puuid) ? 100 : 200,
            matches: []
          }
        }
      })

      // 等待所有请求完成
      playersHistory.value = await Promise.all(playerHistoryPromises)

      // 收集所有英雄ID用于加载资源
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
  
  // 添加行样式
  const getRowClassName = ({ row }: { row: PlayerHistory }) => {
    return row.teamId === 100 ? 'team-blue' : 'team-red'
  }
  
  // 添加这些工具函数
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
  .game-analysis {
    padding: 20px;
    height: 100%;
    display: flex;
    flex-direction: column;
  }
  
  .header-controls {
    margin-bottom: 20px;
  }
  
  .analysis-content {
    flex: 1;
    overflow: auto;
  }
  
  .history-table {
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
    padding: 4px 4px;
    border-radius: 4px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    margin: 0 0px;
  }
  
  .match-cell.victory {
    background-color: var(--el-color-success-light-9);
  }
  
  .match-cell.defeat {
    background-color: var(--el-color-danger-light-9);
  }
  
  .match-cell.empty {
    color: var(--el-text-color-secondary);
  }
  
  .champion-icon {
    width: 28px;
    height: 28px;
    border-radius: 14px;
    border: 1px solid var(--el-border-color);
  }
  
  .match-stats {
    font-size: 11px;
    color: var(--el-text-color-regular);
    margin-top: 2px;
  }
  
  .team-blue {
    background-color: rgba(var(--el-color-primary-rgb), 0.1);
  }
  
  .team-red {
    background-color: rgba(var(--el-color-danger-rgb), 0.1);
  }
  
  .match-cell.victory {
    background-color: rgba(var(--el-color-success-rgb), 0.1);
    border: 1px solid var(--el-color-success-light-5);
  }
  
  .match-cell.defeat {
    background-color: rgba(var(--el-color-danger-rgb), 0.1);
    border: 1px solid var(--el-color-danger-light-5);
  }
  
  :deep(.el-table .cell) {
    padding-left: 8px !important;
    padding-right: 8px !important;
  }
  
  .player-name.clickable {
    cursor: pointer;
    &:hover {
      color: var(--el-color-primary);
    }
  }
  
  </style>