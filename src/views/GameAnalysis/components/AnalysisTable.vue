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
          width="120"
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
                  :style="getPlayerNameStyle(scope.row.puuid, scope.row.teamId)"
                  @click="copyPlayerName(scope.row.playerName)">
                  {{ getDisplayName(scope.row.playerName) }}
                </div>
              </el-tooltip>
            </div>
          </template>
        </el-table-column>

        <!-- 动态生成最近10个对局列 -->
        <el-table-column 
          v-for="index in 10"
          :key="index"
          :label="`G${index}`"
          width="105"
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
                <div class="match-cell-flex">
                  <img 
                    :src="getResourceUrl('champion_icons', scope.row.matches[index - 1].championId)"
                    class="champion-icon square"
                    :alt="scope.row.matches[index - 1].championId">
                  <div class="match-info">
                    <div class="match-mode">{{ getGameModeZh(scope.row.matches[index - 1].gameMode) }}</div>
                    <div class="match-stats">
                      {{ scope.row.matches[index - 1].kills }}/{{ scope.row.matches[index - 1].deaths }}/{{ scope.row.matches[index - 1].assists }}
                    </div>
                  </div>
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
import { ref, onMounted} from 'vue'
import axios from 'axios'
import type { ResourceResponse } from '../../MatchHistory/match'
import { ElMessage } from 'element-plus'
import { useWebSocketStore } from '../../../stores/websocket'
import { useRouter } from 'vue-router'

const props = defineProps<{
  myTeamPuuids: string[]
  theirTeamPuuids: string[]
  myTeamPremadeInfo: Record<string, string[]>
  theirTeamPremadeInfo: Record<string, string[]>
}>()

interface MatchData {
  championId: number
  win: boolean
  kills: number
  deaths: number
  assists: number
  gameId: string
  gameMode: string
}

interface PlayerHistory {
  playerName: string
  teamId: number
  puuid: string
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

// // 监听战绩数据变化
// watch(
//   [
//     () => wsStore.syncFrontData.my_team_match_history,
//     () => wsStore.syncFrontData.their_team_match_history
//   ],
//   async ([newMyTeamHistory, newTheirTeamHistory]) => {
//     console.log("战绩数据变化:", {
//       isCurrentGame: isCurrentGame.value,
//       hasMyTeamHistory: !!newMyTeamHistory,
//       hasTheirTeamHistory: !!newTheirTeamHistory
//     })
    
//     // 只要有新数据就更新，不再判断 isCurrentGame
//     if (newMyTeamHistory || newTheirTeamHistory) {
//       await transformMatchHistories(newMyTeamHistory, newTheirTeamHistory)
//     }
//   },
//   { immediate: true, deep: true }
// )

// 获取战绩数据
const fetchAnalysisData = async (isCurrentGameParam?: boolean) => {
  loading.value = true
  try {
    // 如果提供了参数就使用参数值，否则通过检查判断
    console.log("父组件指定了为当前对局","isCurrentGameParam: ", isCurrentGameParam);
    
    isCurrentGame.value = isCurrentGameParam !== undefined ? isCurrentGameParam : checkIfCurrentGame()

    console.log('isCurrentGame.value', isCurrentGame.value);
    
    if (isCurrentGame.value) {
      // 使用 WebSocket 数据
      console.log("获取战绩数据:", wsStore.syncFrontData.my_team_match_history, wsStore.syncFrontData.their_team_match_history);
      
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
  console.log("开始处理战绩数据:", {
    myTeamHistory: !!myTeamHistory,
    theirTeamHistory: !!theirTeamHistory,
    myTeamPuuids: props.myTeamPuuids,
    theirTeamPuuids: props.theirTeamPuuids
  })

  const allPlayers: PlayerHistory[] = []
  const championIds: number[] = []

  // 处理我方战绩
  if (myTeamHistory) {
    for (const puuid of props.myTeamPuuids) {
      const history = myTeamHistory[puuid]
      console.log("处理我方玩家战绩:", { puuid, hasHistory: !!history?.games?.games })
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
            gameId: game.gameId,
            gameMode: game.gameMode
          }
        })
        allPlayers.push({
          playerName,
          teamId: 100,
          puuid,
          matches
        })
      }
    }
  }

  // 处理敌方战绩
  if (theirTeamHistory) {
    for (const puuid of props.theirTeamPuuids) {
      const history = theirTeamHistory[puuid]
      console.log("处理敌方玩家战绩:", { puuid, hasHistory: !!history?.games?.games })
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
            gameId: game.gameId,
            gameMode: game.gameMode
          }
        })
        allPlayers.push({
          playerName,
          teamId: 200,
          puuid,
          matches
        })
      }
    }
  }

  console.log("处理完成的战绩数据:", {
    allPlayersLength: allPlayers.length,
    championIdsLength: championIds.length
  })

  playersHistory.value = allPlayers
  await loadGameResources(championIds)
}

