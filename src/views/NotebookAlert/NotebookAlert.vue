<template>
  <div class="notebook-alert">
    <div class="title-bar">
      <span class="title">小本本提醒</span>
      <div class="title-actions">
        <el-icon class="close-icon" @click="handleClose">
          <Close />
        </el-icon>
      </div>
    </div>
    
    <div class="content">
      <div v-if="groupedRecords.length > 0" class="records-container">
        <div v-for="record in groupedRecords" :key="`${record.puuid}-${record.type}`" class="record-group">
          <div class="stacked-cards" :style="{ width: cardWidth }">
            <!-- 虚拟卡片背景 -->
            <template v-if="record.records.length > 1">
              <div 
                v-for="index in Math.min(record.records.length - 1, 4)" 
                :key="`bg-${index}`"
                class="virtual-card"
                :style="{
                  transform: `translate(${index * 6}px, ${index * 6}px)`,
                  opacity: 0.4 - (index * 0.08),
                  zIndex: 1 - index,
                  borderColor: record.type === 'blacklist' ? 'var(--el-color-danger-light-5)' : 'var(--el-color-success-light-5)'
                }"
              ></div>
            </template>

            <!-- 主要卡片 -->
            <div 
              class="record-card main-card"
              :data-key="`${record.puuid}-${record.type}`"
              :class="{ 'content-changing': cardStates[`${record.puuid}-${record.type}`]?.isChangingContent }"
            >
              <div class="record-header" :class="record.type">
                <div class="player-info">
                  <div class="player-main">
                    <span class="player-name">{{ record.game_name }}</span>
                    <span class="record-type">{{ record.type === 'blacklist' ? '黑名单' : '白名单' }}</span>
                  </div>
                  <span v-if="record.records.length > 1" class="record-count">
                    {{ (currentIndex[`${record.puuid}-${record.type}`] || 0) + 1 }}/{{ record.records.length }}
                  </span>
                </div>
              </div>
              <div class="record-content">
                <div class="record-details">
                  <div class="reason">
                    <span class="label">原因：</span>
                    <span class="value">{{ getCurrentRecord(record)?.reason || '暂无原因' }}</span>
                  </div>
                  <div class="details">
                    <span class="label">详情：</span>
                    <span class="value">{{ getCurrentRecord(record)?.details || '暂无详情' }}</span>
                  </div>
                  <div class="game-info">
                    <div class="champion-info">
                      <span class="label">使用英雄：</span>
                      <template v-if="getCurrentRecord(record)?.champion_id">
                        <img 
                          :src="getResourceUrl('champion_icons', getCurrentRecord(record)?.champion_id)" 
                          :alt="String(getCurrentRecord(record)?.champion_id)"
                          class="champion-icon"
                        />
                      </template>
                      <span v-else class="no-champion">未记录英雄</span>
                    </div>
                    <el-button
                      v-if="getCurrentRecord(record)?.game_id"
                      type="primary"
                      size="small"
                      plain
                      class="view-game-button"
                      @click="viewGameDetails(getCurrentRecord(record)?.game_id)"
                    >
                      查看对局
                    </el-button>
                  </div>
                </div>
              </div>
            </div>

            <!-- 导航箭头 -->
            <template v-if="record.records.length > 1">
              <div class="card-navigation">
                <el-button 
                  class="nav-button prev-button"
                  :disabled="(currentIndex[`${record.puuid}-${record.type}`] || 0) === 0 || cardStates[`${record.puuid}-${record.type}`]?.isChangingContent"
                  @click="prevCard(record.puuid, record.type)"
                >
                  <el-icon><ArrowLeft /></el-icon>
                </el-button>
                <el-button 
                  class="nav-button next-button"
                  :disabled="(currentIndex[`${record.puuid}-${record.type}`] || 0) === record.records.length - 1 || cardStates[`${record.puuid}-${record.type}`]?.isChangingContent"
                  @click="nextCard(record.puuid, record.type)"
                >
                  <el-icon><ArrowRight /></el-icon>
                </el-button>
              </div>
            </template>
          </div>
        </div>
      </div>
      <el-empty v-else description="暂无记录" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed, onUnmounted } from 'vue'
