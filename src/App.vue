<template>
  <el-container style="height: 100vh">

    <!-- 侧边栏 -->
    <div class="sidebar-container">
      <Sidebar />
    </div>

    <!-- 展示路由视图 -->
    <el-container>
      <router-view />
    </el-container>

  </el-container>
</template>

<script lang="ts" setup>
import Sidebar from "./components/Sidebar.vue";
</script>

<style scoped>
.sidebar-container {
  width: 170px; /* 固定宽度 */
}
</style>