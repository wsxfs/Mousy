<template>
  <div class="notebook-container">
    <el-tabs v-model="activeTab" type="card">
      <el-tab-pane label="黑名单" name="blacklist">
        <div class="list-header">
          <el-button type="primary" @click="handleAdd('black')">
            <el-icon><Plus /></el-icon>添加记录
          </el-button>
          <el-input
            v-model="searchQuery"
            placeholder="搜索召唤师"
            clearable
            class="search-input"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>

        <el-table :data="filteredBlacklist" style="width: 100%">
          <el-table-column prop="summonerName" label="召唤师名称" width="150"/>
          <el-table-column label="召唤师ID" width="120">
            <template #default="scope">
              {{ formatSummonerId(scope.row.summonerId) }}
            </template>
          </el-table-column>
          <el-table-column label="大区" width="100">
            <template #default="scope">
              {{ formatRegion(scope.row.region) }}
            </template>
          </el-table-column>
          <el-table-column prop="reason" label="罪行" width="100" />
          <el-table-column label="英雄" width="60">
            <template #default="scope">
              <el-avatar 
                v-if="scope.row.championId"
                :size="32" 
                :src="getResourceUrl('champion_icons', scope.row.championId)"
              />
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column label="详情" width="60">
            <template #default="scope">
              <el-tooltip
                class="box-item"
                effect="dark"
                :content="scope.row.details"
                placement="top-start"
              >
                <el-icon class="details-icon"><InfoFilled /></el-icon>
              </el-tooltip>
            </template>
          </el-table-column>
          
          <el-table-column label="对局" width="100">
            <template #default="scope">
              <el-tooltip
                v-if="scope.row.gameId"
                :content="`对局ID: ${scope.row.gameId}`"
                placement="top"
              >
                <el-button 
                  link 
                  type="primary" 
                  @click="handleViewMatch(scope.row.gameId)"
                >
                  查看对局
                </el-button>
              </el-tooltip>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150">
            <template #default="scope">
              <el-button-group>
                <el-button type="primary" size="small" @click="handleEdit(scope.row)">
                  编辑
                </el-button>
                <el-button type="danger" size="small" @click="handleDelete(scope.row)">
                  删除
                </el-button>
              </el-button-group>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="白名单" name="whitelist">
        <div class="list-header">
          <el-button type="primary" @click="handleAdd('white')">
            <el-icon><Plus /></el-icon>添加记录
          </el-button>
          <el-input
            v-model="searchQuery"
            placeholder="搜索召唤师"
            clearable
            class="search-input"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>

        <el-table :data="filteredWhitelist" style="width: 100%">
          <el-table-column prop="summonerName" label="召唤师名称" />
          <el-table-column label="召唤师ID" width="120">
            <template #default="scope">
              {{ formatSummonerId(scope.row.summonerId) }}
            </template>
          </el-table-column>
          <el-table-column label="大区" width="100">
            <template #default="scope">
              {{ formatRegion(scope.row.region) }}
            </template>
          </el-table-column>
          <el-table-column prop="reason" label="亮点" width="150" />
          <el-table-column label="详情" width="60">
            <template #default="scope">
              <el-tooltip
                class="box-item"
                effect="dark"
                :content="scope.row.details"
                placement="top-start"
              >
                <el-icon class="details-icon"><InfoFilled /></el-icon>
              </el-tooltip>
            </template>
          </el-table-column>
          <el-table-column label="英雄" width="60">
            <template #default="scope">
              <el-avatar 
                v-if="scope.row.championId"
                :size="32" 
                :src="getResourceUrl('champion_icons', scope.row.championId)"
              />
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column label="对局" width="100">
            <template #default="scope">
              <el-tooltip
                v-if="scope.row.gameId"
                :content="`对局ID: ${scope.row.gameId}`"
                placement="top"
              >
                <el-button 
                  link 
                  type="primary" 
                  @click="handleViewMatch(scope.row.gameId)"
                >
                  查看对局
                </el-button>
              </el-tooltip>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150">
            <template #default="scope">
              <el-button-group>
                <el-button type="primary" size="small" @click="handleEdit(scope.row)">
                  编辑
                </el-button>
                <el-button type="danger" size="small" @click="handleDelete(scope.row)">
                  删除
                </el-button>
              </el-button-group>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '添加记录' : '编辑记录'"
      width="500px"
    >
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="选择对局" prop="gameId" v-if="dialogType === 'add'">
          <el-select 
            v-model="formData.gameId" 
            placeholder="选择一个对局"
            @change="handleGameSelect"
            :loading="matchesLoading"
          >
            <template #prefix v-if="formData.gameId">
              <el-avatar 
                :size="24" 
                :src="getResourceUrl('champion_icons', getSelectedMatchChampionId())"
              />
            </template>
            <el-option
              v-for="match in recentMatches"
              :key="match.gameId"
              :label="formatMatchLabel(match)"
              :value="match.gameId"
            >
              <div class="match-option">
                <el-avatar 
                  :size="24" 
                  :src="getResourceUrl('champion_icons', match.participants[0].championId)"
                />
                <span>{{ getGameModeName(match.gameMode) }}</span>
                <span>{{ formatDate(match.gameCreation) }}</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="召唤师名称" prop="summonerName">
          <el-select 
            v-model="formData.summonerName" 
            placeholder="选择召唤师"
            :disabled="!formData.gameId"
            @change="handleSummonerSelect"
          >
            <template #prefix v-if="formData.summonerName">
              <el-avatar 
                :size="24" 
                :src="getResourceUrl('champion_icons', formData.championId || 0)"
              />
            </template>
            <el-option
              v-for="player in gamePlayers"
              :key="player.participantId"
              :label="player.player?.gameName || player.player?.summonerName"
              :value="player.player?.gameName || player.player?.summonerName"
            >
              <div class="summoner-option">
                <el-avatar 
                  :size="24" 
                  :src="getResourceUrl('champion_icons', getPlayerChampionId(player.participantId))"
                />
                <span>{{ player.player?.gameName || player.player?.summonerName }}</span>
                <span class="team-tag" :class="getPlayerTeam(player.participantId)">
                  {{ getPlayerTeam(player.participantId) === 'blue' ? '蓝方' : '红方' }}
                </span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="召唤师ID" prop="summonerId">
          <el-input :value="formatSummonerId(formData.summonerId)" disabled />
        </el-form-item>
        <el-form-item label="大区" prop="region">
          <el-input :value="formatRegion(formData.region)" disabled />
        </el-form-item>
        <el-form-item :label="currentListType === 'black' ? '罪行' : '亮点'" prop="reason">
          <el-select
            v-model="formData.reason"
            :placeholder="currentListType === 'black' ? '选择或输入罪行' : '选择或输入亮点'"
            filterable
            allow-create
            default-first-option
          >
            <el-option-group v-if="currentListType === 'black'" label="常见罪行">
              <el-option value="玩得太菜" label="玩得太菜" />
              <el-option value="消极游戏" label="消极游戏" />
              <el-option value="挂机" label="挂机" />
              <el-option value="辱骂队友" label="辱骂队友" />
              <el-option value="故意送头" label="故意送头" />
              <el-option value="演员" label="演员" />
              <el-option value="抢位置" label="抢位置" />
              <el-option value="不配合团队" label="不配合团队" />
            </el-option-group>
            <el-option-group v-else label="常见亮点">
              <el-option value="操作细腻" label="操作细腻" />
              <el-option value="意识到位" label="意识到位" />
              <el-option value="指挥有方" label="指挥有方" />
              <el-option value="团队配合好" label="团队配合好" />
              <el-option value="心态好" label="心态好" />
              <el-option value="carry全场" label="carry全场" />
            </el-option-group>
          </el-select>
        </el-form-item>
        <el-form-item label="详情" prop="details">
          <el-input
            v-model="formData.details"
            type="textarea"
            :rows="4"
            placeholder="请输入详细信息"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Plus, Search, InfoFilled } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import dayjs from 'dayjs'

