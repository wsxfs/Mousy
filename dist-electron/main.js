import { app, BrowserWindow, ipcMain } from "electron";
import { fileURLToPath } from "node:url";
import path from "node:path";
import require$$0, { spawn as spawn$1 } from "child_process";
function getDefaultExportFromCjs(x) {
  return x && x.__esModule && Object.prototype.hasOwnProperty.call(x, "default") ? x["default"] : x;
}
var childProcess = require$$0;
var spawn = childProcess.spawn;
var exec = childProcess.exec;
var treeKill = function(pid, signal, callback) {
  if (typeof signal === "function" && callback === void 0) {
    callback = signal;
    signal = void 0;
  }
  pid = parseInt(pid);
  if (Number.isNaN(pid)) {
    if (callback) {
      return callback(new Error("pid must be a number"));
    } else {
      throw new Error("pid must be a number");
    }
  }
  var tree = {};
  var pidsToProcess = {};
  tree[pid] = [];
  pidsToProcess[pid] = 1;
  switch (process.platform) {
    case "win32":
      exec("taskkill /pid " + pid + " /T /F", callback);
      break;
    case "darwin":
      buildProcessTree(pid, tree, pidsToProcess, function(parentPid) {
        return spawn("pgrep", ["-P", parentPid]);
      }, function() {
        killAll(tree, signal, callback);
      });
      break;
    default:
      buildProcessTree(pid, tree, pidsToProcess, function(parentPid) {
        return spawn("ps", ["-o", "pid", "--no-headers", "--ppid", parentPid]);
      }, function() {
        killAll(tree, signal, callback);
      });
      break;
  }
};
function killAll(tree, signal, callback) {
  var killed = {};
  try {
    Object.keys(tree).forEach(function(pid) {
      tree[pid].forEach(function(pidpid) {
        if (!killed[pidpid]) {
          killPid(pidpid, signal);
          killed[pidpid] = 1;
        }
      });
      if (!killed[pid]) {
        killPid(pid, signal);
        killed[pid] = 1;
      }
    });
  } catch (err) {
    if (callback) {
      return callback(err);
    } else {
      throw err;
    }
  }
  if (callback) {
    return callback();
  }
}
function killPid(pid, signal) {
  try {
    process.kill(parseInt(pid, 10), signal);
  } catch (err) {
    if (err.code !== "ESRCH") throw err;
  }
}
function buildProcessTree(parentPid, tree, pidsToProcess, spawnChildProcessesList, cb) {
  var ps = spawnChildProcessesList(parentPid);
  var allData = "";
  ps.stdout.on("data", function(data) {
    var data = data.toString("ascii");
    allData += data;
  });
  var onClose = function(code) {
    delete pidsToProcess[parentPid];
    if (code != 0) {
      if (Object.keys(pidsToProcess).length == 0) {
        cb();
      }
      return;
    }
    allData.match(/\d+/g).forEach(function(pid) {
      pid = parseInt(pid, 10);
      tree[parentPid].push(pid);
      tree[pid] = [];
      pidsToProcess[pid] = 1;
      buildProcessTree(pid, tree, pidsToProcess, spawnChildProcessesList, cb);
    });
  };
  ps.on("close", onClose);
}
const kill = /* @__PURE__ */ getDefaultExportFromCjs(treeKill);
const __dirname = path.dirname(fileURLToPath(import.meta.url));
process.env.APP_ROOT = path.join(__dirname, "..");
const VITE_DEV_SERVER_URL = process.env["VITE_DEV_SERVER_URL"];
const MAIN_DIST = path.join(process.env.APP_ROOT, "dist-electron");
const RENDERER_DIST = path.join(process.env.APP_ROOT, "dist");
process.env.VITE_PUBLIC = VITE_DEV_SERVER_URL ? path.join(process.env.APP_ROOT, "public") : RENDERER_DIST;
let win;
let serverProcess = null;
let champSelectWindow = null;
function startPythonServer() {
  var _a, _b;
  let serverPath;
  console.log(VITE_DEV_SERVER_URL);
  if (VITE_DEV_SERVER_URL) {
    serverPath = path.join(app.getAppPath(), "resources/server/server.exe");
  } else {
    serverPath = path.join(app.getAppPath(), "../server/server.exe");
  }
  console.log(serverPath);
  serverProcess = spawn$1(serverPath, [], {
    shell: true
  });
  (_a = serverProcess.stdout) == null ? void 0 : _a.on("data", (data) => {
    console.log(`Server output: ${data}`);
  });
  (_b = serverProcess.stderr) == null ? void 0 : _b.on("data", (data) => {
    console.error(`Server error: ${data}`);
  });
  serverProcess.on("close", (code) => {
    console.log(`Server exited with code ${code}`);
  });
}
function createWindow() {
  win = new BrowserWindow({
    icon: path.join(process.env.VITE_PUBLIC, "electron-vite.svg"),
    width: 1e3,
    height: 749,
    minWidth: 629,
    // 最小宽度
    minHeight: 749,
    // 最小高度
    webPreferences: {
      preload: path.join(__dirname, "preload.mjs")
      // 预加载脚本
    }
  });
  win.webContents.on("did-finish-load", () => {
    win == null ? void 0 : win.webContents.send("main-process-message", (/* @__PURE__ */ new Date()).toLocaleString());
  });
  if (VITE_DEV_SERVER_URL) {
    win.loadURL(VITE_DEV_SERVER_URL);
  } else {
    win.loadFile(path.join(RENDERER_DIST, "index.html"));
  }
}
app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
    win = null;
  }
});
app.on("will-quit", () => {
  stopServer();
});
app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
app.whenReady().then(() => {
  startPythonServer();
  createWindow();
});
function stopServer() {
  if (serverProcess == null ? void 0 : serverProcess.pid) {
    kill(serverProcess.pid, "SIGTERM", (err) => {
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
    width: 400,
    // 初始宽度
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, "preload.mjs")
    },
    frame: false,
    resizable: true,
    // 允许调整大小
    alwaysOnTop: true,
    minWidth: 400,
    // 最小宽度
    maxWidth: 800
    // 最大宽度(展开后的宽度)
  });
  if (VITE_DEV_SERVER_URL) {
    champSelectWindow.loadURL(`${VITE_DEV_SERVER_URL}#/champ-select`);
  } else {
    champSelectWindow.loadFile(path.join(RENDERER_DIST, "index.html"), {
      hash: "/champ-select"
    });
  }
  champSelectWindow.on("closed", () => {
    champSelectWindow = null;
  });
}
ipcMain.on("open-champ-select", () => {
  if (!champSelectWindow) {
    createChampSelectWindow();
  }
});
ipcMain.on("close-champ-select", () => {
  if (champSelectWindow) {
    champSelectWindow.close();
  }
});
ipcMain.on("open-main-window", (_event, { route, focusWindow }) => {
  if (win) {
    win.webContents.send("navigate-to", route);
    win.show();
    if (focusWindow) {
      win.focus();
    }
  }
});
ipcMain.on("resize-champ-select", (_event, { width }) => {
  if (champSelectWindow) {
    const [currentWidth, height] = champSelectWindow.getSize();
    champSelectWindow.setSize(width, height, true);
  }
});
function broadcastToAllWindows(channel, data) {
  const windows = BrowserWindow.getAllWindows();
  windows.forEach((window) => {
    window.webContents.send(channel, data);
  });
}
ipcMain.on("ws-message", (_event, data) => {
  broadcastToAllWindows("ws-update", data);
});
ipcMain.on("ws-connection-status", (_event, status) => {
  broadcastToAllWindows("ws-connection-status", status);
});
ipcMain.on("sync-front-data-update", (_event, data) => {
  broadcastToAllWindows("sync-front-data-update", data);
});
console.log("中文");
export {
  MAIN_DIST,
  RENDERER_DIST,
  VITE_DEV_SERVER_URL
};
