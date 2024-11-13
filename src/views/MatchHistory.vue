<template>
  <match-history-list
    :matches="matches"
    :loading="loading"
  />
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import MatchHistoryList from '../components/MatchHistoryList.vue'

// 添加 Game 接口定义
interface Game {
  id?: number;
  gameCreation: number;
  gameDuration: number;
  gameMode: string;
  participants: any[];
  participantIdentities: any[];
  teams: any[];
}

// 基础状态
const matches = ref<Game[]>([])
const loading = ref(false)

// 获取对局历史
const fetchMatchHistory = async () => {
  try {
    loading.value = true
    const params = new URLSearchParams()
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

onMounted(() => {
  fetchMatchHistory()
})
</script>