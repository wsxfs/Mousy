import { defineStore } from 'pinia'
import { ref, watch, computed } from 'vue'

// 定义后端同步数据的类型
interface SyncFrontData {
  my_team_puuid_list: string[] | null
  their_team_puuid_list: string[] | null
  current_champion: number | null
  bench_champions: number[] | null
  gameflow_phase: string | null
  swap_champion_button: boolean | null
  selected_champion_id: number | null
  summoner_id: number | null
}

export const useWebSocketStore = defineStore('websocket', () => {
  // 状态
  const ws = ref<WebSocket | null>(null)
  const isConnected = ref(false)
  const reconnectAttempts = ref(0)
  const maxReconnectAttempts = 5
  const messages = ref<any[]>([])
  const disconnectReason = ref<string>('')
  const showChampSelectHelper = ref(false)
  const syncFrontData = ref<SyncFrontData>({
    my_team_puuid_list: null,
    their_team_puuid_list: null,
    current_champion: null,
    bench_champions: null,
    gameflow_phase: null,
    swap_champion_button: null,
    selected_champion_id: null,
    summoner_id: null
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
      showChampSelectHelper.value = false
    }
  }

  // 处理接收到的消息
  const handleWebSocketMessage = (data: any) => {
    console.log('收到WebSocket消息:', data)
    
    try {
      if (data.type === 'event_message') {
        switch (data.event) {
          case 'attribute_change':
            handleAttributeChange(data.content)
            break
          default:
            console.log('未处理的事件类型:', data.event)
        }
      }
      
      // 保存消息历史
      messages.value.push({
        content: data,
        timestamp: new Date().toLocaleTimeString()
      })
      if (messages.value.length > 100) {
        messages.value.shift()
      }
    } catch (error) {
      console.error('处理WebSocket消息时出错:', error)
    }
  }

  // 添加新的处理函数
  const handleAttributeChange = (content: string) => {
    console.log('收到属性变更事件，原始数据:', content)
    
    // 解析属性名和值
    const match = content.match(/^(.+?)=(.+)$/)
    if (!match) {
      console.error('无法解析属性变更数据:', content)
      return
    }
    
    const [, attributeName, rawValue] = match
    console.log('解析结果:', { attributeName, rawValue })
    
    // 根据属性名处理不同类型的值
    try {
      let parsedValue: any
      
      // 处理数组类型的值
      if (rawValue.startsWith('[') && rawValue.endsWith(']')) {
        parsedValue = JSON.parse(rawValue)
      }
      // 处理布尔值
      else if (rawValue === 'true' || rawValue === 'false') {
        parsedValue = rawValue === 'true'
      }
      // 处理数字
      else if (!isNaN(Number(rawValue))) {
        parsedValue = Number(rawValue)
      }
      // 处理null
      else if (rawValue === 'None' || rawValue === 'null') {
        parsedValue = null
      }
      // 其他情况作为字符串处理
      else {
        parsedValue = rawValue
      }
      
      console.log('解析后的值:', parsedValue)
      
      // 更新syncFrontData中对应的属性
      if (attributeName in syncFrontData.value) {
        console.log(`更新属性 ${attributeName}:`, parsedValue)
        syncFrontData.value[attributeName as keyof SyncFrontData] = parsedValue
      } else {
        console.warn('未知的属性名:', attributeName)
      }
      
    } catch (error) {
      console.error('处理属性变更数据时出错:', error)
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

  // 修改游戏状态监听
  const gameState = computed(() => {
    switch (syncFrontData.value.gameflow_phase) {
      case 'none': return '大厅'
      case 'lobby': return '组队中'
      case 'match_making': return '匹配中'
      case 'ready_check': return '确认对局'
      case 'champ_select': return '选择英雄'
      case 'game_start': return '游戏开始'
      default: return syncFrontData.value.gameflow_phase || '未知'
    }
  })

  // 修改监听逻辑
  watch(() => syncFrontData.value.gameflow_phase, (newPhase) => {
    console.log('游戏阶段变化:', newPhase)
    if (!newPhase) return
    
    // 只处理UI相关状态
    showChampSelectHelper.value = newPhase === 'champ_select'
    
    // 处理窗口显示/隐藏
    if (newPhase === 'champ_select') {
      window.ipcRenderer.send('open-champ-select')
    } else {
      window.ipcRenderer.send('close-champ-select')
    }
  })

  return {
    isConnected,
    messages,
    disconnectReason,
    connect,
    disconnect,
    sendMessage,
    clearMessages,
    gameState,
    showChampSelectHelper,
    syncFrontData
  }
})
