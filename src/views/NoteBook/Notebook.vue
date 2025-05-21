<template>
  <div class="notebook-container">
    <div class="global-actions">
      <el-button @click="handleRefresh">
        <el-icon><Refresh /></el-icon>刷新
      </el-button>
      <el-button @click="handleExport">
        <el-icon><Download /></el-icon>导出笔记本
      </el-button>
      <el-button @click="handleImport">
        <el-icon><Upload /></el-icon>导入笔记本
      </el-button>
    </div>
    
    <el-tabs v-model="activeTab" type="card">
      <el-tab-pane label="黑名单" name="blacklist">
        <div class="list-header">
          <div class="left-buttons">
            <el-button type="primary" @click="handleAdd('black')">
              <el-icon><Plus /></el-icon>添加记录
            </el-button>
          </div>
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
          <el-table-column label="罪行" width="100">
            <template #default="scope">
              <span v-if="scope.row.reason">{{ scope.row.reason }}</span>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column label="详情" width="60">
            <template #default="scope">
              <el-tooltip
                v-if="scope.row.details"
                class="box-item"
                effect="dark"
                :content="scope.row.details"
                placement="top-start"
              >
                <el-icon class="details-icon"><InfoFilled /></el-icon>
              </el-tooltip>
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

      <el-tab-pane label="白名单" name="whitelist">
        <div class="list-header">
          <div class="left-buttons">
            <el-button type="primary" @click="handleAdd('white')">
              <el-icon><Plus /></el-icon>添加记录
            </el-button>
          </div>
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
          <el-table-column label="亮点" width="100">
            <template #default="scope">
              <span v-if="scope.row.reason">{{ scope.row.reason }}</span>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column label="详情" width="60">
            <template #default="scope">
              <el-tooltip
                v-if="scope.row.details"
                class="box-item"
                effect="dark"
                :content="scope.row.details"
                placement="top-start"
              >
                <el-icon class="details-icon"><InfoFilled /></el-icon>
              </el-tooltip>
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
          <div class="game-select-wrapper">
            <el-select 
              v-model="formData.gameId" 
              placeholder="选择一个对局"
              @change="handleGameSelect"
              :loading="matchesLoading"
              clearable
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
          </div>
        </el-form-item>

        <el-form-item label="召唤师名称" prop="summonerName">
          <el-select 
            v-if="formData.gameId"
            v-model="formData.summonerName" 
            placeholder="选择召唤师"
            filterable
            @change="handleSummonerSelect"
          >
            <template #prefix v-if="formData.summonerName && formData.championId">
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
                <div class="team-indicator" :class="getPlayerTeam(player.participantId)"></div>
                <el-avatar 
                  :size="24" 
                  :src="getResourceUrl('champion_icons', getPlayerChampionId(player.participantId))"
                />
                <span>{{ player.player?.gameName || player.player?.summonerName }}</span>
              </div>
            </el-option>
          </el-select>
          <el-input
            v-else
            v-model="formData.summonerName"
            placeholder="输入召唤师名称"
          />
        </el-form-item>
        <el-form-item label="召唤师ID" prop="summonerId">
          <el-input 
            v-model="formData.summonerId" 
            :disabled="!!formData.gameId"
            placeholder="输入召唤师ID"
          />
        </el-form-item>
        <el-form-item label="大区" prop="region">
          <el-select
            v-model="formData.region"
            placeholder="选择大区"
            :disabled="!!formData.gameId"
          >
            <el-option
              v-for="(name, code) in regionMap"
              :key="code"
              :label="name"
              :value="code"
            />
          </el-select>
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
import { Plus, Search, InfoFilled, Download, Upload, Refresh } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import dayjs from 'dayjs'
import { useRouter } from 'vue-router'

const router = useRouter()

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

// 修改 SummonerRecord 接口以匹配后端
interface SummonerRecord {
  id: number                // 仅用于前端展示
  summonerName: string     // 对应后端的 game_name
  summonerId: string       // 对应后端的 summoner_id
  region: string
  reason: string
  details: string
  gameId?: number          // 对应后端的 game_id
  championId?: number      // 对应后端的 champion_id
  championName?: string    // 前端展示用
  timestamp?: number       // 对应后端的 timestamp
}

