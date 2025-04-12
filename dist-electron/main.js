import { app as m, BrowserWindow as w, ipcMain as c } from "electron";
import { fileURLToPath as T } from "node:url";
import a from "node:path";
import I, { spawn as O } from "child_process";
function A(e) {
  return e && e.__esModule && Object.prototype.hasOwnProperty.call(e, "default") ? e.default : e;
}
var y = I, R = y.spawn, C = y.exec, L = function(e, n, o) {
  if (typeof n == "function" && o === void 0 && (o = n, n = void 0), e = parseInt(e), Number.isNaN(e)) {
    if (o)
      return o(new Error("pid must be a number"));
    throw new Error("pid must be a number");
  }
  var t = {}, r = {};
  switch (t[e] = [], r[e] = 1, process.platform) {
    case "win32":
      C("taskkill /pid " + e + " /T /F", o);
      break;
    case "darwin":
      g(e, t, r, function(u) {
        return R("pgrep", ["-P", u]);
      }, function() {
        j(t, n, o);
      });
      break;
    default:
      g(e, t, r, function(u) {
        return R("ps", ["-o", "pid", "--no-headers", "--ppid", u]);
      }, function() {
        j(t, n, o);
      });
      break;
  }
};
function j(e, n, o) {
  var t = {};
  try {
    Object.keys(e).forEach(function(r) {
      e[r].forEach(function(u) {
        t[u] || (S(u, n), t[u] = 1);
      }), t[r] || (S(r, n), t[r] = 1);
    });
  } catch (r) {
    if (o)
      return o(r);
    throw r;
  }
  if (o)
    return o();
}
function S(e, n) {
  try {
    process.kill(parseInt(e, 10), n);
  } catch (o) {
    if (o.code !== "ESRCH") throw o;
  }
}
function g(e, n, o, t, r) {
  var u = t(e), E = "";
  u.stdout.on("data", function(d) {
    var d = d.toString("ascii");
    E += d;
  });
  var b = function(W) {
    if (delete o[e], W != 0) {
      Object.keys(o).length == 0 && r();
      return;
    }
    E.match(/\d+/g).forEach(function(d) {
      d = parseInt(d, 10), n[e].push(d), n[d] = [], o[d] = 1, g(d, n, o, t, r);
    });
  };
  u.on("close", b);
}
const U = /* @__PURE__ */ A(L), p = a.dirname(T(import.meta.url));
process.env.APP_ROOT = a.join(p, "..");
const f = process.env.VITE_DEV_SERVER_URL, M = a.join(process.env.APP_ROOT, "dist-electron"), v = a.join(process.env.APP_ROOT, "dist");
process.env.VITE_PUBLIC = f ? a.join(process.env.APP_ROOT, "public") : v;
let l, h = null, i = null, s = null;
function D() {
  var n, o;
  let e;
  console.log(f), f ? e = a.join(m.getAppPath(), "resources/server/server.exe") : e = a.join(m.getAppPath(), "../server/server.exe"), console.log(e), h = O(e, [], {
    shell: !0
  }), (n = h.stdout) == null || n.on("data", (t) => {
    console.log(`Server output: ${t}`);
  }), (o = h.stderr) == null || o.on("data", (t) => {
    console.error(`Server error: ${t}`);
  }), h.on("close", (t) => {
    console.log(`Server exited with code ${t}`);
  });
}
function P() {
  l = new w({
    icon: a.join(process.env.VITE_PUBLIC, "electron-vite.svg"),
    width: 1210,
    height: 832,
    minWidth: 629,
    // 最小宽度
    minHeight: 796,
    // 最小高度
    webPreferences: {
      preload: a.join(p, "preload.mjs")
      // 预加载脚本
    }
  }), l.webContents.on("did-finish-load", () => {
    l == null || l.webContents.send("main-process-message", (/* @__PURE__ */ new Date()).toLocaleString());
  }), f ? l.loadURL(f) : l.loadFile(a.join(v, "index.html"));
}
m.on("window-all-closed", () => {
  process.platform !== "darwin" && (m.quit(), l = null);
});
m.on("will-quit", () => {
  V();
});
m.on("activate", () => {
  w.getAllWindows().length === 0 && P();
});
m.whenReady().then(() => {
  D(), P();
});
function V() {
  h != null && h.pid ? U(h.pid, "SIGTERM", (e) => {
    e ? console.error("Failed to kill server process:", e) : console.log("Server process terminated.");
  }) : console.log("Server process is not running.");
}
function $() {
  i = new w({
    width: 400,
    // 初始宽度
    height: 650,
    webPreferences: {
      preload: a.join(p, "preload.mjs")
    },
    frame: !1,
    resizable: !0,
    // 允许调整大小
    alwaysOnTop: !0,
    minWidth: 400,
    // 最小宽度
    maxWidth: 800
    // 最大宽度(展开后的宽度)
  }), f ? i.loadURL(`${f}#/champ-select`) : i.loadFile(a.join(v, "index.html"), {
    hash: "/champ-select"
  }), i.webContents.on("did-finish-load", () => {
    i && i.show();
  }), i.on("closed", () => {
    i = null;
  });
}
c.on("open-champ-select", () => {
  i || $();
});
c.on("close-champ-select", () => {
  i && i.close();
});
c.on("open-main-window", (e, { route: n, focusWindow: o }) => {
  l && (l.webContents.send("navigate-to", n), l.show(), o && l.focus());
});
c.on("resize-champ-select", (e, { width: n }) => {
  if (i) {
    const [o, t] = i.getSize();
    i.setSize(n, t, !0);
  }
});
function _(e, n) {
  w.getAllWindows().forEach((t) => {
    t.webContents.send(e, n);
  });
}
c.on("ws-message", (e, n) => {
  _("ws-update", n);
});
c.on("ws-connection-status", (e, n) => {
  _("ws-connection-status", n);
});
c.on("sync-front-data-update", (e, n) => {
  _("sync-front-data-update", n);
});
c.on("request-initial-state", (e) => {
  const n = w.getAllWindows().find(
    (o) => !o.webContents.getURL().includes("#/champ-select")
  );
  n && (n.webContents.send("get-current-state"), c.once("current-state-response", (o, t) => {
    e.sender.send("initial-state", t);
  }));
});
function x() {
  if (s) {
    s.show();
    return;
  }
  s = new w({
    width: 1292,
    // 修改宽度为 1292
    height: 678,
    // 修改高度为 678
    webPreferences: {
      preload: a.join(p, "preload.mjs")
    },
    show: !1,
    minWidth: 1292,
    // 同时更新最小宽度
    minHeight: 678
    // 同时更新最小高度
  }), f ? s.loadURL(`${f}#/game-summary`) : s.loadFile(a.join(v, "index.html"), {
    hash: "/game-summary"
  }), s.once("ready-to-show", () => {
    s == null || s.show();
  }), s.on("closed", () => {
    s = null;
  });
}
function F() {
  s && (s.close(), s = null);
}
c.on("open-game-summary", () => {
  x();
});
c.on("close-game-summary", () => {
  F();
});
console.log("中文");
export {
  M as MAIN_DIST,
  v as RENDERER_DIST,
  f as VITE_DEV_SERVER_URL
};
