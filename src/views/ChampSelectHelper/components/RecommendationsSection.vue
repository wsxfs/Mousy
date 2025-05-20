<template>
  <div v-if="championDetail" class="recommendations">
    <el-collapse v-model="activeCollapseNames">
      <!-- 召唤师技能部分 -->
      <el-collapse-item title="召唤师技能" name="spells">
        <div class="section">
          <div v-loading="isGuideLoading || isGuideResourcesLoading" class="spells-container">
            <div v-for="(spell, index) in championDetail.summonerSpells"
                 :key="index"
                 class="spell-set"
                 :class="{ 'selected': localSelectedSpellIndex === index }"
                 @click="handleSpellSelect(index)">
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
              :disabled="localSelectedRuneIndex === null || !championDetail.perks || championDetail.perks.length === 0"
              @click="handleApplyRunes">
              应用符文
            </el-button>
          </div>
          <div v-loading="isGuideLoading || isGuideResourcesLoading" class="runes-container">
            <div v-for="(rune, index) in championDetail.perks"
                 :key="index"
                 :class="['rune-set', { 'selected': localSelectedRuneIndex === index }]"
                 @click="handleRuneSelect(index)">
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
                @click="handleToggleSelectAllItems">
                {{ isAllItemsSelected ? '取消全选' : '全选' }}
              </el-button>
              <el-button
                type="primary"
                size="small"
                :disabled="!hasValidItemBuildSelection"
                @click="handleApplyItems">
                应用装备
              </el-button>
            </div>
          </div>

          <!-- 起始装备 -->
          <div class="item-group" v-if="championDetail.items?.startItems?.length">
            <h4>
              起始装备
              <div class="stats-header">
                <span>胜率</span>
                <span>使用率</span>
              </div>
            </h4>
            <div v-for="(build, index) in championDetail.items.startItems"
                 :key="index"
                 :class="['build-row', { selected: localSelectedStartItems.includes(index) }]"
                 @click="handleToggleItemSelection(index, 'start')">
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
          <div class="item-group" v-if="championDetail.items?.boots?.length">
            <h4>
              鞋子选择
              <div class="stats-header">
                <span>胜率</span>
                <span>使用率</span>
              </div>
            </h4>
            <div v-for="(build, index) in championDetail.items.boots"
                 :key="index"
                 :class="['build-row', { selected: localSelectedBoots.includes(index) }]"
                 @click="handleToggleItemSelection(index, 'boots')">
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
          <div class="item-group" v-if="championDetail.items?.coreItems?.length">
            <h4>
              核心装备
              <div class="stats-header">
                <span>胜率</span>
                <span>使用率</span>
              </div>
            </h4>
            <div v-for="(build, index) in championDetail.items.coreItems"
                 :key="index"
                 :class="['build-row', { selected: localSelectedCoreItems.includes(index) }]"
                 @click="handleToggleItemSelection(index, 'core')">
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
          <div class="item-group" v-if="championDetail.items?.lastItems?.length">
            <h4>可选装备池</h4>
            <div class="build-row selected"> <!-- Assuming this is always "selected" for display -->
              <div class="last-items-grid">
                <div v-for="itemId in championDetail.items.lastItems"
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

<script setup lang="ts">
import { ref, computed, watch, toRefs, type Ref } from 'vue'
import type { PropType } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

