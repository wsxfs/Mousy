import { ipcRenderer, contextBridge } from 'electron'

// --------- Expose some API to the Renderer process ---------
contextBridge.exposeInMainWorld('ipcRenderer', {
  on(...args: Parameters<typeof ipcRenderer.on>) {
    const [channel, listener] = args
    return ipcRenderer.on(channel, (event, ...args) => listener(event, ...args))
  },
  off(...args: Parameters<typeof ipcRenderer.off>) {
    const [channel, ...omit] = args
    return ipcRenderer.off(channel, ...omit)
  },
  send(...args: Parameters<typeof ipcRenderer.send>) {
    const [channel, ...omit] = args
    return ipcRenderer.send(channel, ...omit)
  },
  invoke(...args: Parameters<typeof ipcRenderer.invoke>) {
    const [channel, ...omit] = args
    return ipcRenderer.invoke(channel, ...omit)
  },

  // You can expose other APTs you need here.
  // ...
})

// 添加 electron API
contextBridge.exposeInMainWorld('electron', {
  ipcRenderer: {
    send: (channel: string, ...args: any[]) => {
      const validChannels = [
        'open-champ-select', 
        'close-champ-select',
        'open-main-window',
        'resize-champ-select',
        'ws-message',           // 添加新通道
        'ws-connection-status', // 添加新通道
        'sync-front-data-update', // 添加新通道
        'open-notebook-alert',   // 添加小本本提醒窗口通道
        'close-notebook-alert'   // 添加小本本提醒窗口通道
      ]
      if (validChannels.includes(channel)) {
        ipcRenderer.send(channel, ...args)
      }
    },
    on: (channel: string, func: (...args: any[]) => void) => {
      const validChannels = [
        'navigate-to',
        'ws-update',             // 添加新通道
        'ws-connection-status',  // 添加新通道
        'sync-front-data-update' // 添加新通道
      ]
      if (validChannels.includes(channel)) {
        ipcRenderer.on(channel, (_event, ...args) => func(...args))
      }
    }
  }
})
