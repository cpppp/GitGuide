# GitGuide 项目架构设计

## 1. 整体架构

GitGuide 采用 **Vue 3 + FastAPI + LangChain** 的前后端分离架构，通过 WebSocket 实现实时进度推送，通过协调多个专业化 Agent 来完成 GitHub 仓库的分析、文档生成和智能问答功能。

```
┌───────────────────────────────────────────────────────────────────────────┐
│                           Vue 3 前端 (Element Plus)                       │
├─────────────────────┬──────────────────────┬──────────────────────────────┤
│  🏠 Home 页面       │ 📚 Documentation 页面 │    💬 Chat 页面              │
│  (URL 输入+进度)    │  (文档展示+导出+图谱)  │    (AI 问答)                 │
├─────────────────────┴──────────────────────┴──────────────────────────────┤
│  📦 Repositories 页面 (已分析仓库列表)                                      │
└───────────────────────────────────────────────────────────────────────────┘
                              │
                    HTTP / WebSocket
                              ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                          FastAPI 后端                                     │
├───────────────────────────────────────────────────────────────────────────┤
│  API Routes:                                                              │
│  - /api/analyze (分析任务)                                                 │
│  - /api/chat (问答服务)                                                    │
│  - /api/repositories (仓库管理)                                            │
│  - /api/history (历史记录)                                                 │
│  - /api/favorites (收藏管理)                                               │
│  - /api/health (健康检查)                                                  │
│  WebSocket: /ws/analyze/{job_id} (实时进度推送)                            │
└───────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                          Orchestrator Agent                              │
│                   (工作流协调、任务分发)                                    │
└─────────────────────┬──────────────────────┬─────────────────────────────┘
                     │                      │
                     ▼                      ▼
┌────────────────────────┐      ┌──────────────────────────────┐
│   Analyzer Agent       │      │      DocGen Agent            │
│  (仓库分析专家)         │      │   (文档生成专家)              │
│ - 识别项目类型         │      │ - 生成学习文档                │
│ - 分析目录结构         │      │ - 生成启动指南                │
│ - 解析依赖关系         │      │ - 提取关键信息                │
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

## 2. 项目结构

```
GitGuide/
├── app.py                      # Streamlit 主入口（旧版兼容）
├── pages/                      # Streamlit 页面（旧版兼容）
│   ├── 1_🏠_Home.py
│   ├── 2_📚_Documentation.py
│   └── 3_💬_Chat.py
│
├── backend/                    # FastAPI 后端
│   ├── main.py                 # FastAPI 入口
│   ├── api/                    # API 路由
│   │   ├── analyze.py          # 分析 API + WebSocket
│   │   ├── chat.py             # 问答 API
│   │   ├── data.py             # 数据 API
│   │   ├── health.py           # 健康检查
│   │   └── repositories.py     # 仓库管理 API
│   ├── models/
│   │   ├── schemas.py          # Pydantic 数据模型
│   │   └── database.py         # SQLAlchemy ORM 模型
│   ├── database/
│   │   ├── config.py           # 数据库连接配置
│   │   └── crud.py             # CRUD 操作
│   ├── services/
│   │   └── code_graph.py       # 代码图谱服务
│   ├── websocket/
│   │   └── manager.py          # WebSocket 管理器
│   ├── tasks.py                # RQ 任务队列
│   └── worker.py               # RQ Worker
│
├── frontend/                   # Vue 3 前端
│   ├── src/
│   │   ├── api/                # API 调用
│   │   │   ├── analyze.js
│   │   │   └── chat.js
│   │   ├── components/         # 公共组件
│   │   │   ├── CodeAtlas.vue   # 代码图谱组件
│   │   │   └── CodeGraph.vue   # 代码结构可视化
│   │   ├── views/              # 页面组件
│   │   │   ├── Home.vue
│   │   │   ├── Documentation.vue
│   │   │   ├── Chat.vue
│   │   │   └── Repositories.vue
│   │   ├── stores/             # Pinia 状态管理
│   │   │   ├── analysis.js     # 分析状态
│   │   │   └── settings.js     # 设置状态（主题/语言）
│   │   ├── i18n/               # 国际化
│   │   │   └── index.js
│   │   ├── utils/              # 工具函数
│   │   │   └── export.js       # 导出工具
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
├── scripts/                    # 脚本工具
│   ├── migrate_favorites.py    # 收藏迁移脚本
│   └── test_favorites.py       # 测试脚本
│
├── memory-bank/                # 项目文档
│   ├── architecture.md         # 架构设计文档
│   ├── product-design-document.md
│   ├── tech-stack.md           # 技术栈文档
│   ├── implementation-plan.md  # 实施计划
│   └── process.md              # 进度跟踪
│
├── requirements.txt            # Python 依赖
└── .env.example                # 环境变量示例
```

## 3. 数据库架构

### 3.1 ER 图

```
┌─────────────────────┐       ┌─────────────────────┐
│    repositories     │       │   chat_messages     │
├─────────────────────┤       ├─────────────────────┤
│ id (PK)             │◄──────│ id (PK)             │
│ url (UNIQUE)        │       │ repo_id (FK)        │
│ name                │       │ role                │
│ description         │       │ content             │
│ language            │       │ created_at          │
│ stars               │       └─────────────────────┘
│ learning_doc        │
│ setup_guide         │       ┌─────────────────────┐
│ analysis_result     │       │     favorites       │
│ created_at          │       ├─────────────────────┤
│ updated_at          │◄──────│ id (PK)             │
└─────────────────────┘       │ repo_id (FK)        │
         │                    │ created_at          │
         │                    └─────────────────────┘
         │
         │                    ┌─────────────────────┐
         └───────────────────►│  analysis_history   │
                              ├─────────────────────┤
                              │ id (PK)             │
                              │ repo_id (FK)        │
                              │ analyzed_at         │
                              └─────────────────────┘