// 添加获取组队颜色的函数
const getPremadeColor = (puuid: string, teamId: number) => {
  // 定义一组柔和的颜色
  const colors = [
    'rgba(255, 182, 193, 0.3)',  // 浅粉红
    'rgba(176, 224, 230, 0.3)',  // 粉蓝色
    'rgba(221, 160, 221, 0.3)',  // 梅红色
    'rgba(144, 238, 144, 0.3)',  // 浅绿色
    'rgba(255, 218, 185, 0.3)'   // 桃色
  ]

  const premadeInfo = teamId === 100 ? props.myTeamPremadeInfo : props.theirTeamPremadeInfo
  
  // 查找该玩家所在的组队
  for (const [groupId, members] of Object.entries(premadeInfo)) {
    if (members.includes(puuid)) {
      // 使用组队ID作为颜色索引
      const colorIndex = parseInt(groupId) % colors.length
      return colors[colorIndex]
    }
  }
  
  return 'transparent'  // 如果不在任何组队中
}

// 修改getRowClassName函数
const getRowClassName = (row: { row: PlayerHistory }) => {
  return {
    'custom-row': true,
    'blue-team': row.row.teamId === 100,
    'red-team': row.row.teamId === 200
  }
}

// 添加获取玩家名称样式的函数
const getPlayerNameStyle = (puuid: string, teamId: number) => {
  const backgroundColor = getPremadeColor(puuid, teamId)
  return {
    backgroundColor,
    padding: '4px 8px',
    borderRadius: '4px',
    transition: 'background-color 0.3s ease'
  }
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

// 英文gameMode到中文的映射表
const gameModeMap: Record<string, string> = { // Todo: 待补全
  CLASSIC: '经典模式',
  ARAM: '大乱斗',
  URF: '无限火力',
  TUTORIAL: '教程',
  ONEFORALL: '克隆模式',
  ASSASSINATE: '血月杀',
  CHERRY: '极限闪击',
  ODIN: '水晶之痕',
  PRACTICETOOL: '自定义',
  // ...可根据需要补充
  default: '其它'
}
const getGameModeZh = (mode: string) => {
  return gameModeMap[mode] || gameModeMap.default
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
  padding: 20px;
  box-sizing: border-box;
  overflow: auto;
}

.history-table {
  width: 100%;
  background-color: transparent;
}

/* 自定义行样式 */
:deep(.custom-row) {
  transition: background-color 0.3s ease;
}

:deep(.blue-team) {
  border-left: 3px solid #1890ff;
}

:deep(.red-team) {
  border-left: 3px solid #ff4d4f;
}

.player-info {
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
  z-index: 1;
  min-width: 160px;
}

.team-indicator {
  width: 4px;
  height: 20px;
  border-radius: 2px;
  flex-shrink: 0;
}

.team-indicator.blue {
  background-color: #1890ff;
}

.team-indicator.red {
  background-color: #ff4d4f;
}

.player-name {
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 140px;
  flex-grow: 1;
}

.player-name.clickable {
  cursor: pointer;
  &:hover {
    color: #1890ff;
    text-decoration: underline;
  }
}

.match-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 8px 6px;
  border-radius: 8px;
  background-color: #f6f8fa; /* 默认淡灰蓝 */
  transition: all 0.2s;
  width: 100px;
  min-height: 60px;
  border: 1px solid #e0e3e8;
  box-shadow: 0 1.5px 4px rgba(0,0,0,0.05);
}
.match-cell-flex {
  display: flex;
  flex-direction: row;
  align-items: center;
  width: 100%;
  gap: 5px;
}
.champion-icon.square {
  width: 28px;
  height: 28px;
  border-radius: 4px;
  flex-shrink: 0;
}
.match-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  min-width: 50px;
  max-width: 90px;
  gap: 1px;
}
.match-mode {
  font-size: 14px;
  font-weight: 600;
  color: #444;
  line-height: 1.2;
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.match-cell.victory {
  background-color: #e6f3fd; /* 更柔和的淡蓝 */
  border-color: #b3d8fd;
}
.match-cell.defeat {
  background-color: #fff0f0; /* 柔和淡红 */
  border-color: #ffd6d7;
}
.match-cell:hover {
  background-color: #e6f0fa;
  box-shadow: 0 4px 12px rgba(24,144,255,0.10);
  border-color: #91caff;
}
.match-cell.victory:hover {
  background-color: #d2eafd;
  border-color: #7ec1fa;
}
.match-cell.defeat:hover {
  background-color: #ffeaea;
  border-color: #ffb3b5;
}
.match-cell.victory .match-mode {
  color: #1766b2; /* 深蓝，胜利 */
}
.match-cell.defeat .match-mode {
  color: #d32f2f; /* 深红，失败 */
}
.match-stats {
  font-size: 12px;
  color: #888;
  font-weight: 500;
  line-height: 1.1;
}
.match-cell.empty {
  color: #999;
  background-color: transparent;
  box-shadow: none;
}

.header-controls {
  flex-shrink: 0;
}

.team-blue {
  background-color: rgba(var(--el-color-primary-rgb), 0.1);
}

.team-red {
  background-color: rgba(var(--el-color-danger-rgb), 0.1);
}

/* 调整表格单元格间距 */
:deep(.el-table .cell) {
  padding: 0 2px !important;
  line-height: 1.2;
}

:deep(.el-table td) {
  padding: 6px 0;
}

:deep(.el-table__row) {
  height: 48px;
}

:deep(.el-table__header-wrapper) {
  display: none;
}
</style> 