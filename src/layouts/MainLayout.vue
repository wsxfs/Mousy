<template>
  <el-container style="height: 100vh">
    <!-- 传递 activeMenu 给侧边栏 -->
    <Sidebar :active-menu="activeMenu" />

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
import { ref, watch } from 'vue'
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
</script> 