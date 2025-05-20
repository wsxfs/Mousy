<template>
  <div class="notebook-alert">
    <div class="title-bar">
      <span>小本本提醒</span>
      <div class="title-actions">
        <el-icon class="close-icon" @click="handleClose">
          <Close />
        </el-icon>
      </div>
    </div>
    
    <div class="content">
      <div v-if="records.length > 0" class="records-container">
        <div v-for="record in records" :key="record.puuid" class="record-card">
          <div class="record-header" :class="record.type">
            <span class="record-type">{{ record.type === 'blacklist' ? '黑名单' : '白名单' }}</span>
          </div>
          <div class="record-content">
            <div class="player-info">
              <span class="player-name">{{ record.game_name }}</span>
              <span class="record-time">{{ formatTime(record.timestamp) }}</span>
            </div>
            <div class="record-details">
              <div class="reason">
                <span class="label">原因：</span>
                <span>{{ record.reason }}</span>
              </div>
              <div class="details" v-if="record.details">
                <span class="label">详情：</span>
                <span>{{ record.details }}</span>
              </div>
              <div class="game-info" v-if="record.champion_id">
                <span class="label">使用英雄：</span>
                <img 
                  :src="getResourceUrl('champion_icons', record.champion_id)" 
                  :alt="String(record.champion_id)"
                  class="champion-icon"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
      <el-empty v-else description="暂无记录" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { Close } from '@element-plus/icons-vue'
// import { useWebSocketStore } from '../../stores/websocket' // 不再直接使用 store
import axios from 'axios'

// 导入类型定义
interface NotebookRecord {
  summoner_id: string
  game_name: string
  champion_id?: number
  timestamp: number
  reason?: string
  details?: string
  game_id?: string
  region?: string
  puuid?: string
  type: 'blacklist' | 'whitelist'
}

interface NotebookRecords {
  my_team: NotebookRecord[]
  their_team: NotebookRecord[]
}

// const wsStore = useWebSocketStore() // 不再直接使用 store
const records = ref<NotebookRecord[]>([])
const gameResources = ref<Record<string, Record<number, string>>>({})

// 格式化时间
const formatTime = (timestamp: number) => {
  const date = new Date(timestamp * 1000)
  return date.toLocaleString()
}

// 获取资源URL
const getResourceUrl = (type: string, id: number): string => {
  const resources = gameResources.value[type]
  if (resources?.[id]) {
    return `data:image/png;base64,${resources[id]}`
  }
  return '/placeholder.png'
}

// 加载游戏资源
const loadGameResources = async (championIds: number[]) => {
  try {
    const resourceRequest = {
      champion_icons: championIds
    }

    const response = await axios.post(
      '/api/common/game_resource/batch_get_resources',
      resourceRequest
    )

    gameResources.value = response.data
  } catch (error) {
    console.error('加载游戏资源失败:', error)
  }
}

// 更新记录数据
const updateRecords = async (notebookRecords: NotebookRecords | null) => { // 修改类型
  console.log('NotebookAlert 更新小本本记录:', notebookRecords)
  if (notebookRecords) {
    // 合并我方和敌方的记录
    records.value = [
      ...(notebookRecords.my_team || []),
      ...(notebookRecords.their_team || [])
    ]
    console.log('NotebookAlert 合并后的记录:', records.value)

    // 收集所有英雄ID
    const championIds = records.value
      .filter(record => record.champion_id)
      .map(record => record.champion_id as number)

    // 加载英雄图标
    if (championIds.length > 0) {
      await loadGameResources(championIds)
    }
  }
}

// 关闭窗口
const handleClose = () => {
  window.ipcRenderer.send('close-notebook-alert')
}


onMounted(async () => {
  console.log('小本本提醒窗口已挂载')

  // 监听主进程发送的初始化数据
  window.ipcRenderer.on('initialize-notebook-alert', (_event: any, initialRecords: NotebookRecords) => {
    console.log('NotebookAlert 收到 initialize-notebook-alert 数据:', initialRecords)
    updateRecords(initialRecords)
  })

  // 可选：如果仍然需要通过 wsStore 监听后续更新 (通常主进程会推送)
  // watch(() => wsStore.syncFrontData.notebook_records, (newRecords) => {
  //   console.log('小本本记录发生变化 (wsStore):', newRecords)
  //   updateRecords(newRecords)
  // })
})
</script>

<style scoped>
.notebook-alert {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--el-bg-color);
}

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

.content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.records-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.record-card {
  background: var(--el-bg-color-overlay);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: var(--el-box-shadow-light);
}

.record-header {
  padding: 8px 16px;
  color: white;
  font-weight: bold;
}

.record-header.blacklist {
  background: var(--el-color-danger);
}

.record-header.whitelist {
  background: var(--el-color-success);
}

.record-content {
  padding: 16px;
}

.player-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.player-name {
  font-size: 16px;
  font-weight: bold;
}

.record-time {
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.record-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.reason, .details, .game-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.label {
  color: var(--el-text-color-secondary);
  min-width: 60px;
}

.champion-icon {
  width: 24px;
  height: 24px;
  border-radius: 4px;
}
</style> 