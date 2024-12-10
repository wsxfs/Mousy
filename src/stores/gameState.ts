import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useGameStateStore = defineStore('gameState', () => {
  const gameMode = ref<string | null>(null)

  const fetchGameMode = async () => {
    try {
      const response = await axios.get('/api/hello_world/get_game_mode')
      gameMode.value = response.data.game_mode
    } catch (error) {
      console.error('获取游戏模式失败:', error)
      gameMode.value = null
    }
  }

  return {
    gameMode,
    fetchGameMode
  }
})