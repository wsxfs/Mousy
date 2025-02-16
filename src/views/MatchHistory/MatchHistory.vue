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
import axios from 'axios'
import dayjs from 'dayjs'

// 基础状态
const activeTab = ref('match-list')
const matchTabs = ref<MatchTab[]>([])

// 处理对局点击
const handleMatchClick = async (gameId: number) => {
  const tabName = `match-${gameId}`
  
  // 如果标签页已存在,直接切换
  if (matchTabs.value.find(tab => tab.name === tabName)) {
    activeTab.value = tabName
    return
  }

  try {
    // 获取对局详情
    const params = new URLSearchParams()
    params.append('game_id', gameId.toString())
    const response = await axios.post(
      '/api/match_history/get_game_detail',
      params,
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }
    )
    
    const game = response.data
    // 构建更友好的标题
    const gameMode = getGameModeName(game.gameMode)
    const time = dayjs(game.gameCreation).format('MM-DD HH:mm')
    const title = `${gameMode} ${time}`
    
    matchTabs.value.push({
      title,
      name: tabName,
      gameId: gameId
    })
  } catch (error) {
    console.error('获取对局详情失败:', error)
    // 获取失败时使用简单标题
    matchTabs.value.push({
      title: `对局 ${gameId}`,
      name: tabName, 
      gameId: gameId
    })
  }
  
  activeTab.value = tabName
}

// 添加游戏模式名称转换函数
const getGameModeName = (mode: string): string => {
  const modes: Record<string, string> = {
    'CLASSIC': '经典模式',
    'ARAM': '大乱斗',
    'URF': '无限火力',
    'ARURF': '随机无限火力',
    'ONEFORALL': '克隆大作战',
    'PRACTICETOOL': '训练模式',
    'NEXUSBLITZ': '闪电战',
    'TFT': '云顶之弈',
    'ULTBOOK': '终极魔典',
    'TUTORIAL': '新手教程'
  }
  return modes[mode] || mode
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
  box-sizing: border-box;
  margin: 0 auto;
  max-width: 900px;
  width: 100%;
  background-color: var(--el-bg-color-overlay);
  border-radius: 8px;
  box-shadow: var(--el-box-shadow-light);
  padding: 20px 20px 0px 20px;
  display: flex;
  flex-direction: column;
}

/* 标签页布局优化 */
:deep(.el-tabs) {
  height: 100%;
  display: flex;
}

:deep(.el-tabs__content) {
  flex: 1;
  overflow: hidden;
  height: 100%;
}

:deep(.el-tab-pane) {
  height: 100%;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .match-history-container {
    padding: 10px;
  }
}

/* 美化滚动条 */
:deep(::-webkit-scrollbar) {
  width: 6px;
}

:deep(::-webkit-scrollbar-thumb) {
  background-color: var(--el-border-color-darker);
  border-radius: 3px;
}

:deep(::-webkit-scrollbar-track) {
  background-color: var(--el-border-color-light);
  border-radius: 3px;
}
</style>