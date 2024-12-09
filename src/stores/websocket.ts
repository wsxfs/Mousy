import { defineStore } from 'pinia'
import { ref } from 'vue'

// 定义类型
interface ChampSelectInfo {
  currentChampion: number | null;
  benchChampions: number[];
}

export const useWebSocketStore = defineStore('websocket', () => {
  // 状态
  const ws = ref<WebSocket | null>(null)
  const isConnected = ref(false)
  const reconnectAttempts = ref(0)
  const maxReconnectAttempts = 5
  const messages = ref<any[]>([])
  const disconnectReason = ref<string>('')
  const gameState = ref<string>('未知')
  const champSelectInfo = ref<ChampSelectInfo>({
    currentChampion: null,
    benchChampions: []
  })
  
  // 连接方法
  const connect = () => {
    if (ws.value?.readyState === WebSocket.OPEN) return

    ws.value = new WebSocket('ws://127.0.0.1:8000/api/websocket/test')

    ws.value.onopen = () => {
      console.log('WebSocket 连接已建立')
      isConnected.value = true
      reconnectAttempts.value = 0
    }

    ws.value.onclose = () => {
      console.log('WebSocket 连接已关闭')
      isConnected.value = false
      
      if (reconnectAttempts.value < maxReconnectAttempts) {
        reconnectAttempts.value++
        setTimeout(() => {
          console.log(`尝试重连 (${reconnectAttempts.value}/${maxReconnectAttempts})`)
          connect()
        }, 3000)
      }
    }

    ws.value.onerror = (error) => {
      console.error('WebSocket 错误:', error)
    }

    ws.value.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'disconnect') {
          disconnectReason.value = data.reason
          console.log('WebSocket断开原因:', data.reason)
        }
        handleWebSocketMessage(data)
      } catch (error) {
        console.error('解析 WebSocket 消息失败:', error)
      }
    }
  }

  // 断开连接
  const disconnect = () => {
    if (ws.value) {
      ws.value.close()
      ws.value = null
      isConnected.value = false
      reconnectAttempts.value = 0
    }
  }

  // 处理接收到的消息
  const handleWebSocketMessage = (data: any) => {
    // 处理游戏状态消息
    if (data.type === 'message' && typeof data.content === 'string' && data.content.startsWith('gameflow_phase:')) {
      const phase = data.content.split(':')[1]
      switch (phase) {
        case 'none':
          gameState.value = '大厅'
          break
        case 'lobby':
          gameState.value = '组队中'
          break
        case 'match_making':
          gameState.value = '匹配中'
          break
        case 'ready_check':
          gameState.value = '确认对局'
          break
        default:
          gameState.value = phase
      }
    }
    
    // 处理选人阶段信息
    if (data.type === 'message' && typeof data.content === 'string' && data.content.startsWith('champ_select_changed:')) {
      const content = data.content.replace('champ_select_changed:', '')
      const parts = content.split(',')
      
      const currentChamp = parts[0].split('=')[1]
      const benchChamps = parts[1].split('=')[1].replace(/[\[\]]/g, '').split(' ')
      
      champSelectInfo.value = {
        currentChampion: currentChamp === 'None' ? null : parseInt(currentChamp),
        benchChampions: benchChamps
          .filter((id: string) => id !== '')
          .map((id: string) => parseInt(id))
          .filter((id: number) => !isNaN(id))
      }
    }
    
    messages.value.push({
      content: data,
      timestamp: new Date().toLocaleTimeString()
    })
    if (messages.value.length > 100) {
      messages.value.shift()
    }
  }

  // 发送消息
  const sendMessage = (message: any) => {
    if (ws.value?.readyState === WebSocket.OPEN) {
      ws.value.send(JSON.stringify(message))
    } else {
      console.error('WebSocket 未连接')
    }
  }

  // 清空消息历史
  const clearMessages = () => {
    messages.value = []
  }

  return {
    isConnected,
    messages,
    disconnectReason,
    connect,
    disconnect,
    sendMessage,
    clearMessages,
    gameState,
    champSelectInfo,
  }
})