interface Game {
  gameId: number
  gameCreation: number
  gameMode: string
  participants: Array<{
    championId: number
    summonerId: number
  }>
}

const activeTab = ref('blacklist')
const searchQuery = ref('')
const dialogVisible = ref(false)
const dialogType = ref<'add' | 'edit'>('add')
const currentListType = ref<'black' | 'white'>('black')

// 模拟数据
const blacklist = ref<SummonerRecord[]>([])
const whitelist = ref<SummonerRecord[]>([])

// 添加游戏资源相关
const gameResources = ref<Record<string, Record<number, string>>>({})

const formData = ref<SummonerRecord>({
  id: 0,
  summonerName: '',
  summonerId: '',
  region: '',
  reason: '',
  details: '',
  gameId: undefined,
  championId: undefined,
  championName: undefined
})

// 过滤后的列表
const filteredBlacklist = computed(() => {
  return blacklist.value.filter(item =>
    item.summonerName.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    item.summonerId.includes(searchQuery.value)
  )
})

const filteredWhitelist = computed(() => {
  return whitelist.value.filter(item =>
    item.summonerName.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    item.summonerId.includes(searchQuery.value)
  )
})

// 添加新的接口
interface SummonerRecord {
  id: number
  summonerName: string
  summonerId: string
  region: string
  reason: string
  details: string
  gameId?: number        // 对局ID
  championId?: number    // 英雄ID
  championName?: string  // 英雄名称
}

