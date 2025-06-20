import { app, BrowserWindow, ipcMain } from 'electron'
// import { createRequire } from 'node:module'
import { fileURLToPath } from 'node:url'
import path from 'node:path'
import { spawn, ChildProcess } from "child_process";
import kill from "tree-kill";

//const require = createRequire(import.meta.url)
const __dirname = path.dirname(fileURLToPath(import.meta.url))

// 构建后的目录结构
//
// ├─┬─┬ dist
// │ │ └── index.html  # 渲染进程打包输出
// │ │
// │ ├─┬ dist-electron
// │ │ ├── main.js     # 主进程打包输出
// │ │ └── preload.mjs # 预加载脚本
// │
process.env.APP_ROOT = path.join(__dirname, '..')

// 🚧 使用 ['ENV_NAME'] 避免 vite:define 插件的影响 - Vite@2.x
export const VITE_DEV_SERVER_URL = process.env['VITE_DEV_SERVER_URL']
export const MAIN_DIST = path.join(process.env.APP_ROOT, 'dist-electron')
export const RENDERER_DIST = path.join(process.env.APP_ROOT, 'dist')

// 如果是开发环境，VITE_PUBLIC 指向 public 文件夹，否则指向渲染进程打包输出目录
process.env.VITE_PUBLIC = VITE_DEV_SERVER_URL ? path.join(process.env.APP_ROOT, 'public') : RENDERER_DIST

let win: BrowserWindow | null
let serverProcess: ChildProcess | null = null;
let champSelectWindow: BrowserWindow | null = null
let gameSummaryWindow: BrowserWindow | null = null
let notebookAlertWindow: BrowserWindow | null = null


// 启动 Python 服务器
function startPythonServer() {
  let serverPath: string;

  console.log(VITE_DEV_SERVER_URL);

  if (VITE_DEV_SERVER_URL){
    serverPath = path.join(app.getAppPath(), "resources/server/server.exe");
  }else{
    serverPath = path.join(app.getAppPath(), "../server/server.exe");
  }
  console.log(serverPath);
  

  serverProcess = spawn(serverPath, [], {
    shell: true,
  });

  serverProcess.stdout?.on("data", (data) => {
    console.log(`Server output: ${data}`);
  });

  serverProcess.stderr?.on("data", (data) => {
    console.error(`Server error: ${data}`);
  });

  serverProcess.on("close", (code) => {
    console.log(`Server exited with code ${code}`);
  });
}



function createWindow() {
  win = new BrowserWindow({
    icon: path.join(process.env.VITE_PUBLIC, 'electron-vite.svg'),
    width: 1332,
    height: 940,
    minWidth: 629,    // 最小宽度
    minHeight: 796,   // 最小高度
    webPreferences: {
      preload: path.join(__dirname, 'preload.mjs'),  // 预加载脚本
    },
  })



  // 测试：向渲染进程发送主进程消息
  win.webContents.on('did-finish-load', () => {
    win?.webContents.send('main-process-message', (new Date).toLocaleString())
  })

  if (VITE_DEV_SERVER_URL) {
    win.loadURL(VITE_DEV_SERVER_URL) // 如果是开发环境，加载开发服务器的 URL
  } else {
    // win.loadFile('dist/index.html')
    win.loadFile(path.join(RENDERER_DIST, 'index.html')) // 否则加载打包后的 HTML 文件
  }
}

// 当所有窗口关闭时退出应用，macOS 除外。macOS 上通常应用和菜单栏保持活跃，直到用户使用 Cmd + Q 退出。
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
    win = null
  }
})

app.on("will-quit", () => {
  stopServer();
});

app.on('activate', () => {
  // 在 macOS 上，点击应用图标时通常会重新创建一个窗口（如果没有其他窗口打开）
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow()
  }
})

// 当 Electron 初始化完成时创建窗口
app.whenReady().then(()=>{
  startPythonServer();
  createWindow();
})

function stopServer() {
  if (serverProcess?.pid) {
    kill(serverProcess.pid, 'SIGTERM', (err) => {
      if (err) {
        console.error("Failed to kill server process:", err);
      } else {
        console.log("Server process terminated.");
      }
    });
  } else {
    console.log("Server process is not running.");
  }
}

