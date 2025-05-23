<template>
  <div class="champ-select-helper" :class="{ 'expanded': isExpanded }">
    <div class="title-bar">
      <div class="title-left">
        <el-icon class="helper-icon"><Monitor /></el-icon>
        <span class="title">对局助手</span>
      </div>
      <div class="title-actions">
        <el-icon class="close-icon" @click="handleClose">
          <Close />
        </el-icon>
      </div>
    </div>
    
    <div class="main-content">
      <div class="content-wrapper">
        <div class="content" ref="contentRef">
          <!-- 第一行：游戏模式和位置选择 -->
          <div class="mode-position-row">
            <div class="game-mode-info">
              <span class="label">当前模式:</span>
              <span class="mode-text">{{ gameMode || '未知' }}</span>
            </div>

            <div v-if="gameModeMapping[gameMode || '']?.mode === 'ranked' && availablePositions.length > 0" 
                class="position-selector">
              <el-select 
                v-model="selectedPosition"
                size="small"
                style="width: 100px">
                <el-option
                  v-for="position in availablePositions"
                  :key="position"
                  :label="getPositionLabel(position)"
                  :value="position">
                </el-option>
              </el-select>
            </div>
          </div>

          <!-- 第二行：候选席英雄 -->
          <div v-if="showBenchChampions" class="bench-champs">
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

          <!-- 第三行：当前英雄 -->
          <div class="current-champ-section">
            <template v-if="wsStore.syncFrontData.current_champion">
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
                <div v-if="!autoSwapEnabled" class="check-overlay">
                  <el-icon class="check-icon"><Check /></el-icon>
                </div>
                <div v-if="switchLoading" class="loading-overlay">
                  <el-icon class="loading-icon"><Loading /></el-icon>
                </div>
              </div>
            </template>
            <span v-else class="no-champ-info">未选择英雄</span>
          </div>

          <!-- RecommendationsSection 组件 -->
          <RecommendationsSection
            :championDetail="championDetail"
            :isGuideLoading="isGuideLoading"
            :isGuideResourcesLoading="isGuideResourcesLoading"
            :getResourceUrl="getResourceUrl"
            :getItemName="getItemName"
            :gameMode="gameMode || ''"
            :selectedPosition="selectedPosition"
            :currentChampionId="wsStore.syncFrontData.current_champion || undefined"
            :gameModeMapping="gameModeMapping"
            v-model:selectedRuneIndex="selectedRuneIndex"
            v-model:selectedSpellIndex="selectedSpellIndex"
            v-model:selectedStartItems="selectedStartItems"
            v-model:selectedCoreItems="selectedCoreItems"
            v-model:selectedBoots="selectedBoots"
            v-model:activeCollapse="activeCollapse"
          />
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
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch, nextTick } from 'vue'
import { useGameStateStore } from '../../stores/gameState'
import { useWebSocketStore } from '../../stores/websocket'
import { Close, Loading, Check, ArrowRight, Monitor } from '@element-plus/icons-vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import DrawerAnalysis from './components/DrawerAnalysis.vue'
import RecommendationsSection from './components/RecommendationsSection.vue'