import { Close, ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
// import { useWebSocketStore } from '../../stores/websocket' // 不再直接使用 store
import axios from 'axios'

// 导入类型定义
interface NotebookRecord {
  summoner_id: string
  game_name: string
  champion_id?: number
  timestamp: number
  reason?: string
  details?: string
  game_id?: string
  region?: string
  puuid?: string
  type: 'blacklist' | 'whitelist'
}

interface NotebookRecords {
  my_team: NotebookRecord[]
  their_team: NotebookRecord[]
}

// const wsStore = useWebSocketStore() // 不再直接使用 store
const records = ref<NotebookRecord[]>([])
const gameResources = ref<Record<string, Record<number, string>>>({})
const expandedGroups = ref<Record<string, boolean>>({})

// 添加当前显示卡片的索引记录
const currentIndex = ref<Record<string, number>>({})

// 修改卡片动画状态记录
const cardStates = ref<Record<string, { isChangingContent: boolean }>>({})

// 添加窗口宽度响应式变量
const windowWidth = ref(window.innerWidth)

// 监听窗口大小变化
const handleResize = () => {
  windowWidth.value = window.innerWidth
}

// 计算卡片宽度
const cardWidth = computed(() => {
  if (windowWidth.value >= 1200) {
    return '800px'
  } else if (windowWidth.value >= 992) {
    return '700px'
  } else if (windowWidth.value >= 768) {
    return '600px'
  } else if (windowWidth.value >= 576) {
    return '500px'
  } else {
    return 'calc(100% - 32px)' // 减去左右padding的总和
  }
})

// 格式化时间
const formatTime = (timestamp: number) => {
  const date = new Date(timestamp * 1000)
  return date.toLocaleString()
}

// 获取资源URL
const getResourceUrl = (type: string, id: number | undefined): string => {
  if (!id) return '/placeholder.png';
  const resources = gameResources.value[type];
  if (resources?.[id]) {
    return `data:image/png;base64,${resources[id]}`;
  }
  return '/placeholder.png';
};

// 加载游戏资源
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
    console.error('加载游戏资源失败:', error)
  }
}

// 更新记录数据
const updateRecords = async (notebookRecords: NotebookRecords | null) => { // 修改类型
  console.log('NotebookAlert 更新小本本记录:', notebookRecords)
  if (notebookRecords) {
    // 合并我方和敌方的记录
    records.value = [
      ...(notebookRecords.my_team || []),
      ...(notebookRecords.their_team || [])
    ]
    console.log('NotebookAlert 合并后的记录:', records.value)

    // 收集所有英雄ID
    const championIds = records.value
      .filter(record => record.champion_id)
      .map(record => record.champion_id as number)

    // 加载英雄图标
    if (championIds.length > 0) {
      await loadGameResources(championIds)
    }
    
    // 初始化 currentIndex 和 cardStates
    groupedRecords.value.forEach(group => {
        const key = `${group.puuid}-${group.type}`
        if (currentIndex.value[key] === undefined) {
            currentIndex.value[key] = 0
        }
        if (cardStates.value[key] === undefined) {
             cardStates.value[key] = { isChangingContent: false }
        }
    })
  }
}

// 关闭窗口
const handleClose = () => {
  window.ipcRenderer.send('close-notebook-alert')
}

const viewGameDetails = (gameId: string | undefined) => {
  if (!gameId) return;
  console.log(`NotebookAlert: Requesting to view game details for gameId: ${gameId}`);
  window.ipcRenderer.send('open-main-window', {
    route: `/match-history?gameId=${gameId}`,
    focusWindow: true
  });
};

// 对记录进行分组并按时间排序
const groupedRecords = computed(() => {
  const result: Array<{
    puuid: string;
    game_name: string;
    type: 'blacklist' | 'whitelist';
    records: NotebookRecord[];
    latestRecord: NotebookRecord;
  }> = [];
  
  // 按 puuid 和 type 分组
  const groups: Record<string, { blacklist: NotebookRecord[], whitelist: NotebookRecord[] }> = {};
  
  records.value.forEach((record: NotebookRecord) => {
    if (!record.puuid) return;
    if (!groups[record.puuid]) {
      groups[record.puuid] = {
        blacklist: [],
        whitelist: []
      };
    }
    if (record.type === 'blacklist') {
      groups[record.puuid].blacklist.push(record);
    } else {
      groups[record.puuid].whitelist.push(record);
    }
  });
  
  // 转换为扁平数组
  Object.entries(groups).forEach(([puuid, group]) => {
    if (group.blacklist.length > 0) {
      result.push({
        puuid,
        game_name: group.blacklist[0].game_name,
        type: 'blacklist',
        records: group.blacklist,
        latestRecord: group.blacklist[0]
      });
    }
    if (group.whitelist.length > 0) {
      result.push({
        puuid,
        game_name: group.whitelist[0].game_name,
        type: 'whitelist',
        records: group.whitelist,
        latestRecord: group.whitelist[0]
      });
    }
  });
  
  return result;
})

