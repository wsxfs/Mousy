<template>
  <el-container style="height: 100vh;">

    <div class="sidebar-container">
    <!-- 侧边栏 -->
    <Sidebar />
    </div>

    

    <!-- 主内容区 -->
    <el-container>
      <el-header>
        <h2>LOL助手</h2>
      </el-header>
      <el-main>
        <!-- 路由视图区域，将根据路由展示页面内容 -->
        <HelloWorld></HelloWorld>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script lang="ts" setup>
import Sidebar from './components/Sidebar.vue'
import HelloWorld from './components/HelloWorld.vue';
</script>

<style scoped>
h2 {
  margin: 0;
  padding: 16px;
  color: #333;
}
el-aside{
  height: 100%;
}
.sidebar-container {
  position: relative; /* 使其作为侧边栏的定位参考 */
  width: 70px; /* 固定的宽度，可以根据需要调整 */
  overflow: visible; /* 允许侧边栏在展开时超出容器 */
  height: 100vh;
}
</style>