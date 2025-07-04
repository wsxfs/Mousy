<template>
  <div class="game-summary">
    <div v-if="gameDetail" class="summary-container">
      <!-- 游戏基本信息 -->
      <div class="game-header">
        <div class="game-result" :class="{ 'win': gameDetail.localPlayer.stats.WIN }">
          {{ gameDetail.localPlayer.stats.WIN ? '胜利' : '失败' }}
        </div>
        <div class="game-info">
          <span class="game-mode">{{ getGameModeName(gameDetail.gameMode) }}</span>
          <span class="game-duration">{{ formatGameLength(gameDetail.gameLength) }}</span>
        </div>
      </div>

      <!-- 队伍信息 -->
      <div class="teams-container">
        <!-- 我方队伍 -->
        <div class="team blue-team">
          <div class="team-header">我方队伍</div>
          <div class="team-players">
            <div v-for="player in gameDetail.teams[0].players" 
                 :key="player.summonerId"
                 class="player-card"
                 :class="{ 'local-player': player.isLocalPlayer }">
              <div class="player-info">
                <el-avatar :size="40" :src="getResourceUrl('champion_icons', player.championId)" />
                <div class="player-details">
                  <div class="summoner-name" :class="{ 'bot': !player.game_name }">
                    {{ player.game_name || `${player.championName} (电脑)` }}
                  </div>
                  <div class="champion-name">{{ player.championName }}</div>
                </div>
              </div>
              <div class="player-content">
                <div class="player-stats">
                  <div class="kda">
                    <span>{{ player.stats.CHAMPIONS_KILLED }}</span> /
                    <span class="deaths">{{ player.stats.NUM_DEATHS }}</span> /
                    <span>{{ player.stats.ASSISTS }}</span>
                  </div>
                  <div class="damage-stats">
                    <div class="damage-bar">
                      <div class="damage-fill" 
                           :style="{ width: calculateDamagePercentage(player.stats.TOTAL_DAMAGE_DEALT_TO_CHAMPIONS) + '%' }">
                      </div>
                    </div>
                    <span class="damage-value">{{ player.stats.TOTAL_DAMAGE_DEALT_TO_CHAMPIONS }}</span>
                  </div>
                </div>

                <div v-if="player.game_name" class="player-actions">
                  <el-button 
                    type="primary" 
                    :icon="Star"
                    circle
                    size="small"
                    @click="handleLike(player)"
                  />
                  <el-button 
                    type="danger" 
                    :icon="CircleClose"
                    circle
                    size="small"
                    @click="handleBlock(player)"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 敌方队伍 -->
        <div class="team red-team">
          <div class="team-header">敌方队伍</div>
          <div class="team-players">
            <div v-for="player in gameDetail.teams[1].players" 
                 :key="player.summonerId"
                 class="player-card">
              <div class="player-info">
                <el-avatar :size="40" :src="getResourceUrl('champion_icons', player.championId)" />
                <div class="player-details">
                  <div class="summoner-name" :class="{ 'bot': !player.game_name }">
                    {{ player.game_name || `${player.championName} (电脑)` }}
                  </div>
                  <div class="champion-name">{{ player.championName }}</div>
                </div>
              </div>
              <div class="player-content">
                <div class="player-stats">
                  <div class="kda">
                    <span>{{ player.stats.CHAMPIONS_KILLED }}</span> /
                    <span class="deaths">{{ player.stats.NUM_DEATHS }}</span> /
                    <span>{{ player.stats.ASSISTS }}</span>
                  </div>
                  <div class="damage-stats">
                    <div class="damage-bar">
                      <div class="damage-fill" 
                           :style="{ width: calculateDamagePercentage(player.stats.TOTAL_DAMAGE_DEALT_TO_CHAMPIONS) + '%' }">
                      </div>
                    </div>
                    <span class="damage-value">{{ player.stats.TOTAL_DAMAGE_DEALT_TO_CHAMPIONS }}</span>
                  </div>
                </div>

                <div v-if="player.game_name" class="player-actions">
                  <el-button 
                    type="primary" 
                    :icon="Star"
                    circle
                    size="small"
                    @click="handleLike(player)"
                  />
                  <el-button 
                    type="danger" 
                    :icon="CircleClose"
                    circle
                    size="small"
                    @click="handleBlock(player)"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <el-empty v-else description="对局总结内容将在这里显示" />

    <!-- 拉黑对话框 -->
    <el-dialog
      v-model="blockDialogVisible"
      title="拉黑玩家"
      width="500px"
    >
      <el-form
        ref="blockFormRef"
        :model="blockForm"
        :rules="blockRules"
        label-width="100px"
      >
        <el-form-item label="用户名称" prop="userName">
          <el-input v-model="blockForm.userName" disabled />
        </el-form-item>
        <el-form-item label="用户ID" prop="userId">
          <el-input v-model="blockForm.userId" disabled />
        </el-form-item>
        <el-form-item label="所在大区" prop="region">
          <el-select v-model="blockForm.region" placeholder="请选择大区" disabled>
            <el-option label="艾欧尼亚" value="HN1" />
            <el-option label="祖安" value="HN2" />
            <el-option label="诺克萨斯" value="HN3" />
            <el-option label="班德尔城" value="HN4" />
            <el-option label="皮尔特沃夫" value="HN5" />
            <el-option label="战争学院" value="HN6" />
            <el-option label="巨神峰" value="HN7" />
            <el-option label="雷瑟守备" value="HN8" />
            <el-option label="裁决之地" value="HN9" />
            <el-option label="黑色玫瑰" value="HN10" />
            <el-option label="暗影岛" value="HN11" />
            <el-option label="钢铁烈阳" value="HN12" />
            <el-option label="水晶之痕" value="HN13" />
            <el-option label="均衡教派" value="HN14" />
            <el-option label="影流" value="HN15" />
            <el-option label="守望之海" value="HN16" />
            <el-option label="征服之海" value="HN17" />
            <el-option label="卡拉曼达" value="HN18" />
            <el-option label="皮城警备" value="HN19" />
          </el-select>
        </el-form-item>
        <el-form-item label="当局英雄" prop="champion">
          <el-input v-model="blockForm.champion" disabled />
        </el-form-item>
        <el-form-item label="罪行" prop="crime">
          <el-select v-model="blockForm.crime" placeholder="请选择罪行类型">
            <el-option label="玩得太菜" value="玩得太菜" />
            <el-option label="消极游戏" value="消极游戏" />
            <el-option label="挂机" value="挂机" />
            <el-option label="辱骂队友" value="辱骂队友" />
            <el-option label="故意送头" value="故意送头" />
            <el-option label="演员" value="演员" />
            <el-option label="抢位置" value="抢位置" />
            <el-option label="不配合团队" value="不配合团队" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="详情" prop="details">
          <el-input
            v-model="blockForm.details"
            type="textarea"
            :rows="4"
            placeholder="请输入详细说明"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="blockDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitBlock">
            确认
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 添加点赞对话框 -->
    <el-dialog
      v-model="likeDialogVisible"
      title="点赞玩家"
      width="500px"
    >
      <el-form
        ref="likeFormRef"
        :model="likeForm"
        :rules="likeRules"
        label-width="100px"
      >
        <el-form-item label="用户名称" prop="userName">
          <el-input v-model="likeForm.userName" disabled />
        </el-form-item>
        <el-form-item label="用户ID" prop="userId">
          <el-input v-model="likeForm.userId" disabled />
        </el-form-item>
        <el-form-item label="所在大区" prop="region">
          <el-select v-model="likeForm.region" placeholder="请选择大区" disabled>
            <el-option label="艾欧尼亚" value="HN1" />
            <el-option label="祖安" value="HN2" />
            <el-option label="诺克萨斯" value="HN3" />
            <el-option label="班德尔城" value="HN4" />
            <el-option label="皮尔特沃夫" value="HN5" />
            <el-option label="战争学院" value="HN6" />
            <el-option label="巨神峰" value="HN7" />
            <el-option label="雷瑟守备" value="HN8" />
            <el-option label="裁决之地" value="HN9" />
            <el-option label="黑色玫瑰" value="HN10" />
            <el-option label="暗影岛" value="HN11" />
            <el-option label="钢铁烈阳" value="HN12" />
            <el-option label="水晶之痕" value="HN13" />
            <el-option label="均衡教派" value="HN14" />
            <el-option label="影流" value="HN15" />
            <el-option label="守望之海" value="HN16" />
            <el-option label="征服之海" value="HN17" />
            <el-option label="卡拉曼达" value="HN18" />
            <el-option label="皮城警备" value="HN19" />
          </el-select>
        </el-form-item>
        <el-form-item label="当局英雄" prop="champion">
          <el-input v-model="likeForm.champion" disabled />
        </el-form-item>
        <el-form-item label="亮点" prop="reason">
          <el-select v-model="likeForm.reason" placeholder="请选择亮点类型">
            <el-option label="操作细腻" value="操作细腻" />
            <el-option label="意识到位" value="意识到位" />
            <el-option label="指挥有方" value="指挥有方" />
            <el-option label="团队配合好" value="团队配合好" />
            <el-option label="心态好" value="心态好" />
            <el-option label="carry全场" value="carry全场" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="详情" prop="details">
          <el-input
            v-model="likeForm.details"
            type="textarea"
            :rows="4"
            placeholder="请输入详细说明"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="likeDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitLike">
            确认
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { Star, CircleClose } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

