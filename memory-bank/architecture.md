# GitGuide 项目架构设计

> **文档版本**：v3.1.3\
> **最后更新**：2026-03-22\
> **当前版本**：V3.1（文档质量提升已完成，含Bug修复）

***

## 1. 整体架构

```
┌───────────────────────────────────────────────────────────────────────────┐
│                           Vue 3 前端 (Element Plus)                       │
├─────────────────────┬──────────────────────┬──────────────────────────────┤
│  🏠 Home            │ 📚 Documentation     │ 💬 Chat                      │
│  (URL输入+进度)      │  (7种文档+素材+导出)  │  (AI问答)                     │
├─────────────────────┴──────────────────────┴──────────────────────────────┤
│  📦 Repositories (已分析仓库列表 + 收藏)                                    │
└───────────────────────────────────────────────────────────────────────────┘
                              │ HTTP / WebSocket
                              ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                          FastAPI 后端                                     │
│  API: /analyze, /chat, /repositories, /favorites, /health                 │
│  WebSocket: /ws/analyze/{job_id}                                          │
└───────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                        Multi-Agent System                                  │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                      Orchestrator (入口层)                           │ │
│  │         克隆仓库 → 获取信息 → 调用 Workflow → 清理目录                │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                    │                                      │
│                                    ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                       Workflow (核心编排层)                          │ │
│  │                                                                     │ │
│  │  • WorkflowState 状态管理                                           │ │
│  │  • 任务规划（内置）                                                  │ │
│  │  • 并行调度（ThreadPoolExecutor）                                   │ │
│  │  • 质量审核（内置 _basic_review）                                   │ │
│  │  • 协调 Analyzer Team 和 Generator Team                            │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                    │                                      │
│          ┌─────────────────────────┼─────────────────────────┐           │
│          ▼                         ▼                         ▼           │
│  ┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐  │
│  │   Analyzer Team   │   │   Generator Team  │   │     Chat Agent    │  │
│  │    (并行执行)      │   │    (并行执行)      │   │    (V3.2新增)    │  │
│  ├───────────────────┤   ├───────────────────┤   ├───────────────────┤  │
│  │ TypeAnalyzer      │   │ QuickStartGen     │   │ KnowledgeBuilder  │  │
│  │ StructureAnalyzer │   │ OverviewGen       │   │ RAGRetriever      │  │
│  │ DependencyAnalyzer│   │ ArchitectureGen   │   │ ConversationMgr   │  │
│  │ CodePatternAnalyzer│  │ InstallGuideGen   │   │                   │  │
│  │                   │   │ TutorialGen       │   │                   │  │
│  │                   │   │ DevGuideGen       │   │                   │  │
│  │                   │   │ TroubleshootGen   │   │                   │  │
│  └───────────────────┘   └───────────────────┘   └───────────────────┘  │
│                                                                           │
│  总计：11 个 Agent（Analyzer 4 + Generator 7 + Chat 3）                   │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

***

## 2. 项目结构

```
GitGuide/
├── backend/                    # FastAPI 后端
│   ├── main.py                 # 入口
│   ├── api/                    # API 路由
│   ├── models/                 # Pydantic + SQLAlchemy
│   ├── database/               # 数据库配置和 CRUD
│   ├── services/               # 服务层
│   │   └── code_graph.py       # 代码分析服务（含架构图生成）
│   └── websocket/              # WebSocket 管理
│
├── frontend/                   # Vue 3 前端
│   ├── src/
│   │   ├── api/                # API 调用
│   │   ├── components/         # 组件
│   │   │   ├── CodeAtlas.vue   # 代码图谱（目录树+统计+依赖）
│   │   │   ├── CodeGraph.vue   # 代码图谱组件
│   │   │   ├── ArchitectureDiagram.vue  # Mermaid 架构图（V3.1新增）
│   │   │   └── ExampleCode.vue # 示例代码展示（V3.1新增）
│   │   ├── views/              # 页面
│   │   ├── stores/             # Pinia 状态
│   │   ├── utils/              # 工具函数（导出等）
│   │   └── i18n/               # 国际化
│   └── package.json
│
├── agents/                     # Multi-Agent 系统
│   ├── __init__.py
│   ├── orchestrator.py         # 入口编排器
│   ├── workflow.py             # 核心工作流（状态管理+并行调度+质量审核）
│   ├── chat.py                 # Chat Agent（V3.2）
│   │
│   ├── analyzers/              # Analyzer Team（分析团队）
│   │   ├── __init__.py
│   │   ├── type_analyzer.py
│   │   ├── structure_analyzer.py
│   │   ├── dependency_analyzer.py
│   │   └── code_pattern_analyzer.py
│   │
│   └── generators/             # Generator Team（生成团队）
│       ├── __init__.py
│       ├── quick_start_generator.py      (V3.0)
│       ├── overview_generator.py         (V3.0)
│       ├── architecture_generator.py     (V3.0)
│       ├── install_guide_generator.py    (V3.0)
│       ├── tutorial_generator.py         (V3.1新增)
│       ├── dev_guide_generator.py        (V3.1新增)
│       └── troubleshoot_generator.py     (V3.1新增)
│
├── tools/                      # 工具模块
│   ├── github_tools.py         # GitHub API
│   ├── git_tools.py            # GitPython
│   └── file_tools.py           # 文件操作
│
├── core/                       # 核心模块
│   ├── config.py               # 配置管理
│   ├── sop.py                  # SOP 流程定义
│   └── validators.py           # 验证器
│
└── memory-bank/                # 项目文档
```

***

## 3. 数据库架构

### 3.1 ER 图

```
┌─────────────────────┐       ┌─────────────────────┐
│    repositories     │       │   chat_messages     │
├─────────────────────┤       ├─────────────────────┤
│ id (PK)             │◄──────│ id (PK)             │
│ url (UNIQUE)        │       │ repo_id (FK)        │
│ name, description   │       │ role, content       │
│ language, stars     │       │ created_at          │
│ quick_start         │       └─────────────────────┘
│ overview_doc        │
│ architecture_doc    │       ┌─────────────────────┐
│ install_guide       │       │     favorites       │
│ usage_tutorial      │       ├─────────────────────┤
│ dev_guide           │       │ id (PK)             │
│ troubleshooting     │       │ repo_id (FK)        │
│ analysis_result     │       │ created_at          │
│ quality_score       │       └─────────────────────┘
│ created_at, updated_at│
└─────────────────────┘
```

### 3.2 repositories 表字段

| 字段                | 类型              | 说明         | 版本   |
| :---------------- | :-------------- | :--------- | :--- |
| id                | INTEGER         | 主键         | V1.0 |
| url               | VARCHAR(500)    | 仓库 URL（唯一） | V1.0 |
| name, description | VARCHAR/TEXT    | 基本信息       | V1.0 |
| language, stars   | VARCHAR/INTEGER | 语言和 Star   | V1.0 |
| quick\_start      | TEXT            | 快速入门文档     | V3.0 |
| overview\_doc     | TEXT            | 项目概览文档     | V3.0 |
| architecture\_doc | TEXT            | 架构设计文档     | V3.0 |
| install\_guide    | TEXT            | 安装部署文档     | V3.0 |
| usage\_tutorial   | TEXT            | 使用教程文档     | V3.1 |
| dev\_guide        | TEXT            | 开发指南文档     | V3.1 |
| troubleshooting   | TEXT            | 故障排查文档     | V3.1 |
| analysis\_result  | TEXT            | 分析结果 JSON  | V2.2 |
| quality\_score    | INTEGER         | 文档质量评分     | V3.1 |

***

## 4. API 端点

| 方法              | 路径                             | 功能    |
| :-------------- | :----------------------------- | :---- |
| POST            | `/api/analyze`                 | 启动分析  |
| GET             | `/api/analyze/{job_id}/status` | 查询状态  |
| WS              | `/ws/analyze/{job_id}`         | 实时进度  |
| POST            | `/api/chat`                    | AI 问答 |
| GET/DELETE      | `/api/repositories`            | 仓库管理  |
| GET/POST/DELETE | `/api/favorites`               | 收藏管理  |
| GET             | `/api/health`                  | 健康检查  |

***

## 5. Multi-Agent 架构

### 5.1 架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Orchestrator (入口层)                           │
│                                                                             │
│   职责：克隆仓库 → 获取仓库信息 → 调用 Workflow → 清理临时目录 → 进度回调      │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Workflow (核心编排层)                           │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                        WorkflowState                                 │  │
│   │   • repo_url, repo_path                                             │  │
│   │   • type_result, structure_result, dependency_result, code_pattern  │  │
│   │   • 7种文档结果                                                      │  │
│   │   • quality_score, errors, progress                                 │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│   工作流程：                                                                 │
│   Stage 1: 初始化 ─── 创建状态，设置仓库路径                                  │
│   Stage 2: 分析 ─── 并行执行 4 个 Analyzer（ThreadPoolExecutor）             │
│   Stage 3: 生成 ─── 并行执行 7 个 Generator（ThreadPoolExecutor）            │
│   Stage 4: 审核 ─── 内置质量检查（_basic_review）                            │
│   Stage 5: 输出 ─── 构建最终结果                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          ▼                           ▼                           ▼
┌───────────────────┐       ┌───────────────────┐       ┌───────────────────┐
│   Analyzer Team   │       │   Generator Team  │       │     Chat Agent    │
│    (并行执行)      │       │    (并行执行)      │       │    (V3.2新增)    │
├───────────────────┤       ├───────────────────┤       ├───────────────────┤
│ TypeAnalyzer      │       │ QuickStartGen     │       │ KnowledgeBuilder  │
│ StructureAnalyzer │       │ OverviewGen       │       │ RAGRetriever      │
│ DependencyAnalyzer│       │ ArchitectureGen   │       │ ConversationMgr   │
│ CodePatternAnalyzer│      │ InstallGuideGen   │       │                   │
│                   │       │ TutorialGen       │       │                   │
│                   │       │ DevGuideGen       │       │                   │
│                   │       │ TroubleshootGen   │       │                   │
└───────────────────┘       └───────────────────┘       └───────────────────┘
```

