<template>
    <div class="match-data">
        <!-- 位置选择器 -->
        <div class="position-selector">
            <el-radio-group v-model="selectedPosition" @change="handlePositionChange">
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
                <el-form-item label="段位">
                    <el-select v-model="filterForm.tier" placeholder="选择段位" style="width: 100px;">
                        <el-option label="铂金以上" value="platinum_plus" />
                        <el-option label="钻石以上" value="diamond_plus" />
                        <el-option label="大师以上" value="master_plus" />
                    </el-select>
                </el-form-item>
                <el-form-item label="模式">
                    <el-select v-model="filterForm.mode" placeholder="选择模式" style="width: 100px;">
                        <el-option label="单双排位" value="ranked" />
                        <el-option label="匹配模式" value="normal" />
                    </el-select>
                </el-form-item>
            </el-form>
        </div>

        <!-- 英雄列表 -->
        <div class="champion-tier-list">
            <el-table :data="championList" style="width: 100%" class="centered-table" :default-sort="{ prop: 'tier', order: 'ascending' }">
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
            </el-table>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

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
    mode: 'ranked'
})

// 获取英雄数据
const fetchChampionData = async () => {
    try {
        const params = new URLSearchParams({
            region: 'kr',
            mode: filterForm.value.mode,
            tier: filterForm.value.tier
        })

        const response = await axios.post(
            '/api/match_data/tier_list',
            params,
            {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            }
        )

        if (response.data?.data?.[selectedPosition.value]) {
            championList.value = response.data.data[selectedPosition.value]
            // 加载英雄资源
            await loadGameResources(championList.value)
        }
    } catch (error) {
        ElMessage.error('获取英雄数据失败')
        console.error('获取英雄数据失败:', error)
    }
}

// 处理位置变更
const handlePositionChange = () => {
    fetchChampionData()
}

// 监听筛选条件变化
watch(filterForm, () => {
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
</script>

<style scoped>
.match-data {
    box-sizing: border-box;
    margin: 0 auto;
    max-width: 900px;
    width: 100%;
    height: 100%;
    background-color: var(--el-bg-color-overlay);
    border-radius: 8px;
    box-shadow: var(--el-box-shadow-light);
    padding: 20px;
    display: flex;
    flex-direction: column;
}

.position-selector {
    margin-bottom: 20px;
    text-align: center;
}

.filter-section {
    margin-bottom: 20px;
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
    display: flex;
    justify-content: center;
    flex: 1;
    overflow: hidden;
}

.centered-table {
    max-width: 900px;
    overflow-y: auto;
    height: 100%;
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
</style>