```

### 3.2 表结构

**repositories 表：**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| url | VARCHAR(500) | 仓库 URL（唯一） |
| name | VARCHAR(200) | 仓库名称 |
| description | TEXT | 仓库描述 |
| language | VARCHAR(50) | 主要语言 |
| stars | INTEGER | Star 数 |
| learning_doc | TEXT | 学习文档 |
| setup_guide | TEXT | 启动指南 |
| analysis_result | TEXT | 分析结果 JSON |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

**chat_messages 表：**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| repo_id | INTEGER | 外键（repositories.id） |
| role | VARCHAR(20) | 角色（user/assistant） |
| content | TEXT | 消息内容 |
| created_at | DATETIME | 创建时间 |

**favorites 表：**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| repo_id | INTEGER | 外键（repositories.id） |
| created_at | DATETIME | 收藏时间 |

**analysis_history 表：**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| repo_id | INTEGER | 外键（repositories.id） |
| analyzed_at | DATETIME | 分析时间 |

## 4. API 端点

### 4.1 分析 API

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/api/analyze` | 启动分析，返回 job_id |
| GET | `/api/analyze/{job_id}/status` | 查询任务状态 |
| POST | `/api/analyze/{job_id}/cancel` | 取消分析 |
| WS | `/ws/analyze/{job_id}` | WebSocket 实时进度 |
| GET | `/api/analyze/{job_id}/code-graph` | 获取代码图谱 |

### 4.2 问答 API

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | `/api/chat` | 发送问答请求 |

### 4.3 仓库管理 API

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/repositories` | 获取所有已分析仓库 |
| GET | `/api/repositories/{repo_url}` | 获取指定仓库详情 |
| DELETE | `/api/repositories/{repo_url}` | 删除指定仓库 |

### 4.4 数据 API

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/history` | 获取历史记录 |
| POST | `/api/history/clear` | 清除历史记录 |
| GET | `/api/favorites` | 获取收藏列表 |
| POST | `/api/favorites` | 添加收藏 |
| DELETE | `/api/favorites` | 移除收藏 |

### 4.5 健康检查

| 方法 | 路径 | 功能 |
|------|------|------|
| GET | `/api/health` | 健康检查 |
| GET | `/` | 根路径 |

## 5. 数据结构

### 5.1 分析请求

```python
{
    "repo_url": "https://github.com/user/repo",
    "mode": "fast"  # 或 "detailed"
}
```

### 5.2 任务状态

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
    "error": null,
    "cancelled": false
}
```

### 5.3 WebSocket 消息

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

**取消：**
```json
{
    "type": "cancelled",
    "message": "用户取消了分析"
}
```

## 6. 前端架构

### 6.1 状态管理

使用 Pinia 进行状态管理：

```
frontend/src/stores/
├── analysis.js     # 分析状态管理
│   - repoUrl: string
│   - isAnalyzing: boolean
│   - progress: number
│   - progressMessage: string
│   - stageKey: string
│   - result: object
│   - error: string
│   - isCompleted: boolean
│   - isFailed: boolean
│
└── settings.js     # 设置状态管理
    - theme: 'light' | 'dark'
    - language: 'zh' | 'en'
```

### 6.2 主题系统

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

### 6.3 导出功能

导出工具支持多种格式：

```
frontend/src/utils/export.js
├── exportToMarkdown()    # 导出 Markdown
├── exportToHTML()        # 导出 HTML
├── exportToPDF()         # 导出 PDF
└── downloadFile()        # 通用下载函数
```

### 6.4 代码图谱

代码图谱组件功能：

```
frontend/src/components/
├── CodeAtlas.vue    # 代码图谱组件
│   - 目录结构可视化
│   - 文件统计表格
│   - 依赖关系展示
│
└── CodeGraph.vue    # 代码结构可视化
    - 树形结构展示
    - 文件类型统计