// 添加新的响应式状态
const recentMatches = ref<Game[]>([])
const matchesLoading = ref(false)

// 修改表单验证规则
const formRules = {
  summonerName: [
    { required: true, message: '请输入召唤师名称', trigger: 'blur' }
  ],
  summonerId: [
    { required: true, message: '请输入召唤师ID', trigger: 'blur' }
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
const handleGameSelect = async (gameId: number | undefined) => {
  if (!gameId) {
    // 清除对局相关的数据
    formData.value = {
      ...formData.value,
      gameId: undefined,
      championId: undefined,
      championName: undefined,
      // 保留手动输入的召唤师信息
      summonerName: formData.value.summonerName,
      summonerId: formData.value.summonerId,
      region: formData.value.region
    }
    gamePlayers.value = []
    return
  }
  
  await fetchGameDetail(gameId)
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
  'HN27': '扭曲丛林',

  
  'GZ100': '雷瑟守备'
}

// 添加格式化大区的方法
const formatRegion = (regionCode: string): string => {
  return regionMap[regionCode] || regionCode
}

// 修改处理召唤师选择的方法
const handleSummonerSelect = (summonerName: string) => {
  if (!formData.value.gameId) {
    // 手动输入模式，只更新召唤师名称
    formData.value.summonerName = summonerName
    return
  }

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
      region: selectedPlayer.player.currentPlatformId || '',
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

// 添加表单引用
const formRef = ref()

// 修改提交方法，转换数据格式
const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    
    // 转换为后端需要的格式
    const submitData = {
      summoner_id: formData.value.summonerId,
      game_name: formData.value.summonerName,
      champion_id: formData.value.championId,
      timestamp: formData.value.timestamp || Date.now() / 1000,
      reason: formData.value.reason,
      details: formData.value.details,
      game_id: formData.value.gameId?.toString(),
      region: formData.value.region
    }
    
    const baseApiPath = currentListType.value === 'black' 
      ? '/api/note_book/blacklist'
      : '/api/note_book/whitelist'

    if (dialogType.value === 'edit') {
      // 先删除旧记录
      await axios.post(`${baseApiPath}/remove?summoner_id=${encodeURIComponent(formData.value.summonerId)}`)
    }

    // 使用智能添加接口
    const response = await axios.post(`${baseApiPath}/smart_add`, submitData)
    
    if (response.data?.message) {
      // 更新前端数据
      const list = currentListType.value === 'black' ? blacklist : whitelist
      if (dialogType.value === 'add') {
        list.value.push({ ...formData.value, id: Date.now() })
      } else {
        const index = list.value.findIndex(item => item.id === formData.value.id)
        if (index !== -1) {
          list.value[index] = { ...formData.value }
        }
      }
      
      dialogVisible.value = false
      ElMessage.success(dialogType.value === 'add' ? '添加成功' : '更新成功')
    }
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error('操作失败，请重试')
  }
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

// 修改处理删除记录的方法
const handleDelete = async (row: SummonerRecord) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这条记录吗？',
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    // 根据当前标签页决定调用哪个API
    const apiPath = activeTab.value === 'blacklist' 
      ? '/api/note_book/blacklist/remove'
      : '/api/note_book/whitelist/remove'

    // 修改为查询参数方式调用API
    await axios.post(`${apiPath}?summoner_id=${encodeURIComponent(row.summonerId)}`)

    // 删除成功后更新前端数据
    const list = activeTab.value === 'blacklist' ? blacklist : whitelist
    const index = list.value.findIndex(item => item.id === row.id)
    if (index !== -1) {
      list.value.splice(index, 1)
    }
    
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') { // 忽略用户取消的情况
      console.error('删除失败:', error)
      ElMessage.error('删除失败，请重试')
    }
  }
}

