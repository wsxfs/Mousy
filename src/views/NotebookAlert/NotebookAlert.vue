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

  // 通知主进程Vue组件已就绪，可以发送数据了
  window.ipcRenderer.send('notebook-alert-vue-ready')

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
  background: var(--el-bg-color-page); /* 使用页面背景色 */
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
}

.title-bar {
  -webkit-app-region: drag;
  height: 36px; /* 稍微增加高度 */
  background: var(--el-color-primary-light-3); /* 柔和一些的品牌色 */
  color: var(--el-color-white);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 12px 0 16px; /* 调整内边距 */
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.title-bar span {
  font-weight: 600;
}

.close-icon {
  -webkit-app-region: no-drag;
  cursor: pointer;
  font-size: 18px; /* 调整大小 */
  color: var(--el-color-white);
  padding: 4px; /* 增加点击区域 */
  border-radius: 50%;
  transition: background-color 0.2s ease-in-out;
}

.close-icon:hover {
  background-color: var(--el-color-primary-light-5); /* 悬停效果 */
}

.content {
  flex: 1;
  padding: 16px; /* 统一内边距 */
  overflow-y: auto;
}

.records-container {
  display: flex;
  flex-direction: column;
  gap: 12px; /* 调整卡片间距 */
}

.record-card {
  background: var(--el-bg-color-overlay);
  border-radius: 6px; /* 调整圆角 */
  overflow: hidden;
  box-shadow: var(--el-box-shadow);
  border: 1px solid var(--el-border-color-lighter);
  transition: box-shadow 0.3s ease;
}

.record-card:hover {
  box-shadow: var(--el-box-shadow-darker);
}

.record-header {
  padding: 10px 16px; /* 调整内边距 */
  color: white;
  font-weight: 500; /* 调整字重 */
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.record-header.blacklist {
  background: var(--el-color-danger-light-3); /* 使用柔和的危险色 */
}

.record-header.whitelist {
  background: var(--el-color-success-light-3); /* 使用柔和的成功色 */
}

.record-type {
  font-size: 14px;
}

.record-content {
  padding: 12px 16px; /* 调整内边距 */
}

.player-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px; /* 调整间距 */
}

.player-name {
  font-size: 16px;
  font-weight: 600; /* 加粗 */
  color: var(--el-text-color-primary);
}

.record-time {
  color: var(--el-text-color-secondary);
  font-size: 13px; /* 调整大小 */
}

.record-details {
  display: flex;
  flex-direction: column;
  gap: 6px; /* 调整间距 */
  font-size: 14px; /* 统一字体大小 */
}

.reason, .details, .game-info {
  display: flex;
  /* align-items: center; */ /* 改为 baseline 对齐，如果内容多行 */
  align-items: baseline;
  gap: 8px;
}

.label {
  color: var(--el-text-color-regular); /* 调整颜色 */
  min-width: 65px; /* 稍微调整宽度 */
  font-weight: 500;
  flex-shrink: 0; /* 防止标签被压缩 */
}

.reason span:not(.label),
.details span:not(.label) {
  word-break: break-all; /* 处理长文本换行 */
  color: var(--el-text-color-regular);
}

.champion-icon {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  border: 1px solid var(--el-border-color-lighter); /* 给图标添加边框 */
  margin-right: 4px; /* 图标和文字间距 */
}

/* 自定义滚动条样式 (Webkit) */
.content::-webkit-scrollbar {
  width: 8px;
}

.content::-webkit-scrollbar-track {
  background: transparent;
  border-radius: 4px;
}

.content::-webkit-scrollbar-thumb {
  background: var(--el-border-color); 
  border-radius: 4px;
}

.content::-webkit-scrollbar-thumb:hover {
  background: var(--el-text-color-placeholder);
}

/* 调整 el-empty 样式 */
.el-empty {
  margin-top: 20px; /* 增加顶部外边距，使其视觉上更居中 */
}

</style> 