```

### 6.5 多语言支持

国际化配置：

```
frontend/src/i18n/index.js
├── translations: { zh, en }
└── t(key, lang)  # 翻译函数
```

## 7. 后端架构

### 7.1 API 层

```
backend/api/
├── analyze.py       # 分析 API + WebSocket
│   - POST /analyze
│   - GET /analyze/{job_id}/status
│   - POST /analyze/{job_id}/cancel
│   - WS /ws/analyze/{job_id}
│   - GET /analyze/{job_id}/code-graph
│   - GET /history
│   - POST /history/clear
│   - GET /favorites
│   - POST /favorites
│   - DELETE /favorites
│
├── chat.py          # 问答 API
│   - POST /chat
│
├── repositories.py  # 仓库管理 API
│   - GET /repositories
│   - GET /repositories/{repo_url}
│   - DELETE /repositories/{repo_url}
│
├── data.py          # 数据 API
│   - GET /data/favorites
│   - POST /data/favorites
│   - DELETE /data/favorites
│
└── health.py        # 健康检查
    - GET /health
    - GET /
```

### 7.2 数据层

```
backend/database/
├── config.py        # 数据库连接配置
│   - init_db()
│   - get_db()
│   - SessionLocal
│
└── crud.py          # CRUD 操作
    ├── RepositoryCRUD
    │   - get_by_url()
    │   - get_by_id()
    │   - create()
    │   - update()
    │   - get_all()
    │   - delete()
    │
    ├── ChatMessageCRUD
    │   - create()
    │   - get_by_repo()
    │   - delete_by_repo()
    │   - delete_by_id()
    │
    ├── FavoriteCRUD
    │   - add()
    │   - add_by_url()
    │   - remove()
    │   - remove_by_url()
    │   - get_all()
    │   - get_all_with_repo()
    │   - is_favorite()
    │   - is_favorite_by_url()
    │
    └── AnalysisHistoryCRUD
        - create()
        - get_by_repo()
```

### 7.3 服务层

```
backend/services/
└── code_graph.py    # 代码图谱服务
    ├── analyze_structure()
    ├── _build_tree()
    ├── _get_file_stats()
    ├── _analyze_dependencies()
    ├── _extract_python_imports()
    └── _extract_js_imports()
```

### 7.4 WebSocket 管理

```
backend/websocket/manager.py
├── WebSocketManager
│   - connect()
│   - disconnect()
│   - send_progress()
│   - send_result()
│   - send_error()
│   - send_cancelled()
│   - cleanup()
│
└── TaskStore
    - create_task()
    - get_task()
    - update_progress()
    - set_result()
    - set_error()
    - set_cancel_flag()
    - set_cancelled()
    - is_cancelled()
```

## 8. Agent 架构

### 8.1 Orchestrator Agent

工作流协调器，负责协调各 Agent 的工作流程：

```
agents/orchestrator.py
├── run()                    # 基础工作流
├── run_with_progress()      # 带进度回调的详细分析
├── run_simple()             # 简化版本
├── run_fast()               # 快速版本
├── set_cancelled_checker()  # 设置取消检查器
└── check_cancelled()        # 检查是否取消
```

### 8.2 Analyzer Agent

仓库分析专家：

```
agents/analyzer.py
└── run_analyzer()           # 分析仓库结构
```

### 8.3 DocGen Agent

文档生成专家：

```
agents/doc_generator.py
├── run_docgen()             # 生成文档
└── run_docgen_fast()        # 快速生成文档
```

### 8.4 Chat Agent

问答专家：

```
agents/chat.py
└── run_chat()               # 处理用户问答
```

## 9. 工具模块

```
tools/
├── github_tools.py          # GitHub API 工具
│   - get_repo_info()
│   - get_readme()
│   - get_file_content()
│   - get_directory_structure()
│
├── git_tools.py             # GitPython 工具
│   - clone_repo()
│   - get_commit_history()
│   - get_branches()
│
└── file_tools.py            # 文件读取工具
    - read_file()
    - read_directory()
    - get_file_extension()
```

## 10. 启动服务

```bash
# 1. 安装后端依赖
pip install -r requirements.txt

# 2. 安装前端依赖
cd frontend && npm install

# 3. 启动后端
cd backend && uvicorn main:app --reload --port 8000

# 4. 启动前端
cd frontend && npm run dev
```

## 11. 可复用模块

以下模块在新旧架构中均可复用：

| 模块 | 路径 | 说明 |
|------|------|------|
| agents/ | `agents/*.py` | LangChain Agent 定义 |
| tools/ | `tools/*.py` | GitHub API、文件操作工具 |
| core/ | `core/*.py` | 配置、验证、历史、收藏 |

---

*Last updated: 2026-03-20*
