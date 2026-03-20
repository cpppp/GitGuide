# GitGuide 项目架构设计

## 1. 整体架构

GitGuide 采用 **Vue 3 + FastAPI + LangChain** 的前后端分离架构，通过 WebSocket 实现实时进度推送，通过协调多个专业化 Agent 来完成 GitHub 仓库的分析、文档生成和智能问答功能。

```
┌───────────────────────────────────────────────────────────────────────────┐
│                           Vue 3 前端 (Element Plus)                      │
├─────────────────────┬──────────────────────┬───────────────────────────────┤
│  🏠 Home 页面       │ 📚 Documentation 页面 │        💬 Chat 页面           │
│  (URL 输入+进度)    │  (文档展示+导出+图谱)  │     (AI 问答)                │
└─────────────────────┴──────────────────────┴───────────────────────────────┘
                              │
                    HTTP / WebSocket
                              ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                          FastAPI 后端                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  API Routes: /api/analyze | /api/chat | /api/history | /api/favorites    │
│  WebSocket: /ws/analyze/{job_id} (实时进度推送)                           │
└─────────────────────┬─────────────────────────────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                          Orchestrator Agent                              │
│                   (工作流协调、任务分发)                                   │
└─────────────────────┬──────────────────────┬───────────────────────────────┘
                     │                      │
                     ▼                      ▼
┌────────────────────────┐      ┌──────────────────────────────┐
│   Analyzer Agent       │      │      DocGen Agent            │
│  (仓库分析专家)         │      │   (文档生成专家)             │
│ - 识别项目类型         │      │ - 生成学习文档               │
│ - 分析目录结构         │      │ - 生成启动指南               │
│ - 解析依赖关系         │      │ - 提取关键信息               │
└──────────┬─────────────┘      └──────────────────────────────┘
           │
           ▼
┌────────────────────────┐
│    Chat Agent          │
│  (问答专家)             │
│ - 回答用户问题         │
│ - 解释代码逻辑         │
│ - 提供项目建议         │
└────────────────────────┘
```

### 1.1 前端状态管理

使用 Pinia 进行状态管理，新增 settings store 管理主题和语言：

```
frontend/src/stores/
├── analysis.js     # 分析状态管理（已有）
└── settings.js     # 设置状态管理（新增）
    - theme: 'light' | 'dark'
    - language: 'zh' | 'en'
```

### 1.2 主题系统

使用 CSS 变量实现主题切换：

```css
/* 浅色主题 */
:root {
  --bg-color: #f5f7fa;
  --bg-color-secondary: #ffffff;
  --text-color: #303133;
  --text-color-secondary: #606266;
  --border-color: #dcdfe6;
  --primary-color: #409eff;
  --header-bg: #ffffff;
}

/* 深色主题 */
.dark-theme {
  --bg-color: #1a1a1a;
  --bg-color-secondary: #2d2d2d;
  --text-color: #e0e0e0;
  --text-color-secondary: #a0a0a0;
  --border-color: #404040;
  --header-bg: #2d2d2d;
}
```

### 1.3 导出功能

新增导出工具函数，支持多种格式：

```
frontend/src/utils/
└── export.js        # 导出工具（新增）
    - exportToMarkdown()
    - exportToHTML()
    - exportToPDF()
    - downloadFile()
```

### 1.4 代码图谱

新增代码图谱组件：

```
frontend/src/components/
└── CodeAtlas.vue    # 代码图谱组件（新增）
    - 目录结构可视化
    - 文件统计表格
    - 依赖关系展示
```

### 1.5 多语言支持

新增国际化配置：

```
frontend/src/i18n/
└── index.js         # 多语言配置（新增）
    - translations: { zh, en }
    - t(key, lang)  # 翻译函数
```

**启动服务：**

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 安装前端依赖
cd frontend && npm install

# 3. 启动后端
cd backend && uvicorn main:app --reload --port 8000