// Define interfaces locally or import if they become shared
interface RuneData {
  primaryId: number
  secondaryId: number
  perks: number[]
  // icons: number[] // Not directly used in template, but part of data structure
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

const props = defineProps({
  championDetail: {
    type: Object as PropType<ChampionDetailData | null>,
    default: null
  },
  isGuideLoading: {
    type: Boolean,
    default: false
  },
  isGuideResourcesLoading: {
    type: Boolean,
    default: false
  },
  getResourceUrl: {
    type: Function as PropType<(type: string, id: number) => string>,
    required: true
  },
  getItemName: {
    type: Function as PropType<(id: number) => string>,
    required: true
  },
  // For applyItems/Runes
  gameMode: {
    type: String,
    required: true
  },
  selectedPosition: {
    type: String,
    required: true
  },
  currentChampionId: {
    type: Number,
    default: null
  },
  gameModeMapping: {
    type: Object as PropType<Record<string, { mode: string; hasBench: boolean }>>,
    required: true
  },
  // For v-model on selections
  selectedRuneIndex: {
    type: Number,
    default: 0
  },
  selectedSpellIndex: {
    type: Number,
    default: 0
  },
  selectedStartItems: {
    type: Array as PropType<number[]>,
    default: () => [0]
  },
  selectedCoreItems: {
    type: Array as PropType<number[]>,
    default: () => [0]
  },
  selectedBoots: {
    type: Array as PropType<number[]>,
    default: () => [0]
  },
  activeCollapse: {
    type: Array as PropType<string[]>,
    default: () => ['spells', 'runes', 'items']
  }
})

const emit = defineEmits([
  'update:selectedRuneIndex',
  'update:selectedSpellIndex',
  'update:selectedStartItems',
  'update:selectedCoreItems',
  'update:selectedBoots',
  'update:activeCollapse'
])

const {
  selectedRuneIndex: propSelectedRuneIndex,
  selectedSpellIndex: propSelectedSpellIndex,
  selectedStartItems: propSelectedStartItems,
  selectedCoreItems: propSelectedCoreItems,
  selectedBoots: propSelectedBoots,
  activeCollapse: propActiveCollapse
} = toRefs(props)

// Local refs for selections to enable two-way binding with parent
const localSelectedRuneIndex = ref(propSelectedRuneIndex.value)
const localSelectedSpellIndex = ref(propSelectedSpellIndex.value)
const localSelectedStartItems = ref([...propSelectedStartItems.value])
const localSelectedCoreItems = ref([...propSelectedCoreItems.value])
const localSelectedBoots = ref([...propSelectedBoots.value])
const activeCollapseNames = ref([...propActiveCollapse.value])


watch(propSelectedRuneIndex, (newVal) => {
  localSelectedRuneIndex.value = newVal
})
watch(localSelectedRuneIndex, (newVal) => {
  emit('update:selectedRuneIndex', newVal)
})

watch(propSelectedSpellIndex, (newVal) => {
  localSelectedSpellIndex.value = newVal
})
watch(localSelectedSpellIndex, (newVal) => {
  emit('update:selectedSpellIndex', newVal)
})

watch(propSelectedStartItems, (newVal) => {
  localSelectedStartItems.value = [...newVal]
}, { deep: true })
watch(localSelectedStartItems, (newVal) => {
  emit('update:selectedStartItems', [...newVal])
}, { deep: true })

watch(propSelectedCoreItems, (newVal) => {
  localSelectedCoreItems.value = [...newVal]
}, { deep: true })
watch(localSelectedCoreItems, (newVal) => {
  emit('update:selectedCoreItems', [...newVal])
}, { deep: true })

watch(propSelectedBoots, (newVal) => {
  localSelectedBoots.value = [...newVal]
}, { deep: true })
watch(localSelectedBoots, (newVal) => {
  emit('update:selectedBoots', [...newVal])
}, { deep: true })

watch(propActiveCollapse, (newVal) => {
  activeCollapseNames.value = [...newVal]
}, { deep: true })
watch(activeCollapseNames, (newVal) => {
  emit('update:activeCollapse', [...newVal])
}, { deep: true })


const handleRuneSelect = (index: number) => {
  localSelectedRuneIndex.value = index
}

const handleSpellSelect = (index: number) => {
  localSelectedSpellIndex.value = index
}

const handleApplyRunes = async () => {
  if (!props.championDetail?.perks || localSelectedRuneIndex.value === null || localSelectedRuneIndex.value >= props.championDetail.perks.length) {
    ElMessage.warning('符文数据不完整或选择无效')
    return
  }

  try {
    const selectedRune = props.championDetail.perks[localSelectedRuneIndex.value]
    const winRate = (selectedRune.win / selectedRune.play * 100).toFixed(1)
    const pickRate = (selectedRune.pickRate * 100).toFixed(1)

    const perksData = {
      name: `${props.championDetail.summary.name}|胜率${winRate}%|使用率${pickRate}%(Best Wishes From Mousy🐹)`,
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

const hasValidItemBuildSelection = computed(() => {
  const items = props.championDetail?.items
  if (!items) return false

  const hasStart = !items.startItems?.length || localSelectedStartItems.value.length > 0
  const hasBoots = !items.boots?.length || localSelectedBoots.value.length > 0
  const hasCore = !items.coreItems?.length || localSelectedCoreItems.value.length > 0

  const hasAnySelection = (items.startItems?.length && localSelectedStartItems.value.length > 0) ||
                         (items.boots?.length && localSelectedBoots.value.length > 0) ||
                         (items.coreItems?.length && localSelectedCoreItems.value.length > 0)

  return hasStart && hasBoots && hasCore && hasAnySelection
})

const handleApplyItems = async () => {
  if (!props.championDetail?.items) {
    ElMessage.warning('装备数据不完整')
    return
  }
  if (!props.currentChampionId) {
     ElMessage.warning('当前英雄ID缺失')
    return
  }

  const items = props.championDetail.items
  const itemsData = {
    title: props.championDetail.summary.name,
    source: 'kr',
    tier: 'platinum_plus', // Consider making this dynamic if needed
    mode: props.gameModeMapping[props.gameMode]?.mode || 'ranked',
    position: props.selectedPosition,
    associatedChampions: [props.currentChampionId],
    associatedMaps: [props.gameModeMapping[props.gameMode]?.mode === 'aram' ? 12 : 11],
    items: {
      startItems: items.startItems?.length ? localSelectedStartItems.value.map(index => ({
        icons: items.startItems[index].icons,
        winRate: (items.startItems[index].win / items.startItems[index].play * 100).toFixed(1),
        pickRate: (items.startItems[index].pickRate * 100).toFixed(1)
      })) : [],
      boots: items.boots?.length ? localSelectedBoots.value.map(index => ({
        icons: items.boots[index].icons,
        winRate: (items.boots[index].win / items.boots[index].play * 100).toFixed(1),
        pickRate: (items.boots[index].pickRate * 100).toFixed(1)
      })) : [],
      coreItems: items.coreItems?.length ? localSelectedCoreItems.value.map(index => ({
        icons: items.coreItems[index].icons,
        winRate: (items.coreItems[index].win / items.coreItems[index].play * 100).toFixed(1),
        pickRate: (items.coreItems[index].pickRate * 100).toFixed(1)
      })) : [],
      lastItems: items.lastItems || []
    }
  }

  try {
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

const handleToggleItemSelection = (index: number, type: 'start' | 'boots' | 'core') => {
  let selectionRef: Ref<number[]> | null = null
  if (type === 'start') selectionRef = localSelectedStartItems
  else if (type === 'boots') selectionRef = localSelectedBoots
  else if (type === 'core') selectionRef = localSelectedCoreItems

  if (!selectionRef) return

  const currentSelection = selectionRef.value
  const itemIndexInSelection = currentSelection.indexOf(index)

  if (itemIndexInSelection === -1) {
    currentSelection.push(index)
  } else {
    if (currentSelection.length > 1) { // Prevent deselecting the last item
      currentSelection.splice(itemIndexInSelection, 1)
    }
  }
  // Vue's reactivity should handle updates if selectionRef.value is modified directly.
  // Explicitly reassign if issues arise, e.g., selectionRef.value = [...currentSelection];
}

const isAllItemsSelected = computed(() => {
  const items = props.championDetail?.items
  if (!items) return false

  const hasStartItems = items.startItems?.length > 0
  const hasBoots = items.boots?.length > 0
  const hasCoreItems = items.coreItems?.length > 0

  const allStartSelected = !hasStartItems || (items.startItems && localSelectedStartItems.value.length === items.startItems.length)
  const allBootsSelected = !hasBoots || (items.boots && localSelectedBoots.value.length === items.boots.length)
  const allCoreSelected = !hasCoreItems || (items.coreItems && localSelectedCoreItems.value.length === items.coreItems.length)
  
  // Ensure at least one category exists to be "all selected"
  if (!hasStartItems && !hasBoots && !hasCoreItems) return false;

  return allStartSelected && allBootsSelected && allCoreSelected
})

const handleToggleSelectAllItems = () => {
  const items = props.championDetail?.items
  if (!items) return

  if (isAllItemsSelected.value) {
    // Cancel select all: keep only the first item selected if items exist
    localSelectedStartItems.value = items.startItems?.length ? [0] : []
    localSelectedBoots.value = items.boots?.length ? [0] : []
    localSelectedCoreItems.value = items.coreItems?.length ? [0] : []
  } else {
    // Select all
    localSelectedStartItems.value = items.startItems?.map((_, i) => i) || []
    localSelectedBoots.value = items.boots?.map((_, i) => i) || []
    localSelectedCoreItems.value = items.coreItems?.map((_, i) => i) || []
  }
}

</script>

<style scoped>
/* Styles from ChampSelectHelper.vue specific to recommendations, runes, items */
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

.item-group h4 {
  margin-bottom: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 8px;
}

.stats-header {
  display: grid;
  grid-template-columns: repeat(2, 80px);
  text-align: left;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-left: auto;
  gap: 8px;
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

.header-actions {
  display: flex;
  gap: 8px;
}

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

.spell-set.selected {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}

.spell-set:hover {
  transform: translateY(-1px);
  box-shadow: var(--el-box-shadow-light);
}

:deep(.el-collapse) {
  border: none;
  width: 100%;
}

:deep(.el-collapse-item) {
  width: 100%;
}

:deep(.el-collapse-item__header) {
  font-size: 16px;
  font-weight: bold;
  color: var(--el-text-color-primary);
  background: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color-light);
  padding: 12px;
  width: 100%;
}

:deep(.el-collapse-item__wrap) {
  border-bottom: none;
  width: 100%;
}

:deep(.el-collapse-item__content) {
  padding: 12px 0;
  width: 100%;
}
</style> 