// 切换展开/折叠状态
const toggleExpand = (puuid: string) => {
  expandedGroups.value[puuid] = !expandedGroups.value[puuid]
}

// 切换到上一张卡片
const prevCard = (puuid: string, type: 'blacklist' | 'whitelist') => {
  const key = `${puuid}-${type}`;
  const recordGroup = groupedRecords.value.find(g => g.puuid === puuid && g.type === type);
  
  // 如果正在动画或已在第一张，或者找不到记录组，则不执行
  if (cardStates.value[key]?.isChangingContent || (currentIndex.value[key] || 0) === 0 || !recordGroup) {
    return;
  }

  // 设置动画状态，触发离开动画
  cardStates.value[key] = { isChangingContent: true };

  // 动画结束后更新内容和状态
  setTimeout(() => {
    currentIndex.value[key] = (currentIndex.value[key] || 0) - 1; // 更新索引，Vue 会自动更新内容
    cardStates.value[key] = { isChangingContent: false }; // 移除动画类
  }, 300); // 动画时间与 CSS 动画时间一致
};

// 切换到下一张卡片
const nextCard = (puuid: string, type: 'blacklist' | 'whitelist') => {
  const key = `${puuid}-${type}`;
  const recordGroup = groupedRecords.value.find(g => g.puuid === puuid && g.type === type);
  
   // 如果正在动画或已在最后一张，或者找不到记录组，则不执行
  if (cardStates.value[key]?.isChangingContent || !recordGroup || (currentIndex.value[key] || 0) === recordGroup.records.length - 1) {
    return;
  }

   // 设置动画状态，触发离开动画
  cardStates.value[key] = { isChangingContent: true };

  // 动画结束后更新内容和状态
  setTimeout(() => {
    currentIndex.value[key] = (currentIndex.value[key] || 0) + 1; // 更新索引，Vue 会自动更新内容
     cardStates.value[key] = { isChangingContent: false }; // 移除动画类
  }, 300); // 动画时间与 CSS 动画时间一致
};

// 获取当前显示的记录
const getCurrentRecord = (group: any) => {
  const key = `${group.puuid}-${group.type}`;
  const index = currentIndex.value[key] || 0; // 确保有默认值
  return group.records?.[index]; // 添加可选链操作符
};

