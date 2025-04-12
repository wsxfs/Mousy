<template>
  <div class="champ-select-helper" :class="{ 'expanded': isExpanded }">
    <div class="main-content">
      <div class="title-bar">
        <span>对局助手</span>
        <div class="title-actions">
          <el-icon class="close-icon" @click="handleClose">
            <Close />
          </el-icon>
        </div>
      </div>
      
      <div class="content">
        <!-- 游戏模式信息 -->
        <div class="game-mode-info">
          <h3>当前游戏模式</h3>
          <p>{{ gameMode || '未知' }}</p>
        </div>

        <!-- 选择英雄信息 -->
        <div class="champ-select-info">
          <div class="champ-info">
            <!-- 候选席英雄 -->
            <div v-if="showBenchChampions" class="bench-champs">
              <h4>候选席英雄</h4>
              <div v-if="sortedBenchChampions.length > 0" class="bench-list">
                <div v-for="championId in sortedBenchChampions" 
                     :key="championId" 
                     class="bench-item"
                     @click="selectBenchChampion(championId)">
                  <img 
                    :src="getResourceUrl('champion_icons', championId)" 
                    :alt="'Champion ' + championId"
                    class="champion-icon"
                    :class="getChampionTierClass(championId)"
                  />
                  <el-tag 
                    v-if="getChampionTier(championId, selectedPosition)"
                    size="small"
                    :style="{ backgroundColor: getTierColor(getChampionTier(championId, selectedPosition) || 0), border: 'none', color: '#ffffff' }"
                    class="tier-tag">
                    T{{ getChampionTier(championId, selectedPosition) }}
                  </el-tag>
                </div>
              </div>
              <span v-else class="no-champ-info">无候选席英雄</span>
            </div>
            
            <!-- 当前英雄 -->
            <div class="current-champ">
              <h4>当前英雄</h4>
              <template v-if="wsStore.syncFrontData.current_champion">
                <div class="current-champ-info">
                  <div class="current-champ-container" 
                       @click="handleAutoSwapChange(!autoSwapEnabled)"
                       :class="{ 'locked': !autoSwapEnabled }">
                    <img 
                      :src="getResourceUrl('champion_icons', wsStore.syncFrontData.current_champion)" 
                      :alt="'Champion ' + wsStore.syncFrontData.current_champion"
                      class="champion-icon current"
                      :class="getChampionTierClass(wsStore.syncFrontData.current_champion)"
                    />
                    <el-tag 
                      v-if="getChampionTier(wsStore.syncFrontData.current_champion, selectedPosition)"
                      size="small"
                      :style="{ backgroundColor: getTierColor(getChampionTier(wsStore.syncFrontData.current_champion, selectedPosition) || 0), border: 'none', color: '#ffffff' }"
                      class="tier-tag current">
                      T{{ getChampionTier(wsStore.syncFrontData.current_champion, selectedPosition) }}
                    </el-tag>
                    <!-- 添加锁定状态对勾图标 -->
                    <div v-if="!autoSwapEnabled" class="check-overlay">
                      <el-icon class="check-icon"><Check /></el-icon>
                    </div>
                    <!-- 加载状态遮罩 -->
                    <div v-if="switchLoading" class="loading-overlay">
                      <el-icon class="loading-icon"><Loading /></el-icon>
                    </div>
                  </div>
                </div>
                
                <template v-if="gameModeMapping[gameMode || '']?.mode === 'ranked' && availablePositions.length > 0">
                  <div class="position-selector">
                    <h4>选择位置</h4>
                    <el-select 
                      v-model="selectedPosition"
                      size="small"
                      style="width: 120px">
                      <el-option
                        v-for="position in availablePositions"
                        :key="position"
                        :label="getPositionLabel(position)"
                        :value="position">
                      </el-option>
                    </el-select>
                  </div>
                </template>

                <!-- 添加召唤师技能部分 -->
                <div v-if="championDetail?.summonerSpells" class="recommendations">
                  <el-collapse v-model="activeCollapse">
                    <!-- 召唤师技能部分 -->
                    <el-collapse-item title="召唤师技能" name="spells">
                      <div class="section">
                        <div v-loading="isGuideLoading || isGuideResourcesLoading" class="spells-container">
                          <div v-for="(spell, index) in championDetail.summonerSpells"
                               :key="index"
                               class="spell-set"
                               :class="{ 'selected': selectedSpellIndex === index }"
                               @click="selectedSpellIndex = index">
                            <div class="spell-content">
                              <div class="spell-icons">
                                <img v-for="icon in spell.icons"
                                     :key="icon"
                                     :src="getResourceUrl('summoner_spell_icons', icon)"
                                     class="spell-icon">
                              </div>
                              <div class="spell-stats">
                                <span class="stat-item">
                                  <span class="stat-label">胜率:</span>
                                  <span class="stat-value">{{ (spell.win / spell.play * 100).toFixed(1) }}%</span>
                                </span>
                                <span class="stat-item">
                                  <span class="stat-label">使用率:</span>
                                  <span class="stat-value">{{ (spell.pickRate * 100).toFixed(1) }}%</span>
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </el-collapse-item>

                    <!-- 符文推荐部分 -->
                    <el-collapse-item title="符文推荐" name="runes">
                      <div class="section">
                        <div class="section-header">
                          <el-button 
                            type="primary" 
                            size="small"
                            :disabled="selectedRuneIndex === null"
                            @click="applyRunes">
                            应用符文
                          </el-button>
                        </div>
                        <div v-loading="isGuideLoading || isGuideResourcesLoading" class="runes-container">
                          <div v-for="(rune, index) in championDetail.perks"
                               :key="index"
                               :class="['rune-set', { 'selected': selectedRuneIndex === index }]"
                               @click="selectedRuneIndex = index">
                            <div class="rune-trees">
                              <img :src="getResourceUrl('perk_icons', rune.primaryId)" 
                                   :alt="'Primary ' + rune.primaryId"
                                   class="tree-icon">
                              <img :src="getResourceUrl('perk_icons', rune.secondaryId)" 
                                   :alt="'Secondary ' + rune.secondaryId"
                                   class="tree-icon">
                            </div>
                            <div class="rune-icons">
                              <img v-for="perkId in rune.perks"
                                   :key="perkId"
                                   :src="getResourceUrl('perk_icons', perkId)"
                                   :alt="'Perk ' + perkId"
                                   class="rune-icon">
                            </div>
                            <div class="rune-stats">
                              <span>胜率: {{ (rune.win / rune.play * 100).toFixed(1) }}%</span>
                              <span>使用率: {{ (rune.pickRate * 100).toFixed(1) }}%</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </el-collapse-item>

                    <!-- 装备推荐部分 -->
                    <el-collapse-item title="装备推荐" name="items">
                      <div class="section">
                        <div class="section-header">
                          <div class="header-actions">
                            <el-button 
                              type="primary" 
                              size="small"
                              @click="toggleSelectAllItems">
                              {{ isAllSelected ? '取消全选' : '全选' }}
                            </el-button>
                            <el-button 
                              type="primary" 
                              size="small"
                              :disabled="!hasValidItemSelection"
                              @click="applyItems">
                              应用装备
                            </el-button>
                          </div>
                        </div>
                        
                        <!-- 起始装备 -->
                        <div class="item-group" v-if="championDetail?.items?.startItems?.length">
                          <h4>
                            起始装备
                            <div class="stats-header">
                              <span>胜率</span>
                              <span>使用率</span>
                            </div>
                          </h4>
                          <div v-for="(build, index) in championDetail.items?.startItems"
                               :key="index"
                               :class="['build-row', { selected: selectedStartItems.includes(index) }]"
                               @click="toggleItemSelection(index, 'start')">
                            <div class="item-icons">
                              <img v-for="icon in build.icons"
                                   :key="icon"
                                   :src="getResourceUrl('item_icons', icon)"
                                   class="item-icon">
                            </div>
                            <div class="build-stats">
                              <span>{{ (build.win / build.play * 100).toFixed(1) }}%</span>
                              <span>{{ (build.pickRate * 100).toFixed(1) }}%</span>
                            </div>
                          </div>
                        </div>

                        <!-- 鞋子选择 -->
                        <div class="item-group" v-if="championDetail?.items?.boots?.length">
                          <h4>
                            鞋子选择
                            <div class="stats-header">
                              <span>胜率</span>
                              <span>使用率</span>
                            </div>
                          </h4>
                          <div v-for="(build, index) in championDetail.items?.boots"
                               :key="index"
                               :class="['build-row', { selected: selectedBoots.includes(index) }]"
                               @click="toggleItemSelection(index, 'boots')">
                            <div class="item-icons">
                              <img v-for="icon in build.icons"
                                   :key="icon"
                                   :src="getResourceUrl('item_icons', icon)"
                                   class="item-icon">
                            </div>
                            <div class="build-stats">
                              <span>{{ (build.win / build.play * 100).toFixed(1) }}%</span>
                              <span>{{ (build.pickRate * 100).toFixed(1) }}%</span>
                            </div>
                          </div>
                        </div>

                        <!-- 核心装备 -->
                        <div class="item-group" v-if="championDetail?.items?.coreItems?.length">
                          <h4>
                            核心装备
                            <div class="stats-header">
                              <span>胜率</span>
                              <span>使用率</span>
                            </div>
                          </h4>
                          <div v-for="(build, index) in championDetail.items?.coreItems"
                               :key="index"
                               :class="['build-row', { selected: selectedCoreItems.includes(index) }]"
                               @click="toggleItemSelection(index, 'core')">
                            <div class="item-icons">
                              <img v-for="icon in build.icons"
                                   :key="icon"
                                   :src="getResourceUrl('item_icons', icon)"
                                   class="item-icon">
                            </div>
                            <div class="build-stats">
                              <span>{{ (build.win / build.play * 100).toFixed(1) }}%</span>
                              <span>{{ (build.pickRate * 100).toFixed(1) }}%</span>
                            </div>
                          </div>
                        </div>

                        <!-- 可选装备池 -->
                        <div class="item-group" v-if="championDetail?.items?.lastItems?.length">
                          <h4>可选装备池</h4>
                          <div class="build-row selected">
                            <div class="last-items-grid">
                              <div v-for="itemId in championDetail.items?.lastItems"
                                   :key="itemId"
                                   class="last-item">
                                <img :src="getResourceUrl('item_icons', itemId)"
                                     class="item-icon"
                                     :title="getItemName(itemId)">
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </el-collapse-item>
                  </el-collapse>
                </div>
              </template>
              <span v-else class="no-champ-info">未选择英雄</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 展开按钮 -->
    <div class="expand-button" @click="toggleExpand">
      <el-icon :class="{ 'rotated': isExpanded }">
        <ArrowRight />
      </el-icon>
    </div>

    <!-- 展开后的内容 -->
    <div class="drawer-content">
      <div class="drawer-inner">
        <DrawerAnalysis />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch, nextTick } from 'vue'
