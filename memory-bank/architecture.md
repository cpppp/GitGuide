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
│                        Multi-Agent System (V3.0)                          │
├───────────────────────────────────────────────────────────────────────────┤
│                        Supervisor Agent                                    │
│              (Planner + Scheduler + Reviewer + Optimizer)                 │
└─────────────────────┬──────────────────────┬─────────────────────────────┘
                     │                      │
                     ▼                      ▼
┌────────────────────────┐      ┌──────────────────────────────┐
│    Analyzer Team       │      │      Generator Team          │
│   (仓库分析团队)        │      │     (文档生成团队)            │
│ - TypeAnalyzer         │      │ - QuickStartGenerator        │
│ - StructureAnalyzer    │      │ - OverviewGenerator          │
│ - DependencyAnalyzer   │      │ - ArchitectureGenerator      │
│ - CodePatternAnalyzer  │      │ - InstallGuideGenerator      │
└────────────────────────┘      └──────────────────────────────┘
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
├── agents/                     # Multi-Agent 系统 (V3.0)
│   ├── __init__.py
│   ├── workflow.py             # 工作流协调器
│   │
│   ├── supervisor/             # Supervisor Agent
│   │   ├── __init__.py
│   │   ├── planner.py          # 规划器：任务分解、优先级排序
│   │   ├── scheduler.py        # 调度器：并行任务调度
│   │   ├── reviewer.py         # 审核器：文档质量审核
│   │   └── optimizer.py        # 优化器：文档优化建议
│   │
│   ├── analyzers/              # Analyzer Team
│   │   ├── type_analyzer.py        # 项目类型识别
│   │   ├── structure_analyzer.py    # 目录结构分析
│   │   ├── dependency_analyzer.py   # 依赖关系分析
│   │   └── code_pattern_analyzer.py # 代码模式识别
│   │
│   └── generators/             # Generator Team
│       ├── __init__.py
│       ├── quick_start_generator.py    # 快速入门文档
│       ├── overview_generator.py        # 项目概览文档
│       ├── architecture_generator.py    # 架构设计文档
│       └── install_guide_generator.py   # 安装部署文档
│
├── tools/                      # 工具函数
│   ├── github_tools.py         # GitHub API 工具
│   ├── git_tools.py            # GitPython 工具
│   └── file_tools.py           # 文件读取工具
│
├── core/                       # 核心模块
│   ├── __init__.py
│   ├── config.py               # 配置管理
│   ├── utils.py                # 工具函数
│   ├── sop.py                  # SOP 标准化流程
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
│ quick_start         │       │     favorites       │
│ overview_doc        │       ├─────────────────────┤
│ architecture_doc    │       │ id (PK)             │
│ install_guide       │       │ repo_id (FK)        │
│ usage_tutorial      │       │ created_at          │
│ dev_guide           │       └─────────────────────┘
│ troubleshooting     │
│ analysis_result     │       ┌─────────────────────┐
│ quality_score       │       │  analysis_history   │
│ created_at          │       ├─────────────────────┤
│ updated_at          │◄──────│ id (PK)             │
└─────────────────────┘       │ repo_id (FK)        │
         │                    │ analyzed_at         │
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
| quick_start | TEXT | 快速入门文档 (V3.0) |
| overview_doc | TEXT | 项目概览文档 (V3.0) |
| architecture_doc | TEXT | 架构设计文档 (V3.0) |
| install_guide | TEXT | 安装部署文档 (V3.0) |
| usage_tutorial | TEXT | 使用教程文档 (V3.1) |
| dev_guide | TEXT | 开发指南文档 (V3.1) |
| troubleshooting | TEXT | 故障排查文档 (V3.1) |
| analysis_result | TEXT | 分析结果 JSON |
| quality_score | INTEGER | 文档质量评分 (V3.1) |
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
    "stage_key": "generating_learning_doc",
    "result": {
        "repo_url": "...",
        "learning_doc": "## 学习文档\n\n...",
        "setup_guide": "## 启动指南\n\n...",
        "quick_start": "## 快速入门\n\n...",
        "overview_doc": "## 项目概览\n\n...",
        "architecture_doc": "## 架构设计\n\n...",
        "install_guide": "## 安装部署\n\n...",
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

## 8. Multi-Agent 架构 (V3.0)

### 8.1 架构概览

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Supervisor Agent                               │
│                    (任务规划、进度协调、质量控制)                           │
│                                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │   Planner   │  │  Scheduler  │  │  Reviewer   │  │  Optimizer  │   │
│  │  (规划器)   │  │  (调度器)   │  │  (审核器)   │  │  (优化器)   │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐
│   Analyzer Team   │   │   Generator Team  │   │   Quality Team    │
│    (分析团队)      │   │    (生成团队)      │   │    (质量团队)      │
├───────────────────┤   ├───────────────────┤   ├───────────────────┤
│ TypeAnalyzer      │   │ QuickStartGen     │   │ DocReviewer       │
│ StructureAnalyzer │   │ OverviewGen       │   │ DocOptimizer      │
│ DependencyAnalyzer│   │ ArchitectureGen   │   │ QualityScorer     │
│ CodePatternAnalyzer│  │ InstallGuideGen   │   │                   │
│                   │   │ TutorialGen (V3.1)│   │                   │
│                   │   │ DevGuideGen (V3.1)│   │                   │
│                   │   │ TroubleshootGen   │   │                   │
└───────────────────┘   └───────────────────┘   └───────────────────┘
                                │
                                ▼
                    ┌───────────────────┐
                    │   Shared Context  │
                    │    (共享上下文)    │
                    └───────────────────┘
```

### 8.2 SOP 标准化流程

```
┌──────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────┐   ┌────────────┐   ┌─────────────┐
│ Planning │──►│ Analysis     │──►│ Generation   │──►│ Review   │──►│ Optimization│──►│ Finalization│
│  (规划)   │   │ (并行分析)    │   │ (并行生成)    │   │ (审核)   │   │ (迭代优化)  │   │ (输出)      │
└──────────┘   └──────────────┘   └──────────────┘   └──────────┘   └────────────┘   └─────────────┘
     │               │                  │                │                │
     ▼               ▼                  ▼                ▼                ▼
  任务分解        多维度分析         文档生成          质量评分         多轮优化
  优先级排序      并行执行           并行执行          问题识别         达标输出
```

### 8.3 Supervisor Agent

```
agents/supervisor/
├── __init__.py
├── planner.py          # 规划器
│   ├── analyze_repo_type()      # 分析仓库类型
│   ├── decompose_tasks()        # 任务分解
│   ├── prioritize_tasks()       # 优先级排序
│   └── generate_analysis_outline()  # 生成分析大纲
│
├── scheduler.py        # 调度器
│   ├── schedule_parallel()      # 并行调度
│   ├── manage_dependencies()    # 管理任务依赖
│   ├── monitor_progress()       # 监控执行进度
│   └── handle_failures()        # 处理失败任务
│
├── reviewer.py         # 审核器
│   ├── check_completeness()     # 检查文档完整性
│   ├── validate_accuracy()      # 验证技术准确性
│   ├── evaluate_readability()   # 评估可读性
│   └── generate_feedback()      # 生成审核反馈
│
└── optimizer.py        # 优化器
    ├── analyze_feedback()       # 分析审核反馈
    ├── generate_suggestions()   # 生成优化建议
    ├── apply_optimizations()    # 应用优化
    └── iterate_improve()        # 迭代改进（最多3轮）
```

### 8.4 Analyzer Team

```
agents/analyzers/
├── type_analyzer.py            # 项目类型识别
│   ├── detect_language()       # 检测编程语言
│   ├── detect_framework()      # 检测框架
│   ├── detect_build_system()   # 检测构建系统
│   └── classify_project_type() # 分类项目类型
│
├── structure_analyzer.py       # 目录结构分析
│   ├── analyze_directory_tree()    # 分析目录树
│   ├── identify_modules()          # 识别模块
│   ├── find_entry_points()         # 查找入口点
│   └── extract_key_files()         # 提取关键文件
│
├── dependency_analyzer.py      # 依赖关系分析
│   ├── parse_dependencies()    # 解析依赖
│   ├── check_compatibility()   # 检查版本兼容性
│   ├── analyze_dependency_tree()   # 分析依赖树
│   └── identify_core_deps()    # 识别核心依赖
│
└── code_pattern_analyzer.py    # 代码模式识别
    ├── detect_architecture_style() # 检测架构风格
    ├── identify_patterns()         # 识别设计模式
    ├── analyze_code_structure()    # 分析代码结构
    └── extract_conventions()       # 提取代码规范
```

### 8.5 Generator Team

```
agents/generators/
├── __init__.py
├── quick_start_generator.py    # 快速入门文档生成器
│   ├── generate_one_liner()    # 生成一句话概括
│   ├── generate_concepts()     # 生成核心概念图解
│   └── generate_minimal_run()  # 生成最小化运行命令
│
├── overview_generator.py       # 项目概览文档生成器
│   ├── generate_background()   # 生成项目背景
│   ├── generate_features()     # 生成功能列表
│   ├── generate_tech_stack()   # 生成技术选型
│   └── generate_use_cases()    # 生成适用场景
│
├── architecture_generator.py   # 架构设计文档生成器
│   ├── generate_architecture_diagram()  # 生成架构图
│   ├── generate_module_description()    # 生成模块说明
│   ├── generate_data_flow()             # 生成数据流
│   └── generate_design_decisions()      # 生成设计决策
│
└── install_guide_generator.py  # 安装部署文档生成器
    ├── generate_requirements()     # 生成环境要求
    ├── generate_install_steps()    # 生成安装步骤
    ├── generate_configuration()    # 生成配置说明
    └── generate_troubleshooting()  # 生成常见问题
```

### 8.6 工作流协调器

```
agents/workflow.py
├── SOPWorkflow                 # SOP 工作流类
│   ├── __init__()              # 初始化工作流
│   ├── run()                   # 运行完整工作流
│   ├── run_planning_stage()    # 运行规划阶段
│   ├── run_analysis_stage()    # 运行分析阶段（并行）
│   ├── run_generation_stage()  # 运行生成阶段（并行）
│   ├── run_review_stage()      # 运行审核阶段
│   └── run_optimization_stage() # 运行优化阶段
│
├── SharedContext               # 共享上下文类
│   ├── set()                   # 设置上下文数据
│   ├── get()                   # 获取上下文数据
│   ├── update()                # 更新上下文数据
│   └── clear()                 # 清除上下文数据
│
└── ParallelExecutor            # 并行执行器
    ├── execute_parallel()      # 并行执行任务
    ├── wait_all()              # 等待所有任务完成
    └── handle_timeout()        # 处理超时
```

### 8.7 Agent 职责说明

| Agent 类型 | 组件 | 职责 | 版本 |
|:---|:---|:---|:---|
| **Supervisor Agent** | Planner | 任务分解、优先级排序、生成分析大纲 | V3.0 |
| | Scheduler | 并行调度、任务依赖管理、进度监控 | V3.0 |
| | Reviewer | 文档完整性检查、技术准确性验证、质量评分 | V3.0 |
| | Optimizer | 根据反馈优化、迭代改进（最多3轮） | V3.0 |
| **Analyzer Team** | TypeAnalyzer | 项目类型识别、语言/框架/构建系统检测 | V3.0 |
| | StructureAnalyzer | 目录结构分析、模块识别、入口点提取 | V3.0 |
| | DependencyAnalyzer | 依赖关系分析、版本兼容性检查 | V3.0 |
| | CodePatternAnalyzer | 代码模式识别、架构风格分析 | V3.0 |
| **Generator Team** | QuickStartGen | 快速入门文档生成 | V3.0 |
| | OverviewGen | 项目概览文档生成 | V3.0 |
| | ArchitectureGen | 架构设计文档生成 | V3.0 |
| | InstallGuideGen | 安装部署文档生成 | V3.0 |
| | TutorialGen | 使用教程文档生成 | V3.1 |
| | DevGuideGen | 开发指南文档生成 | V3.1 |
| | TroubleshootGen | 故障排查文档生成 | V3.1 |
| **Quality Team** | DocReviewer | 文档质量审核 | V3.1 |
| | DocOptimizer | 文档优化建议 | V3.1 |
| | QualityScorer | 质量评分计算 | V3.1 |

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

## 10. 核心模块

```
core/
├── __init__.py
├── config.py               # 配置管理
│   - get_settings()
│   - load_env()
│
├── sop.py                  # SOP 标准化流程配置
│   - SOP_STAGES            # 流程阶段定义
│   - STAGE_DEPENDENCIES    # 阶段依赖关系
│   - TIMEOUT_CONFIG        # 超时配置
│   - RETRY_CONFIG          # 重试配置
│
├── utils.py                # 工具函数
│   - format_timestamp()
│   - truncate_text()
│   - safe_json_loads()
│
├── favorites.py            # 收藏仓库管理
│   - add_favorite()
│   - remove_favorite()
│   - get_favorites()
│
├── history.py              # 历史记录管理
│   - add_history()
│   - get_history()
│   - clear_history()
│
└── validators.py           # URL 验证和错误处理
    - validate_github_url()
    - validate_repo_exists()
    - handle_api_error()
```

## 11. 启动服务

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

## 12. 可复用模块

以下模块在新旧架构中均可复用：

| 模块 | 路径 | 说明 |
|------|------|------|
| agents/ | `agents/*.py` | Multi-Agent 系统 |
| tools/ | `tools/*.py` | GitHub API、文件操作工具 |
| core/ | `core/*.py` | 配置、验证、历史、收藏、SOP |

---

*Last updated: 2026-03-21*
