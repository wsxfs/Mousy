<template>
  <div class="other-tools">
    <h1>其它功能</h1>
    <nav>
      <router-link to="/other_tools/claim_rewards">领取奖励</router-link>
      <!-- 未来可扩展其它子页面入口 -->
    </nav>
    <router-view />
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.other-tools {
  padding: 24px;
}
nav {
  margin-bottom: 16px;
}
nav a {
  margin-right: 16px;
  text-decoration: none;
  color: #409eff;
}
nav a.router-link-exact-active {
  font-weight: bold;
  color: #1a73e8;
}
</style> 