import { useGameStateStore } from '../../stores/gameState'
import { useWebSocketStore } from '../../stores/websocket'
import { Close, Loading, Check, ArrowRight } from '@element-plus/icons-vue'
import axios from 'axios'
import { ElMessage} from 'element-plus'
import DrawerAnalysis from './components/DrawerAnalysis.vue'

const gameStateStore = useGameStateStore()
const wsStore = useWebSocketStore()
const emit = defineEmits(['close'])

// 游戏资源状态
const gameResources = ref<Record<string, Record<string | number, string>>>({})
const contentRef = ref<HTMLElement | null>(null)

// 添加更详细的符文相关接口定义
interface RuneData {
  primaryId: number    // 主系符文ID
  secondaryId: number  // 副系符文ID
  perks: number[]      // 所有选择的符文ID（包括主系、副系和属性符文）
  icons: number[]      // 所有符文图标ID
  win: number
  play: number
  pickRate: number
}

interface ChampionDetail {
  perks: RuneData[]
  items: {
    startItems: Array<{
      icons: number[]
      win: number
      play: number
      pickRate: number
    }>
    coreItems: Array<{
      icons: number[]
      win: number
      play: number
      pickRate: number
    }>
    boots: Array<{
      icons: number[]
      win: number
      play: number
      pickRate: number
    }>
    lastItems: number[]
  }
  summary: {
    name: string
  }
  summonerSpells: Array<{
    icons: number[]
    win: number
    play: number
    pickRate: number
  }>
}

