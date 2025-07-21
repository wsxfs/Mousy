import { app, BrowserWindow, ipcMain, Tray, Menu } from 'electron'
// import { createRequire } from 'node:module'
import { fileURLToPath } from 'node:url'
import path from 'node:path'
import { spawn, ChildProcess } from "child_process";
import kill from "tree-kill";
import { SingleInstanceManager, CloseActionManager } from './managers';
import { Logger, LogLevel } from './utils';

//const require = createRequire(import.meta.url)
const __dirname = path.dirname(fileURLToPath(import.meta.url))

// 初始化日志工具
const logger = Logger.getInstance();
logger.setAppName('Mousy');
logger.setLogLevel(LogLevel.INFO);

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
let tray: Tray | null = null
let ifQuit = false


// 启动 Python 服务器
function startPythonServer() {
  let serverPath: string;

  logger.debug('VITE_DEV_SERVER_URL:', VITE_DEV_SERVER_URL);

  if (VITE_DEV_SERVER_URL) {
    serverPath = path.join(app.getAppPath(), "resources/server/server.exe");
  } else {
    serverPath = path.join(app.getAppPath(), "../server/server.exe");
  }
  logger.debug('Server path:', serverPath);


  serverProcess = spawn(serverPath, [], {
    shell: true,
  });

  serverProcess.stdout?.on("data", (data) => {
    logger.info(`Server output: ${data}`);
  });

  serverProcess.stderr?.on("data", (data) => {
    logger.error(`Server error: ${data}`);
  });

  serverProcess.on("close", (code) => {
    logger.info(`Server exited with code ${code}`);
  });
}

// 获取 icon 路径，兼容开发和生产环境
function getIconPath() {
  if (VITE_DEV_SERVER_URL) {
    // 开发环境，路径相对于项目根目录
    return path.join(process.env.APP_ROOT, 'resources/icon/Mousy_950-圆角2-6种尺寸.ico')
  } else {
    // 生产环境，路径相对于 app.getAppPath() 或其上级目录
    // 这里假设 resources 会被放在 app.getAppPath() 的同级目录
    return path.join(app.getAppPath(), '../icon/Mousy_950-圆角2-6种尺寸.ico')
  }
}

