# LOL工具助手

一个基于 Electron + Vue 3 + TypeScript 的英雄联盟工具助手应用。

## 功能特性

- 🎮 自动接受对局
- 🎯 自动选择英雄
- 🛡️ 自动禁用英雄
- 🔄 自动接受换位请求
- 📊 对局数据统计
- 🏆 英雄胜率排名
- 📜 对局历史记录
- ⚔️ 英雄出装推荐

## 技术栈

- Electron
- Vue 3
- TypeScript
- Vite
- Element Plus
- Pinia
- Vue Router
- Axios
- WebSocket

## 开发环境要求

- Node.js >= 16
- Python 3.x (用于后端服务)
- Conda 环境 (用于管理Python依赖)

## 安装与运行

1. 安装 Python 依赖
```bash
pip install -r server_app/requirements.txt
```

2. 安装 Node.js 依赖
```bash
npm install
```

3. 打包后端服务
```bash
python build.py
```

4. 开发模式运行
```bash
npm run dev
```

5. 构建应用

```bash
npm run build
```

## 项目结构
```
├── dist/ # 前端构建输出目录
├── dist-electron/ # Electron构建输出目录
├── electron/ # Electron主进程源码
├── resources/ # 资源文件
├── src/ # 前端源码
│ ├── components/ # 组件
│ ├── views/ # 页面
│ ├── router/ # 路由配置
│ ├── stores/ # Pinia状态管理
│ └── style.css # 全局样式
└── server_app/ # Python后端服务
```

## 开发指南

1. IDE推荐
- VS Code
- 安装Volar插件
- 禁用Vetur插件
- 安装TypeScript Vue Plugin (Volar)

2. 开启Volar接管模式（可选）
- 在VSCode命令面板中运行`Extensions: Show Built-in Extensions`
- 找到`TypeScript and JavaScript Language Features`
- 右键选择`Disable (Workspace)`
- 重新加载VSCode窗口

## 打包发布

使用electron-builder进行应用打包：

```bash
npm run build
```
支持的平台：
- Windows (portable & installer)
- macOS
- Linux

## 许可证

[MIT License](LICENSE)