// 从 RecommendationsSection.vue 导入 ChampionDetailData 接口
// 假设 RecommendationsSection.vue 导出了这个接口
// 如果没有，我们需要先在 RecommendationsSection.vue 中导出它
// import type { ChampionDetailData } from './components/RecommendationsSection.vue';
// 或者，直接在这里重新定义，确保与子组件一致
interface RuneData {
  primaryId: number
  secondaryId: number
  perks: number[]
  win: number
  play: number
  pickRate: number
}
interface ItemBuild {
  icons: number[]
  win: number
  play: number
  pickRate: number
}
interface ChampionDetailData {
  perks: RuneData[]
  items: {
    startItems: ItemBuild[]
    coreItems: ItemBuild[]
    boots: ItemBuild[]
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

const gameStateStore = useGameStateStore()
const wsStore = useWebSocketStore()
const emit = defineEmits(['close'])

// 游戏资源状态
const gameResources = ref<Record<string, Record<string | number, string>>>({})
const contentRef = ref<HTMLElement | null>(null)

// 使用与 RecommendationsSection 一致的类型
const championDetail = ref<ChampionDetailData | null>(null)

// 选择状态，这些将通过 v-model 传递给 RecommendationsSection
const selectedRuneIndex = ref<number>(0)
const selectedStartItems = ref<number[]>([0])
const selectedCoreItems = ref<number[]>([0])
const selectedBoots = ref<number[]>([0])
const selectedSpellIndex = ref<number>(0)
const activeCollapse = ref(['spells', 'runes', 'items']) // 默认全部展开

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

    if (Array.isArray(response.data.data)) {
      championTierData.value = response.data.data.map((champion: any) => ({
        championId: champion.championId,
        tier: champion.tier,
        position: null
      }))
    } else {
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
  
  if (!wsStore.isConnected) {
    window.electron.ipcRenderer.send('request-initial-state')
  }
  
  await fetchChampionTierList()
})

const localSelections = ref<{
  // runeIndex, startItems, boots, coreItems, spellIndex 移至 RecommendationsSection
  scrollTop: number
}>({ 
  scrollTop: 0
})

watch(
  () => wsStore.syncFrontData.current_champion,
  async (newVal, oldVal) => {
    if (newVal !== oldVal) {
      localSelections.value.scrollTop = contentRef.value?.scrollTop || 0
      
      if (newVal) {
        await fetchChampionDetail(newVal)
      } else {
        championDetail.value = null
        selectedPosition.value = 'none'
        availablePositions.value = []
        // 重置选择状态，因为它们是父组件的状态
        selectedRuneIndex.value = 0
        selectedStartItems.value = [0]
        selectedBoots.value = [0]
        selectedCoreItems.value = [0]
        selectedSpellIndex.value = 0
        activeCollapse.value = ['spells', 'runes', 'items']
      }
      
      nextTick(() => {
        if (contentRef.value && localSelections.value.scrollTop) {
          contentRef.value.scrollTop = localSelections.value.scrollTop
        }
      })
    }
  }
)

const gameMode = computed(() => gameStateStore.gameMode)

interface ResourceRequest {
  champion_icons: number[]
  spell_icons: number[]
  item_icons: number[]
  rune_icons: number[]
}

watch(
  () => wsStore.syncFrontData.current_champion,
  async (newChampionId, oldChampionId) => {
    console.log('当前英雄变化:', { new: newChampionId, old: oldChampionId })
    if (newChampionId && newChampionId !== oldChampionId) {
      try {
        localSelections.value.scrollTop = contentRef.value?.scrollTop || 0
        selectedPosition.value = 'none'
        activeCollapse.value = ['spells', 'runes', 'items']
        
        await loadGameResources(newChampionId, 'hero')
        
        if (selectedPosition.value === 'none') {
          await fetchAvailablePositions(newChampionId)
        }
        
        nextTick(() => {
          if (contentRef.value && localSelections.value.scrollTop) {
            contentRef.value.scrollTop = localSelections.value.scrollTop
          }
        })
        
        loadGuideData(newChampionId).catch(error => {
          console.error('异步加载攻略数据失败:', error)
          ElMessage.error('加载攻略数据失败')
        })
      } catch (error) {
        console.error('切换英雄时加载数据失败:', error)
        ElMessage.error('加载数据失败')
      }
    } else if (!newChampionId) {
      championDetail.value = null
      selectedPosition.value = 'none'
      availablePositions.value = []
      // 重置选择状态
      selectedRuneIndex.value = 0
      selectedStartItems.value = [0]
      selectedBoots.value = [0]
      selectedCoreItems.value = [0]
      selectedSpellIndex.value = 0
      activeCollapse.value = ['spells', 'runes', 'items']
    }
  }
)

watch(
  () => wsStore.syncFrontData.bench_champions,
  async (newBenchChampions) => {
    console.log('候选席英雄变化:', newBenchChampions)
    if (newBenchChampions && newBenchChampions.length > 0) {
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
    immediate: true
  }
)

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
  return '/placeholder.png' // 保留占位符图像
}

const handleClose = () => {
  window.electron.ipcRenderer.send('close-champ-select')
}

// 移除 hasValidItemSelection，因为它移到了 RecommendationsSection

const gameModeMapping: Record<string, { mode: string, hasBench: boolean }> = {
  'ARAM': { mode: 'aram', hasBench: true },
  'CLASSIC': { mode: 'ranked', hasBench: false },
  'URF': { mode: 'urf', hasBench: false },
  'PRACTICETOOL': { mode: 'ranked', hasBench: false }
}

const availablePositions = ref<string[]>([])
const selectedPosition = ref('none')

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
    if (selectedPosition.value === 'none') {
      selectedPosition.value = availablePositions.value[0] || 'all'
    }
  } catch (error) {
    console.error('获取位置信息失败:', error)
    ElMessage.error('获取位置信息失败')
  }
}