function createWindow(): BrowserWindow {
  win = new BrowserWindow({
    icon: getIconPath(),
    width: 1332,
    height: 940,
    minWidth: 629,    // 最小宽度
    minHeight: 796,   // 最小高度
    webPreferences: {
      preload: path.join(__dirname, 'preload.mjs'),  // 预加载脚本
    },
  })
  // 隐藏英文菜单栏
  win.setMenuBarVisibility(false)

  // 关闭时根据用户偏好设置决定行为
  win.on('close', (event) => {
    if (process.platform === 'win32' && !ifQuit) {
      // 使用 CloseActionManager 处理关闭行为
      CloseActionManager.handleWindowClose(event, win as BrowserWindow);
    }
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
  return win
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

// 检查是否为单实例
if (!SingleInstanceManager.checkSingleInstance()) {
  // 如果不是单实例，应用程序将退出
  // checkSingleInstance 内部已经调用了 app.quit()
} else {
  // 当 Electron 初始化完成时创建窗口
  app.whenReady().then(() => {
    startPythonServer();
    createWindow();
    createTray();
  });
}

function stopServer() {
  if (serverProcess?.pid) {
    kill(serverProcess.pid, 'SIGTERM', (err) => {
      if (err) {
        logger.error("Failed to kill server process:", err);
      } else {
        logger.info("Server process terminated.");
      }
    });
  } else {
    logger.info("Server process is not running.");
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
  logger.info('创建英雄选择窗口')

  if (!champSelectWindow) {
    createChampSelectWindow()
  }
})

ipcMain.on('close-champ-select', () => {
  logger.info('关闭英雄选择窗口')
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
  logger.info('主进程：收到调整小本本提醒窗口高度请求:', height);
  if (notebookAlertWindow) {
    const [width, _currentHeight] = notebookAlertWindow.getSize();
    notebookAlertWindow.setSize(width, height, true);
  }
});

// 创建小本本提醒窗口
function createNotebookAlertWindow(notebookRecords?: any) {
  logger.info('主进程：尝试创建/显示小本本提醒窗口，接收到的数据:', notebookRecords);

  if (notebookAlertWindow) {
    logger.info('主进程：小本本提醒窗口已存在，先关闭再重新创建');
    // 监听关闭事件，关闭后再创建新窗口
    notebookAlertWindow.once('closed', () => {
      notebookAlertWindow = null;
      createNotebookAlertWindow(notebookRecords);
    });
    notebookAlertWindow.close();
    return;
  }

  logger.info('主进程：创建新的小本本提醒窗口');
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
    logger.info('主进程：开发环境，加载 URL:', url);
    notebookAlertWindow.loadURL(url);
  } else {
    logger.info('主进程：生产环境，加载文件:', url);
    notebookAlertWindow.loadFile(path.join(RENDERER_DIST, 'index.html'), {
      hash: '/notebook-alert'
    });
  }

  // 当页面准备好显示时才显示窗口，避免闪烁
  notebookAlertWindow.once('ready-to-show', () => {
    logger.info('主进程：小本本提醒窗口已准备好显示 (ready-to-show)');
    notebookAlertWindow?.show();
  });

  // 定义渲染进程就绪的处理器
  const rendererReadyHandler = () => {
    if (notebookAlertWindow && !notebookAlertWindow.isDestroyed()) {
      logger.info('主进程：小本本提醒窗口的Vue组件已就绪 (notebook-alert-vue-ready)');
      if (notebookRecords) {
        logger.info('主进程：向新的小本本提醒窗口发送初始数据:', notebookRecords);
        notebookAlertWindow.webContents.send('initialize-notebook-alert', notebookRecords);
      } else {
        logger.info('主进程：无初始数据需要发送给小本本提醒窗口');
      }
    }
  };

  // 监听来自Vue组件的就绪信号，仅处理一次
  ipcMain.once('notebook-alert-vue-ready', rendererReadyHandler);

  notebookAlertWindow.on('closed', () => {
    logger.info('主进程：小本本提醒窗口已关闭');
    // 移除监听器，以防窗口在Vue组件就绪前关闭
    ipcMain.removeListener('notebook-alert-vue-ready', rendererReadyHandler);
    notebookAlertWindow = null;
  });
}

function closeNotebookAlertWindow() {
  logger.info('关闭小本本提醒窗口');
  if (notebookAlertWindow) {
    notebookAlertWindow.close();
  }
}

// IPC listener for opening the notebook alert window
ipcMain.on('open-notebook-alert', (_event, receivedNotebookRecords?: any) => {
  logger.info('主进程收到 open-notebook-alert 请求, 数据:', receivedNotebookRecords);
  createNotebookAlertWindow(receivedNotebookRecords);
});

ipcMain.on('close-notebook-alert', () => {
  logger.info('主进程收到 close-notebook-alert 请求');
  closeNotebookAlertWindow();
});

// 添加关闭对话框响应的 IPC 监听器
ipcMain.on('close-dialog-response', async (_event, result: { action: 'minimize' | 'close' | 'cancel', rememberChoice: boolean }) => {
  logger.info('主进程收到关闭对话框响应:', result);

  try {
    // 如果用户选择记住选择，则保存偏好设置
    if (result.rememberChoice && (result.action === 'minimize' || result.action === 'close')) {
      logger.info('保存关闭偏好设置:', { action: result.action, rememberChoice: true });
      await CloseActionManager.saveClosePreference({
        action: result.action,
        rememberChoice: true
      });
      
      // 验证设置是否保存成功
      const savedPreference = await CloseActionManager.getClosePreference();
      logger.info('验证保存的关闭偏好设置:', savedPreference);
    } else if (result.action === 'cancel') {
      // 如果用户取消关闭操作，不执行任何操作
      logger.info('用户取消关闭操作，不执行任何操作');
      return;
    } else if (!result.rememberChoice) {
      // 如果用户不记住选择，清除之前的偏好设置
      logger.info('用户不记住选择，清除之前的偏好设置');
      await CloseActionManager.clearClosePreference();
      
      // 验证设置是否清除成功
      const clearedPreference = await CloseActionManager.getClosePreference();
      logger.info('验证清除后的关闭偏好设置:', clearedPreference);
    }

    // 执行相应的关闭操作
    if (result.action === 'minimize') {
      // 最小化到托盘
      logger.info('最小化窗口到托盘');
      if (win) {
        win.hide();
      }
    } else if (result.action === 'close') {
      // 完全关闭应用程序
      logger.info('完全关闭应用程序');
      ifQuit = true;
      app.quit();
    }
  } catch (error) {
    logger.error('处理关闭对话框响应时出错:', error);
  }
});

function createTray() {
  if (tray) return
  tray = new Tray(getIconPath())
  const contextMenu = Menu.buildFromTemplate([
    {
      label: '显示主界面',
      click: () => {
        if (win) {
          win.show()
          win.focus()
        }
      }
    },
    {
      label: '设置',
      click: () => {
        if (win) {
          // 如果窗口已经打开，显示并导航到设置页面
          win.show()
          win.focus()
          win.webContents.send('navigate-to', '/settings')
        } else {
          // 如果窗口不存在，创建窗口并导航到设置页面
          const createdWin = createWindow()
          createdWin.webContents.once('did-finish-load', () => {
            createdWin.webContents.send('navigate-to', '/settings')
          })
        }
      }
    },
    { type: 'separator' },
    {
      label: '退出',
      click: () => {
        ifQuit = true
        app.quit()
      }
    }
  ])
  tray.setToolTip('Mousy')
  tray.setContextMenu(contextMenu)
  tray.on('double-click', () => {
    if (win) {
      win.show()
      win.focus()
    }
  })
}

logger.info('应用程序初始化完成');