onMounted(async () => {
  console.log('小本本提醒窗口已挂载')

  // 通知主进程Vue组件已就绪，可以发送数据了
  window.ipcRenderer.send('notebook-alert-vue-ready')

  // 监听主进程发送的初始化数据
  window.ipcRenderer.on('initialize-notebook-alert', (_event: any, initialRecords: NotebookRecords) => {
    console.log('NotebookAlert 收到 initialize-notebook-alert 数据:', initialRecords)
    updateRecords(initialRecords)
  })

  // 可选：如果仍然需要通过 wsStore 监听后续更新 (通常主进程会推送)
  // watch(() => wsStore.syncFrontData.notebook_records, (newRecords) => {
  //   console.log('小本本记录发生变化 (wsStore):', newRecords)
  //   updateRecords(newRecords)
  // })

  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.notebook-alert {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--el-bg-color-page);
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
}

.title-bar {
  -webkit-app-region: drag;
  height: 40px;
  background: linear-gradient(to right, var(--el-color-primary-light-3), var(--el-color-primary-light-5));
  color: var(--el-color-white);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.title {
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.close-icon {
  -webkit-app-region: no-drag;
  cursor: pointer;
  font-size: 18px;
  padding: 6px;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.close-icon:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: rotate(90deg);
}

.content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background: var(--el-bg-color-page);
}

.records-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
}

.record-group {
  width: 100%;
  display: flex;
  justify-content: center;
}

.stacked-cards {
  position: relative;
  margin-bottom: 20px;
  height: 220px;
  padding: 0 40px;
  transition: all 0.3s ease;
  box-sizing: border-box;
  padding-right: calc(40px + 24px); /* 增加右侧padding以容纳更多卡片 */
  background: transparent;
}

.virtual-card {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 100%;
  background: transparent;
  border-radius: 8px;
  border: 2px solid; /* 增加边框宽度 */
  box-shadow: var(--el-box-shadow-light);
  transition: all 0.3s ease;
  pointer-events: none;
  backdrop-filter: blur(1px);
  animation: virtualCardEnter 0.3s ease;
}

.record-card {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 100%;
  background: var(--el-bg-color-overlay);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border: 2px solid; /* 增加边框宽度 */
  transition: all 0.3s ease;
  box-sizing: border-box;
  z-index: 2;
  transform-origin: center;
  animation: cardEnter 0.3s ease;
  will-change: transform, opacity;
}

.record-card.main-card {
  border-color: var(--el-border-color);
}

.record-card.main-card .record-header.blacklist {
  border-color: var(--el-color-danger-light-3);
}

.record-card.main-card .record-header.whitelist {
  border-color: var(--el-color-success-light-3);
}

/* 为主卡片添加类型特定的边框 */
.record-card.main-card[data-key*="-blacklist"] {
  border-color: var(--el-color-danger-light-5);
  box-shadow: 0 4px 12px rgba(255, 77, 79, 0.1);
}

.record-card.main-card[data-key*="-whitelist"] {
  border-color: var(--el-color-success-light-5);
  box-shadow: 0 4px 12px rgba(82, 196, 26, 0.1);
}

.record-header {
  padding: 12px 16px;
  color: white;
  font-weight: 500;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.record-header.blacklist {
  background: linear-gradient(to right, var(--el-color-danger), var(--el-color-danger-light-3));
}

.record-header.whitelist {
  background: linear-gradient(to right, var(--el-color-success), var(--el-color-success-light-3));
}

.player-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.player-main {
  display: flex;
  align-items: center;
  gap: 12px;
}

.player-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--el-color-white);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.record-type {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(4px);
}

.record-count {
  font-size: 12px;
  opacity: 0.9;
  background: rgba(255, 255, 255, 0.2);
  padding: 2px 8px;
  border-radius: 4px;
  backdrop-filter: blur(4px);
  transition: all 0.3s ease;
  animation: countUpdate 0.3s ease;
  display: flex;
  align-items: center;
  gap: 4px;
}

.record-count::before {
  content: '';
  display: inline-block;
  width: 12px;
  height: 12px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'%3E%3Cpath d='M4 6h16v2H4zm0 5h16v2H4zm0 5h16v2H4z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
  opacity: 0.8;
}

.record-content {
  height: calc(100% - 48px);
  overflow-y: auto;
  padding: 16px;
  background: var(--el-bg-color-overlay);
  animation: contentFade 0.3s ease;
}

.record-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.reason, .details, .game-info {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.label {
  color: var(--el-text-color-secondary);
  min-width: 70px;
  font-weight: 500;
  flex-shrink: 0;
}

.value {
  color: var(--el-text-color-primary);
  line-height: 1.5;
  word-break: break-all;
}

/* 黑名单和白名单卡片内容特定样式 */
.record-card[data-key*="-blacklist"] .record-content {
  background: linear-gradient(to bottom, rgba(255, 77, 79, 0.03), transparent);
}

.record-card[data-key*="-whitelist"] .record-content {
  background: linear-gradient(to bottom, rgba(82, 196, 26, 0.03), transparent);
}

.value:empty::before,
.value:not(:empty) {
  content: attr(data-placeholder);
  color: var(--el-text-color-secondary);
  font-style: italic;
}

/* 黑名单和白名单空值样式 */
.record-card[data-key*="-blacklist"] .no-champion,
.record-card[data-key*="-blacklist"] .value:empty::before {
  background: rgba(255, 77, 79, 0.05);
  border-color: var(--el-color-danger-light-8);
}

.record-card[data-key*="-whitelist"] .no-champion,
.record-card[data-key*="-whitelist"] .value:empty::before {
  background: rgba(82, 196, 26, 0.05);
  border-color: var(--el-color-success-light-8);
}

.no-champion {
  color: var(--el-text-color-secondary);
  font-style: italic;
  font-size: 14px;
  padding: 4px 8px;
  background: var(--el-fill-color-light);
  border-radius: 4px;
  border: 1px dashed var(--el-border-color);
}

.champion-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.champion-icon {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  border: 1px solid var(--el-border-color-lighter);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.view-game-button {
  margin-left: auto;
  transition: all 0.3s ease;
}

.view-game-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.card-navigation {
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  transform: translateY(-50%);
  display: flex;
  justify-content: space-between;
  z-index: 3;
  pointer-events: none;
}

.nav-button {
  pointer-events: auto;
  width: 36px; /* 增加按钮大小 */
  height: 36px;
  border-radius: 50%;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--el-bg-color-overlay);
  border: 2px solid var(--el-border-color);
  box-shadow: var(--el-box-shadow-light);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 3;
}

/* 为黑名单和白名单卡片添加特定的导航按钮样式 */
.record-card[data-key*="-blacklist"] ~ .card-navigation .nav-button:hover:not(:disabled) {
  background: var(--el-color-danger-light-9);
  border-color: var(--el-color-danger-light-5);
}

.record-card[data-key*="-whitelist"] ~ .card-navigation .nav-button:hover:not(:disabled) {
  background: var(--el-color-success-light-9);
  border-color: var(--el-color-success-light-5);
}

.nav-button:hover:not(:disabled) {
  background: var(--el-color-primary-light-9);
  border-color: var(--el-color-primary);
  transform: translateY(-50%) scale(1.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.nav-button:active:not(:disabled) {
  transform: translateY(-50%) scale(0.95);
}

.nav-button .el-icon {
  font-size: 18px; /* 增加图标大小 */
}

.nav-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.nav-button.prev-button {
  left: 0;
}

.nav-button.next-button {
  right: 0;
}

/* 自定义滚动条样式 */
.record-content::-webkit-scrollbar {
  width: 6px;
}

.record-content::-webkit-scrollbar-track {
  background: transparent;
}

.record-content::-webkit-scrollbar-thumb {
  background: var(--el-border-color);
  border-radius: 3px;
}

.record-content::-webkit-scrollbar-thumb:hover {
  background: var(--el-text-color-placeholder);
}

/* 响应式调整 */
@media screen and (max-width: 576px) {
  .content {
    padding: 12px;
  }

  .stacked-cards {
    padding: 0 32px;
    padding-right: calc(32px + 12px);
    height: 200px;
  }

  .nav-button {
    width: 28px;
    height: 28px;
  }

  .record-content {
    padding: 12px;
  }

  .player-name {
    font-size: 14px;
  }

  .record-type {
    font-size: 11px;
    padding: 1px 6px;
  }
}

/* 主要卡片动画样式 */
.record-card.main-card {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 100%;
  background: var(--el-bg-color-overlay);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border: 2px solid; /* 增加边框宽度 */
  transition: all 0.3s ease-in-out; /* 使用 ease-in-out 动画 */
  box-sizing: border-box;
  z-index: 2;
  transform-origin: center;
  /* 默认状态 */
   opacity: 1;
   transform: translateY(0);
   transition: opacity 0.3s ease-in-out, transform 0.3s ease-in-out; /* 明确过渡属性 */
}

/* 内容切换动画 */
.record-card.main-card.content-changing {
  opacity: 0;
  transform: translateY(10px); /* 或其他你喜欢的动画效果 */
}

/* 虚拟卡片动画 */
@keyframes virtualCardEnter {
  from {
    opacity: 0;
    transform: translate(0, 0);
  }
  to {
    opacity: 0.4;
    transform: translate(var(--translate-x), var(--translate-y));
  }
}

/* 内容切换动画 */
.record-content {
  height: calc(100% - 48px);
  overflow-y: auto;
  padding: 16px;
  background: var(--el-bg-color-overlay);
  animation: contentFade 0.3s ease;
}

@keyframes contentFade {
  from {
    opacity: 0;
    transform: translateY(5px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 记录计数动画 */
@keyframes countUpdate {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 0.9;
    transform: scale(1);
  }
}
</style> 