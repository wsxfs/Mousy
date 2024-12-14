import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

// 定义类型
interface ChampSelectInfo {
  benchChampions: number[]
  currentChampion: number | null
  // ... 其他属性
}

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
  const gameState = ref<string>('未知')
  const champSelectInfo = ref<ChampSelectInfo>({
    benchChampions: [],
    currentChampion: null
  })
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
    console.log('收到消息:', data)
    // 处理事件消息
    if (data.type === 'event_message') {
      switch (data.event) {
        case 'gameflow_phase':
          handleGameflowPhase(data.content)
          break
        case 'champ_select_changed':
          handleChampSelectChanged(data.content)
          break
        case 'attribute_change':
          handleAttributeChange(data.content)
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

    if (data.type === 'gameflow_phase' && data.phase === 'champ_select') {
      showChampSelectHelper.value = true
    }
  }

  // 添加处理游戏状态的辅助函数
  const handleGameflowPhase = (phase: string) => {
    switch (phase) {
      case 'none':
        gameState.value = '大厅'
        showChampSelectHelper.value = false
        break
      case 'lobby':
        gameState.value = '组队中'
        showChampSelectHelper.value = false
        break
      case 'match_making':
        gameState.value = '匹配中'
        showChampSelectHelper.value = false
        break
      case 'ready_check':
        gameState.value = '确认对局'
        showChampSelectHelper.value = false
        break
      case 'champ_select':
        gameState.value = '选择英雄'
        showChampSelectHelper.value = true
        break
      case 'game_start':
        gameState.value = '游戏开始'
        showChampSelectHelper.value = false
        break
      default:
        gameState.value = phase
        showChampSelectHelper.value = false
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
      benchChampions: benchChamps,
      currentChampion: currentChamp === 'None' ? null : parseInt(currentChamp)
    }
    
    console.log('最终处理结果:', result)
    champSelectInfo.value = result
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

  // 监听游戏状态变化
  watch(gameState, (newState) => {
    console.log('游戏状态变化:', newState)
    if (newState === '选择英雄') {
      // 发送消息给主进程打开选人窗口
      window.ipcRenderer.send('open-champ-select')
    }
    else {
      // 发送消息给主进程关闭选人窗口
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
    champSelectInfo,
    showChampSelectHelper,
    syncFrontData
  }
})
