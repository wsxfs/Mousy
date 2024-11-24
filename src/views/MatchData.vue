<template>
    <div class="match-data">
        <el-tabs v-model="activeTab" type="card" @tab-remove="removeTab" class="match-data-tabs">
            <el-tab-pane name="champion-list" :closable="false">
                <template #label>
                    <el-icon><List /></el-icon>
                </template>
                <div class="champion-list-container">
                    <!-- 位置选择器 -->
                    <div class="position-selector">
                        <el-radio-group v-model="selectedPosition" @change="handlePositionChange" :disabled="isARAM">
                            <el-radio-button label="ALL">全部</el-radio-button>
                            <el-radio-button label="TOP">上路</el-radio-button>
                            <el-radio-button label="JUNGLE">打野</el-radio-button>
                            <el-radio-button label="MID">中路</el-radio-button>
                            <el-radio-button label="ADC">下路</el-radio-button>
                            <el-radio-button label="SUPPORT">辅助</el-radio-button>
                        </el-radio-group>
                    </div>

                    <!-- 筛选条件 -->
                    <div class="filter-section">
                        <el-form :inline="true" :model="filterForm">
                            <el-form-item label="搜索">
                                <el-input
                                    v-model="searchQuery"
                                    placeholder="搜索英雄"
                                    clearable
                                    @clear="handleSearch"
                                    @input="handleSearch"
                                    style="width: 150px;"
                                >
                                    <template #prefix>
                                        <el-icon><Search /></el-icon>
                                    </template>
                                </el-input>
                            </el-form-item>
                            <el-form-item label="服务器">
                                <el-select v-model="filterForm.region" placeholder="选择服务器" style="width: 100px;">
                                    <el-option label="全球" value="global" />
                                    <el-option label="韩服" value="kr" />
                                    <el-option label="欧服" value="euw" />
                                    <el-option label="美服" value="na" />
                                </el-select>
                            </el-form-item>
                            <el-form-item label="段位">
                                <el-select v-model="filterForm.tier" placeholder="选择段位" style="width: 100px;">
                                    <el-option label="全部" value="all" />
                                    <el-option label="青铜" value="bronze" />
                                    <el-option label="白银" value="silver" />
                                    <el-option label="黄金" value="gold" />
                                    <el-option label="黄金及以上" value="gold_plus" />
                                    <el-option label="铂金" value="platinum" />
                                    <el-option label="铂金及以上" value="platinum_plus" />
                                    <el-option label="钻石" value="diamond" />
                                    <el-option label="钻石及以上" value="diamond_plus" />
                                    <el-option label="大师" value="master" />
                                    <el-option label="大师及以上" value="master_plus" />
                                    <el-option label="宗师" value="grandmaster" />
                                    <el-option label="王者" value="challenger" />
                                </el-select>
                            </el-form-item>
                            <el-form-item label="模式">
                                <el-select v-model="filterForm.mode" placeholder="选择模式" style="width: 100px;">
                                    <el-option label="单双排位" value="ranked" />
                                    <el-option label="极地大乱斗" value="aram" />
                                </el-select>
                            </el-form-item>
                            <el-form-item>
                                <el-button 
                                    type="primary"
                                    @click="applyAllChampionsItems"
                                    :loading="isApplyingItems">
                                    一键应用所有英雄装备
                                </el-button>
                            </el-form-item>
                            <el-form-item>
                                <el-button 
                                    type="default"
                                    @click="resetAllChampionsItems"
                                    :loading="isApplyingItems">
                                    恢复默认出装
                                </el-button>
                            </el-form-item>
                        </el-form>
                    </div>

                    <!-- 英雄列表 -->
                    <div class="champion-tier-list">
                        <el-table :data="filteredChampionList" 
                                style="width: 100%" 
                                class="centered-table" 
                                :default-sort="{ prop: 'tier', order: 'ascending' }" 
                                @row-click="handleRowClick"
                                height="calc(100% - 40px)">
                            <el-table-column label="Tier" width="80" sortable prop="tier" :sort-orders="['ascending', 'descending', null]">
                                <template #default="scope">
                                    <el-tag :type="getTierType(scope.row.tier)">
                                        T{{ scope.row.tier }}
                                    </el-tag>
                                </template>
                            </el-table-column>
                            <el-table-column label="英雄" width="200">
                                <template #default="scope">
                                    <div class="champion-info">
                                        <div class="champion-avatar">
                                            <img :src="getResourceUrl('champion_icons', scope.row.championId)" class="champion-icon">
                                        </div>
                                        <span class="champion-name">{{ scope.row.name }}</span>
                                    </div>
                                </template>
                            </el-table-column>
                            <el-table-column prop="winRate" label="胜率" width="100" sortable :sort-orders="['descending', 'ascending', null]">
                                <template #default="scope">
                                    {{ (scope.row.winRate * 100).toFixed(1) }}%
                                </template>
                            </el-table-column>
                            <el-table-column prop="pickRate" label="登场率" width="100" sortable :sort-orders="['descending', 'ascending', null]">
                                <template #default="scope">
                                    {{ (scope.row.pickRate * 100).toFixed(1) }}%
                                </template>
                            </el-table-column>
                            <el-table-column prop="banRate" label="禁用率" width="100" sortable :sort-orders="['descending', 'ascending', null]">
                                <template #default="scope">
                                    {{ (scope.row.banRate * 100).toFixed(1) }}%
                                </template>
                            </el-table-column>
                            <el-table-column label="克制英雄" width="200">
                                <template #default="scope">
                                    <div class="counter-champions">
                                        <img v-for="counter in scope.row.counters" :key="counter.championId"
                                            :src="getResourceUrl('champion_icons', counter.championId)" 
                                            class="counter-icon">
                                    </div>
                                </template>
                            </el-table-column>
                            <el-table-column label="位置" width="100" v-if="selectedPosition === 'ALL'">
                                <template #default="scope">
                                    {{ getPositionLabel(scope.row.position) }}
                                </template>
                            </el-table-column>
                        </el-table>
                    </div>
                </div>
            </el-tab-pane>

            <!-- 动态英雄详情标签页 -->
            <el-tab-pane
                v-for="item in championTabs"
                :key="item.name"
                :label="item.title"
                :name="item.name"
                :closable="true"
            >
                <champion-detail 
                    :champion-id="item.championId"
                    :initial-position="item.position"
                    :initial-tier="filterForm.tier"
                    :initial-region="item.region"
                    :mode="item.mode"
                    @back="handleBack"
                    @champion-click="handleChampionClick"
                    @position-change="handleDetailPositionChange(item.name, $event)"
                />
            </el-tab-pane>
        </el-tabs>

        <!-- 在合适的位置添加进度条 -->
        <el-dialog
            v-model="progressVisible"
            title="正在应用装备"
            :close-on-click-modal="false"
            :close-on-press-escape="false"
            :show-close="false"
            width="400px"
        >
            <div class="progress-content">
                <el-progress 
                    :percentage="progress.percentage"
                    :format="(_format: number) => `${progress.current}/${progress.total}`"
                    status="success"
                />
                <div class="progress-text">
                    正在处理英雄装备，请稍候...
                </div>
            </div>
        </el-dialog>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import ChampionDetail from './ChampionDetail.vue'
