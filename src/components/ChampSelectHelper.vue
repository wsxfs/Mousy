<template>
  <div class="champ-select-helper">
    <div class="title-bar">
      <span>选人助手</span>
      <el-icon class="close-icon" @click="handleClose">
        <Close />
      </el-icon>
    </div>
    
    <div class="content">
      <!-- 游戏模式信息 -->
      <div class="game-mode-info">
        <h3>当前游戏模式</h3>
        <p>{{ gameMode || '未知' }}</p>
        
        <!-- 添加位置选择器 -->
        <template v-if="gameModeMapping[gameMode || ''] === 'ranked' && availablePositions.length > 0">
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
      </div>

      <!-- 选择英雄信息 -->
      <div class="champ-select-info">
        <div class="champ-info">
          <!-- 候选席英雄 -->
          <div class="bench-champs">
            <h4>候选席英雄</h4>
            <div v-if="wsStore.champSelectInfo.benchChampions?.length > 0" class="bench-list">
              <div v-for="championId in wsStore.champSelectInfo.benchChampions" 
                   :key="championId" 
                   class="bench-item"
                   @click="selectBenchChampion(championId)">
                <img 
                  :src="getResourceUrl('champion_icons', championId)" 
                  :alt="'Champion ' + championId"
                  class="champion-icon"
                />
              </div>
            </div>
            <span v-else class="no-champ-info">无候选席英雄</span>
          </div>
          
          <!-- 当前英雄 -->
          <div class="current-champ">
            <h4>当前英雄</h4>
            <template v-if="wsStore.champSelectInfo.currentChampion">
              <img 
                :src="getResourceUrl('champion_icons', wsStore.champSelectInfo.currentChampion)" 
                :alt="'Champion ' + wsStore.champSelectInfo.currentChampion"
                class="champion-icon current"
              />
            </template>
            <span v-else class="no-champ-info">未选择英雄</span>
          </div>
        </div>
      </div>

      <!-- 添加符文和装备推荐部分 -->
      <div v-if="championDetail" class="recommendations">
        <!-- 符文推荐 -->
        <div class="section">
          <div class="section-header">
            <h3>符文推荐</h3>
            <el-button 
              type="primary" 
              size="small"
              :disabled="selectedRuneIndex === null"
              @click="applyRunes">
              应用符文
            </el-button>
          </div>
          <div class="runes-container">
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

        <!-- 装备推荐 -->
        <div class="section">
          <div class="section-header">
            <h3>装备推荐</h3>
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
          <div class="item-group">
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
          <div class="item-group">
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
          <div class="item-group">
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
          <div class="item-group">
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
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useGameStateStore } from '../stores/gameState'
import { useWebSocketStore } from '../stores/websocket'
import { Close } from '@element-plus/icons-vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const gameStateStore = useGameStateStore()
const wsStore = useWebSocketStore()

// 游戏资源状态
const gameResources = ref<Record<string, Record<string | number, string>>>({})

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
}

// 修改 championDetail 的类型
const championDetail = ref<ChampionDetail | null>(null)
const selectedRuneIndex = ref<number>(0)
const selectedStartItems = ref<number[]>([0])
const selectedCoreItems = ref<number[]>([0])
const selectedBoots = ref<number[]>([0])

onMounted(async () => {
  await gameStateStore.fetchGameMode()
  // 确保 WebSocket 连接
  if (!wsStore.isConnected) {
    wsStore.connect()
  }
})

const gameMode = computed(() => gameStateStore.gameMode)

// 修改 ResourceRequest 接口定义
interface ResourceRequest {
  champion_icons: number[]
  spell_icons: number[]
  item_icons: number[]
  rune_icons: number[]  // 添加 rune_icons
}

// 修改监听逻辑，同时监听候选席英雄变化
watch(
  [
    () => wsStore.champSelectInfo.currentChampion,
    () => wsStore.champSelectInfo.benchChampions
  ],
  async ([newChampionId, newBenchChampions]) => {
    // 加载当前英雄的详细信息
    if (newChampionId) {
      await fetchChampionDetail(newChampionId)
    } else {
      championDetail.value = null
      gameResources.value = {}
    }

    // 加载候选席英雄的资源
    if (newBenchChampions && newBenchChampions.length > 0) {
      await loadGameResources(newChampionId || 0) // 确保加载所有需要的资源
    }
  }
)

