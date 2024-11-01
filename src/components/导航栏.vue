<template>
  <div >
    <el-menu
      default-active="1"
      class="el-menu-vertical-demo"
      :collapse="isCollapse"
      @open="handleOpen"
      @close="handleClose"
      
      @mouseenter="isCollapse = false"
      @mouseleave="isCollapse = true"
    >
      <!-- 用户主页 -->
      <el-menu-item index="1">
        <el-icon>
          <HomeFilled />
        </el-icon>
        <template #title>用户主页</template>
      </el-menu-item>

      <!-- 赛前预设 -->
      <el-menu-item index="2">
        <el-icon>
          <Setting />
        </el-icon>
        <template #title>赛前预设</template>
      </el-menu-item>

      <!-- 战绩查询 -->
      <el-menu-item index="3">
        <el-icon>
          <Document />
        </el-icon>
        <template #title>战绩查询</template>
      </el-menu-item>

      <!-- 对战资料 -->
      <el-menu-item index="4">
        <el-icon>
          <Location />
        </el-icon>
        <template #title>对战资料</template>
      </el-menu-item>
      
    </el-menu>
  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
import {
  Document,
  HomeFilled,
  Location,
  Setting,
} from '@element-plus/icons-vue'

const isCollapse = ref(true)
const handleOpen = (key: string, keyPath: string[]) => {
  console.log('打开菜单项：', key, keyPath)
}
const handleClose = (key: string, keyPath: string[]) => {
  console.log('关闭菜单项：', key, keyPath)
}
</script>

<style>
.el-menu-vertical-demo:not(.el-menu--collapse) {
  width: 200px;
  min-height: 400px;
}

.el-menu-vertical-demo.el-menu--collapse {
  width: 64px; /* 设置折叠时的宽度 */
}
</style>