import { List, Search } from '@element-plus/icons-vue'
import { pinyin } from 'pinyin-pro'

// 修改接口定义
interface Champion {
    championId: number
    name: string
    winRate: number
    pickRate: number
    banRate: number
    kda: number
    tier: number
    rank: number
    position: string
    counters: Array<{
        championId: number
    }>
}

interface ResourceResponse {
    champion_icons?: Record<string | number, string>
}

// 添加资源状态
const gameResources = ref<ResourceResponse>({})

// 添加获取资源URL的工具函数
const getResourceUrl = (
    type: keyof ResourceResponse,
    id: number | string
): string => {
    const resources = gameResources.value[type] as Record<string | number, string>
    if (resources?.[id]) {
        return `data:image/png;base64,${resources[id]}`
    }
    return '/placeholder.png'
}

// 添加资源加载函数
const loadGameResources = async (champions: Champion[]) => {
    try {
        const resourceRequest = {
            champion_icons: [] as number[]
        }
        
        champions.forEach(champion => {
            if (!resourceRequest.champion_icons.includes(champion.championId)) {
                resourceRequest.champion_icons.push(champion.championId)
            }
            
            champion.counters.forEach(counter => {
                if (!resourceRequest.champion_icons.includes(counter.championId)) {
                    resourceRequest.champion_icons.push(counter.championId)
                }
            })
        })
        
        const response = await axios.post<ResourceResponse>(
            '/api/common/game_resource/batch_get_resources',
            resourceRequest
        )
        
        gameResources.value = response.data
    } catch (error) {
        console.error('加载游戏资源失败:', error)
        ElMessage.error('加载游戏资源失败')
    }
}