### 5.2 Agent 职责

| Agent 类型       | 组件                  | 职责                  | 版本   |
| :------------- | :------------------ | :------------------ | :--- |
| **编排层**        | Orchestrator        | 入口管理、仓库克隆、进度回调、资源清理 | V3.0 |
| <br />         | Workflow            | 状态管理、并行调度、质量审核、结果整合 | V3.0 |
| **Analyzer**   | TypeAnalyzer        | 项目类型识别、语言/框架/构建系统检测 | V3.0 |
| <br />         | StructureAnalyzer   | 目录结构分析、模块识别、入口点提取   | V3.0 |
| <br />         | DependencyAnalyzer  | 依赖关系分析、版本兼容性检查      | V3.0 |
| <br />         | CodePatternAnalyzer | 代码模式识别、架构风格分析       | V3.0 |
| **Generator**  | QuickStartGen       | 快速入门文档              | V3.0 |
| <br />         | OverviewGen         | 项目概览文档              | V3.0 |
| <br />         | ArchitectureGen     | 架构设计文档              | V3.0 |
| <br />         | InstallGuideGen     | 安装部署文档              | V3.0 |
| <br />         | TutorialGen         | 使用教程文档              | V3.1 |
| <br />         | DevGuideGen         | 开发指南文档              | V3.1 |
| <br />         | TroubleshootGen     | 故障排查文档              | V3.1 |
| **Chat Agent** | KnowledgeBuilder    | 构建仓库知识库             | V3.2 |
| <br />         | RAGRetriever        | 检索增强生成              | V3.2 |
| <br />         | ConversationManager | 多轮对话管理              | V3.2 |

