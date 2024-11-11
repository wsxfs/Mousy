<template>
  <el-container style="height: 100vh">

    <!-- 侧边栏 -->
    <Sidebar />

    <!-- 展示路由视图 -->
    <el-main>
      <router-view v-slot="{ Component }">
        <keep-alive>
          <component :is="Component" />
        </keep-alive>
      </router-view>
    </el-main>

  </el-container>
</template>

<script lang="ts" setup>
// import Sidebar from "./components/Sidebar_计时展开.vue";
import Sidebar from "./components/Sidebar_按钮展开.vue";
</script>

<style scoped>

</style>