// 改 championDetail 类型
const championDetail = ref<ChampionDetail | null>(null)
const selectedRuneIndex = ref<number>(0)
const selectedStartItems = ref<number[]>([0])
const selectedCoreItems = ref<number[]>([0])
const selectedBoots = ref<number[]>([0])
const selectedSpellIndex = ref<number>(0)

// 添加OPGG英雄梯度数据接口
interface ChampionTierData {
  championId: number
  tier: number
  position: string | null
}

// 添加状态
const championTierData = ref<ChampionTierData[]>([])

// 添加获取英雄梯度数据的方法
const fetchChampionTierList = async () => {
  try {
    const modeInfo = gameModeMapping[gameMode.value || ''] || { mode: 'ranked', hasBench: false }
    const params = new URLSearchParams({
      region: 'kr',
      mode: modeInfo.mode,
      tier: 'platinum_plus'
    })

    const response = await axios.post(
      '/api/match_data/champion_ranking_data/tier_list',
      params,
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }
    )

    // 根据返回数据格式进行不同处理
    if (Array.isArray(response.data.data)) {
      // 无位置信息的数据格式
      championTierData.value = response.data.data.map((champion: any) => ({
        championId: champion.championId,
        tier: champion.tier,
        position: null
      }))
    } else {
      // 有位置信息的数据格式
      championTierData.value = Object.entries(response.data.data).flatMap(([position, champions]) => 
        (champions as any[]).map(champion => ({
          championId: champion.championId,
          tier: champion.tier,
          position: position
        }))
      )
    }
  } catch (error) {
    console.error('获取英雄梯度数据失败:', error)
    ElMessage.error('获取英雄梯度数据失败')
  }
}

// 添加计算属性：排序后的候选席英雄
const sortedBenchChampions = computed(() => {
  if (!wsStore.syncFrontData.bench_champions) return []
  
  const position = selectedPosition.value
  return [...wsStore.syncFrontData.bench_champions].sort((a, b) => {
    const tierA = getChampionTier(a, position) || 999
    const tierB = getChampionTier(b, position) || 999
    return tierA - tierB
  })
})

onMounted(async () => {
  await gameStateStore.fetchGameMode()
  
  // 确保在组件挂载后请求初始状态
  if (!wsStore.isConnected) {
    // 请求初始状态
    window.electron.ipcRenderer.send('request-initial-state')
  }
  
  // 获取英雄梯度数据
  await fetchChampionTierList()
})

// 添加本地状态缓存
const localSelections = ref<{
  runeIndex: number
  startItems: number[]
  boots: number[]
  coreItems: number[]
  spellIndex: number
  scrollTop: number
}>({
  runeIndex: 0,
  startItems: [0],
  boots: [0],
  coreItems: [0],
  spellIndex: 0,
  scrollTop: 0
})

// 精确监听英雄ID变化
watch(
  () => wsStore.syncFrontData.current_champion,
  async (newVal, oldVal) => {
    if (newVal !== oldVal) {
      // 保存当前滚动位置
      localSelections.value.scrollTop = contentRef.value?.scrollTop || 0
      
      if (newVal) {
        // 当英雄变化时加载新数据
        await fetchChampionDetail(newVal)
      } else {
        // 清空英雄时重置所有状态
        championDetail.value = null
        selectedPosition.value = 'none'
        availablePositions.value = []
      }
      
      // 恢复滚动位置
      nextTick(() => {
        if (contentRef.value && localSelections.value.scrollTop) {
          contentRef.value.scrollTop = localSelections.value.scrollTop
        }
      })
    }
  }
)

const gameMode = computed(() => gameStateStore.gameMode)

// 修改 ResourceRequest 接口定义
interface ResourceRequest {
  champion_icons: number[]
  spell_icons: number[]
  item_icons: number[]
  rune_icons: number[]
}

// 修改监听逻辑，分监听当前英雄和候选席英雄变化
watch(
  () => wsStore.syncFrontData.current_champion,
  async (newChampionId, oldChampionId) => {
    console.log('当前英雄变化:', { new: newChampionId, old: oldChampionId })
    if (newChampionId && newChampionId !== oldChampionId) {
      try {
        // 保存当前滚动位置
        localSelections.value.scrollTop = contentRef.value?.scrollTop || 0
        
        // 重置位置选择
        selectedPosition.value = 'none'
        // 重置折叠面板状态
        activeCollapse.value = ['spells', 'runes', 'items']
        
        // 先加载英雄资源
        await loadGameResources(newChampionId, 'hero')
        
        // 如果是首次加载，才获取位置信息
        if (selectedPosition.value === 'none') {
          await fetchAvailablePositions(newChampionId)
        }
        
        // 恢复滚动位置
        nextTick(() => {
          if (contentRef.value && localSelections.value.scrollTop) {
            contentRef.value.scrollTop = localSelections.value.scrollTop
          }
        })
        
        // 异步加载攻略数据，不等待结果
        loadGuideData(newChampionId).catch(error => {
          console.error('异步加载攻略数据失败:', error)
          ElMessage.error('加载攻略数据失败')
        })
      } catch (error) {
        console.error('切换英雄时加载数据失败:', error)
        ElMessage.error('加载数据失败')
      }
    } else if (!newChampionId) {
      // 清空英雄时重置所有状态
      championDetail.value = null
      selectedPosition.value = 'none'
      availablePositions.value = []
    }
  }
)

