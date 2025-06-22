<template>
  <div class="other-tools">
    <el-menu mode="horizontal" router :default-active="$route.path" class="el-menu-demo">
      <el-menu-item index="/other_tools/claim_rewards">领取奖励</el-menu-item>
    </el-menu>
    <div class="divider"></div>
    <div class="content-area">
      <router-view />
    </div>
  </div>
</template>

<script setup lang="ts">
// 这里暂时不需要脚本
</script>

<style scoped>
.other-tools {
  margin-top: -20px; /* 抵消 el-main 的 padding-top */
  padding: 0;
  height: 100%;
  box-sizing: border-box;
}
.el-menu-demo {
  position: sticky;
  top: -20px;
  z-index: 100;
  width: 100%;
  margin-bottom: 0;
  border-radius: 0;
  height: 40px;
  min-height: 40px;
  line-height: 40px;
  background: #fff;
}
:deep(.el-menu--horizontal) {
  height: 40px !important;
  min-height: 40px !important;
}
:deep(.el-menu--horizontal > .el-menu-item) {
  height: 40px !important;
  line-height: 40px !important;
  font-size: 15px;
  padding: 0 18px;
}
.content-area {
  padding-top: 0;
  padding: 24px;
}
.divider {
  display: none;
}
</style> 