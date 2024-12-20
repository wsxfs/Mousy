<template>
  <router-view></router-view>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

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
</script>