// 修改候选席英雄监听
watch(
  () => wsStore.syncFrontData.bench_champions,
  async (newBenchChampions) => {
    console.log('候选席英雄变化:', newBenchChampions)
    if (newBenchChampions && newBenchChampions.length > 0) {
      // 构建资源请求对象，只包含英雄图标
      const resourceRequest: ResourceRequest = {
        champion_icons: newBenchChampions,
        spell_icons: [],
        item_icons: [],
        rune_icons: []
      }

      try {
        const response = await axios.post(
          '/api/common/game_resource/batch_get_resources',
          resourceRequest
        )
        
        // 合并新的资源，保留现有的其他资源
        gameResources.value = {
          ...gameResources.value,
          champion_icons: {
            ...gameResources.value.champion_icons,
            ...response.data.champion_icons
          }
        }
      } catch (error) {
        console.error('加载候选席英雄资源失败:', error)
      }
    }
  },
  {
    immediate: true // 确保组件挂载时也执行一次
  }
)

// 修改获取资源URL法，使用与 ChampionDetail.vue 相同的类型映射
const getResourceUrl = (type: string, id: number): string => {
  const typeMapping: Record<string, string> = {
    'champion_icons': 'champion_icons',
    'summoner_spell_icons': 'spell_icons',
    'item_icons': 'item_icons',
    'perk_icons': 'rune_icons'
  }

  const backendType = typeMapping[type]
  const resources = gameResources.value[backendType]
  if (resources?.[id]) {
    return `data:image/png;base64,${resources[id]}`
  }
  return '/placeholder.png'
}

const handleClose = () => {
  // 通过 electron 的 preload 脚本暴露的方法关闭窗口
  window.electron.ipcRenderer.send('close-champ-select')
}

// 计算属性
const hasValidItemSelection = computed(() => {
  const items = championDetail.value?.items
  if (!items) return false
  
  // 检查每个装备组是否有数据，如果有数据则必须有选中项
  const hasValidStart = !items.startItems?.length || selectedStartItems.value.length > 0
  const hasValidBoots = !items.boots?.length || selectedBoots.value.length > 0
  const hasValidCore = !items.coreItems?.length || selectedCoreItems.value.length > 0
  
  // 至少要有一个装备组有数据且被选中
  const hasAnySelection = (items.startItems?.length && selectedStartItems.value.length > 0) ||
                         (items.boots?.length && selectedBoots.value.length > 0) ||
                         (items.coreItems?.length && selectedCoreItems.value.length > 0)
  
  return hasValidStart && hasValidBoots && hasValidCore && hasAnySelection
})

// 修改游戏模式映射，增加候选席信息
const gameModeMapping: Record<string, { mode: string, hasBench: boolean }> = {
  'ARAM': { mode: 'aram', hasBench: true },
  'CLASSIC': { mode: 'ranked', hasBench: false },
  'URF': { mode: 'urf', hasBench: false },
  'PRACTICETOOL': { mode: 'ranked', hasBench: false }
}

// 添加位置相关的状态
const availablePositions = ref<string[]>([])
const selectedPosition = ref('none')

// 修改获取可用位置的方法
const fetchAvailablePositions = async (championId: number) => {
  try {
    if (gameModeMapping[gameMode.value || '']?.mode !== 'ranked') {
      availablePositions.value = ['none']
      return
    }

    const params = new URLSearchParams({
      champion_id: championId.toString(),
      region: 'kr',
      tier: 'platinum_plus'
    })

    const response = await axios.post(
      '/api/match_data/champion_ranking_data/champion_positions',
      params,
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }
    )

    availablePositions.value = response.data
    // 只在位置未选择时设置默认位置
    if (selectedPosition.value === 'none') {
      selectedPosition.value = availablePositions.value[0] || 'all'
    }
  } catch (error) {
    console.error('获取位置信息失败:', error)
    ElMessage.error('获取位置信息失败')
  }
}

// 添加攻略加载状态
const isGuideLoading = ref(false)

// 添加攻略资源加载状态
const isGuideResourcesLoading = ref(false)

// 修改 loadGameResources 方法，分离资源加载
const loadGameResources = async (championId: number, type: 'hero' | 'guide' = 'hero') => {
  try {
    if (type === 'guide') {
      isGuideResourcesLoading.value = true
    }

    const resourceRequest: ResourceRequest = {
      champion_icons: [],
      spell_icons: [],
      item_icons: [],
      rune_icons: []
    }

    if (type === 'hero') {
      // 只加载英雄图标
      resourceRequest.champion_icons = [championId]
    } else if (type === 'guide' && championDetail.value) {
      // 加载攻略相关的所有资源
      // 添加召唤师技能图标收集逻辑
      if (championDetail.value.summonerSpells) {
        championDetail.value.summonerSpells.forEach(spell => {
          resourceRequest.spell_icons.push(...spell.icons)
        })
      }

      // 收集所需的符文图标ID
      if (championDetail.value.perks) {
        championDetail.value.perks.forEach((rune) => {
          // 添加主系和副系符文树图标
          resourceRequest.rune_icons.push(rune.primaryId, rune.secondaryId)
          // 添加所有选择的符文图标
          resourceRequest.rune_icons.push(...rune.perks)
        })
      }
      
      // 收集所需的装备图标ID
      if (championDetail.value.items) {
        // 添加起始装备图标
        championDetail.value.items.startItems?.forEach((build) => {
          resourceRequest.item_icons.push(...build.icons)
        })
        // 添加核心装备图标
        championDetail.value.items.coreItems?.forEach((build) => {
          resourceRequest.item_icons.push(...build.icons)
        })
        // 添加鞋子装备图标
        championDetail.value.items.boots?.forEach((build) => {
          resourceRequest.item_icons.push(...build.icons)
        })
        // 添加可选装备池图标
        if (championDetail.value.items.lastItems) {
          resourceRequest.item_icons.push(...championDetail.value.items.lastItems)
        }
      }

      // 去重
      resourceRequest.spell_icons = [...new Set(resourceRequest.spell_icons)]
      resourceRequest.rune_icons = [...new Set(resourceRequest.rune_icons)]
      resourceRequest.item_icons = [...new Set(resourceRequest.item_icons)]
    }

    const response = await axios.post(
      '/api/common/game_resource/batch_get_resources',
      resourceRequest
    )

    // 合并新的资源
    gameResources.value = {
      ...gameResources.value,
      ...(type === 'hero' ? {
        champion_icons: {
          ...gameResources.value.champion_icons,
          [championId]: response.data.champion_icons[championId]
        }
      } : {
        spell_icons: {
          ...gameResources.value.spell_icons,
          ...response.data.spell_icons
        },
        rune_icons: {
          ...gameResources.value.rune_icons,
          ...response.data.rune_icons
        },
        item_icons: {
          ...gameResources.value.item_icons,
          ...response.data.item_icons
        }
      })
    }
  } catch (error) {
    console.error('加载游戏资源失败:', error)
    ElMessage.error('加载游戏资源失败')
  } finally {
    if (type === 'guide') {
      isGuideResourcesLoading.value = false
    }
  }
}