interface PlayerStats {
  WIN: boolean
  CHAMPIONS_KILLED: number
  NUM_DEATHS: number
  ASSISTS: number
  TOTAL_DAMAGE_DEALT_TO_CHAMPIONS: number
}

interface Player {
  summonerId: number
  summonerName: string
  championName: string
  championSquarePortraitPath: string
  isLocalPlayer: boolean
  stats: PlayerStats
  game_name?: string
  championId: number
  puuid?: string
}

interface Team {
  teamId: number
  players: Player[]
}

interface GameDetail {
  gameId: number
  gameMode: string
  gameLength: number
  localPlayer: Player
  teams: Team[]
}

const gameDetail = ref<GameDetail | null>(null)

// 添加游戏模式映射
const gameModeMap: Record<string, string> = {
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
}

// 获取游戏资源
const gameResources = ref<Record<string, Record<number, string>>>({})

const loadGameResources = async () => {
  try {
    if (!gameDetail.value) return

    const resourceRequest = {
      champion_icons: [] as number[]
    }

    // 收集所有英雄ID
    gameDetail.value.teams.forEach(team => {
      team.players.forEach(player => {
        if (!resourceRequest.champion_icons.includes(player.championId)) {
          resourceRequest.champion_icons.push(player.championId)
        }
      })
    })

    const response = await axios.post(
      '/api/common/game_resource/batch_get_resources',
      resourceRequest
    )

    gameResources.value = response.data
  } catch (error) {
    console.error('加载游戏资源失败:', error)
  }
}