// 状态定义
const selectedPosition = ref('TOP')
const championList = ref<Champion[]>([])
const filterForm = ref({
    tier: 'platinum_plus',
    mode: 'ranked',
    region: 'kr'
})

// 添加标签页相关的状态
const activeTab = ref('champion-list')
const championTabs = ref<Array<{
    title: string
    name: string
    championId: number
    position: string
    tier: string
    region: string
    mode: string
}>>([])

// 添加计算属性判断是否为极地大乱斗模式
const isARAM = computed(() => filterForm.value.mode === 'aram')

// 修改获取英雄数据的方法
const fetchChampionData = async () => {
    try {
        const params = new URLSearchParams({
            region: filterForm.value.region,
            mode: filterForm.value.mode,
            tier: filterForm.value.tier
        })

        const response = await axios.post(
            '/api/match_data/match_data/tier_list',
            params,
            {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            }
        )

        if (filterForm.value.mode === 'aram') {
            championList.value = response.data.data
        } else if (selectedPosition.value === 'ALL') {
            // 合并所有分路的数据
            const allPositions = ['TOP', 'JUNGLE', 'MID', 'ADC', 'SUPPORT']
            championList.value = allPositions.flatMap(position => {
                const championsInPosition = response.data.data[position] || []
                return championsInPosition.map((champion: Champion) => ({
                    ...champion,
                    position: position
                }))
            })
        } else if (response.data?.data?.[selectedPosition.value]) {
            championList.value = response.data.data[selectedPosition.value]
        }
        
        await loadGameResources(championList.value)
    } catch (error) {
        ElMessage.error('获取英雄数据失败')
        console.error('获取英雄数据失败:', error)
    }
}

// 修改处理位置变更的方法
const handlePositionChange = () => {
    if (!isARAM.value) {
        fetchChampionData()
    }
}

// 修改监听筛选条件的方法
watch(filterForm, (newValue) => {
    if (newValue.mode === 'aram') {
        selectedPosition.value = 'ALL'
    } else if (selectedPosition.value === 'ALL') {
        selectedPosition.value = 'TOP'
    }
    fetchChampionData()
}, { deep: true })

onMounted(() => {
    fetchChampionData()
})

// 添加 Tier 标签样式判断方法
const getTierType = (tier: number): '' | 'success' | 'warning' | 'info' => {
    switch (tier) {
        case 1:
            return 'success'
        case 2:
            return 'warning'
        case 3:
            return 'info'
        default:
            return ''
    }
}

// 修改处理点击英雄事件
const handleChampionClick = (championId: number, championName?: string) => {
    const tabName = `champion-${championId}`
    
    if (!championTabs.value.find(tab => tab.name === tabName)) {
        championTabs.value.push({
            title: championName || `英雄 ${championId}`,
            name: tabName,
            championId: championId,
            position: selectedPosition.value,
            tier: filterForm.value.tier,
            region: filterForm.value.region,
            mode: filterForm.value.mode
        })
    }
    
    activeTab.value = tabName
}

// 修改行点击处理函数
const handleRowClick = (row: Champion) => {
    handleChampionClick(row.championId, row.name)
}

