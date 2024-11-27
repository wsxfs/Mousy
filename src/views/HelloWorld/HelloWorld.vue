<script setup lang="ts">
import axios from 'axios';
import { onMounted, ref } from 'vue';

// 状态引用
const serverMessage = ref("检查服务器状态...");
const wsStatus = ref("检查 LCU 连接状态...");
const playerName = ref("");
const playerId = ref("");
const isConnected = ref(false);

// 检查服务器状态
const checkServerStatus = async () => {
  try {
    serverMessage.value = "正在检查服务器状态...";
    const response = await axios.get("/api/hello_world/get_fastapi_status");
    serverMessage.value = response.data.message;
  } catch (error) {
    serverMessage.value = "服务器未运行或无法访问";
  }
};

// 检查 LCU Websocket 连接状态
const checkLCUConnection = async () => {
  try {
    wsStatus.value = "正在检查 LCU 连接...";
    const response = await axios.get("/api/hello_world/get_lcu_status");
    
    if (response.data.is_connected) {
      isConnected.value = true;
      wsStatus.value = "已连接到 LCU";
      playerName.value = response.data.game_name || "";
      playerId.value = response.data.tag_line || "";
    } else {
      isConnected.value = false;
      wsStatus.value = "未连接到 LCU";
      playerName.value = "";
      playerId.value = "";
    }
  } catch (error) {
    wsStatus.value = "检查 LCU 连接失败";
    isConnected.value = false;
    playerName.value = "";
    playerId.value = "";
  }
};

// 连接 LCU
const connectLCU = async () => {
  try {
    wsStatus.value = "正在连接 LCU...";
    const response = await axios.get("/api/hello_world/connect_lcu");
    
    if (response.data.is_connected) {
      isConnected.value = true;
      wsStatus.value = "已连接到 LCU";
      playerName.value = response.data.game_name || "";
      playerId.value = response.data.tag_line || "";
    } else {
      isConnected.value = false;
      wsStatus.value = "连接 LCU 失败";
      playerName.value = "";
      playerId.value = "";
    }
  } catch (error) {
    wsStatus.value = "连接 LCU 失败";
    isConnected.value = false;
    playerName.value = "";
    playerId.value = "";
  }
};

// 断开 LCU
const disconnectLCU = async () => {
  try {
    wsStatus.value = "正在断开 LCU...";
    const response = await axios.get("/api/hello_world/disconnect_lcu");
    
    if (response.data.is_connected) {
      isConnected.value = true;
      wsStatus.value = "已连接到 LCU";
      playerName.value = response.data.game_name || "";
      playerId.value = response.data.tag_line || "";
    } else {
      isConnected.value = false;
      wsStatus.value = "已断开 LCU 连接";
      playerName.value = "";
      playerId.value = "";
    }
  } catch (error) {
    wsStatus.value = "断开 LCU 连接失败";
    isConnected.value = false;
    playerName.value = "";
    playerId.value = "";
  }
};

onMounted(() => {
  checkServerStatus();
  checkLCUConnection();
});
</script>

<template>
  <div class="dashboard">
    <!-- 服务器状态卡片 -->
    <div class="status-card">
      <h2 class="card-title">服务器状态</h2>
      <p :class="['status-message', { 'error': serverMessage.includes('未运行') }]">
        {{ serverMessage }}
      </p>
      <ElButton type="primary" size="large" @click="checkServerStatus">
        检查服务器状态
      </ElButton>
    </div>

    <!-- LCU 连接状态卡片 -->
    <div class="status-card">
      <h2 class="card-title">LCU 连接状态</h2>
      <p :class="['status-message', { 'connected': isConnected }]">
        {{ wsStatus }}
      </p>
      
      <div class="button-group">
        <ElButton type="primary" size="large" @click="checkLCUConnection">
          检查 LCU 连接
        </ElButton>
        <ElButton 
          type="success" 
          size="large" 
          @click="connectLCU"
          :disabled="isConnected"
        >
          连接 LCU
        </ElButton>
        <ElButton 
          type="danger" 
          size="large" 
          @click="disconnectLCU"
          :disabled="!isConnected"
        >
          断开 LCU
        </ElButton>
      </div>

      <!-- 玩家信息卡片 -->
      <div v-if="isConnected && playerName" class="player-card">
        <p class="player-name">{{ playerName }}</p>
        <p v-if="playerId" class="player-tag">#{{ playerId }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  max-width: 800px;
  margin: 1rem auto;
  padding: 0 1rem;
  display: grid;
  gap: 1rem;
}

.status-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  text-align: center;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #2c3e50;
}

.status-message {
  font-size: 1rem;
  margin: 1rem 0;
  padding: 0.4rem;
  border-radius: 4px;
  background: #f8f9fa;
}

.error {
  color: #dc3545;
  background: #fff5f5;
}

.connected {
  color: #28a745;
  background: #f0fff4;
}

.button-group {
  display: flex;
  gap: 0.75rem;
  justify-content: center;
  margin: 1rem 0;
  flex-wrap: wrap;
}

.player-card {
  margin-top: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.player-name {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 0.3rem;
  color: #2c3e50;
}

.player-tag {
  color: #6c757d;
  font-size: 1rem;
}

@media (max-width: 640px) {
  .button-group {
    flex-direction: column;
  }
  
  .status-card {
    padding: 1rem;
  }
}
</style>