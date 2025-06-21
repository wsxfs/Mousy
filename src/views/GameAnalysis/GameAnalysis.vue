<template>
  <div class="game-analysis">
    <el-tabs v-model="activeTab" type="card" @tab-remove="removeTab">
      <el-tab-pane name="main" :closable="false">
        <template #label>
          <el-icon><List /></el-icon>
          当前对局
        </template>
        <analysis-table
          ref="mainAnalysisTable"
          :my-team-puuids="myTeamPuuids"
          :their-team-puuids="theirTeamPuuids"
          :my-team-premade-info="myTeamPremadeInfo"
          :their-team-premade-info="theirTeamPremadeInfo"
        />
      </el-tab-pane>
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
          :my-team-premade-info="tab.myTeamPremadeInfo"
          :their-team-premade-info="tab.theirTeamPremadeInfo"
        />
      </el-tab-pane>
    </el-tabs>
    <!-- 仅在当前对局时显示刷新按钮 -->
    <el-button
      v-if="activeTab === 'main'"
      circle
      size="small"
      @click="handleRefresh"
      :loading="loading"
      class="refresh-btn-abs"
      :icon="Refresh"
      title="刷新战绩"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { Refresh, List } from '@element-plus/icons-vue'
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
  myTeamPremadeInfo: Record<string, string[]>
  theirTeamPremadeInfo: Record<string, string[]>
}

const activeTab = ref('main')
const analysisTabs = ref<AnalysisTab[]>([])

const route = useRoute()

// 计算属性获取当前队伍成员
const myTeamPuuids = computed(() => wsStore.syncFrontData.my_team_puuid_list || [])
const theirTeamPuuids = computed(() => wsStore.syncFrontData.their_team_puuid_list || [])

// 计算属性获取组队信息
const myTeamPremadeInfo = computed(() => wsStore.syncFrontData.my_team_premade_info || {})
const theirTeamPremadeInfo = computed(() => wsStore.syncFrontData.their_team_premade_info || {})

// 计算属性获取战绩信息
const myTeamMatchHistory = computed(() => wsStore.syncFrontData.my_team_match_history || {})
const theirTeamMatchHistory = computed(() => wsStore.syncFrontData.their_team_match_history || {})

// 监听队伍成员、战绩数据和组队信息变化
watch(
  [
    myTeamPuuids, 
    theirTeamPuuids, 
    myTeamMatchHistory, 
    theirTeamMatchHistory,
    myTeamPremadeInfo,
    theirTeamPremadeInfo
  ],
  async ([
    newMyTeam, 
    newTheirTeam, 
    newMyTeamHistory, 
    newTheirTeamHistory,
    newMyTeamPremade,
    newTheirTeamPremade
  ], [
    oldMyTeam, 
    oldTheirTeam, 
    oldMyTeamHistory, 
    oldTheirTeamHistory,
    oldMyTeamPremade,
    oldTheirTeamPremade
  ]) => {
    console.log("监听到数据变化：");
    console.log("队伍成员变化：", "\n", oldMyTeam, "\n", oldTheirTeam, "\n", newMyTeam, "\n", newTheirTeam);
    console.log("战绩数据变化：", "\n", oldMyTeamHistory, "\n", oldTheirTeamHistory, "\n", newMyTeamHistory, "\n", newTheirTeamHistory);
    console.log("组队信息变化：", "\n", oldMyTeamPremade, "\n", oldTheirTeamPremade, "\n", newMyTeamPremade, "\n", newTheirTeamPremade);
    
    const hasTeamChanges = JSON.stringify([oldMyTeam, oldTheirTeam]) !== JSON.stringify([newMyTeam, newTheirTeam]);
    const hasHistoryChanges = JSON.stringify([oldMyTeamHistory, oldTheirTeamHistory]) !== JSON.stringify([newMyTeamHistory, newTheirTeamHistory]);
    const hasPremadeChanges = JSON.stringify([oldMyTeamPremade, oldTheirTeamPremade]) !== JSON.stringify([newMyTeamPremade, newTheirTeamPremade]);

    if (hasTeamChanges || hasHistoryChanges || hasPremadeChanges) {
      loading.value = true
      try {
        // 等待主分析表格重新加载数据，指定为当前对局
        console.log("等待主分析表格重新加载数据，指定为当前对局");
        
        await mainAnalysisTable.value?.fetchAnalysisData(true)
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
  const myTeamPremadeInfo = JSON.parse((route.query.myTeamPremadeInfo as string) || '{}')
  const theirTeamPremadeInfo = JSON.parse((route.query.theirTeamPremadeInfo as string) || '{}')
  
  if (route.query.createTab === 'true' && gameId && (blueTeam.length > 0 || redTeam.length > 0)) {
    const tabName = `game-${gameId}`
    
    // 检查标签是否已存在
    if (!analysisTabs.value.find(tab => tab.name === tabName)) {
      analysisTabs.value.push({
        title: `对局 ${gameId}`,
        name: tabName,
        myTeamPuuids: blueTeam,
        theirTeamPuuids: redTeam,
        myTeamPremadeInfo,
        theirTeamPremadeInfo
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
</script>

<style scoped>
.game-analysis {
  height: 100%;
  display: flex;
  flex-direction: column;
  position: relative;
}

.refresh-btn-abs {
  position: absolute;
  top: 10px;
  right: 32px;
  z-index: 10;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
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