function createChampSelectWindow() {
  champSelectWindow = new BrowserWindow({
    width: 400,  // 初始宽度
    height: 650,
    webPreferences: {
      preload: path.join(__dirname, 'preload.mjs')
    },
    frame: false,
    resizable: true,  // 允许调整大小
    alwaysOnTop: true,
    minWidth: 400,    // 最小宽度
    maxWidth: 800,    // 最大宽度(展开后的宽度)
    show: false  // 初始不显示窗口
  })

  if (VITE_DEV_SERVER_URL) {
    champSelectWindow.loadURL(`${VITE_DEV_SERVER_URL}#/champ-select`)
  } else {
    champSelectWindow.loadFile(path.join(RENDERER_DIST, 'index.html'), {
      hash: '/champ-select'
    })
  }

  // 等待窗口加载完成后再显示并设置位置
  champSelectWindow.webContents.on('did-finish-load', () => {
    if (champSelectWindow) {
      const [currentX, currentY] = champSelectWindow.getPosition();
      champSelectWindow.setPosition(currentX + 500, currentY); // 向右偏移500像素
      champSelectWindow.show();
    }
  })

  champSelectWindow.on('closed', () => {
    champSelectWindow = null
  })
}

// 监听 IPC 消息来控制窗口
ipcMain.on('open-champ-select', () => {
  console.log('创建英雄选择窗口')

  if (!champSelectWindow) {
    createChampSelectWindow()
  }
})

ipcMain.on('close-champ-select', () => {
  console.log('关闭英雄选择窗口')
  if (champSelectWindow) {
    champSelectWindow.close()
  }
})

// 添加 IPC 监听器
ipcMain.on('open-main-window', (_event, { route, focusWindow }) => {
  // 如果主窗口已经创建
  if (win) {
    // 发送消息给主窗口进行路由导航
    win.webContents.send('navigate-to', route)
    // 显示并聚焦窗口
    win.show()
    if (focusWindow) {
      win.focus()
    }
  }
})

// 添加新的 IPC 监听器
ipcMain.on('resize-champ-select', (_event, { width }) => {
  if (champSelectWindow) {
    const [_currentWidth, height] = champSelectWindow.getSize()
    champSelectWindow.setSize(width, height, true)
  }
})

// 添加 WebSocket 状态广播函数
function broadcastToAllWindows(channel: string, data: any) {
  const windows = BrowserWindow.getAllWindows()
  windows.forEach(window => {
    window.webContents.send(channel, data)
  })
}

// 添加新的 IPC 监听器
ipcMain.on('ws-message', (_event, data) => {
  broadcastToAllWindows('ws-update', data)
})

// 添加 WebSocket 连接状态同步
ipcMain.on('ws-connection-status', (_event, status) => {
  broadcastToAllWindows('ws-connection-status', status)
})

// 添加 syncFrontData 更新同步
ipcMain.on('sync-front-data-update', (_event, data) => {
  broadcastToAllWindows('sync-front-data-update', data)
})

// 添加新的 IPC 监听器用于处理初始状态请求
ipcMain.on('request-initial-state', (event) => {
  // 获取主窗口
  const mainWindow = BrowserWindow.getAllWindows().find(win => 
    !win.webContents.getURL().includes('#/champ-select')
  )
  
  if (mainWindow) {
    // 向主窗口请求当前状态
    mainWindow.webContents.send('get-current-state')
    
    // 设置一次性监听器来接收主窗口的响应
    ipcMain.once('current-state-response', (_event, state) => {
      // 将状态发送给请求的窗口
      event.sender.send('initial-state', state)
    })
  }
})

// 添加创建游戏总结窗口的函数
function createGameSummaryWindow() {
  if (gameSummaryWindow) {
    gameSummaryWindow.show()
    return
  }

  gameSummaryWindow = new BrowserWindow({
    width: 1292,  // 修改宽度为 1292
    height: 678,  // 修改高度为 678
    webPreferences: {
      preload: path.join(__dirname, 'preload.mjs')
    },
    show: false,
    minWidth: 1292,  // 同时更新最小宽度
    minHeight: 678   // 同时更新最小高度
  })

  // 加载游戏总结页面
  if (VITE_DEV_SERVER_URL) {
    gameSummaryWindow.loadURL(`${VITE_DEV_SERVER_URL}#/game-summary`)
  } else {
    gameSummaryWindow.loadFile(path.join(RENDERER_DIST, 'index.html'), {
      hash: '/game-summary'
    })
  }

  gameSummaryWindow.once('ready-to-show', () => {
    gameSummaryWindow?.show()
  })

  gameSummaryWindow.on('closed', () => {
    gameSummaryWindow = null
  })
}