const isGuideLoading = ref(false)
const isGuideResourcesLoading = ref(false)

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
      resourceRequest.champion_icons = [championId]
    } else if (type === 'guide' && championDetail.value) {
      // 确保 championDetail.value 存在并且符合 ChampionDetailData 结构
      if (championDetail.value.summonerSpells) {
        championDetail.value.summonerSpells.forEach((spell) => { // spell 类型现在是明确的
          resourceRequest.spell_icons.push(...spell.icons)
        })
      }
      if (championDetail.value.perks) {
        championDetail.value.perks.forEach((rune) => { // rune 类型现在是明确的
          resourceRequest.rune_icons.push(rune.primaryId, rune.secondaryId)
          resourceRequest.rune_icons.push(...rune.perks)
        })
      }
      if (championDetail.value.items) {
        championDetail.value.items.startItems?.forEach((build) => { // build 类型现在是明确的
          resourceRequest.item_icons.push(...build.icons)
        })
        championDetail.value.items.coreItems?.forEach((build) => {
          resourceRequest.item_icons.push(...build.icons)
        })
        championDetail.value.items.boots?.forEach((build) => {
          resourceRequest.item_icons.push(...build.icons)
        })
        if (championDetail.value.items.lastItems) {
          resourceRequest.item_icons.push(...championDetail.value.items.lastItems)
        }
      }
      resourceRequest.spell_icons = [...new Set(resourceRequest.spell_icons)]
      resourceRequest.rune_icons = [...new Set(resourceRequest.rune_icons)]
      resourceRequest.item_icons = [...new Set(resourceRequest.item_icons)]
    }

    if (resourceRequest.champion_icons.length > 0 || resourceRequest.spell_icons.length > 0 || resourceRequest.item_icons.length > 0 || resourceRequest.rune_icons.length > 0) {
      const response = await axios.post(
        '/api/common/game_resource/batch_get_resources',
        resourceRequest
      )

      gameResources.value = {
        ...gameResources.value,
        ...(type === 'hero' && response.data.champion_icons ? { 
            champion_icons: { ...gameResources.value.champion_icons, ...response.data.champion_icons }
          } : {}),
        ...(type === 'guide' && response.data.spell_icons ? { 
            spell_icons: { ...gameResources.value.spell_icons, ...response.data.spell_icons }
          } : {}),
        ...(type === 'guide' && response.data.rune_icons ? { 
            rune_icons: { ...gameResources.value.rune_icons, ...response.data.rune_icons }
          } : {}),
        ...(type === 'guide' && response.data.item_icons ? { 
            item_icons: { ...gameResources.value.item_icons, ...response.data.item_icons }
          } : {}),
      }
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

const fetchChampionDetail = async (championId: number) => {
  try {
    championDetail.value = null // 清空旧数据
    // 重置选择状态，这些状态现在由父组件管理
    selectedRuneIndex.value = 0
    selectedStartItems.value = [0]
    selectedBoots.value = [0]
    selectedCoreItems.value = [0]
    selectedSpellIndex.value = 0
    
    if (selectedPosition.value === 'none') {
      await fetchAvailablePositions(championId)
    }
    
    await loadGameResources(championId, 'hero')
    
    loadGuideData(championId).catch(error => {
      console.error('异步加载攻略数据失败:', error)
      ElMessage.error('加载攻略数据失败')
    })
  } catch (error) {
    console.error('获取英雄详情失败:', error)
    ElMessage.error('获取英雄详情失败')
  }
}

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

    // 直接将获取的数据赋值，类型应与 ChampionDetailData 匹配
    championDetail.value = response.data.data as ChampionDetailData | null

    // 确保数据存在才加载资源
    if (championDetail.value) {
        loadGameResources(championId, 'guide').catch(error => {
        console.error('异步加载攻略资源失败:', error)
        ElMessage.error('加载攻略资源失败')
      })
    }

  } catch (error) {
    console.error('加载攻略数据失败:', error)
    ElMessage.error('加载攻略数据失败')
    championDetail.value = null // 发生错误时清空
  } finally {
    isGuideLoading.value = false
  }
}

