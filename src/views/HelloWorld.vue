<script setup lang="ts">
import axios from 'axios';
import { onMounted, ref } from 'vue';

const serverMessage = ref("Checking server status...");
const checkServerStatus = async () => {
  try {
    serverMessage.value = "Checking server status...";
    const response = await axios.get("/api/hello");
    serverMessage.value = response.data.message;
  } catch (error) {
    serverMessage.value = "Server is not running or cannot be reached";
  }
};

onMounted(() => {
  checkServerStatus();
});
</script>

<template>
  <h1 class="server-status">{{ serverMessage }}</h1>
  <ElButton type="primary" size="large" @click="checkServerStatus">Check Server Status</ElButton>
</template>

<style scoped></style>
