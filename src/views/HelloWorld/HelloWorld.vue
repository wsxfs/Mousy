<script setup lang="ts">
import axios from 'axios';
import { onMounted, ref, onUnmounted, watch } from 'vue';
import { useWebSocketStore } from '../../stores/websocket'

// 状态引用
const serverMessage = ref("检查服务器状态...");
const wsStatus = ref("检查 LCU 连接状态...");
const playerName = ref("");
const playerId = ref("");
const isConnected = ref(false);

// WebSocket Store
const wsStore = useWebSocketStore()

// 新增的消息输入框状态
const messageToSend = ref("")
const showMessages = ref(true) // 控制消息显示/隐藏

// 添加游戏资源状态
const gameResources = ref<Record<string, Record<string | number, string>>>({})

// 添加加载游戏资源的方法
const loadGameResources = async (championIds: number[]) => {
  try {
    const resourceRequest = {
      champion_icons: championIds
    }
    
    const response = await axios.post(
      '/api/common/game_resource/batch_get_resources',
      resourceRequest
    )
    
    gameResources.value = response.data
  } catch (error) {
    console.error('加载英雄图标失败:', error)
  }
}

// 添加获取资源URL的方法
const getResourceUrl = (id: number) => {
  const resources = gameResources.value['champion_icons']
  if (resources?.[id]) {
    return `data:image/png;base64,${resources[id]}`
  }
  return '/placeholder.png'
}

// 监听英雄信息变化并加载资源
watch(() => wsStore.champSelectInfo, async (newInfo) => {
  const championIds = [
    ...(newInfo.currentChampion ? [newInfo.currentChampion] : []),
    ...newInfo.benchChampions
  ]
  if (championIds.length > 0) {
    await loadGameResources(championIds)
  }
}, { deep: true })

// 发送消息方法
const sendMessage = () => {
  if (messageToSend.value.trim() !== "") {
    wsStore.sendMessage({ message: messageToSend.value })
    messageToSend.value = "" // 清空输入框
  }
}

// 清空消息历史
const clearMessages = () => {
  wsStore.clearMessages()
}

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
  wsStore.connect(); // 连接 WebSocket
});

onUnmounted(() => {
  wsStore.disconnect(); // 断开 WebSocket
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

    <!-- WebSocket 状态卡片 -->
    <div class="status-card">
      <h2 class="card-title">WebSocket 状态</h2>
      <p :class="['status-message', { 'connected': wsStore.isConnected }]">
        {{ wsStore.isConnected ? 'WebSocket 已连接' : 'WebSocket 未连接' }}
      </p>
      
      <div class="button-group">
        <ElButton 
          type="success" 
          size="large" 
          @click="wsStore.connect"
          :disabled="wsStore.isConnected"
        >
          连接 WebSocket
        </ElButton>
        <ElButton 
          type="danger" 
          size="large" 
          @click="wsStore.disconnect"
          :disabled="!wsStore.isConnected"
        >
          断开 WebSocket
        </ElButton>
      </div>

      <!-- 添加游戏状态显示 -->
      <div class="game-state">
        <h3>当前游戏状态</h3>
        <p :class="['status-message', { 'connected': wsStore.isConnected }]">
          {{ wsStore.gameState }}
        </p>
        
        <!-- 添加选择英雄状态的显示 -->
        <div v-if="wsStore.gameState === '选择英雄'" class="champ-select-info">
          <h3>选择英雄阶段</h3>
          <div class="champ-info">
            <!-- 当前英雄显示 -->
            <div class="current-champ">
              <h4>当前英雄</h4>
              <template v-if="wsStore.champSelectInfo.currentChampion">
                <img 
                  :src="getResourceUrl(wsStore.champSelectInfo.currentChampion)" 
                  :alt="'Champion ' + wsStore.champSelectInfo.currentChampion"
                  class="champion-icon"
                />
                <span>ID: {{ wsStore.champSelectInfo.currentChampion }}</span>
              </template>
              <span v-else class="no-champ-info">未选择英雄</span>
            </div>
            
            <!-- 候选席英雄显示 -->
            <div class="bench-champs">
              <h4>候选席英雄</h4>
              <div v-if="wsStore.champSelectInfo.benchChampions.length > 0" class="bench-list">
                <div v-for="championId in wsStore.champSelectInfo.benchChampions" 
                     :key="championId" 
                     class="bench-item">
                  <img 
                    :src="getResourceUrl(championId)" 
                    :alt="'Champion ' + championId"
                    class="champion-icon"
                  />
                  <span>ID: {{ championId }}</span>
                </div>
              </div>
              <span v-else class="no-champ-info">无候选席英雄</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 消息历史记录 -->
      <div class="message-history">
        <div class="message-header">
          <h3>消息历史</h3>
          <div class="message-controls">
            <ElButton type="primary" size="small" @click="showMessages = !showMessages">
              {{ showMessages ? '隐藏消息' : '显示消息' }}
            </ElButton>
            <ElButton type="warning" size="small" @click="clearMessages">
              清空消息
            </ElButton>
          </div>
        </div>
        
        <div v-show="showMessages" class="message-list">
          <div v-if="wsStore.messages.length === 0" class="no-messages">
            暂无消息
          </div>
          <div v-else v-for="(msg, index) in wsStore.messages" :key="index" class="message-item">
            <span class="message-time">{{ msg.timestamp }}</span>
            <span class="message-content">{{ JSON.stringify(msg.content) }}</span>
          </div>
        </div>
      </div>

      <!-- 消息发送功能 -->
      <div class="message-send">
        <input 
          v-model="messageToSend" 
          placeholder="输入消息" 
          @keyup.enter="sendMessage"
        />
        <ElButton type="primary" @click="sendMessage">发送消息</ElButton>
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

.message-history {
  margin-top: 1rem;
  border: 1px solid #eee;
  border-radius: 4px;
  padding: 1rem;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.message-header h3 {
  margin: 0;
  font-size: 1rem;
}

.message-controls {
  display: flex;
  gap: 0.5rem;
}

.message-list {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #eee;
  border-radius: 4px;
  padding: 0.5rem;
}

.message-item {
  padding: 0.5rem;
  border-bottom: 1px solid #f5f5f5;
  font-size: 0.9rem;
}

.message-item:last-child {
  border-bottom: none;
}

.message-time {
  color: #666;
  margin-right: 0.5rem;
  font-size: 0.8rem;
}

.message-content {
  word-break: break-all;
}

.no-messages {
  text-align: center;
  color: #999;
  padding: 1rem;
}

.message-send {
  margin-top: 1rem;
  display: flex;
  gap: 0.5rem;
  justify-content: center;
}

.message-send input {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  outline: none;
}

.message-send input:focus {
  border-color: #409eff;
}

@media (max-width: 640px) {
  .message-header {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .message-controls {
    width: 100%;
    justify-content: center;
  }
}

.game-state {
  margin-top: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.game-state h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
  color: #2c3e50;
}

.champ-select-info {
  margin-top: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.champ-select-info h3, 
.champ-select-info h4 {
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
  color: #2c3e50;
}

.champ-select-info h4 {
  font-size: 0.9rem;
  color: #6c757d;
}

.champion-icon {
  width: 48px;
  height: 48px;
  border-radius: 6px;
  border: 2px solid #e9ecef;
  margin-bottom: 0.3rem;
}

.bench-list {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: center;
  margin-top: 0.5rem;
}

.bench-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  font-size: 0.8rem;
  color: #666;
}

.no-champ-info {
  text-align: center;
  color: #999;
  font-size: 0.9rem;
}

.current-champ {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 1.5rem;
}
</style>