watch(selectedPosition, async (newPosition, oldPosition) => {
  if (wsStore.syncFrontData.current_champion && newPosition !== 'none' && newPosition !== oldPosition) {
    loadGuideData(wsStore.syncFrontData.current_champion).catch(error => {
      console.error('切换位置加载数据失败:', error)
      ElMessage.error('加载数据失败')
    })
  }
})

// 移除 toggleItemSelection, applyRunes, applyItems, isAllSelected, toggleSelectAllItems
// 这些逻辑已移至 RecommendationsSection

const getItemName = (itemId: number): string => {
  // 实际项目中可能需要从一个全局的物品数据源获取名称
  return `装备 ${itemId}`
}

const selectBenchChampion = async (championId: number) => {
  try {
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

const positionLabels: Record<string, string> = {
  'top': '上路',
  'jungle': '打野',
  'mid': '中路',
  'bottom': '下路',
  'support': '辅助',
  'all': '所有位置'
}

const getPositionLabel = (position: string) => {
  return positionLabels[position] || position
}

const getTierColor = (tier: number): string => {
    switch (tier) {
        case 0: return '#ff0000';
        case 1: return '#ff4400';
        case 2: return '#FFA500';
        case 3: return '#B9CA2E';
        case 4: return '#85CB62';
        case 5: return '#808080';
        default: return '#808080';
    }
}

watch(gameMode, async () => {
  await fetchChampionTierList()
  // 如果当前有英雄，则重新加载攻略数据以匹配新的游戏模式
  if (wsStore.syncFrontData.current_champion) {
    loadGuideData(wsStore.syncFrontData.current_champion).catch(error => {
      console.error('游戏模式变化，重新加载攻略数据失败:', error)
      // ElMessage.error('加载攻略数据失败') // 避免重复提示
    })
  }
})

const getChampionTier = (championId: number, position: string = 'all'): number | undefined => {
  if (position !== 'all') {
    const championData = championTierData.value.find(c => 
      c.championId === championId && c.position === position
    )
    if (championData) return championData.tier ?? undefined
  }
  
  const championData = championTierData.value.find(c => 
    c.championId === championId && (c.position === null || position === 'all')
  )
  return championData?.tier ?? undefined
}

const getChampionTierClass = (championId: number): string => {
  const position = selectedPosition.value
  const tier = getChampionTier(championId, position)
  switch (tier) {
    case 1: return 'tier-1';
    case 2: return 'tier-2';
    case 3: return 'tier-3';
    case 4: return 'tier-4';
    case 5: return 'tier-5';
    default: return '';
  }
}

const showBenchChampions = computed(() => {
  const currentMode = gameMode.value || ''
  return gameModeMapping[currentMode]?.hasBench ?? false
})

const autoSwapEnabled = ref(true)
const switchLoading = ref(false)

const handleAutoSwapChange = async (value: boolean) => {
  if (switchLoading.value) return
  
  switchLoading.value = true
  try {
    const endpoint = value ? 'swap_champion_on' : 'swap_champion_off'
    const response = await axios.get(`/api/champ_select_helper/${endpoint}`)
    
    if (response.data.success) {
      autoSwapEnabled.value = value
      ElMessage.success(response.data.message)
    } else {
      throw new Error(response.data.message || '操作失败')
    }
  } catch (error: any) {
    console.error('切换自动换人状态失败:', error)
    ElMessage.error(error.message || '切换自动换人状态失败')
  } finally {
    switchLoading.value = false
  }
}

const isExpanded = ref(false)

const toggleExpand = () => {
  isExpanded.value = !isExpanded.value
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
  flex-direction: column;
  background: var(--el-bg-color);
  min-width: 400px;
}

.title-bar {
  -webkit-app-region: drag;
  height: 44px;
  background: linear-gradient(90deg, var(--el-color-primary-dark-2), var(--el-color-primary));
  color: var(--el-color-white);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 12px 0 16px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.15);
  position: relative;
  z-index: 10;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  width: 100%;
  box-sizing: border-box;
}

.title-left {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  min-width: 0;
}

.title {
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 1px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.title-actions {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.content-wrapper {
  width: 400px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.content {
  flex: 1;
  padding: 12px;
  overflow-y: auto;
}

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

.title-bar::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
}

.helper-icon {
  font-size: 20px;
  color: rgba(255, 255, 255, 0.9);
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.2));
}

.close-icon {
  -webkit-app-region: no-drag;
  cursor: pointer;
  font-size: 18px;
  padding: 8px;
  border-radius: 4px;
  transition: all 0.2s ease;
  background: rgba(255, 255, 255, 0.05);
  margin-right: -8px;
}

.close-icon:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: rotate(90deg);
}