// 移除标签页
const removeTab = (tabName: string) => {
    const tabs = championTabs.value
    let activeName = activeTab.value
    
    if (activeName === tabName) {
        tabs.forEach((tab, index) => {
            if (tab.name === tabName) {
                const nextTab = tabs[index + 1] || tabs[index - 1]
                if (nextTab) {
                    activeName = nextTab.name
                } else {
                    activeName = 'champion-list'
                }
            }
        })
    }
    
    activeTab.value = activeName
    championTabs.value = tabs.filter(tab => tab.name !== tabName)
}

// 修改返回处理函数
const handleBack = () => {
    activeTab.value = 'champion-list'
}

// 添加处理详情页位置变更的方法
const handleDetailPositionChange = (tabName: string, newPosition: string) => {
    const tab = championTabs.value.find(tab => tab.name === tabName)
    if (tab) {
        tab.position = newPosition
    }
}

// 添加加载状态
const isApplyingItems = ref(false)

// 在 setup 中添加进度相关的状态
const progressVisible = ref(false)
const progress = ref({
  total: 0,
  current: 0,
  percentage: 0
})

// 添加轮询进度的方法
const pollProgress = async () => {
  try {
    const response = await axios.get('/api/match_data/match_data/get_apply_items_progress')
    const { total, current, is_running } = response.data
    
    if (total > 0) {
      progress.value.total = total
      progress.value.current = current
      progress.value.percentage = Math.round((current / total) * 100)
    }
    
    if (is_running) {
      setTimeout(pollProgress, 100) // 每秒轮询一次
    } else {
      progressVisible.value = false
    }
  } catch (error) {
    console.error('获取进度失败:', error)
    progressVisible.value = false
  }
}

// 修改一键应用所有英雄装备的方
const applyAllChampionsItems = async () => {
  try {
    isApplyingItems.value = true
    progressVisible.value = true
    progress.value = { total: 0, current: 0, percentage: 0 }
    
    const requestData = {
      region: filterForm.value.region,
      mode: filterForm.value.mode,
      tier: filterForm.value.tier,
      position: selectedPosition.value
    }

    // 开始轮询进度
    pollProgress()

    await axios.post(
      '/api/match_data/match_data/apply_all_champions_items',
      requestData,
      {
        headers: {
          'Content-Type': 'application/json'
        }
      }
    )
    
    ElMessage.success('所有英雄装备已更新')
  } catch (error) {
    console.error('应用装备失败:', error)
    ElMessage.error('应用装备失败')
  } finally {
    isApplyingItems.value = false
  }
}

// 修改恢复默认出装的方法
const resetAllChampionsItems = async () => {
    try {
        isApplyingItems.value = true

        await axios.post(
            '/api/match_data/match_data/reset_all_champions_items',  // 确保路径正确
            {},  // 不携带任何数据
            {
                headers: {
                    'Content-Type': 'application/json'  // 明确指定 Content-Type
                }
            }
        )
        
        ElMessage.success('所有英雄装备已恢复默认')
    } catch (error) {
        console.error('恢复默认装备失败:', error)
        ElMessage.error('恢复默认装备失败')
    } finally {
        isApplyingItems.value = false
    }
}

// 添加搜索相关的状态和方法
const searchQuery = ref('')

// 修改拼音转换工具函数
const getPinyinAndFirstLetters = (text: string) => {
    // 获取完整拼音
    const pinyinText = pinyin(text, { toneType: 'none' })
    // 获取拼音首字母并移除空格
    const firstLetters = pinyin(text, { pattern: 'first', toneType: 'none' }).replace(/\s/g, '')
    // 获取拼音首字母并保留空格，用于分开匹配
    const firstLettersWithSpace = pinyin(text, { pattern: 'first', toneType: 'none' })
    return {
        pinyin: pinyinText.toLowerCase(),
        firstLetters: firstLetters.toLowerCase(),
        firstLettersWithSpace: firstLettersWithSpace.toLowerCase()
    }
}