// 获取资源URL的方法
const getResourceUrl = (type: string, id: number): string => {
  const resources = gameResources.value[type]
  if (resources?.[id]) {
    return `data:image/png;base64,${resources[id]}`
  }
  return '/placeholder.png'
}

// 获取游戏模式名称
const getGameModeName = (mode: string): string => {
  return gameModeMap[mode] || mode
}

onMounted(async () => {
  try {
    const response = await axios.get('/api/note_book/get_game_detail_when_end_of_game')
    gameDetail.value = response.data
    await loadGameResources()
  } catch (error) {
    console.error('获取对局详情失败:', error)
  }
})

const formatGameLength = (seconds: number): string => {
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
}

const maxDamage = computed(() => {
  if (!gameDetail.value) return 0
  return Math.max(
    ...gameDetail.value.teams.flatMap(team => 
      team.players.map(player => player.stats.TOTAL_DAMAGE_DEALT_TO_CHAMPIONS)
    )
  )
})

const calculateDamagePercentage = (damage: number): number => {
  return (damage / maxDamage.value) * 100
}

// 拉黑对话框相关
const blockDialogVisible = ref(false)
const blockFormRef = ref()
const blockForm = ref({
  userName: '',
  userId: '',
  region: '',
  champion: '',
  crime: '',
  details: '',
  puuid: ''
})

// 修改表单验证规则
const blockRules = {
  crime: [], // 移除必填限制
  details: [] // 移除必填和长度限制
}

// 修改 handleBlock 函数
const handleBlock = async (player: Player) => {
  // 分离召唤师名称和标签
  const [gameName, tagLine] = (player.game_name || '').split('#')
  
  blockForm.value = {
    userName: gameName || '', // 只使用纯召唤师名称
    userId: tagLine ? `#${tagLine}` : player.summonerId.toString(), // 标签号加上 # 前缀
    region: '',
    champion: player.championName,
    crime: '',
    details: '',
    puuid: player.puuid || ''
  }
  
  // 如果有 puuid，尝试获取服务器信息
  if (player.puuid) {
    try {
      const response = await axios.get(`/api/note_book/get_platformId_by_puuid?puuid=${player.puuid}`)
      blockForm.value.region = response.data
    } catch (error) {
      console.error('获取服务器信息失败:', error)
    }
  }
  
  blockDialogVisible.value = true
}

// 修改提交拉黑表单
const submitBlock = async () => {
  if (!blockFormRef.value) return
  
  try {
    await blockFormRef.value.validate()
    
    // 获取用户ID（去除开头的#号）
    const summonerId = blockForm.value.userId.startsWith('#') 
      ? blockForm.value.userId.slice(1) 
      : blockForm.value.userId
    
    // 转换为后端需要的格式
    const submitData = {
      summoner_id: summonerId,
      game_name: blockForm.value.userName,
      champion_id: gameDetail.value?.teams.flatMap(team => 
        team.players.find(p => 
          p.game_name?.split('#')[0] === blockForm.value.userName
        )
      ).find(p => p)?.championId,
      timestamp: Date.now() / 1000,
      reason: blockForm.value.crime,
      details: blockForm.value.details,
      game_id: gameDetail.value?.gameId?.toString(),
      region: blockForm.value.region,
      puuid: blockForm.value.puuid
    }

    // 调用智能添加黑名单API
    await axios.post('/api/note_book/blacklist/smart_add', submitData)
    
    ElMessage.success('已将该玩家加入黑名单')
    blockDialogVisible.value = false
  } catch (error) {
    console.error('拉黑失败:', error)
    ElMessage.error('拉黑失败，请重试')
  }
}

