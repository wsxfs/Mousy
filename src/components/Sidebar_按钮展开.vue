<template>
  <div class="sidebar-container" :class="{ 'expanded': !isCollapse }">
    <div class="collapse-control" @click="toggleCollapse">
      <div class="control-content">
        <el-icon class="toggle-icon" :class="{ 'is-active': !isCollapse }">
          <Menu v-if="isCollapse" />
          <Close v-else />
        </el-icon>
        <span class="control-text">收起菜单</span>
      </div>
    </div>

    <el-menu
      default-active="/hello"
      class="el-menu-vertical"
      :collapse="isCollapse"
      @open="handleOpen"
      @close="handleClose"
      router
    >
      <el-menu-item index="/hello">
        <el-icon><Opportunity /></el-icon>
        <span>Hello World</span>
      </el-menu-item>
      
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
    </el-menu>
  </div>
</template>

<script lang="ts" setup>
import { HomeFilled, Location, Search, Document, Opportunity, Menu, Close } from "@element-plus/icons-vue";
import { ref } from "vue";

const isCollapse = ref(true);

const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value;
};

const handleOpen = (key: string, keyPath: string[]) => {
  console.log(`Opened: ${key}`, keyPath);
};
const handleClose = (key: string, keyPath: string[]) => {
  console.log(`Closed: ${key}`, keyPath);
};
</script>

<style scoped>
.sidebar-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--el-border-color-light);
  position: relative;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  width: 64px;
  background: white;
}

.sidebar-container.expanded {
  width: 200px;
}

.collapse-control {
  height: 56px;
  display: flex;
  align-items: center;
  padding: 0;
  cursor: pointer;
  border-bottom: 1px solid var(--el-border-color-light);
  background-color: white;
  position: relative;
}

.control-content {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 0 16px;
  position: relative;
}

.toggle-icon {
  font-size: 20px;
  color: var(--el-text-color-secondary);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  position: absolute;
  left: 18px;
}

.toggle-icon.is-active {
  transform: rotate(180deg);
}

.collapse-control:hover .toggle-icon {
  color: var(--el-color-primary);
  background-color: var(--el-color-primary-light-9);
}

.control-text {
  font-size: 14px;
  color: var(--el-text-color-regular);
  opacity: 0;
  transform: translateX(-10px);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  white-space: nowrap;
  margin-left: 40px;
}

.expanded .control-text {
  opacity: 1;
  transform: translateX(0);
}

.el-menu-vertical {
  border-right: none;
}

:deep(.el-menu-item) {
  display: flex;
  align-items: center;
  padding: 0 !important;
  height: 44px;
  margin: 4px 8px;
  border-radius: 6px;
  position: relative;
}

:deep(.el-menu-item .el-icon) {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  flex-shrink: 0;
  position: absolute;
  left: 11px;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

:deep(.el-menu-item:hover) {
  color: var(--el-color-primary);
  background-color: var(--el-color-primary-light-9);
}

:deep(.el-menu-item:hover .el-icon) {
  color: var(--el-color-primary);
  transform: translateX(2px) scale(1.1);
}

:deep(.el-menu-item.is-active) {
  background-color: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
  border-left: 3px solid var(--el-color-primary);
}

:deep(.el-menu-item.is-active .el-icon) {
  color: var(--el-color-primary);
  transform: scale(1.1);
}

:deep(.el-menu--collapse .el-menu-item) {
  padding: 0 !important;
  justify-content: center;
}

:deep(.el-menu--collapse .el-menu-item .el-icon) {
  position: absolute;
  left: 11px;
  transform: none;
  margin: 0;
}

:deep(.el-menu-item span) {
  padding-left: 40px;
  display: inline-block;
  opacity: 0;
  transform: translateX(-10px);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  white-space: nowrap;
}

.expanded :deep(.el-menu-item span) {
  opacity: 1;
  transform: translateX(0);
}
</style>
