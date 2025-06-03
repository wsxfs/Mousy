import { defineStore } from 'pinia'
import { ref, watch, computed } from 'vue'

// 定义后端同步数据的类型
interface ChampSelectSession {
  timer: {
    phase: string;
  };
  bans: {
    myTeamBans: number[];
    theirTeamBans: number[];
  };
  actions: Array<Array<{
    actorCellId: number;
    championId: number;
    completed: boolean;
    id: number;
    isAllyAction: boolean;
    isInProgress: boolean;
    type: string;
  }>>;
  myTeam: Array<{
    cellId: number;
    championId: number;
    championPickIntent: number;
    assignedPosition: string;
  }>;
  theirTeam: Array<{
    cellId: number;
    championId: number;
    championPickIntent: number;
    assignedPosition: string;
  }>;
}

// 添加小本本记录的类型定义
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

interface SyncFrontData {
  gameflow_phase: string | null;
  current_champion: number | null;
  bench_champions: number[];
  my_team_puuid_list: string[];
  their_team_puuid_list: string[];
  // 组队信息
  my_team_premade_info: Record<string, string[]> | null;  // key是teamParticipantId, value是该小队的puuid列表
  their_team_premade_info: Record<string, string[]> | null;  // key是teamParticipantId, value是该小队的puuid列表
  current_puuid: string | null;
  champ_select_session: ChampSelectSession | null;
  swap_champion_button: boolean | null;
  selected_champion_id: number | null;
  summoner_id: number | null;
  lcu_connected: boolean | null;
  my_team_match_history: Record<string, any> | null;
  their_team_match_history: Record<string, any> | null;
  notebook_records: NotebookRecords | null
}

export const useWebSocketStore = defineStore('websocket', () => {
  // 状态
  const ws = ref<WebSocket | null>(null)
  const isConnected = ref(false)
  const reconnectAttempts = ref(0)
  const messages = ref<any[]>([])
  const disconnectReason = ref<string>('')
  const showChampSelectHelper = ref(false)
  const syncFrontData = ref<SyncFrontData>({
    my_team_puuid_list: [],
    their_team_puuid_list: [],
    my_team_premade_info: null,
    their_team_premade_info: null,
    current_champion: null,
    bench_champions: [],
    gameflow_phase: null,
    swap_champion_button: null,
    selected_champion_id: null,
    summoner_id: null,
    lcu_connected: null,
    my_team_match_history: null,
    their_team_match_history: null,
    current_puuid: null,
    champ_select_session: null,
    notebook_records: null
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
      // 设置 lcu_connected 为 false
      syncFrontData.value.lcu_connected = false
      // 广播连接状态
      safeSendIpcMessage('ws-connection-status', { isConnected: false })
      
      // 无限重连（限时为1s内连接）
      reconnectAttempts.value++
      setTimeout(() => {
        console.log(`尝试第${reconnectAttempts.value}次重连`)
        connect()
      }, 1000)

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

  // 新增：封装处理小本本记录更新和打开弹窗的逻辑
  const openNotebookAlertIfNeeded = (notebookRecords: any) => {
    console.log('检查是否需要打开小本本提醒:', notebookRecords)
    if (notebookRecords?.my_team && notebookRecords?.their_team && 
        (notebookRecords.my_team.length > 0 || notebookRecords.their_team.length > 0)) {
      console.log('条件满足 (封装函数)，打开小本本提醒窗口并发送数据')
      try {
        const serializableRecords = JSON.parse(JSON.stringify(notebookRecords))
        window.ipcRenderer.send('open-notebook-alert', serializableRecords)
      } catch (error) {
        console.error('序列化小本本记录失败 (封装函数):', error, notebookRecords)
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

      // 添加处理初始sync_data的逻辑
      if (data.type === 'sync_data') {
        console.log('收到初始sync_data:', data.data)
        // 使用解构赋值来保留现有值
        syncFrontData.value = {
          ...syncFrontData.value,
          ...data.data
        }

        // *** 初始化时也检查是否需要打开小本本提醒 ***
        if (syncFrontData.value.notebook_records) {
            openNotebookAlertIfNeeded(syncFrontData.value.notebook_records)
        }
        
        // 如果是主窗口，广播同步数据给其他窗口
        if (isMainWindow.value) {
          const frontData = JSON.parse(JSON.stringify(syncFrontData.value))
          safeSendIpcMessage('sync-front-data-update', frontData)
        }
        return
      }

      // 处理消息
      messages.value.push({
        content: data,
        timestamp: new Date().toLocaleTimeString()
      })
      if (messages.value.length > 100) {
        messages.value.shift()
      }

      // 处理事件消息
      if (data.type === 'event_message' && data.event === 'attribute_change') {
        console.log('收到 attribute_change 消息:', data)
        const eventContent = data.content
        if (eventContent.type === 'attribute_change') {
          const { attribute, value } = eventContent.data
          
          // 使用类型守卫确保类型安全
          if (isSyncFrontDataKey(attribute)) {
            console.log(`更新属性 ${attribute}:`, value)
            // 使用解构赋值来保留其他属性值
            syncFrontData.value = {
              ...syncFrontData.value,
              [attribute]: value
            }

            // *** 调用封装的函数处理 notebook_records ***
            if (attribute === 'notebook_records') {
              openNotebookAlertIfNeeded(value) // value 就是最新的 notebook_records
            }
            
            // 如果是主窗口，在更新完数据后广播给其他窗口
            if (isMainWindow.value) {
              const serializableData = JSON.parse(JSON.stringify(syncFrontData.value))
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
      case 'end_of_game': return '游戏结束'
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
    } else if (newPhase === 'end_of_game') {
      // 添加游戏结束时打开总结窗口
      window.ipcRenderer.send('open-game-summary')
    } else {
      window.ipcRenderer.send('close-champ-select')
    }
  })

  // 添加 IPC 监听
  if (!isMainWindow.value) {
    // 子窗口的监听逻辑
    window.electron.ipcRenderer.send('request-initial-state')

    window.electron.ipcRenderer.on('initial-state', (state) => {
      isConnected.value = state.isConnected
      syncFrontData.value = state.syncFrontData
    })

    // ... 其他子窗口监听器 ...
    window.electron.ipcRenderer.on('ws-update', (data) => {
      handleMessage(data)
    })

    window.electron.ipcRenderer.on('ws-connection-status', (status) => {
      isConnected.value = status.isConnected
    })

    window.electron.ipcRenderer.on('sync-front-data-update', (data) => {
      console.log('子窗口收到 sync-front-data-update 消息:', data)
      // 使用解构赋值来保留现有值
      syncFrontData.value = {
        ...syncFrontData.value,
        ...data
      }
    })
  } else {
    // 主窗口的监听逻辑
    window.electron.ipcRenderer.on('get-current-state', () => {
      const currentState = {
        isConnected: isConnected.value,
        syncFrontData: syncFrontData.value,
        gameState: gameState.value
      }
      window.electron.ipcRenderer.send('current-state-response', currentState)
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