# 4. 启动前端
cd frontend && npm run dev
```

## 2. 项目结构

```
GitGuide/
├── app.py                      # Streamlit 主入口（旧版，保留兼容）
├── pages/                      # Streamlit 页面（旧版）
│   ├── 1_🏠_Home.py
│   ├── 2_📚_Documentation.py
│   └── 3_💬_Chat.py
│
├── backend/                    # FastAPI 后端
│   ├── main.py                 # FastAPI 入口
│   ├── api/                    # API 路由
│   │   ├── analyze.py          # 分析 API
│   │   ├── chat.py             # 问答 API
│   │   └── health.py           # 健康检查
│   ├── models/
│   │   └── schemas.py          # Pydantic 数据模型
│   ├── websocket/
│   │   └── manager.py          # WebSocket 管理器
│   ├── tasks.py                # RQ 任务队列（可选）
│   └── worker.py               # RQ Worker（可选）
│
├── frontend/                   # Vue 3 前端
│   ├── src/
│   │   ├── api/                # API 调用
│   │   │   ├── analyze.js
│   │   │   └── chat.js
│   │   ├── components/         # 公共组件
│   │   │   └── CodeAtlas.vue   # 代码图谱（新增）
│   │   ├── views/              # 页面组件
│   │   │   ├── Home.vue
│   │   │   ├── Documentation.vue
│   │   │   └── Chat.vue
│   │   ├── stores/             # Pinia 状态管理
│   │   │   ├── analysis.js
│   │   │   └── settings.js     # 设置状态（新增）
│   │   ├── i18n/               # 国际化（新增）
│   │   │   └── index.js
│   │   ├── utils/              # 工具函数
│   │   │   └── export.js       # 导出工具（新增）
│   │   ├── router/             # 路由配置
│   │   │   └── index.js
│   │   ├── main.js
│   │   └── App.vue
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
│
├── agents/                     # LangChain Agent
│   ├── orchestrator.py         # 协调器 Agent
│   ├── analyzer.py             # 仓库分析 Agent
│   ├── doc_generator.py        # 文档生成 Agent
│   └── chat.py                 # 问答 Agent
│
├── tools/                      # 工具函数
│   ├── github_tools.py         # GitHub API 工具
│   ├── git_tools.py            # GitPython 工具
│   └── file_tools.py           # 文件读取工具
│
├── core/                       # 核心模块
│   ├── config.py               # 配置管理
│   ├── utils.py                # 工具函数
│   ├── favorites.py            # 收藏仓库管理
│   ├── history.py              # 历史记录管理
│   └── validators.py           # URL 验证和错误处理
│
├── data/                       # 数据存储
│   ├── favorites.json          # 收藏仓库数据
│   └── history.json            # 历史记录数据
│
├── memory-bank/                # 项目文档
│   ├── architecture.md         # 架构设计文档
│   ├── product-design-document.md # 产品设计文档
│   ├── tech-stack.md           # 技术栈文档
│   ├── implementation-plan.md  # 实施计划
│   └── process.md              # 进度跟踪
│
├── docs/
│   └── CHANGELOG.md            # 变更日志
│
├── requirements.txt            # Python 依赖
└── .env                        # 环境变量
```

## 3. API 端点

### 3.1 分析 API

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/api/analyze` | 启动分析，返回 job_id |
| GET | `/api/analyze/{job_id}/status` | 查询任务状态 |
| POST | `/api/analyze/{job_id}/cancel` | 取消分析 |
| WS | `/ws/analyze/{job_id}` | WebSocket 实时进度 |

### 3.2 问答 API

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/api/chat` | 发送问答请求 |

### 3.3 数据 API

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/history` | 获取历史记录 |
| POST | `/api/history/clear` | 清除历史记录 |
| GET | `/api/favorites` | 获取收藏列表 |
| POST | `/api/favorites` | 添加收藏 |
| DELETE | `/api/favorites` | 移除收藏 |

### 3.4 健康检查

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/health` | 健康检查 |
| GET | `/` | 根路径 |

## 4. 数据结构

### 4.1 分析请求

```python
{
    "repo_url": "https://github.com/user/repo",
    "mode": "fast"  # 或 "detailed"
}
```

### 4.2 任务状态

```python
{
    "job_id": "uuid",
    "status": "pending|running|completed|failed|cancelled",
    "progress": 50,
    "progress_message": "正在生成学习文档...",
    "result": {
        "repo_url": "...",
        "learning_doc": "## 学习文档\n\n...",
        "setup_guide": "## 启动指南\n\n...",
        "repo_info": {...}
    },
    "error": null
}
```

### 4.3 WebSocket 消息

**进度更新：**
```json
{
    "type": "progress",
    "stage_key": "generating_learning_doc",
    "progress": 65,
    "message": "正在生成学习文档..."
}
```

**结果：**
```json
{
    "type": "result",
    "result": {...}
}
```

**错误：**
```json
{
    "type": "error",
    "error": "错误信息"
}
```

## 5. 技术栈

| 类别 | 技术 | 版本 |
|------|------|------|
| 前端框架 | Vue 3 | 3.4+ |
| 前端 UI | Element Plus | 2.5+ |
| 前端构建 | Vite | 5.0+ |
| 状态管理 | Pinia | 2.1+ |
| 后端框架 | FastAPI | 0.109+ |
| Agent 框架 | LangChain | 1.0+ |
| LLM | 智谱 GLM | glm-4 |
| 仓库分析 | PyGithub + GitPython | - |

## 6. 可复用模块

以下模块在新旧架构中均可复用：

| 模块 | 路径 | 说明 |
|------|------|------|
| agents/ | `agents/*.py` | LangChain Agent 定义 |
| tools/ | `tools/*.py` | GitHub API、文件操作工具 |
| core/ | `core/*.py` | 配置、验证、历史、收藏 |

---

*Last updated: 2026-03-20*