<script setup lang="ts">
console.log("Hello, world!");

import { ref, onMounted } from "vue";
import axios from "axios"; // 引入 axios

const serverMessage = ref("Checking server status...");
console.log("Checking server status...");
const checkServerStatus = async () => {
  console.log("Checking server status...");
  try {
    // 使用 axios 发送 HTTP GET 请求
    serverMessage.value = "Checking server status...";
    const response = await axios.get("/api/hello");
    serverMessage.value = response.data.message;
  } catch (error) {
    serverMessage.value = "Server is not running or cannot be reached";
    console.error("Error fetching server status:", error);
  }
};

onMounted(() => {
  checkServerStatus();
});
</script>

<template>
  <div>
    <!-- 服务器状态展示 -->
    <h1>{{ serverMessage }}</h1>

    <!-- 原有内容 -->
    <a href="https://electron-vite.github.io" target="_blank">
      <img src="/electron-vite.svg" class="logo" alt="Vite logo" />
    </a>
    <a href="https://vuejs.org/" target="_blank">
      <img src="./assets/vue.svg" class="logo vue" alt="Vue logo" />
    </a>
    <div>Vite + Vue</div>
    <button @click="checkServerStatus">Check Server Status</button>
  </div>
</template>

<style scoped>
.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}
.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}
</style>
