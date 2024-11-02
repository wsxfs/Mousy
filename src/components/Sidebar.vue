<template>
  <el-menu
    default-active="/home"
    class="el-menu-vertical-demo"
    :collapse="isCollapse"
    @open="handleOpen"
    @close="handleClose"
    @mouseenter="isCollapse = false"
    @mouseleave="isCollapse = true"
    router
  >

    <el-menu-item index="/home">
      <el-icon><HomeFilled /></el-icon>
      <span>用户主页</span>
    </el-menu-item>

    <el-menu-item index="/pregame">
      <el-icon><Location /></el-icon>
      <span>赛前预设</span>
    </el-menu-item>

    <el-menu-item index="/match-history">
      <el-icon><Search /></el-icon>
      <span>战绩查询</span>
    </el-menu-item>

    <el-menu-item index="/match-data">
      <el-icon><Document /></el-icon>
      <span>对战资料</span>
    </el-menu-item>

    <el-menu-item index="/hello">
      <el-icon><Opportunity /></el-icon>
      <span>Hello World</span>
    </el-menu-item>

  </el-menu>
</template>

<script lang="ts" setup>
import { HomeFilled, Location, Search, Document, Opportunity } from "@element-plus/icons-vue";
import { ref } from "vue";

const isCollapse = ref(true);

const handleOpen = (key: string, keyPath: string[]) => {
  console.log(`Opened: ${key}`, keyPath);
};
const handleClose = (key: string, keyPath: string[]) => {
  console.log(`Closed: ${key}`, keyPath);
};
</script>

<style scoped>
.el-menu-vertical-demo {
  position: absolute; /* 绝对定位使其能够超出容器 */
  height: 100%;
}
</style>