// 修改 fetchChampionDetail 方法
const fetchChampionDetail = async (championId: number) => {
  try {
    // 先重置相关状态
    championDetail.value = null
    selectedRuneIndex.value = 0
    selectedStartItems.value = [0]
    selectedBoots.value = [0]
    selectedCoreItems.value = [0]
    selectedSpellIndex.value = 0
    
    // 如果是首次加载，才获取位置信息
    if (selectedPosition.value === 'none') {
      await fetchAvailablePositions(championId)
    }
    
    // 先加载英雄资源
    await loadGameResources(championId, 'hero')
    
    // 异步加载攻略数据，不等待结果
    loadGuideData(championId).catch(error => {
      console.error('异步加载攻略数据失败:', error)
      ElMessage.error('加载攻略数据失败')
    })
  } catch (error) {
    console.error('获取英雄详情失败:', error)
    ElMessage.error('获取英雄详情失败')
  }
}

// 修改 loadGuideData 方法
const loadGuideData = async (championId: number) => {
  try {
    isGuideLoading.value = true
    const modeInfo = gameModeMapping[gameMode.value || ''] || { mode: 'ranked', hasBench: false }
    const params = new URLSearchParams({
      champion_id: championId.toString(),
      region: 'kr',
      mode: modeInfo.mode,
      position: selectedPosition.value,
      tier: 'platinum_plus'
    })

    const response = await axios.post(
      '/api/match_data/champion_ranking_data/champion_build',
      params,
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }
    )

    // 修改数据完整性检查
    if (!response.data.data?.perks?.length) {
      throw new Error('符文数据不完整')
    }

    // 确保至少有一种装备数据
    const items = response.data.data?.items
    if (!items || (
      !items.startItems?.length && 
      !items.boots?.length && 
      !items.coreItems?.length && 
      !items.lastItems?.length
    )) {
      throw new Error('装备数据不完整')
    }

    // 更新攻略数据
    championDetail.value = response.data.data
    
    // 异步加载攻略资源，不等待结果
    loadGameResources(championId, 'guide').catch(error => {
      console.error('异步加载攻略资源失败:', error)
      ElMessage.error('加载攻略资源失败')
    })
  } catch (error) {
    console.error('加载攻略数据失败:', error)
    ElMessage.error('加载攻略数据失败')
  } finally {
    isGuideLoading.value = false
  }
}

// 修改监听位置变化的逻辑
watch(selectedPosition, async (newPosition, oldPosition) => {
  if (wsStore.syncFrontData.current_champion && newPosition !== 'none' && newPosition !== oldPosition) {
    // 异步加载攻略数据，不等待结果
    loadGuideData(wsStore.syncFrontData.current_champion).catch(error => {
      console.error('切换位置加载数据失败:', error)
      ElMessage.error('加载数据失败')
    })
  }
})

// 修改装选择方法
const toggleItemSelection = (index: number, type: 'start' | 'boots' | 'core') => {
  const selectionMap = {
    'start': selectedStartItems,
    'boots': selectedBoots,
    'core': selectedCoreItems
  }
  
  const selection = selectionMap[type]
  const currentIndex = selection.value.indexOf(index)
  
  if (currentIndex === -1) {
    selection.value.push(index)
  } else {
    if (selection.value.length > 1) {
      selection.value.splice(currentIndex, 1)
    }
  }
}

// 修改应用符文方法，添加空值检查
const applyRunes = async () => {
  try {
    if (!championDetail.value?.perks) {
      ElMessage.warning('符文数据不完整')
      return
    }

    const selectedRune = championDetail.value.perks[selectedRuneIndex.value]
    const winRate = (selectedRune.win / selectedRune.play * 100).toFixed(1)
    const pickRate = (selectedRune.pickRate * 100).toFixed(1)
    
    const perksData = {
      name: `${championDetail.value.summary.name}|胜率${winRate}%|使用率${pickRate}%(Best Wishes From Mousy🐹)`,
      primary_style_id: selectedRune.primaryId,
      sub_style_id: selectedRune.secondaryId,
      selected_perk_ids: selectedRune.perks
    }

    const response = await axios.post('/api/match_data/perks_and_items/apply_perks', perksData)
    
    if (response.data.success) {
      ElMessage.success(response.data.message || '符文应用成功')
    } else {
      ElMessage.error(response.data.message || '符文应用失败')
    }
  } catch (error: any) {
    console.error('应用符文失败:', error)
    ElMessage.error(error.response?.data?.detail || '应用符文失败')
  }
}

