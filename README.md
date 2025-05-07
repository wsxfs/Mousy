# Mousy

这是一个基于Vue 3和FastAPI开发的英雄联盟战斗工具应用，提供前后端分离的架构设计。

## 快速开始

### 下载安装包
1. 访问 [Releases](https://github.com/your-username/Mousy/releases) 页面
2. 下载最新版本的安装包
3. 双击安装即可使用

### 开发环境设置
如果您是开发者，需要设置开发环境，请参考以下说明。

## 开发环境配置

### Node.js环境配置（使用NVM）
1. 安装NVM for Windows
2. 配置PowerShell执行策略（以管理员身份运行PowerShell）：
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```
3. 安装并使用Node.js：
```powershell
nvm list available
nvm install 23.3.0
nvm use 23.3.0
```

### Python环境配置（使用Conda）
1. 安装Miniconda或Anaconda
2. 创建并激活虚拟环境：
```bash
conda create -n fastapi
conda activate fastapi
```
3. 安装依赖：
```bash
pip install -r server_app/requirements.txt
```

## 技术栈

### 前端
### 前端
- Vue 3
- TypeScript
- Element Plus
- Pinia (状态管理)
- Pinia (状态管理)
- Vue Router
- Axios

### 后端
- FastAPI
- Python 3.x
- Uvicorn
- Pydantic

### 后端
- FastAPI
- Python 3.x
- Uvicorn
- Pydantic
- WebSocket

## 项目结构

```
LOL_fight_tools/
├── src/                    # 前端源代码
│   ├── assets/            # 静态资源
│   ├── components/        # Vue组件
│   ├── layouts/           # 布局组件
│   ├── router/            # 路由配置
│   ├── stores/            # Pinia状态管理
│   ├── types/             # TypeScript类型定义
│   ├── views/             # 页面视图
│   ├── App.vue            # 根组件
│   └── main.ts            # 入口文件
│
└── server_app/            # 后端源代码
    ├── api/               # API路由
    ├── models/            # 数据模型
    ├── services/          # 业务逻辑
    ├── utils/             # 工具函数
    ├── test/              # 测试文件
    └── main.py            # 服务器入口
```

## 安装说明

### 使用安装包（推荐）
1. 从 [Releases](https://github.com/your-username/Mousy/releases) 下载最新版本安装包
2. 双击安装即可使用

### 开发环境设置
如果您需要开发或修改功能，请按照以下步骤设置开发环境：

#### 前端设置
1. 确保已按照上述说明配置好Node.js环境
2. 在项目根目录下运行：
```bash
npm install
npm run dev
npm run dev
```

#### 后端设置
1. 确保已按照上述说明配置好Python环境
2. 在项目根目录下运行：
#### 后端设置
1. 确保已按照上述说明配置好Python环境
2. 在项目根目录下运行：
```bash
python build.py
```

## 运行说明

### 启动后端服务
在server_app目录下运行：
```bash
python main.py
```
服务器将在 http://127.0.0.1:8000 启动

### 启动前端开发服务器
在项目根目录下运行：
## 运行说明

### 启动后端服务
在server_app目录下运行：
```bash
python main.py
```
服务器将在 http://127.0.0.1:8000 启动

### 启动前端开发服务器
在项目根目录下运行：
```bash
npm run dev
```

## 开发说明

- 前端开发服务器默认运行在 http://localhost:5173
- 后端API服务器运行在 http://127.0.0.1:8000
- 前端已配置代理，可以直接访问后端API

## 注意事项

- 使用安装包版本时，无需手动启动后端服务，程序会自动处理
- 开发环境需要确保在运行前端应用前，后端服务已经启动
- 确保使用正确的Node.js版本（23.3.0）
- 确保使用正确的Python环境（fastapi虚拟环境）
- 前端开发需要Node.js环境
- 后端开发需要Python 3.x环境
## 开发说明

- 前端开发服务器默认运行在 http://localhost:5173
- 后端API服务器运行在 http://127.0.0.1:8000
- 前端已配置代理，可以直接访问后端API

## 注意事项

- 使用安装包版本时，无需手动启动后端服务，程序会自动处理
- 开发环境需要确保在运行前端应用前，后端服务已经启动
- 确保使用正确的Node.js版本（23.3.0）
- 确保使用正确的Python环境（fastapi虚拟环境）
- 前端开发需要Node.js环境
- 后端开发需要Python 3.x环境

## 许可证

[MIT License](LICENSE) 
[MIT License](LICENSE) 