// 添加新的响应式状态
const recentMatches = ref<Game[]>([])
const matchesLoading = ref(false)

// 修改表单验证规则
const formRules = {
  region: [
    { required: true, message: '请选择大区', trigger: 'change' }
  ],
  reason: [
    { required: true, message: currentListType.value === 'black' ? '请选择或输入罪行' : '请选择或输入亮点', trigger: 'change' }
  ],
  details: [
    { required: true, message: '请输入详细信息', trigger: 'blur' },
    { min: 10, message: '详细信息至少10个字符', trigger: 'blur' }
  ]
}

// 添加获取最近对局的方法
const fetchRecentMatches = async () => {
  try {
    matchesLoading.value = true
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
      recentMatches.value = response.data.games.games
      await loadGameResources()
    }
  } catch (error) {
    console.error('获取最近对局失败:', error)
    ElMessage.error('获取最近对局失败')
  } finally {
    matchesLoading.value = false
  }
}

// 修改加载游戏资源的方法
const loadGameResources = async () => {
  try {
    // 收集所有需要的英雄ID
    const championIds = new Set<number>()
    
    // 从最近对局中收集
    recentMatches.value.forEach(match => {
      match.participants.forEach(p => {
        championIds.add(p.championId)
      })
    })
    
    // 从游戏详情中收集
    if (gameDetail.value) {
      gameDetail.value.participants.forEach(p => {
        championIds.add(p.championId)
      })
    }
    
    // 从已有记录中收集
    blacklist.value.forEach(record => {
      if (record.championId) {
        championIds.add(record.championId)
      }
    })
    whitelist.value.forEach(record => {
      if (record.championId) {
        championIds.add(record.championId)
      }
    })

    const resourceRequest = {
      champion_icons: Array.from(championIds)
    }

    const response = await axios.post(
      '/api/common/game_resource/batch_get_resources',
      resourceRequest
    )

    if (response.data) {
      gameResources.value = response.data
    }
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

// 添加格式化对局标签的方法
const formatMatchLabel = (match: Game): string => {
  return `${getGameModeName(match.gameMode)} ${formatDate(match.gameCreation)}`
}

// 添加游戏模式名称转换方法
const getGameModeName = (mode: string): string => {
  const modes: Record<string, string> = {
    'CLASSIC': '经典模式',
    'ARAM': '大乱斗',
    'URF': '无限火力'
    // ... 其他模式
  }
  return modes[mode] || mode
}

// 添加格式化日期的方法
const formatDate = (timestamp: number): string => {
  return dayjs(timestamp).format('MM-DD HH:mm')
}

// 添加游戏详情相关接口
interface GamePlayer {
  participantId: number
  player?: {
    gameName?: string
    summonerName?: string
    summonerId?: number
    currentPlatformId?: string
    tagLine?: string  // 添加 tagLine
  }
}

interface GameDetail {
  gameId: number
  participantIdentities: GamePlayer[]
  participants: Array<{
    participantId: number
    championId: number
    teamId: number
  }>
}

// 添加响应式状态
const gameDetail = ref<GameDetail | null>(null)
const gamePlayers = ref<GamePlayer[]>([])

// 添加获取游戏详情的方法
const fetchGameDetail = async (gameId: number) => {
  try {
    const params = new URLSearchParams()
    params.append('game_id', gameId.toString())
    
    const response = await axios.post(
      '/api/match_history/get_game_detail',
      params,
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }
    )
    
    if (response.data) {
      gameDetail.value = response.data
      gamePlayers.value = response.data.participantIdentities
    }
  } catch (error) {
    console.error('获取游戏详情失败:', error)
    ElMessage.error('获取游戏详情失败')
  }
}

// 修改处理对局选择的方法
const handleGameSelect = async (gameId: number) => {
  if (!gameId) return
  
  await fetchGameDetail(gameId)
  
  // 重新加载资源以获取新选择的对局中的英雄头像
  await loadGameResources()
  
  formData.value = {
    ...formData.value,
    gameId,
    summonerName: '',
    summonerId: '',
    region: ''
  }
}

// 添加大区映射
const regionMap: Record<string, string> = {
  'HN1': '艾欧尼亚',
  'HN2': '祖安',
  'HN3': '诺克萨斯',
  'HN4': '班德尔城',
  'HN5': '皮尔特沃夫',
  'HN6': '战争学院',
  'HN7': '巨神峰',
  'HN8': '雷瑟守备',
  'HN9': '裁决之地',
  'HN10': '黑色玫瑰',
  'HN11': '暗影岛',
  'HN12': '钢铁烈阳',
  'HN13': '水晶之痕',
  'HN14': '均衡教派',
  'HN15': '守望之海',
  'HN16': '征服之海',
  'HN17': '卡拉曼达',
  'HN18': '皮城警备',
  'HN19': '比尔吉沃特',
  'HN20': '德玛西亚',
  'HN21': '弗雷尔卓德',
  'HN22': '恕瑞玛',
  'HN23': '巨龙之巢',
  'HN24': '男爵领域',
  'HN25': '峡谷之巅',
  'HN26': '无畏先锋',
  'HN27': '扭曲丛林'
}

// 添加格式化大区的方法
const formatRegion = (regionCode: string): string => {
  return regionMap[regionCode] || regionCode
}

// 修改处理召唤师选择的方法
const handleSummonerSelect = (summonerName: string) => {
  const selectedPlayer = gamePlayers.value.find(
    p => (p.player?.gameName || p.player?.summonerName) === summonerName
  )
  
  if (selectedPlayer?.player) {
    const participant = gameDetail.value?.participants.find(
      p => p.participantId === selectedPlayer.participantId
    )
    
    formData.value = {
      ...formData.value,
      summonerName,
      summonerId: selectedPlayer.player.tagLine || '',
      region: selectedPlayer.player.currentPlatformId || '', // 保存大区代号
      championId: participant?.championId,
      championName: undefined
    }
  }
}

// 添加获取玩家英雄ID的方法
const getPlayerChampionId = (participantId: number): number => {
  const participant = gameDetail.value?.participants.find(
    p => p.participantId === participantId
  )
  return participant?.championId || 0
}

// 添加获取玩家队伍的方法
const getPlayerTeam = (participantId: number): 'blue' | 'red' => {
  const participant = gameDetail.value?.participants.find(
    p => p.participantId === participantId
  )
  return participant?.teamId === 100 ? 'blue' : 'red'
}

// 添加获取选中对局英雄ID的方法
const getSelectedMatchChampionId = (): number => {
  if (!formData.value.gameId) return 0
  const match = recentMatches.value.find(m => m.gameId === formData.value.gameId)
  return match?.participants[0].championId || 0
}

// 处理添加记录
const handleAdd = async (type: 'black' | 'white') => {
  dialogType.value = 'add'
  currentListType.value = type
  formData.value = {
    id: Date.now(),
    summonerName: '',
    summonerId: '',
    region: '',
    reason: '',
    details: '',
    gameId: undefined,
    championId: undefined,
    championName: undefined
  }
  await fetchRecentMatches()
  dialogVisible.value = true
}

// 处理编辑记录
const handleEdit = (row: SummonerRecord) => {
  dialogType.value = 'edit'
  formData.value = { ...row }
  dialogVisible.value = true
}

// 处理删除记录
const handleDelete = (row: SummonerRecord) => {
  ElMessageBox.confirm(
    '确定要删除这条记录吗？',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    const list = activeTab.value === 'blacklist' ? blacklist : whitelist
    const index = list.value.findIndex(item => item.id === row.id)
    if (index !== -1) {
      list.value.splice(index, 1)
      ElMessage.success('删除成功')
    }
  }).catch(() => {})
}