// 修改 loadGameResources 方法
const loadGameResources = async (championId: number) => {
  try {
    const resourceRequest: ResourceRequest = {
      champion_icons: [championId, ...wsStore.champSelectInfo.benchChampions],
      spell_icons: [],
      item_icons: [],
      rune_icons: []
    }

    // 确保 championDetail.value 不为空
    if (championDetail.value) {
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
    }
    
    // 去重
    resourceRequest.rune_icons = [...new Set(resourceRequest.rune_icons)]
    resourceRequest.item_icons = [...new Set(resourceRequest.item_icons)]
    
    console.log('Resource request:', resourceRequest)
    
    const response = await axios.post(
      '/api/common/game_resource/batch_get_resources',
      resourceRequest
    )
    
    gameResources.value = response.data
  } catch (error) {
    console.error('加载游戏资源失败:', error)
  }
}

// 修改获取资源URL方法，使用与 ChampionDetail.vue 相同的类型映射
const getResourceUrl = (type: string, id: number): string => {
  const typeMapping: Record<string, string> = {
    'champion_icons': 'champion_icons',
    'summoner_spell_icons': 'spell_icons',
    'item_icons': 'item_icons',
    'perk_icons': 'rune_icons'  // 修改这里：perk_icons 映射到 rune_icons
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
  return selectedStartItems.value.length > 0 && 
         selectedBoots.value.length > 0 &&
         selectedCoreItems.value.length > 0
})

// 简化游戏模式映射
const gameModeMapping: Record<string, string> = {
  'ARAM': 'aram',
  'CLASSIC': 'ranked',
  'URF': 'urf',
  'PRACTICETOOL': 'ranked'
}

// 添加位置相关的状态
const availablePositions = ref<string[]>([])
const selectedPosition = ref('none')