// 在组件挂载时加载资源
onMounted(async () => {
  try {
    const response = await axios.get('/api/note_book/get_settings')
    if (response.data) {
      // 转换后端数据为前端格式
      blacklist.value = (response.data.blacklist || []).map((item: any) => ({
        id: Date.now() + Math.random(),
        summonerName: item.game_name,
        summonerId: item.summoner_id,
        region: item.region || '',
        reason: item.reason || '',
        details: item.details || '',
        gameId: item.game_id ? parseInt(item.game_id) : undefined,
        championId: item.champion_id,
        timestamp: item.timestamp
      }))
      
      whitelist.value = (response.data.whitelist || []).map((item: any) => ({
        id: Date.now() + Math.random(),
        summonerName: item.game_name,
        summonerId: item.summoner_id,
        region: item.region || '',
        reason: item.reason || '',
        details: item.details || '',
        gameId: item.game_id ? parseInt(item.game_id) : undefined,
        championId: item.champion_id,
        timestamp: item.timestamp
      }))
    }
  } catch (error) {
    console.error('获取设置失败:', error)
    ElMessage.error('获取设置失败')
  }
  
  await loadGameResources()
})

// 修改格式化召唤师ID的方法
const formatSummonerId = (id: string): string => {
  if (!id) return ''
  return id.startsWith('#') ? id : `#${id}`
}

// 添加查看对局的方法
const handleViewMatch = (gameId: number) => {
  router.push({
    name: 'MatchHistory',
    query: {
      gameId: gameId.toString()
    }
  })
}

// 修改导出方法
const handleExport = () => {
  const exportData = {
    blacklist: blacklist.value,
    whitelist: whitelist.value
  }
  
  const data = JSON.stringify(exportData, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  
  const link = document.createElement('a')
  link.href = url
  link.download = '笔记本记录.json'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

// 修改导入方法
const handleImport = () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.json'
  
  input.onchange = async (e) => {
    const file = (e.target as HTMLInputElement).files?.[0]
    if (!file) return
    
    try {
      const text = await file.text()
      const data = JSON.parse(text)
      
      if (data && typeof data === 'object') {
        if (Array.isArray(data.blacklist)) {
          blacklist.value = data.blacklist
        }
        if (Array.isArray(data.whitelist)) {
          whitelist.value = data.whitelist
        }
        ElMessage.success('导入成功')
      } else {
        throw new Error('无效的文件格式')
      }
    } catch (error) {
      console.error('导入失败:', error)
      ElMessage.error('导入失败，请确保文件格式正确')
    }
  }
  
  input.click()
}

// 添加刷新方法
const handleRefresh = async () => {
  try {
    const response = await axios.get('/api/note_book/get_settings')
    if (response.data) {
      // 转换后端数据为前端格式
      blacklist.value = (response.data.blacklist || []).map((item: any) => ({
        id: Date.now() + Math.random(),
        summonerName: item.game_name,
        summonerId: item.summoner_id,
        region: item.region || '',
        reason: item.reason || '',
        details: item.details || '',
        gameId: item.game_id ? parseInt(item.game_id) : undefined,
        championId: item.champion_id,
        timestamp: item.timestamp
      }))
      
      whitelist.value = (response.data.whitelist || []).map((item: any) => ({
        id: Date.now() + Math.random(),
        summonerName: item.game_name,
        summonerId: item.summoner_id,
        region: item.region || '',
        reason: item.reason || '',
        details: item.details || '',
        gameId: item.game_id ? parseInt(item.game_id) : undefined,
        championId: item.champion_id,
        timestamp: item.timestamp
      }))

      await loadGameResources()
      ElMessage.success('刷新成功')
    }
  } catch (error) {
    console.error('刷新失败:', error)
    ElMessage.error('刷新失败')
  }
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
  padding-left: 0; /* 移除默认内边距 */
}

.team-indicator {
  width: 3px;
  height: 15px;
  /* border-radius: 2px; */
  margin-right: 4px;
}

.team-indicator.blue {
  background-color: var(--el-color-primary);
}

.team-indicator.red {
  background-color: var(--el-color-danger);
}

/* 移除旧的 team-tag 相关样式 */
.team-tag {
  display: none;
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

.game-select-wrapper {
  display: flex;
  gap: 10px;
  align-items: center;
  width: 100%;
}

.game-select-wrapper :deep(.el-select) {
  width: 100%;
}

.left-buttons {
  display: flex;
  gap: 10px;
}

.global-actions {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}
</style> 