// 修改 filteredChampionList 计算属性
const filteredChampionList = computed(() => {
    if (!searchQuery.value) {
        return championList.value
    }
    const query = searchQuery.value.toLowerCase()
    // 移除查询中的空格，用于匹配连续的首字母
    const queryNoSpace = query.replace(/\s/g, '')
    
    return championList.value.filter(champion => {
        const name = champion.name.toLowerCase()
        const { pinyin: namePinyin, firstLetters, firstLettersWithSpace } = getPinyinAndFirstLetters(champion.name)
        
        return name.includes(query) || 
               namePinyin.includes(query) || 
               firstLetters.includes(queryNoSpace) ||  // 匹配连续的首字母（如"jt"）
               firstLettersWithSpace.includes(query)   // 匹配带空格的首字母（如"j t"）
    })
})

const handleSearch = () => {
    // 搜索时不需要特别处理，因为使用了计算属性
}

// 添加位置标签转换函数
const getPositionLabel = (position: string) => {
    const positionMap: Record<string, string> = {
        'TOP': '上路',
        'JUNGLE': '打野',
        'MID': '中路',
        'ADC': '下路',
        'SUPPORT': '辅助'
    }
    return positionMap[position] || position
}
</script>

<style scoped>
.match-data {
    box-sizing: border-box;
    margin: 0 auto;
    max-width: 900px;
    width: 100%;
    height: 100vh;
    background-color: var(--el-bg-color-overlay);
    border-radius: 8px;
    box-shadow: var(--el-box-shadow-light);
    padding: 20px;
    display: flex;
    flex-direction: column;
}

.match-data-tabs {
    height: 100%;
    display: flex;
}

.champion-list-container {
    height: 110%;
    display: flex;
    flex-direction: column;
}

.position-selector {
    margin-bottom: 20px;
    text-align: center;
    flex-shrink: 0;
}

.filter-section {
    margin-bottom: 20px;
    flex-shrink: 0;
}

.champion-tier-list {
    flex: 1;
    overflow: hidden;
}

.champion-info {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 0 10px;
}

.champion-avatar {
    width: 40px;
    min-width: 40px;
    height: 40px;
    display: flex;
    justify-content: center;
    align-items: center;
}

.champion-icon {
    width: 40px;
    height: 40px;
    border-radius: 50%;
}

.counter-champions {
    display: flex;
    gap: 8px;
}

.counter-icon {
    width: 24px;
    height: 24px;
    border-radius: 50%;
}

@media (max-width: 768px) {
    .match-data {
        padding: 10px;
    }

    .position-selector {
        overflow-x: auto;
    }

    :deep(.el-form--inline) {
        flex-wrap: wrap;
    }

    :deep(.el-form-item) {
        margin-right: 0;
        margin-bottom: 10px;
        width: 100%;
    }
}

/* 添加 Tier 标签样式 */
:deep(.el-tag) {
    width: 40px;
    text-align: center;
}

/* 添加表格居中样式 */
.champion-tier-list {
    flex: 1;
    min-height: 0;
}

.centered-table {
    max-width: 900px;
    
}

/* 美化滚动条样式 */
.centered-table::-webkit-scrollbar {
    width: 6px;
}

.centered-table::-webkit-scrollbar-thumb {
    background-color: var(--el-border-color-darker);
    border-radius: 3px;
}

.centered-table::-webkit-scrollbar-track {
    background-color: var(--el-border-color-light);
    border-radius: 3px;
}

/* 调整列宽和对齐方式 */
:deep(.el-table .cell) {
    text-align: center;
    white-space: nowrap;
}

:deep(.champion-info) {
    justify-content: flex-start;
}

/* 调整百分比列的样式 */
:deep(.el-table td.el-table__cell) {
    background-color: var(--el-bg-color-overlay);
}

/* 保克制英雄图标居中显示 */
:deep(.counter-champions) {
    justify-content: center;
}

/* 调整样式以适应标签页布局 */
.match-data {
    display: flex;
    flex-direction: column;
    height: 100%;
}

:deep(.el-tabs) {
    height: 100%;
    display: flex;
}

:deep(.el-tabs__content) {
    flex: 1;
    overflow: hidden;
    height: 100%;
}

:deep(.el-tab-pane) {
    height: 100%;
}

.progress-content {
    padding: 20px;
    text-align: center;
}

.progress-text {
    margin-top: 15px;
    color: var(--el-text-color-secondary);
}
</style>