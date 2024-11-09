<template>
  <el-container style="height: 100vh">

    <!-- 侧边栏 -->
    <Sidebar />

    <!-- 展示路由视图 -->
    <el-main>
      <router-view />
    </el-main>

  </el-container>
</template>

<script lang="ts" setup>
import Sidebar from "./components/Sidebar.vue";
</script>

<style scoped>

</style>