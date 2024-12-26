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
  lcu_connected: boolean | null
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
    summoner_id: null,
    lcu_connected: null
  })
  
  // 添加窗口类型标识
  const isMainWindow = ref(window.location.hash !== '#/champ-select')

  // 连接方法
  const connect = () => {
    if (!isMainWindow.value) return  // 只允许主窗口建立连接
    
    if (ws.value?.readyState === WebSocket.OPEN) return

    ws.value = new WebSocket('ws://127.0.0.1:8000/api/websocket/test')

    ws.value.onopen = () => {
      console.log('WebSocket 连接已建立')
      isConnected.value = true
      reconnectAttempts.value = 0
      // 广播连接状态
      safeSendIpcMessage('ws-connection-status', { isConnected: true })
    }

    ws.value.onclose = () => {
      console.log('WebSocket 连接已关闭')
      isConnected.value = false
      // 广播连接状态
      safeSendIpcMessage('ws-connection-status', { isConnected: false })
      
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
        handleMessage(data)
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

  // 添加类型守卫函数
  function isSyncFrontDataKey(key: string): key is keyof SyncFrontData {
    console.log('检查属性:', key)
    return key in syncFrontData.value
  }

  // 添加安全发送函数
  const safeSendIpcMessage = (channel: string, data: any) => {
    try {
      if (window.electron?.ipcRenderer) {
        window.electron.ipcRenderer.send(channel, data)
      } else {
        console.warn('electron.ipcRenderer 不可用')
      }
    } catch (error: unknown) {
      if (error instanceof Error) {
        console.error('发送 IPC 消息失败:', error.message)
      } else {
        console.error('发送 IPC 消息失败:', error)
      }
    }
  }

  // 修改消息处理函数
  const handleMessage = (data: any) => {
    try {
      // 如果是主窗口，广播消息给其他窗口
      if (isMainWindow.value) {
        // 创建一个可序列化的消息副本
        const serializableMessage = {
          type: data.type,
          event: data.event,
          content: data.content ? JSON.parse(JSON.stringify(data.content)) : null
        }
        safeSendIpcMessage('ws-message', serializableMessage)
      }

      // 处理消息
      messages.value.push({
        content: data,
        timestamp: new Date().toLocaleTimeString()
      })
      if (messages.value.length > 100) {
        messages.value.shift() // 保持最多100条消息
      }

      // 处理事件消息
      console.log('收到消息:', data)
      if (data.type === 'event_message' && data.event === 'attribute_change') {
        console.log('收到 attribute_change 消息:', data)
        const eventContent = data.content
        if (eventContent.type === 'attribute_change') {
          const { attribute, value } = eventContent.data
          
          // 使用类型守卫确保类型安全
          if (isSyncFrontDataKey(attribute)) {
            console.log(`更新属性 ${attribute}:`, value)
            syncFrontData.value[attribute] = value
            
            // 如果是主窗口，在更新完数据后广播给其他窗口
            if (isMainWindow.value) {
              const serializableData = JSON.parse(JSON.stringify({
                my_team_puuid_list: syncFrontData.value.my_team_puuid_list,
                their_team_puuid_list: syncFrontData.value.their_team_puuid_list,
                current_champion: syncFrontData.value.current_champion,
                bench_champions: syncFrontData.value.bench_champions,
                gameflow_phase: syncFrontData.value.gameflow_phase,
                swap_champion_button: syncFrontData.value.swap_champion_button,
                selected_champion_id: syncFrontData.value.selected_champion_id,
                summoner_id: syncFrontData.value.summoner_id
              }))
              safeSendIpcMessage('sync-front-data-update', serializableData)
            }
          } else {
            console.warn(`未知的属性名: ${attribute}`)
          }
        }
      }
    } catch (error: unknown) {
      if (error instanceof Error) {
        console.error('处理 WebSocket 消息失败:', error.message)
        console.error('错误堆栈:', error.stack)
      } else {
        console.error('处理 WebSocket 消息失败:', error)
      }
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

  // 添加 IPC 监听
  if (!isMainWindow.value) {
    window.electron.ipcRenderer.on('ws-update', (data) => {
      handleMessage(data)
    })

    window.electron.ipcRenderer.on('ws-connection-status', (status) => {
      isConnected.value = status.isConnected
    })

    window.electron.ipcRenderer.on('sync-front-data-update', (data) => {
      console.log('子窗口收到 sync-front-data-update 消息:', data)
      syncFrontData.value = data
    })
  }

  // 可以添加一个计算属性来方便地访问 LCU 连接状态
  const lcuConnected = computed(() => syncFrontData.value.lcu_connected ?? false)

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
    syncFrontData,
    lcuConnected
  }
})
