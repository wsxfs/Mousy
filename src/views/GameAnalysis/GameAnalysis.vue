<template>
  <div class="game-analysis">
    <el-tabs v-model="activeTab" type="card" @tab-remove="removeTab">
      <!-- 主页面标签 -->
      <el-tab-pane name="main" :closable="false">
        <template #label>
          <el-icon><List /></el-icon>
          当前对局
        </template>
        
        <div class="header-controls">
          <el-button 
            type="primary" 
            size="small" 
            @click="$emit('back')"
            :icon="ArrowLeft">
            返回对局详情
          </el-button>
          <el-button 
            type="primary" 
            size="small" 
            @click="handleRefresh"
            :loading="loading"
            :icon="Refresh">
            刷新战绩
          </el-button>
        </div>

        <analysis-table
          ref="mainAnalysisTable"
          :my-team-puuids="myTeamPuuids"
          :their-team-puuids="theirTeamPuuids"
        />
      </el-tab-pane>

      <!-- 动态标签页 -->
      <el-tab-pane
        v-for="tab in analysisTabs"
        :key="tab.name"
        :label="tab.title"
        :name="tab.name"
        closable
      >
        <analysis-table
          :my-team-puuids="tab.myTeamPuuids"
          :their-team-puuids="tab.theirTeamPuuids"
        />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { ArrowLeft, Refresh, List } from '@element-plus/icons-vue'
import { useWebSocketStore } from '../../stores/websocket'
import AnalysisTable from './components/AnalysisTable.vue'
import { useRoute } from 'vue-router'

const wsStore = useWebSocketStore()
const loading = ref(false)
const mainAnalysisTable = ref<InstanceType<typeof AnalysisTable> | null>(null)

interface AnalysisTab {
  title: string
  name: string
  myTeamPuuids: string[]
  theirTeamPuuids: string[]
}

const activeTab = ref('main')
const analysisTabs = ref<AnalysisTab[]>([])

const route = useRoute()

// 计算属性获取当前队伍成员
const myTeamPuuids = computed(() => wsStore.syncFrontData.my_team_puuid_list || [])
const theirTeamPuuids = computed(() => wsStore.syncFrontData.their_team_puuid_list || [])

// 监听队伍成员变化
watch(
  [myTeamPuuids, theirTeamPuuids],
  async ([newMyTeam, newTheirTeam], [oldMyTeam, oldTheirTeam]) => {
    if (JSON.stringify([oldMyTeam, oldTheirTeam]) !== JSON.stringify([newMyTeam, newTheirTeam])) {
      loading.value = true
      try {
        // 等待主分析表格重新加载数据
        await mainAnalysisTable.value?.fetchAnalysisData()
      } finally {
        loading.value = false
      }
    }
  },
  { deep: true }
)

// 刷新处理函数
const handleRefresh = async () => {
  loading.value = true
  try {
    await mainAnalysisTable.value?.fetchAnalysisData()
  } finally {
    loading.value = false
  }
}

// 移除标签页
const removeTab = (tabName: string) => {
  const tabs = analysisTabs.value
  let activeName = activeTab.value
  
  if (activeName === tabName) {
    tabs.forEach((tab, index) => {
      if (tab.name === tabName) {
        const nextTab = tabs[index + 1] || tabs[index - 1]
        if (nextTab) {
          activeName = nextTab.name
        } else {
          activeName = 'main'
        }
      }
    })
  }
  
  activeTab.value = activeName
  analysisTabs.value = tabs.filter(tab => tab.name !== tabName)
}

// 添加创建标签页的函数
const createAnalysisTab = () => {
  console.log("route.query:", route.query)
  const gameId = route.query.gameId as string
  const blueTeam = (route.query.blueTeam as string)?.split(',') || []
  const redTeam = (route.query.redTeam as string)?.split(',') || []
  
  if (route.query.createTab === 'true' && gameId && (blueTeam.length > 0 || redTeam.length > 0)) {
    const tabName = `game-${gameId}`
    
    // 检查标签是否已存在
    if (!analysisTabs.value.find(tab => tab.name === tabName)) {
      analysisTabs.value.push({
        title: `对局 ${gameId}`,
        name: tabName,
        myTeamPuuids: blueTeam,
        theirTeamPuuids: redTeam
      })
      
      // 切换到新标签
      activeTab.value = tabName
    }
  }
}

// 在组件挂载时检查是否需要创建新标签
onMounted(() => {
  createAnalysisTab()
})

// 监听路由变化，处理新的标签创建请求
watch(
  () => route.query,
  () => {
    createAnalysisTab()
  }
)

// 定义 emit
defineEmits<{
  (e: 'back'): void
}>()
</script>

<style scoped>
.game-analysis {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.header-controls {
  margin: 10px;
  display: flex;
  gap: 10px;
}

:deep(.el-tabs) {
  height: 100%;
  display: flex;
}

:deep(.el-tabs__content) {
  flex: 1;
  overflow: hidden;
  position: relative;
}

:deep(.el-tab-pane) {
  height: 100%;
  position: absolute;
  width: 100%;
  top: 0;
  left: 0;
}
</style>