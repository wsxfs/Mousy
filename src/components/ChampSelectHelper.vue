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
      </div>

      <!-- 选择英雄信息 -->
      <div class="champ-select-info">
        <div class="champ-info">
          <!-- 候选席英雄 -->
          <div class="bench-champs">
            <h4>候选席英雄</h4>
            <div v-if="wsStore.champSelectInfo.benchChampions.length > 0" class="bench-list">
              <div v-for="championId in wsStore.champSelectInfo.benchChampions" 
                   :key="championId" 
                   class="bench-item">
                <img 
                  :src="getResourceUrl(championId)" 
                  :alt="'Champion ' + championId"
                  class="champion-icon"
                />
                <span>ID: {{ championId }}</span>
              </div>
            </div>
            <span v-else class="no-champ-info">无候选席英雄</span>
          </div>
          
          <!-- 当前英雄 -->
          <div class="current-champ">
            <h4>当前英雄</h4>
            <template v-if="wsStore.champSelectInfo.currentChampion">
              <img 
                :src="getResourceUrl(wsStore.champSelectInfo.currentChampion)" 
                :alt="'Champion ' + wsStore.champSelectInfo.currentChampion"
                class="champion-icon"
              />
              <span>ID: {{ wsStore.champSelectInfo.currentChampion }}</span>
            </template>
            <span v-else class="no-champ-info">未选择英雄</span>
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

const gameStateStore = useGameStateStore()
const wsStore = useWebSocketStore()

// 游戏资源状态
const gameResources = ref<Record<string, Record<string | number, string>>>({})

onMounted(async () => {
  await gameStateStore.fetchGameMode()
  // 确保 WebSocket 连接
  if (!wsStore.isConnected) {
    wsStore.connect()
  }
})

const gameMode = computed(() => gameStateStore.gameMode)

// 加载游戏资源方法
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
    console.error('加载英雄图标失败:', error)
  }
}

// 获取资源URL方法
const getResourceUrl = (id: number) => {
  const resources = gameResources.value['champion_icons']
  if (resources?.[id]) {
    return `data:image/png;base64,${resources[id]}`
  }
  return '/placeholder.png'
}

// 监听英雄信息变化并加载资源
watch(() => wsStore.champSelectInfo, async (newInfo) => {
  console.log('champSelectInfo changed:', newInfo) // 添加日志
  const championIds = [
    ...(newInfo.currentChampion ? [newInfo.currentChampion] : []),
    ...newInfo.benchChampions
  ]
  if (championIds.length > 0) {
    await loadGameResources(championIds)
  }
})

const handleClose = () => {
  // 通过 electron 的 preload 脚本暴露的方法关闭窗口
  window.electron.ipcRenderer.send('close-champ-select')
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
</style>