// 添加关闭游戏总结窗口的函数
function closeGameSummaryWindow() {
  if (gameSummaryWindow) {
    gameSummaryWindow.close()
    gameSummaryWindow = null
  }
}

// 添加 IPC 监听器
ipcMain.on('open-game-summary', () => {
  createGameSummaryWindow()
})

ipcMain.on('close-game-summary', () => {
  closeGameSummaryWindow()
})

// 监听小本本提醒窗口大小调整请求
ipcMain.on('resize-notebook-alert', (_event, { height }) => {
  console.log('主进程：收到调整小本本提醒窗口高度请求:', height);
  if (notebookAlertWindow) {
    const [width, _currentHeight] = notebookAlertWindow.getSize();
    notebookAlertWindow.setSize(width, height, true);
  }
});

// 创建小本本提醒窗口
function createNotebookAlertWindow(notebookRecords?: any) {
  console.log('主进程：尝试创建/显示小本本提醒窗口，接收到的数据:', notebookRecords);

  if (notebookAlertWindow) {
    console.log('主进程：小本本提醒窗口已存在，先关闭再重新创建');
    // 监听关闭事件，关闭后再创建新窗口
    notebookAlertWindow.once('closed', () => {
      notebookAlertWindow = null;
      createNotebookAlertWindow(notebookRecords);
    });
    notebookAlertWindow.close();
    return;
  }

  console.log('主进程：创建新的小本本提醒窗口');
  notebookAlertWindow = new BrowserWindow({
    width: 400,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.mjs')
    },
    frame: false,
    resizable: true,
    alwaysOnTop: true,
    show: false // 初始化时隐藏窗口，等待 'ready-to-show' 事件
  });

  const url = VITE_DEV_SERVER_URL
    ? `${VITE_DEV_SERVER_URL}#/notebook-alert`
    : path.join(RENDERER_DIST, 'index.html') + '#/notebook-alert';

  if (VITE_DEV_SERVER_URL) {
    console.log('主进程：开发环境，加载 URL:', url);
    notebookAlertWindow.loadURL(url);
  } else {
    console.log('主进程：生产环境，加载文件:', url);
    notebookAlertWindow.loadFile(path.join(RENDERER_DIST, 'index.html'), {
      hash: '/notebook-alert'
    });
  }

  // 当页面准备好显示时才显示窗口，避免闪烁
  notebookAlertWindow.once('ready-to-show', () => {
    console.log('主进程：小本本提醒窗口已准备好显示 (ready-to-show)');
    notebookAlertWindow?.show();
  });
  
  // 定义渲染进程就绪的处理器
  const rendererReadyHandler = () => {
    if (notebookAlertWindow && !notebookAlertWindow.isDestroyed()) {
      console.log('主进程：小本本提醒窗口的Vue组件已就绪 (notebook-alert-vue-ready)');
      if (notebookRecords) {
        console.log('主进程：向新的小本本提醒窗口发送初始数据:', notebookRecords);
        notebookAlertWindow.webContents.send('initialize-notebook-alert', notebookRecords);
      } else {
        console.log('主进程：无初始数据需要发送给小本本提醒窗口');
      }
    }
  };

  // 监听来自Vue组件的就绪信号，仅处理一次
  ipcMain.once('notebook-alert-vue-ready', rendererReadyHandler);

  notebookAlertWindow.on('closed', () => {
    console.log('主进程：小本本提醒窗口已关闭');
    // 移除监听器，以防窗口在Vue组件就绪前关闭
    ipcMain.removeListener('notebook-alert-vue-ready', rendererReadyHandler);
    notebookAlertWindow = null;
  });
}

function closeNotebookAlertWindow() {
  console.log('关闭小本本提醒窗口');
  if (notebookAlertWindow) {
    notebookAlertWindow.close();
  }
}

// IPC listener for opening the notebook alert window
ipcMain.on('open-notebook-alert', (_event, receivedNotebookRecords?: any) => {
  console.log('主进程收到 open-notebook-alert 请求, 数据:', receivedNotebookRecords);
  createNotebookAlertWindow(receivedNotebookRecords);
});

ipcMain.on('close-notebook-alert', () => {
  console.log('主进程收到 close-notebook-alert 请求');
  closeNotebookAlertWindow();
});

console.log('中文');