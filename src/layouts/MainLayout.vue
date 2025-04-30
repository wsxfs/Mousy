<template>
  <el-container style="height: 100vh">
    <!-- 传递 activeMenu 给侧边栏 -->
    <el-aside width="auto" class="sidebar-wrapper">
      <Sidebar :active-menu="activeMenu" />
    </el-aside>

    <el-main>
      <router-view v-slot="{ Component }">
        <keep-alive>
          <component :is="Component" />
        </keep-alive>
      </router-view>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import Sidebar from '../components/Sidebar_按钮展开.vue'
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const activeMenu = ref('')

// 监听路由变化，更新侧边栏选中状态
watch(
  () => route.path,
  (newPath) => {
    // 根据路径设置当前选中的菜单项
    activeMenu.value = newPath
  },
  { immediate: true } // 确保组件加载时也执行一次
)

// 添加对route-changed事件的监听
onMounted(() => {
  const mainLayout = document.querySelector('.el-container')
  if (mainLayout) {
    mainLayout.addEventListener('route-changed', handleRouteChanged as EventListener)
  }
})

onUnmounted(() => {
  const mainLayout = document.querySelector('.el-container')
  if (mainLayout) {
    mainLayout.removeEventListener('route-changed', handleRouteChanged as EventListener)
  }
})

// 处理路由变化事件
const handleRouteChanged = (event: Event) => {
  const customEvent = event as CustomEvent<{ path: string }>
  activeMenu.value = customEvent.detail.path
}
</script>

<style scoped>
.sidebar-wrapper {
  flex-shrink: 0;
  height: 100vh;
  overflow: hidden;
}
</style> 