// 添加点赞对话框相关
const likeDialogVisible = ref(false)
const likeFormRef = ref()
const likeForm = ref({
  userName: '',
  userId: '',
  region: '',
  champion: '',
  reason: '',
  details: '',
  puuid: ''
})

// 修改表单验证规则
const likeRules = {
  reason: [], // 移除必填限制
  details: [] // 移除必填和长度限制
}

// 修改 handleLike 函数
const handleLike = async (player: Player) => {
  // 分离召唤师名称和标签
  const [gameName, tagLine] = (player.game_name || '').split('#')
  
  likeForm.value = {
    userName: gameName || '',
    userId: tagLine ? `#${tagLine}` : player.summonerId.toString(),
    region: '',
    champion: player.championName,
    reason: '',
    details: '',
    puuid: player.puuid || ''
  }
  
  // 如果有 puuid，尝试获取服务器信息
  if (player.puuid) {
    try {
      const response = await axios.get(`/api/note_book/get_platformId_by_puuid?puuid=${player.puuid}`)
      likeForm.value.region = response.data
    } catch (error) {
      console.error('获取服务器信息失败:', error)
    }
  }
  
  likeDialogVisible.value = true
}

// 修改提交点赞表单
const submitLike = async () => {
  if (!likeFormRef.value) return
  
  try {
    await likeFormRef.value.validate()
    
    // 获取用户ID（去除开头的#号）
    const summonerId = likeForm.value.userId.startsWith('#') 
      ? likeForm.value.userId.slice(1) 
      : likeForm.value.userId
    
    // 转换为后端需要的格式
    const submitData = {
      summoner_id: summonerId,
      game_name: likeForm.value.userName,
      champion_id: gameDetail.value?.teams.flatMap(team => 
        team.players.find(p => 
          p.game_name?.split('#')[0] === likeForm.value.userName
        )
      ).find(p => p)?.championId,
      timestamp: Date.now() / 1000,
      reason: likeForm.value.reason,
      details: likeForm.value.details,
      game_id: gameDetail.value?.gameId?.toString(),
      region: likeForm.value.region,
      puuid: likeForm.value.puuid
    }

    // 调用智能添加白名单API
    await axios.post('/api/note_book/whitelist/smart_add', submitData)
    
    ElMessage.success('已将该玩家加入白名单')
    likeDialogVisible.value = false
  } catch (error) {
    console.error('点赞失败:', error)
    ElMessage.error('点赞失败，请重试')
  }
}
</script>

<style scoped>
.game-summary {
  min-height: 100vh;
  padding: 20px;
  background: var(--el-bg-color);
}

.summary-container {
  max-width: 1200px;
  margin: 0 auto;
  background: var(--el-bg-color-overlay);
  border-radius: 8px;
  padding: 20px;
  box-shadow: var(--el-box-shadow-light);
}

.game-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.game-result {
  font-size: 24px;
  font-weight: bold;
  color: var(--el-color-danger);
}

.game-result.win {
  color: var(--el-color-success);
}

.game-info {
  display: flex;
  gap: 12px;
  color: var(--el-text-color-secondary);
}

.teams-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.team {
  padding: 16px;
  border-radius: 8px;
}

.blue-team {
  background: rgba(var(--el-color-primary-rgb), 0.1);
}

.red-team {
  background: rgba(var(--el-color-danger-rgb), 0.1);
}

.team-header {
  font-size: 18px;
  font-weight: 500;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.player-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  margin-bottom: 8px;
  border-radius: 6px;
  background: var(--el-bg-color);
}

.player-card.local-player {
  background: var(--el-color-primary-light-9);
}

.player-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.player-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.summoner-name {
  font-weight: 500;
}

.summoner-name.bot {
  color: var(--el-text-color-secondary);
  font-style: italic;
}

.champion-name {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.player-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.player-stats {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
  min-width: 160px; /* 确保有足够空间显示数据 */
}

.kda {
  font-weight: 500;
}

.deaths {
  color: var(--el-color-danger);
}

.damage-stats {
  display: flex;
  align-items: center;
  gap: 8px;
}

.damage-bar {
  width: 100px;
  height: 6px;
  background: var(--el-fill-color-lighter);
  border-radius: 3px;
  overflow: hidden;
}

.damage-fill {
  height: 100%;
  background: var(--el-color-warning);
  border-radius: 3px;
}

.damage-value {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  min-width: 60px;
  text-align: right;
}

.player-actions {
  display: flex;
  gap: 8px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style> 