// 处理提交
const handleSubmit = () => {
  const list = currentListType.value === 'black' ? blacklist : whitelist
  if (dialogType.value === 'add') {
    list.value.push({ ...formData.value })
  } else {
    const index = list.value.findIndex(item => item.id === formData.value.id)
    if (index !== -1) {
      list.value[index] = { ...formData.value }
    }
  }
  dialogVisible.value = false
  ElMessage.success(dialogType.value === 'add' ? '添加成功' : '更新成功')
}

// 在组件挂载时加载资源
onMounted(async () => {
  await loadGameResources()
})

// 修改格式化召唤师ID的方法
const formatSummonerId = (id: string): string => {
  if (!id) return ''
  return id.startsWith('#') ? id : `#${id}`
}

// 添加查看对局的方法
const handleViewMatch = (gameId: number) => {
  console.log('查看对局:', gameId)
  // TODO: 实现查看对局的功能
}
</script>

<style scoped>
.notebook-container {
  padding: 20px;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.search-input {
  width: 300px;
}

.el-table {
  margin-top: 20px;
}

:deep(.el-table__row) {
  cursor: pointer;
}

:deep(.el-table__row:hover) {
  background-color: var(--el-table-row-hover-bg-color);
}

.game-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.game-id {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.match-option {
  display: flex;
  align-items: center;
  gap: 12px;
}

.match-option span {
  color: var(--el-text-color-regular);
  font-size: 14px;
}

.match-option span:first-of-type {
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.summoner-option {
  display: flex;
  align-items: center;
  gap: 12px;
}

.team-tag {
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 4px;
}

.team-tag.blue {
  background-color: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
}

.team-tag.red {
  background-color: var(--el-color-danger-light-9);
  color: var(--el-color-danger);
}

:deep(.el-select .el-input) {
  /* 调整输入框样式以适应头像 */
  .el-input__prefix {
    display: flex;
    align-items: center;
    left: 8px;
  }
  
  .el-input__inner {
    padding-left: 40px; /* 为头像留出空间 */
  }
}

/* 确保两个选择框的样式一致 */
.el-form-item {
  :deep(.el-select) {
    width: 100%;
  }
}

:deep(.el-select-dropdown__item) {
  padding: 0 12px;
}

:deep(.el-select-group__title) {
  padding-left: 12px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

/* 调整表格中头像的样式 */
:deep(.el-table .el-avatar) {
  display: block;
  margin: 0 auto;
}

/* 修改详情图标样式 */
.details-icon {
  font-size: 16px;
  color: var(--el-text-color-secondary);
  cursor: help;
  transition: color 0.2s;
  
  &:hover {
    color: var(--el-color-primary);
  }
}

/* 调整提示框样式 */
:deep(.el-tooltip__popper) {
  max-width: 300px;
  line-height: 1.5;
  padding: 10px;
  font-size: 14px;
  word-break: break-all;
  white-space: pre-wrap;
}
</style> 