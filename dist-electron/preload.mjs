"use strict";
const electron = require("electron");
electron.contextBridge.exposeInMainWorld("ipcRenderer", {
  on(...args) {
    const [channel, listener] = args;
    return electron.ipcRenderer.on(channel, (event, ...args2) => listener(event, ...args2));
  },
  off(...args) {
    const [channel, ...omit] = args;
    return electron.ipcRenderer.off(channel, ...omit);
  },
  send(...args) {
    const [channel, ...omit] = args;
    return electron.ipcRenderer.send(channel, ...omit);
  },
  invoke(...args) {
    const [channel, ...omit] = args;
    return electron.ipcRenderer.invoke(channel, ...omit);
  }
  // You can expose other APTs you need here.
  // ...
});
electron.contextBridge.exposeInMainWorld("electron", {
  ipcRenderer: {
    send: (channel, ...args) => {
      const validChannels = [
        "open-champ-select",
        "close-champ-select",
        "open-main-window",
        "resize-champ-select",
        "ws-message",
        // 添加新通道
        "ws-connection-status",
        // 添加新通道
        "sync-front-data-update"
        // 添加新通道
      ];
      if (validChannels.includes(channel)) {
        electron.ipcRenderer.send(channel, ...args);
      }
    },
    on: (channel, func) => {
      const validChannels = [
        "navigate-to",
        "ws-update",
        // 添加新通道
        "ws-connection-status",
        // 添加新通道
        "sync-front-data-update"
        // 添加新通道
      ];
      if (validChannels.includes(channel)) {
        electron.ipcRenderer.on(channel, (_event, ...args) => func(...args));
      }
    }
  }
});