// 修改应用装备方法，添加空值检查
const applyItems = async () => {
  try {
    if (!championDetail.value?.items) {
      ElMessage.warning('装备数据不完整')
      return
    }

    const items = championDetail.value.items
    const itemsData = {
      title: championDetail.value.summary.name,
      source: 'kr',
      tier: 'platinum_plus',
      mode: gameModeMapping[gameMode.value || '']?.mode || 'ranked',
      position: selectedPosition.value,
      associatedChampions: [wsStore.syncFrontData.current_champion],
      associatedMaps: [gameModeMapping[gameMode.value || '']?.mode === 'aram' ? 12 : 11],
      items: {
        startItems: items.startItems?.length ? selectedStartItems.value.map(index => ({
          icons: items.startItems[index].icons,
          winRate: (items.startItems[index].win / items.startItems[index].play * 100).toFixed(1),
          pickRate: (items.startItems[index].pickRate * 100).toFixed(1)
        })) : [],
        boots: items.boots?.length ? selectedBoots.value.map(index => ({
          icons: items.boots[index].icons,
          winRate: (items.boots[index].win / items.boots[index].play * 100).toFixed(1),
          pickRate: (items.boots[index].pickRate * 100).toFixed(1)
        })) : [],
        coreItems: items.coreItems?.length ? selectedCoreItems.value.map(index => ({
          icons: items.coreItems[index].icons,
          winRate: (items.coreItems[index].win / items.coreItems[index].play * 100).toFixed(1),
          pickRate: (items.coreItems[index].pickRate * 100).toFixed(1)
        })) : [],
        lastItems: items.lastItems || []
      }
    }

    const response = await axios.post('/api/match_data/perks_and_items/apply_items', itemsData)
    
    if (response.data.success) {
      ElMessage.success(response.data.message || '出装应用成功')
    } else {
      ElMessage.error(response.data.message || '出装应用失败')
    }
  } catch (error: any) {
    console.error('应用出装失败:', error)
    ElMessage.error(error.response?.data?.detail || '应用出装失败')
  }
}

// 添加一个获取装备名称的方法
const getItemName = (itemId: number): string => {
  // 这里可以添加获取装备名称的逻辑
  // 暂时返回装备ID的字符串形式
  return `装备 ${itemId}`
}

// 添加全选状态计算属性
const isAllSelected = computed(() => {
  const items = championDetail.value?.items
  if (!items) return false
  
  const hasStartItems = items.startItems?.length > 0
  const hasBoots = items.boots?.length > 0
  const hasCoreItems = items.coreItems?.length > 0
  
  const allStartItemsSelected = !hasStartItems || selectedStartItems.value.length === items.startItems.length
  const allBootsSelected = !hasBoots || selectedBoots.value.length === items.boots.length
  const allCoreItemsSelected = !hasCoreItems || selectedCoreItems.value.length === items.coreItems.length
  
  return allStartItemsSelected && allBootsSelected && allCoreItemsSelected
})

// 修改切换全选/取消全选方法
const toggleSelectAllItems = () => {
  const items = championDetail.value?.items
  if (!items) return
  
  if (isAllSelected.value) {
    // 取消全选，每类只保留第一个选项
    selectedStartItems.value = items.startItems?.length ? [0] : []
    selectedBoots.value = items.boots?.length ? [0] : []
    selectedCoreItems.value = items.coreItems?.length ? [0] : []
  } else {
    // 全选所有选项
    selectedStartItems.value = items.startItems?.map((_, index) => index) || []
    selectedBoots.value = items.boots?.map((_, index) => index) || []
    selectedCoreItems.value = items.coreItems?.map((_, index) => index) || []
  }
}

// 修改 selectBenchChampion 方法
const selectBenchChampion = async (championId: number) => {
  try {
    // 调用后端接口行英雄交换
    const response = await axios.post('/api/common/common_control/bench_swap', null, {
      params: { champion_id: championId }
    })
    
    if (response.data.message) {
      ElMessage.success(response.data.message)
    }
  } catch (error) {
    console.error('交换候选席英雄失败:', error)
    ElMessage.error('交换候选席英雄失败')
  }
}

// 添加位置标签映射
const positionLabels: Record<string, string> = {
  'top': '上路',
  'jungle': '打野',
  'mid': '中路',
  'bottom': '下路',
  'support': '辅助',
  'all': '所有位置'
}

// 获取位置显示标签
const getPositionLabel = (position: string) => {
  return positionLabels[position] || position
}

// 修改获取Tier颜色的方法
const getTierColor = (tier: number): string => {
    switch (tier) {
        case 0:
            return '#ff0000'
        case 1:
            return '#ff4400'
        case 2:
            return '#FFA500'
        case 3:
            return '#B9CA2E'
        case 4:
            return '#85CB62'
        case 5:
            return '#808080'
        default:
            return '#808080'
    }
}

// 监听游戏模式变化
watch(gameMode, async () => {
  await fetchChampionTierList()
})

// 修改获取英雄 tier 的方法
const getChampionTier = (championId: number, position: string = 'all'): number | undefined => {
  // 如果有位置信息且指定了具体位置，则按位置查找
  if (position !== 'all') {
    const championData = championTierData.value.find(c => 
      c.championId === championId && c.position === position
    )
    if (championData) return championData.tier
  }
  
  // 如果没有找到指定位置的数据，或者不需要位置信息，
  // 则查找 position 为 null 的数据或第一个匹配的数据
  const championData = championTierData.value.find(c => 
    c.championId === championId && (c.position === null || position === 'all')
  )
  return championData?.tier
}

// 修改获取英雄 tier 类名的方法
const getChampionTierClass = (championId: number): string => {
  const position = selectedPosition.value
  const tier = getChampionTier(championId, position)
  switch (tier) {
    case 1: return 'tier-1'
    case 2: return 'tier-2'
    case 3: return 'tier-3'
    case 4: return 'tier-4'
    case 5: return 'tier-5'
    default: return ''
  }
}

// 添加计算性判断是否显示候选席
const showBenchChampions = computed(() => {
  const currentMode = gameMode.value || ''
  return gameModeMapping[currentMode]?.hasBench ?? false
})

// 添加自动换人相关的状态
const autoSwapEnabled = ref(true) // 默认开启
const switchLoading = ref(false)

