<script setup lang="ts">
import axios from 'axios';
import { onMounted, ref, onUnmounted, watch, computed } from 'vue';
import { useWebSocketStore } from '../../stores/websocket'

// 状态引用
const playerName = ref("");
const playerId = ref("");

// WebSocket Store
const wsStore = useWebSocketStore()

// 使用计算属性获取 LCU 连接状态
const lcuStatus = computed(() => {
  return wsStore.lcuConnected ? "已连接到 LCU" : "未连接到 LCU"
})

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

// 添加获取资源URL方法
const getResourceUrl = (id: number) => {
  const resources = gameResources.value['champion_icons']
  if (resources?.[id]) {
    return `data:image/png;base64,${resources[id]}`
  }
  return '/placeholder.png'
}

// 修改监听方式
watch(
  // 分别监听两个关键属性
  [
    () => wsStore.syncFrontData.current_champion,
    () => wsStore.syncFrontData.bench_champions
  ],
  ([newCurrentChamp, newBenchChamps]) => {
    console.log('英雄数据变化:', {
      current: newCurrentChamp,
      bench: newBenchChamps
    })
    
    const championIds = [
      ...(newCurrentChamp ? [newCurrentChamp] : []),
      ...(newBenchChamps || [])
    ]
    
    if (championIds.length > 0) {
      console.log('加载英雄资源:', championIds)
      loadGameResources(championIds)
    }
  },
  { 
    deep: true,
    immediate: true // 添加immediate确保首次加载时也执行
  }
)

// 添加调试用的监听
watch(
  () => wsStore.syncFrontData,
  (newData) => {
    console.log('syncFrontData变化:', newData)
  },
  { 
    deep: true,
    immediate: true
  }
)

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

// 自动检查玩家信息
const checkPlayerInfo = async () => {
  try {
    const response = await axios.get("/api/hello_world/get_lcu_status");
    playerName.value = response.data.game_name || "";
    playerId.value = response.data.tag_line || "";
  } catch (error) {
    playerName.value = "";
    playerId.value = "";
  }
};

// 连接 LCU
const connectLCU = async () => {
  try {
    const response = await axios.get("/api/hello_world/connect_lcu");
    if (response.data.is_connected) {
      playerName.value = response.data.game_name || "";
      playerId.value = response.data.tag_line || "";
    } else {
      playerName.value = "";
      playerId.value = "";
    }
  } catch (error) {
    playerName.value = "";
    playerId.value = "";
  }
};

// 断开 LCU
const disconnectLCU = async () => {
  try {
    await axios.get("/api/hello_world/disconnect_lcu");
    playerName.value = "";
    playerId.value = "";
  } catch (error) {
    console.error("断开 LCU 连接失败:", error);
  }
};

// 监听 LCU 连接状态变化
watch(() => wsStore.lcuConnected, (newConnected) => {
  if (newConnected) {
    checkPlayerInfo();
  } else {
    playerName.value = "";
    playerId.value = "";
  }
});

onMounted(() => {
  wsStore.connect(); // 连接 WebSocket
});

onUnmounted(() => {
  wsStore.disconnect(); // 断开 WebSocket
});
</script>