.game-info-section {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 8px 12px;
  background: var(--el-bg-color-page);
  border-radius: 8px;
  margin-bottom: 12px;
}

.game-mode-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.game-mode-info .label {
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.game-mode-info .mode-text {
  color: var(--el-color-primary);
  font-weight: 500;
}

.current-champ-section {
  display: flex;
  justify-content: center;
  padding: 12px;
  background: var(--el-bg-color-page);
  border-radius: 8px;
  margin-bottom: 12px;
}

.bench-champs {
  background: var(--el-bg-color-page);
  border-radius: 8px;
  padding: 8px 12px;
  margin-bottom: 12px;
}

.bench-list {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.champion-icon {
  width: 36px;
  height: 36px;
  border-radius: 6px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.2s;
  border: 2px solid transparent;
}

.champion-icon.current {
  width: 64px;
  height: 64px;
}

.current-champ-container {
  position: relative;
  display: inline-block;
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 6px;
  padding: 2px;
}

.no-champ-info {
  color: var(--el-text-color-secondary);
  font-size: 14px;
  padding: 8px;
}

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

.tier-tag.current {
  top: -12px;
  right: -12px;
  font-size: 12px;
  padding: 3px 6px;
}

.current-champ-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.current-champ-container {
  position: relative;
  display: inline-block;
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 6px;
  padding: 2px;
}

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

.current-champ-container:hover {
  transform: scale(1.05);
}

.current-champ-container:hover .check-overlay {
  background: var(--el-color-success-dark-2);
}

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

.mode-position-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: var(--el-bg-color-page);
  border-radius: 8px;
  margin-bottom: 12px;
}

.bench-champs {
  background: var(--el-bg-color-page);
  border-radius: 8px;
  padding: 8px 12px;
  margin-bottom: 12px;
}

.bench-list {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.current-champ-section {
  display: flex;
  justify-content: center;
  padding: 12px;
  background: var(--el-bg-color-page);
  border-radius: 8px;
  margin-bottom: 12px;
}

.champion-icon {
  width: 36px;
  height: 36px;
  border-radius: 6px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.2s;
  border: 2px solid transparent;
}

.champion-icon.current {
  width: 64px;
  height: 64px;
}

.current-champ-container {
  position: relative;
  display: inline-block;
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 6px;
  padding: 2px;
}

.champion-icon.tier-1 {
  border-color: #f5222d;
  box-shadow: 0 0 8px rgba(245, 34, 45, 0.7);
}

.champion-icon.tier-2 {
  border-color: #fa8c16;
  box-shadow: 0 0 8px rgba(250, 140, 22, 0.7);
}

.champion-icon.tier-3 {
  border-color: #52c41a;
  box-shadow: 0 0 8px rgba(82, 196, 26, 0.6);
}

.champion-icon.tier-4 {
  border-color: #1890ff;
  box-shadow: 0 0 8px rgba(24, 144, 255, 0.6);
}

.champion-icon.tier-5 {
  border-color: #8c8c8c;
  box-shadow: 0 0 8px rgba(140, 140, 140, 0.6);
}

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

.bench-item {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
}
</style>
