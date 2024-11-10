import { app as f, BrowserWindow as w } from "electron";
import { fileURLToPath as j } from "node:url";
import l from "node:path";
import I, { spawn as O } from "child_process";
function T(e) {
  return e && e.__esModule && Object.prototype.hasOwnProperty.call(e, "default") ? e.default : e;
}
var E = I, v = E.spawn, y = E.exec, A = function(e, n, o) {
  if (typeof n == "function" && o === void 0 && (o = n, n = void 0), e = parseInt(e), Number.isNaN(e)) {
    if (o)
      return o(new Error("pid must be a number"));
    throw new Error("pid must be a number");
  }
  var r = {}, t = {};
  switch (r[e] = [], t[e] = 1, process.platform) {
    case "win32":
      y("taskkill /pid " + e + " /T /F", o);
      break;
    case "darwin":
      p(e, r, t, function(s) {
        return v("pgrep", ["-P", s]);
      }, function() {
        h(r, n, o);
      });
      break;
    default:
      p(e, r, t, function(s) {
        return v("ps", ["-o", "pid", "--no-headers", "--ppid", s]);
      }, function() {
        h(r, n, o);
      });
      break;
  }
};
function h(e, n, o) {
  var r = {};
  try {
    Object.keys(e).forEach(function(t) {
      e[t].forEach(function(s) {
        r[s] || (m(s, n), r[s] = 1);
      }), r[t] || (m(t, n), r[t] = 1);
    });
  } catch (t) {
    if (o)
      return o(t);
    throw t;
  }
  if (o)
    return o();
}
function m(e, n) {
  try {
    process.kill(parseInt(e, 10), n);
  } catch (o) {
    if (o.code !== "ESRCH") throw o;
  }
}
function p(e, n, o, r, t) {
  var s = r(e), d = "";
  s.stdout.on("data", function(i) {
    var i = i.toString("ascii");
    d += i;
  });
  var P = function(S) {
    if (delete o[e], S != 0) {
      Object.keys(o).length == 0 && t();
      return;
    }
    d.match(/\d+/g).forEach(function(i) {
      i = parseInt(i, 10), n[e].push(i), n[i] = [], o[i] = 1, p(i, n, o, r, t);
    });
  };
  s.on("close", P);
}
const D = /* @__PURE__ */ T(A), R = l.dirname(j(import.meta.url));
process.env.APP_ROOT = l.join(R, "..");
const u = process.env.VITE_DEV_SERVER_URL, N = l.join(process.env.APP_ROOT, "dist-electron"), _ = l.join(process.env.APP_ROOT, "dist");
process.env.VITE_PUBLIC = u ? l.join(process.env.APP_ROOT, "public") : _;
let a, c = null;
function V() {
  var n, o;
  let e;
  console.log(u), u ? e = l.join(f.getAppPath(), "resources/server/server.exe") : e = l.join(f.getAppPath(), "../server/server.exe"), console.log(e), c = O(e, [], {
    shell: !0
  }), (n = c.stdout) == null || n.on("data", (r) => {
    console.log(`Server output: ${r}`);
  }), (o = c.stderr) == null || o.on("data", (r) => {
    console.error(`Server error: ${r}`);
  }), c.on("close", (r) => {
    console.log(`Server exited with code ${r}`);
  });
}
function g() {
  a = new w({
    icon: l.join(process.env.VITE_PUBLIC, "electron-vite.svg"),
    width: 950,
    height: 749,
    minWidth: 629,
    // 最小宽度
    minHeight: 749,
    // 最小高度
    webPreferences: {
      preload: l.join(R, "preload.mjs")
      // 预加载脚本
    }
  }), a.webContents.on("did-finish-load", () => {
    a == null || a.webContents.send("main-process-message", (/* @__PURE__ */ new Date()).toLocaleString());
  }), u ? a.loadURL(u) : a.loadFile(l.join(_, "index.html"));
}
f.on("window-all-closed", () => {
  process.platform !== "darwin" && (f.quit(), a = null);
});
f.on("will-quit", () => {
  b();
});
f.on("activate", () => {
  w.getAllWindows().length === 0 && g();
});
f.whenReady().then(() => {
  V(), g();
});
function b() {
  c != null && c.pid ? D(c.pid, "SIGTERM", (e) => {
    e ? console.error("Failed to kill server process:", e) : console.log("Server process terminated.");
  }) : console.log("Server process is not running.");
}
console.log("中文");
export {
  N as MAIN_DIST,
  _ as RENDERER_DIST,
  u as VITE_DEV_SERVER_URL
};
