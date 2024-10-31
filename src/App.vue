<script setup lang="ts">
import { ref, onMounted } from "vue";

const serverMessage = ref("Checking server status...");

const checkServerStatus = async () => {
  try {
    const response = await fetch("http://127.0.0.1:8000/api/hello");
    if (!response.ok) {
      throw new Error("Network response was not ok");
    }
    const data = await response.json();
    serverMessage.value = data.message;
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
