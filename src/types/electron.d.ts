interface IpcRenderer {
  send: (channel: string, ...args: any[]) => void;
  on: (channel: string, func: (...args: any[]) => void) => void;
  off: (channel: string, func: (...args: any[]) => void) => void;
}

declare global {
  interface Window {
    electron: {
      ipcRenderer: IpcRenderer;
    };
  }
}

export {} 