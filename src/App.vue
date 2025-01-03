<template>
  <router-view></router-view>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useWebSocketStore } from './stores/websocket'

const router = useRouter()
const wsStore = useWebSocketStore()

onMounted(() => {
  // 使用 window.electron.ipcRenderer.on 监听导航请求
  const handleNavigate = (route: string) => {
    router.push(route)
  }
  
  window.electron.ipcRenderer.on('navigate-to', handleNavigate)
  
  // 清理监听器
  onUnmounted(() => {
    window.electron.ipcRenderer.off('navigate-to', handleNavigate)
  })
})

// 监听主进程请求当前状态
window.electron.ipcRenderer.on('get-current-state', () => {
  // 获取并发送当前状态
  const currentState = wsStore.getCurrentState()
  window.electron.ipcRenderer.send('current-state-response', currentState)
})
</script>