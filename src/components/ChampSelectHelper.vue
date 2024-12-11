<template>
  <div class="champ-select-helper">
    <!-- 添加标题栏 -->
    <div class="title-bar">
      <span>选人助手</span>
      <el-icon class="close-icon" @click="handleClose">
        <Close />
      </el-icon>
    </div>
    
    <div class="content">
      <div class="game-mode-info">
        <h3>当前游戏模式</h3>
        <p>{{ gameMode || '未知' }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useGameStateStore } from '../stores/gameState'
import { Close } from '@element-plus/icons-vue'

const gameStateStore = useGameStateStore()

onMounted(async () => {
  await gameStateStore.fetchGameMode()
})

const gameMode = computed(() => gameStateStore.gameMode)

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