### 5.3 工作流程

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              完整工作流                                       │
└──────────────────────────────────────────────────────────────────────────────┘

用户请求 (GitHub URL)
        │
        ▼
┌─────────────────┐
│   Orchestrator  │
│                 │
│ 1. 克隆仓库      │
│ 2. 获取仓库信息  │
│ 3. 调用 Workflow │
│ 4. 清理临时目录  │
└─────────────────┘
        │
        ▼
┌─────────────────┐
│    Workflow     │
│                 │
│ Stage 1: 初始化  │ ─── 创建 WorkflowState
└─────────────────┘
        │
        ▼
┌─────────────────┐
│ Stage 2: 分析    │ ─── 并行执行（ThreadPoolExecutor）
│                 │
│ ┌─────────────┐ │
│ │TypeAnalyzer │ │
│ │Structure    │ │── 并行
│ │Dependency   │ │
│ │CodePattern  │ │
│ └─────────────┘ │
└─────────────────┘
        │
        ▼
┌─────────────────┐
│ Stage 3: 生成    │ ─── 并行执行（ThreadPoolExecutor）
│                 │
│ ┌─────────────┐ │
│ │QuickStart   │ │
│ │Overview     │ │
│ │Architecture │ │
│ │InstallGuide │ │── 并行
│ │Tutorial     │ │
│ │DevGuide     │ │
│ │Troubleshoot │ │
│ └─────────────┘ │
└─────────────────┘
        │
        ▼