<template>
  <div class="dashboard">

    <!-- LCU 连接状态卡片 -->
    <div class="status-card">
      <h2 class="card-title">LCU 连接状态</h2>
      <p :class="['status-message', { 'connected': wsStore.lcuConnected }]">
        {{ lcuStatus }}
      </p>
      
      <div class="button-group">
        <ElButton 
          type="success" 
          size="large" 
          @click="connectLCU"
          :disabled="wsStore.lcuConnected"
        >
          连接 LCU
        </ElButton>
        <ElButton 
          type="danger" 
          size="large" 
          @click="disconnectLCU"
          :disabled="!wsStore.lcuConnected"
        >
          断开 LCU
        </ElButton>
      </div>

      <!-- 玩家信息卡片 -->
      <div v-if="wsStore.lcuConnected && playerName" class="player-card">
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

        <!-- 添加队伍 PUUID 列表显示 -->
        <div class="team-puuid-info">
          <h4>队伍 PUUID 列表</h4>
          
          <!-- 我方队伍 -->
          <div class="team-section">
            <h5>我方队伍</h5>
            <div v-if="wsStore.syncFrontData.my_team_puuid_list?.length" class="puuid-list">
              <div v-for="(puuid, index) in wsStore.syncFrontData.my_team_puuid_list" 
                   :key="index" 
                   class="puuid-item">
                {{ puuid }}
              </div>
            </div>
            <div v-else class="no-data">暂无我方队伍数据</div>
          </div>

          <!-- 敌方队伍 -->
          <div class="team-section">
            <h5>敌方队伍</h5>
            <div v-if="wsStore.syncFrontData.their_team_puuid_list?.length" class="puuid-list">
              <div v-for="(puuid, index) in wsStore.syncFrontData.their_team_puuid_list" 
                   :key="index" 
                   class="puuid-item">
                {{ puuid }}
              </div>
            </div>
            <div v-else class="no-data">暂无敌方队伍数据</div>
          </div>
        </div>

        <!-- 原有的选择英雄状态显示部分 -->
        <div v-if="wsStore.gameState === '选择英雄'" class="champ-select-info">
          <h3>选择英雄阶段</h3>
          <div class="champ-info">
            <!-- 候选席英雄显示 -->
            <div class="bench-champs">
              <h4>候选席英雄</h4>
              <div v-if="Array.isArray(wsStore.syncFrontData.bench_champions) && wsStore.syncFrontData.bench_champions.length > 0" class="bench-list">
                <div v-for="championId in wsStore.syncFrontData.bench_champions" 
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
            
            <!-- 当前英雄显示 -->
            <div class="current-champ">
              <h4>当前英雄</h4>
              <template v-if="wsStore.syncFrontData.current_champion">
                <img 
                  :src="getResourceUrl(wsStore.syncFrontData.current_champion)" 
                  :alt="'Champion ' + wsStore.syncFrontData.current_champion"
                  class="champion-icon"
                />
                <span>ID: {{ wsStore.syncFrontData.current_champion }}</span>
              </template>
              <span v-else class="no-champ-info">未选择英雄</span>
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

.champ-info {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.bench-champs {
  order: 1;  /* 确保候选席英雄在上方 */
}

.current-champ {
  order: 2;  /* 确保当前英雄在下方 */
  margin-bottom: 0;  /* 移除之前的底部边距 */
  padding-top: 1rem; /* 添加上边距 */
  border-top: 1px solid #e9ecef; /* 添加隔线 */
}

.bench-list {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: center;
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: #fff;  /* 添加白色背景 */
  border-radius: 4px;
}

.bench-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  font-size: 0.8rem;
  color: #666;
  padding: 0.5rem;
  background: #f8f9fa;
  border-radius: 4px;
  transition: transform 0.2s;
}

.bench-item:hover {
  transform: translateY(-2px);
}

.no-champ-info {
  text-align: center;
  color: #999;
  font-size: 0.9rem;
}

.team-puuid-info {
  margin-top: 1rem;
  padding: 1rem;
  background: #fff;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.team-section {
  margin-bottom: 1rem;
}

.team-section:last-child {
  margin-bottom: 0;
}

.team-section h5 {
  margin: 0.5rem 0;
  font-size: 0.9rem;
  color: #6c757d;
  border-bottom: 1px solid #e9ecef;
  padding-bottom: 0.3rem;
}

.puuid-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.puuid-item {
  padding: 0.5rem;
  background: #f8f9fa;
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.8rem;
  word-break: break-all;
  color: #495057;
}

.no-data {
  text-align: center;
  color: #999;
  padding: 0.5rem;
  font-size: 0.9rem;
  font-style: italic;
}
</style>