// 修改获取可用位置的方法 - 不再自动设置选中位置
const fetchAvailablePositions = async (championId: number) => {
  try {
    if (gameModeMapping[gameMode.value || ''] !== 'ranked') {
      availablePositions.value = ['none']
      selectedPosition.value = 'none'
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
    // 只在初次加载时设置默认位置
    if (selectedPosition.value === 'none') {
      selectedPosition.value = availablePositions.value[0] || 'all'
    }
  } catch (error) {
    console.error('获取位置信息失败:', error)
    ElMessage.error('获取位置信息失败')
  }
}

// 修改 fetchChampionDetail 方法
const fetchChampionDetail = async (championId: number) => {
  try {
    // 先获取可用位置
    await fetchAvailablePositions(championId)
    
    const mode = gameModeMapping[gameMode.value || ''] || 'ranked'
    const params = new URLSearchParams({
      champion_id: championId.toString(),
      region: 'kr',
      mode: mode,
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

    championDetail.value = response.data.data
    await loadGameResources(championId)
  } catch (error) {
    console.error('获取英雄详情失败:', error)
    ElMessage.error('获取英雄详情失败')
  }
}

// 监听位置变化
watch(selectedPosition, async (newPosition) => {
  if (wsStore.champSelectInfo.currentChampion && newPosition !== 'none') {
    await fetchChampionDetail(wsStore.champSelectInfo.currentChampion)
  }
})

// 修改装备选择方法
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

    const itemsData = {
      title: championDetail.value.summary.name,
      source: 'kr',
      tier: 'platinum_plus',
      mode: 'aram',
      position: 'none',
      associatedChampions: [wsStore.champSelectInfo.currentChampion],
      associatedMaps: [12],
      items: {
        startItems: selectedStartItems.value.map(index => ({
          icons: championDetail.value!.items.startItems[index].icons,
          winRate: (championDetail.value!.items.startItems[index].win / 
                   championDetail.value!.items.startItems[index].play * 100).toFixed(1),
          pickRate: (championDetail.value!.items.startItems[index].pickRate * 100).toFixed(1)
        })),
        boots: selectedBoots.value.map(index => ({
          icons: championDetail.value!.items.boots[index].icons,
          winRate: (championDetail.value!.items.boots[index].win / 
                   championDetail.value!.items.boots[index].play * 100).toFixed(1),
          pickRate: (championDetail.value!.items.boots[index].pickRate * 100).toFixed(1)
        })),
        coreItems: selectedCoreItems.value.map(index => ({
          icons: championDetail.value!.items.coreItems[index].icons,
          winRate: (championDetail.value!.items.coreItems[index].win / 
                   championDetail.value!.items.coreItems[index].play * 100).toFixed(1),
          pickRate: (championDetail.value!.items.coreItems[index].pickRate * 100).toFixed(1)
        })),
        lastItems: championDetail.value.items.lastItems
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
  if (!championDetail.value?.items) return false
  
  const allStartItemsSelected = selectedStartItems.value.length === championDetail.value.items.startItems.length
  const allBootsSelected = selectedBoots.value.length === championDetail.value.items.boots.length
  const allCoreItemsSelected = selectedCoreItems.value.length === championDetail.value.items.coreItems.length
  
  return allStartItemsSelected && allBootsSelected && allCoreItemsSelected
})

// 修改为切换全选/取消全选方法
const toggleSelectAllItems = () => {
  if (!championDetail.value?.items) return
  
  if (isAllSelected.value) {
    // 取消全选，每类只保留第一个选项
    selectedStartItems.value = [0]
    selectedBoots.value = [0]
    selectedCoreItems.value = [0]
  } else {
    // 全选所有选项
    selectedStartItems.value = championDetail.value.items.startItems.map((_, index) => index)
    selectedBoots.value = championDetail.value.items.boots.map((_, index) => index)
    selectedCoreItems.value = championDetail.value.items.coreItems.map((_, index) => index)
  }
}

// 添加 selectBenchChampion 方法
const selectBenchChampion = async (championId: number) => {
  try {
    // 这里添加选择候选席英雄的逻辑
    await fetchChampionDetail(championId)
  } catch (error) {
    console.error('选择候选席英雄失败:', error)
    ElMessage.error('选择候选席英雄失败')
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
</script>

<style scoped>
.champ-select-helper {
  height: 100vh;
  background: var(--el-bg-color);
  display: flex;
  flex-direction: column;
}

.title-bar {
  -webkit-app-region: drag; /* 允许拖动窗口 */
  height: 32px;
  background: var(--el-color-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
}

.close-icon {
  -webkit-app-region: no-drag; /* 允许点击关闭按钮 */
  cursor: pointer;
  font-size: 20px;
}

.content {
  flex: 1;
  padding: 20px;
  overflow: auto;
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
}

.section {
  background: var(--el-bg-color);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: var(--el-box-shadow-lighter);
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
  gap: 8px;
}

.rune-set {
  padding: 8px;
  border: 1px solid var(--el-border-color);
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
}

.rune-set.selected {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}

.item-group {
  margin-bottom: 16px;
}

.build-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px;
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
  min-height: 48px;
}

.build-row.selected {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}

.item-icons {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

.item-icon {
  width: 32px;
  height: 32px;
  border-radius: 4px;
}

.build-stats {
  display: grid;
  grid-template-columns: repeat(2, 60px);
  text-align: right;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-left: auto;
}

/* 添加或修改符文相关样式 */
.rune-trees {
  display: flex;
  gap: 4px;
  margin-bottom: 4px;
}

.tree-icon {
  width: 20px;
  height: 20px;
  border-radius: 3px;
}

.rune-icons {
  display: flex;
  gap: 2px;
  flex-wrap: nowrap;
  margin-bottom: 4px;
  align-items: center;
}

.rune-icon {
  width: 24px;
  height: 24px;
  border-radius: 3px;
}

.rune-stats {
  display: flex;
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

/* 修改标题行的统计列样式 */
.stats-header {
  display: grid;
  grid-template-columns: repeat(2, 60px);
  text-align: right;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-left: auto;
}

/* 修改英雄图标样式 */
.champion-icon {
  width: 40px;
  height: 40px;
  border-radius: 6px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
}

.champion-icon:hover {
  transform: scale(1.1);
}

.champion-icon.current {
  width: 56px;
  height: 56px;
  border: 2px solid var(--el-color-primary);
}

.bench-list {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  justify-content: center;
  padding: 6px;
}

.bench-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.current-champ {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
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
  gap: 10px;
  padding: 10px;
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
  margin-top: 12px;
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
</style>