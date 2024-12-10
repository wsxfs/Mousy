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
    // 处理事件消息
    if (data.type === 'event_message') {
      switch (data.event) {
        case 'gameflow_phase':
          handleGameflowPhase(data.content)
          break
        case 'champ_select_changed':
          handleChampSelectChanged(data.content)
          break
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

  // 添加处理游戏状态的辅助函数
  const handleGameflowPhase = (phase: string) => {
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

  // 添加处理选人阶段的辅助函数
  const handleChampSelectChanged = (content: string) => {
    // content = "current_champion=105,bench_champions=[13, 5, 164, 166, 245]"  // 示例数据
    console.log('收到选人阶段变化事件，原始数据:', content)
    
    // 分别获取当前英雄和候选席英雄数据
    const currentChampMatch = content.match(/current_champion=(\d+|None)/)
    const benchChampsMatch = content.match(/bench_champions=\[(.*?)\]/)
    
    console.log('正则匹配结果:', { currentChampMatch, benchChampsMatch })
    
    // 处理当前英雄ID
    const currentChamp = currentChampMatch ? currentChampMatch[1] : 'None'
    console.log('当前英雄ID (处理前):', currentChamp)
    
    // 处理候选席英雄列表
    const benchChampsStr = benchChampsMatch ? benchChampsMatch[1] : ''
    console.log('候选席英雄字符串 (处理前):', benchChampsStr)
    
    // 将候选席英雄字符串转换为数字数组
    const benchChamps = benchChampsStr
      .split(',')
      .map(s => s.trim())
      .filter(s => s.length > 0)
      .map(s => parseInt(s))
      .filter(n => !isNaN(n))
      
    console.log('处理后的候选席英雄ID列表:', benchChamps)
    
    const result = {
      currentChampion: currentChamp === 'None' ? null : parseInt(currentChamp),
      benchChampions: benchChamps
    }
    
    console.log('最终处理结果:', result)
    champSelectInfo.value = result
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