// 修改处理自动换人开关变化的方法
const handleAutoSwapChange = async (value: boolean) => {
  if (switchLoading.value) return // 防止重复点击
  
  switchLoading.value = true
  try {
    const endpoint = value ? 'swap_champion_on' : 'swap_champion_off'
    const response = await axios.get(`/api/champ_select_helper/${endpoint}`)
    
    if (response.data.success) { // 假设后端返回 success 字段表示操作成功
      autoSwapEnabled.value = value // 只在成功时更新状态
      ElMessage.success(response.data.message)
    } else {
      throw new Error(response.data.message || '操作失败')
    }
  } catch (error: any) {
    console.error('切换自动换人状态失败:', error)
    ElMessage.error(error.message || '切换自动换人状态失败')
    // 不需要手动恢复状态，因为状态只在成功时更新
  } finally {
    switchLoading.value = false
  }
}

const activeCollapse = ref(['spells', 'runes', 'items']) // 默认全部展开

const isExpanded = ref(false)

const toggleExpand = () => {
  isExpanded.value = !isExpanded.value
  // 通知主进程调整窗口大小
  window.electron.ipcRenderer.send('resize-champ-select', {
    width: isExpanded.value ? 800 : 400
  })
}
</script>

<style scoped>
.champ-select-helper {
  position: relative;
  width: 100%;
  height: 100vh;
  display: flex;
  transition: all 0.3s ease;
  background: var(--el-bg-color);
}

