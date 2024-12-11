interface IElectronAPI {
  ipcRenderer: {
    send: (channel: string, ...args: any[]) => void
  }
}

declare global {
  interface Window {
    electron: IElectronAPI
  }
}

export {} 