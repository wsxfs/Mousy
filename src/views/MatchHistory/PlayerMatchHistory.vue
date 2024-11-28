<template>
    <div class="player-match-history">
      <div class="header">
        <h3>{{ playerName }}的对局历史</h3>
      </div>
      
      <match-history-list
        :matches="matches"
        :loading="loading"
        @match-click="handleMatchClick"
      />
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, onMounted } from 'vue'
  import axios from 'axios'
  import { ElMessage } from 'element-plus'
  import MatchHistoryList from './MatchHistoryList.vue'
  import type { Game } from './match'
  
  const props = defineProps<{
    puuid: string
    playerName: string
  }>()
  
  const emit = defineEmits<{
    (e: 'match-click', gameId: number): void
  }>()
  
  const matches = ref<Game[]>([])
  const loading = ref(false)
  
  const fetchPlayerMatchHistory = async () => {
    try {
      loading.value = true
      const params = new URLSearchParams()
      params.append('puuid', props.puuid)
      params.append('beg_index', '0')
      params.append('end_index', '19')
  
      const response = await axios.post(
        '/api/match_history/get_match_history',
        params,
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        }
      )
      
      if (response.data?.games?.games) {
        matches.value = response.data.games.games
      }
    } catch (error) {
      ElMessage.error('获取对局历史失败')
      console.error('获取对局历史失败:', error)
    } finally {
      loading.value = false
    }
  }
  
  const handleMatchClick = (gameId: number) => {
    emit('match-click', gameId)
  }
  
  onMounted(() => {
    fetchPlayerMatchHistory()
  })
  </script>
  
  <style scoped>
  .player-match-history {
    padding: 20px;
  }
  
  .header {
    margin-bottom: 20px;
  }
  
  .header h3 {
    margin: 0;
    color: var(--el-text-color-primary);
  }
  </style>