.main-content {
  width: 400px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.content {
  flex: 1;
  padding: 12px;
  overflow-y: auto;
}

/* 添加抽屉相关样式 */
.expand-button {
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 24px;
  height: 48px;
  background: var(--el-color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-radius: 0 4px 4px 0;
  z-index: 100;
  transition: all 0.3s ease;
}

.expand-button:hover {
  background: var(--el-color-primary-dark-2);
}

.expand-button .el-icon {
  color: white;
  transition: transform 0.3s ease;
}

.expand-button .rotated {
  transform: rotate(180deg);
}

.drawer-content {
  width: 0;
  overflow: hidden;
  transition: width 0.3s ease;
  background: var(--el-bg-color);
  border-left: 1px solid var(--el-border-color-light);
}

.champ-select-helper.expanded .drawer-content {
  width: 400px;
}

.drawer-inner {
  width: 400px;
  height: 100%;
  padding: 16px;
  overflow-y: auto;
}

/* 保留原有样式 */
.title-bar {
  -webkit-app-region: drag;
  height: 32px;
  background: var(--el-color-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
}

.close-icon {
  -webkit-app-region: no-drag;
  cursor: pointer;
  font-size: 20px;
}

.game-mode-info {
  text-align: center;
}

.game-mode-info h3 {
  margin-bottom: 10px;
  color: var(--el-text-color-primary);
}

.game-mode-info p {
  font-size: 18px;
  color: var(--el-color-primary);
}

/* 添加新的样式 */
.recommendations {
  margin-top: 20px;
  width: 100%;
}

.section {
  background: var(--el-bg-color);
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 12px;
  box-shadow: var(--el-box-shadow-lighter);
  width: 100%;
  box-sizing: border-box;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.runes-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.rune-set {
  padding: 12px;
  border: 1px solid var(--el-border-color);
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.rune-set.selected {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}

.item-group {
  margin-bottom: 12px;
}

.build-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px;
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
  margin-bottom: 6px;
  cursor: pointer;
  min-height: 40px;
}

.build-row.selected {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}

/* 继续保留其他原有样式... */
.item-icons {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

.item-icon {
  width: 28px;
  height: 28px;
  border-radius: 4px;
}

.build-stats {
  display: grid;
  grid-template-columns: repeat(2, 80px);
  text-align: left;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-left: auto;
  gap: 8px;
}

/* 添加或修改符文相关样式 */
.rune-trees {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.tree-icon {
  width: 20px;
  height: 20px;
  border-radius: 3px;
}

.rune-icons {
  display: flex;
  gap: 8px;
  flex-wrap: nowrap;
  margin-bottom: 4px;
  align-items: center;
}

.rune-icon {
  width: 25px;
  height: 25px;
  border-radius: 3px;
}

.rune-stats {
  display: grid;
  grid-template-columns: repeat(2, auto);
  gap: 8px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

/* 添加标题行样式 */
.item-group h4 {
  margin-bottom: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 8px;
}

/* 修改标题行统计列样式 */
.stats-header {
  display: grid;
  grid-template-columns: repeat(2, 80px);
  text-align: left;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-left: auto;
  gap: 8px;
}

/* 修改英雄图标样式 */
.champion-icon {
  width: 36px;
  height: 36px;
  border-radius: 6px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.2s;
  border: 2px solid transparent;
}

/* T1英雄光圈 - 红色(OP) */
.champion-icon.tier-1 {
  border-color: #f5222d;  /* 鲜艳的红色 */
  box-shadow: 0 0 8px rgba(245, 34, 45, 0.7);
}

/* T2英雄光圈 - 橙色(强势) */
.champion-icon.tier-2 {
  border-color: #fa8c16;  /* 橙色 */
  box-shadow: 0 0 8px rgba(250, 140, 22, 0.7);
}

/* T3英雄光圈 - 绿色(平衡) */
.champion-icon.tier-3 {
  border-color: #52c41a;  /* 绿色 */
  box-shadow: 0 0 8px rgba(82, 196, 26, 0.6);
}

/* T4英雄光圈 - 蓝色(较弱) */
.champion-icon.tier-4 {
  border-color: #1890ff;  /* 蓝色 */
  box-shadow: 0 0 8px rgba(24, 144, 255, 0.6);
}

/* T5英雄光圈 - 灰色(弱势) */
.champion-icon.tier-5 {
  border-color: #8c8c8c;  /* 灰色 */
  box-shadow: 0 0 8px rgba(140, 140, 140, 0.6);
}

/* 当前英雄的特殊样式 */
.champion-icon.current {
  width: 48px;
  height: 48px;
}

/* 当前英雄的光圈效果加强 */
.champion-icon.current.tier-1 {
  box-shadow: 0 0 12px rgba(245, 34, 45, 0.9);
}

.champion-icon.current.tier-2 {
  box-shadow: 0 0 12px rgba(250, 140, 22, 0.9);
}

.champion-icon.current.tier-3 {
  box-shadow: 0 0 12px rgba(82, 196, 26, 0.8);
}

.champion-icon.current.tier-4 {
  box-shadow: 0 0 12px rgba(24, 144, 255, 0.8);
}

.champion-icon.current.tier-5 {
  box-shadow: 0 0 12px rgba(140, 140, 140, 0.8);
}

/* 悬停效果 */
.champion-icon:hover {
  transform: scale(1.1);
}

.champion-icon.tier-1:hover {
  box-shadow: 0 0 16px rgba(245, 34, 45, 1);
}

.champion-icon.tier-2:hover {
  box-shadow: 0 0 16px rgba(250, 140, 22, 1);
}

.champion-icon.tier-3:hover {
  box-shadow: 0 0 16px rgba(82, 196, 26, 1);
}

.champion-icon.tier-4:hover {
  box-shadow: 0 0 16px rgba(24, 144, 255, 1);
}

.champion-icon.tier-5:hover {
  box-shadow: 0 0 16px rgba(140, 140, 140, 1);
}

.bench-list {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  justify-content: center;
  padding: 6px;
}

.bench-item {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.current-champ {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
}

.no-champ-info {
  color: var(--el-text-color-secondary);
  font-size: 14px;
  padding: 8px;
}

.last-items-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(40px, 1fr));
  gap: 6px;
  padding: 6px;
}

@media (min-width: 768px) {
  .last-items-grid {
    grid-template-columns: repeat(6, minmax(40px, 1fr));
  }
}

@media (min-width: 1024px) {
  .last-items-grid {
    grid-template-columns: repeat(8, minmax(40px, 1fr));
  }
}

.last-item .item-icon {
  width: 40px;
  height: 40px;
  border-radius: 4px;
}

/* 添加新的样式 */
.header-actions {
  display: flex;
  gap: 8px;
}

/* 添加位置选择器样式 */
.position-selector {
  margin-top: 4px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.position-selector h4 {
  margin: 0;
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.tier-tag {
  position: absolute;
  top: -8px;
  right: -8px;
  font-size: 10px;
  padding: 2px 4px;
  border-radius: 4px;
}

.current-champ-container {
  position: relative;
  display: inline-block;
}

/* 修改当前英雄的tier标签样式 */
.tier-tag.current {
  top: -12px;
  right: -12px;
  font-size: 12px;
  padding: 3px 6px;
}

/* 添加新的样式 */
.current-champ-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.auto-swap-btn {
  min-width: 120px;
}

/* 调整当前英雄容器的样式 */
.current-champ-container {
  position: relative;
  display: inline-block;
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 6px;
  padding: 2px;
}

/* 锁定状态下的对勾遮罩 */
.check-overlay {
  position: absolute;
  right: -6px;
  bottom: -6px;
  width: 20px;
  height: 20px;
  background: var(--el-color-success);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  transform: scale(0);
  animation: pop-in 0.3s ease forwards;
}

.check-icon {
  font-size: 14px;
  color: white;
}

@keyframes pop-in {
  from {
    transform: scale(0);
  }
  to {
    transform: scale(1);
  }
}

/* 悬停效果 */
.current-champ-container:hover {
  transform: scale(1.05);
}

.current-champ-container:hover .check-overlay {
  background: var(--el-color-success-dark-2);
}

/* 加载遮罩样式 */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-icon {
  font-size: 24px;
  color: var(--el-color-primary);
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 添加新的召唤师技能样式 */
.spells-container {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 4px;
}

.spell-set {
  padding: 6px 8px;
  border: 1px solid var(--el-border-color);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.spell-content {
  display: flex;
  align-items: center;
  justify-content: space-between; /* 改为两端对齐 */
  padding-right: 16px; /* 右侧添加内边距 */
  width: 100%; /* 确保内容占满容器 */
}

.spell-icons {
  display: flex;
  gap: 4px;
  width: 68px; /* 固定宽度，确保对齐 */
  flex-shrink: 0; /* 防止图标被压缩 */
}

.spell-icon {
  width: 32px;
  height: 32px;
  border-radius: 4px;
}

.spell-stats {
  display: flex;
  gap: 24px; /* 增加胜率和使用率之间的间距 */
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-left: auto; /* 让统计信息靠右 */
  min-width: 220px; /* 确保统计信息有足够空间 */
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  white-space: nowrap;
  width: 98px; /* 固定每个统计项的宽度 */
  justify-content: flex-end; /* 内容靠右对齐 */
}

.stat-label {
  color: var(--el-text-color-regular);
  width: 45px; /* 保持标签宽度一致 */
  text-align: right; /* 标签文字靠右 */
}

.stat-value {
  font-weight: 500;
  width: 45px; /* 固定数值宽度 */
  text-align: right; /* 数值靠右对齐 */
}

/* 选中状态样式 */
.spell-set.selected {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}

/* 悬停效果 */
.spell-set:hover {
  transform: translateY(-1px);
  box-shadow: var(--el-box-shadow-light);
}

/* 添加折叠面板相关样式 */
:deep(.el-collapse) {
  border: none;
  width: 100%; /* 确保折叠面板始终占满容器宽度 */
}

:deep(.el-collapse-item) {
  width: 100%; /* 确保每个折叠项也占满宽度 */
}

:deep(.el-collapse-item__header) {
  font-size: 16px;
  font-weight: bold;
  color: var(--el-text-color-primary);
  background: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color-light);
  padding: 12px;
  width: 100%; /* 确保头部占满宽度 */
}

:deep(.el-collapse-item__wrap) {
  border-bottom: none;
  width: 100%; /* 确保包装器占满宽度 */
}

:deep(.el-collapse-item__content) {
  padding: 12px 0;
  width: 100%; /* 确保内容区域占满宽度 */
}

/* 修改标题栏样式 */
.title-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background-color: var(--el-color-primary);
  color: white;
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
}

/* 添加标题操作区样式 */
.title-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.close-icon {
  cursor: pointer;
  font-size: 20px;
  transition: transform 0.2s;
}

.close-icon:hover {
  transform: scale(1.1);
}
</style>