┌─────────────────┐
│ Stage 4: 审核    │ ─── 内置质量检查
│                 │
│ _basic_review() │
│ • 完整性检查     │
│ • 准确性评估     │
│ • 可读性评估     │
│ • 实用性评估     │
│                 │
│ 输出：质量评分   │
└─────────────────┘
        │
        ▼
┌─────────────────┐
│ Stage 5: 输出    │
│                 │
│ • 整理文档       │
│ • 计算总评分     │
│ • 生成元数据     │
└─────────────────┘
        │
        ▼
    最终输出
    • 7种文档
    • 质量评分
    • 执行时间
```

***

## 6. Chat Agent 两步迭代

### 6.1 第一阶段：基础问答（无 RAG）

```
用户问题 ──► 问题分类 ──► 上下文构建 ──► LLM 回答
                    │
                    ▼
         上下文来源：GitHub工具 + 已生成文档 + 分析结果
```

**特点**：快速实现，复用现有工具，无需额外依赖

### 6.2 第二阶段：RAG 增强（方案 C）

```
知识库构建：分析结果 + 仓库文件 ──► HuggingFaceEmbeddings ──► Chroma
问答流程：用户问题 ──► 向量检索 ──► 上下文构建 ──► LLM 回答
```

**特点**：精准检索，零 API 成本，多语言支持

***

## 7. 技术栈

| 层级    | 技术                             | 用途              |
| :---- | :----------------------------- | :-------------- |
| 前端    | Vue 3 + Element Plus + Vite    | 用户界面            |
| 后端    | FastAPI + WebSocket            | REST API + 实时通信 |
| Agent | LangChain + asyncio            | Multi-Agent 系统  |
| LLM   | OpenAI GPT-4 / 智谱 GLM-4        | 智能分析生成          |
| 向量库   | Chroma + HuggingFaceEmbeddings | RAG 知识库         |
| 数据库   | SQLite / PostgreSQL            | 数据持久化           |
| ORM   | SQLAlchemy                     | 数据库操作           |

***

## 8. 启动服务

```bash
# 后端
pip install -r requirements.txt
cd backend && uvicorn main:app --reload --port 8000

# 前端
cd frontend && npm install && npm run dev
```

***

## 9. 架构演进历史

| 版本   | 架构变化           | 说明                                                    |
| :--- | :------------- | :---------------------------------------------------- |
| V3.0 | Multi-Agent 架构 | 引入 Orchestrator + Workflow + Analyzer/Generator Teams |
| V3.0.1 | 架构简化           | 移除 Supervisor Team，职责合并到 Workflow，保持简洁高效              |
| V3.0.3 | Bug修复           | 修复文档生成并行执行问题，使用 functools.partial |
| V3.1 | 文档类型扩展         | 新增 3 种文档类型，辅助素材生成，前端7标签页支持 |
| V3.1.1 | 生成器导出修复       | 修复 agents/generators/__init__.py 导出问题 |
| V3.1.2 | LLM文档生成         | 添加 BaseGenerator 基类，所有生成器支持 LLM，修复代码图谱数据存储 |
| V3.1.3 | 前端UI优化+英文文档   | 优化导航栏样式，新增已分析仓库单独删除按钮，所有文档生成器改为英文输出 |

***

*Last updated: 2026-03-22*
