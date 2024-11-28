<template>
  <div class="match-history-container">
    <el-tabs v-model="activeTab" type="card" @tab-remove="removeTab">
      <!-- 我的主页标签页 -->
      <el-tab-pane name="match-list" :closable="false">
        <template #label>
          <el-icon><List /></el-icon>
        </template>
        <player-match-history
          :puuid="''"
          player-name="我"
          @match-click="handleMatchClick"
        />
      </el-tab-pane>

      <!-- 动态其它标签页 -->
      <el-tab-pane
        v-for="item in matchTabs"
        :key="item.name"
        :label="item.title"
        :name="item.name"
        :closable="true"
      >
        <template v-if="item.gameId">
          <match-detail 
            :game-id="item.gameId"
            @back="handleBack"
            @player-click="handlePlayerClick"
          />
        </template>
        <template v-else-if="item.puuid">
          <player-match-history
            :puuid="item.puuid"
            :player-name="item.title"
            @match-click="handleMatchClick"
            @back="handleBack"
          />
        </template>
      </el-tab-pane>

      <!-- 清除所有标签页的标签 -->
      <el-tab-pane 
        v-if="matchTabs.length > 0" 
        name="clear-all" 
        :closable="false"
      >
        <template #label>
          <el-button 
            type="danger" 
            link
            @click.stop="clearAllTabs"
          >
            清除全部
          </el-button>
        </template>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { List } from '@element-plus/icons-vue'
import MatchDetail from './MatchDetail.vue'
import PlayerMatchHistory from './PlayerMatchHistory.vue'
import type { MatchTab } from './match'

// 基础状态
const activeTab = ref('match-list')
const matchTabs = ref<MatchTab[]>([])

// 处理对局点击
const handleMatchClick = (gameId: number) => {
  const tabName = `match-${gameId}`
  
  if (!matchTabs.value.find(tab => tab.name === tabName)) {
    matchTabs.value.push({
      title: `对局 ${gameId}`,
      name: tabName,
      gameId: gameId
    })
  }
  
  activeTab.value = tabName
}

// 移除标签页
const removeTab = (tabName: string) => {
  const tabs = matchTabs.value
  let activeName = activeTab.value
  
  if (activeName === tabName) {
    tabs.forEach((tab, index) => {
      if (tab.name === tabName) {
        const nextTab = tabs[index + 1] || tabs[index - 1]
        if (nextTab) {
          activeName = nextTab.name
        } else {
          activeName = 'match-list'
        }
      }
    })
  }
  
  activeTab.value = activeName
  matchTabs.value = tabs.filter(tab => tab.name !== tabName)
}

// 返回列表
const handleBack = () => {
  activeTab.value = 'match-list'
}

// 处理玩家点击
const handlePlayerClick = (puuid: string, playerName: string) => {
  const tabName = `player-${puuid}`
  
  // 如果标签页已存在，直接切换
  if (matchTabs.value.find(tab => tab.name === tabName)) {
    activeTab.value = tabName
    return
  }
  
  // 添加新标签页
  matchTabs.value.push({
    title: playerName,
    name: tabName,
    puuid
  })
  activeTab.value = tabName
}

// 清除所有标签页
const clearAllTabs = () => {
  matchTabs.value = []
  activeTab.value = 'match-list'
}
</script>

<style scoped>
.match-history-container {
  width: 100%;
  min-height: 100vh;
  background-color: var(--el-bg-color-page);
}

.tabs-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-right: 16px;
}

/* 确保 tabs 组件占据主要空间 */
.tabs-header :deep(.el-tabs) {
  flex: 1;
}
</style>