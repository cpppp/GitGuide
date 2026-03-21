# GitGuide 项目实施计划

> **文档版本**：v3.6\
> **最后更新**：2026-03-21

***

## 1. 项目概述

GitGuide 是一个帮助开发者快速上手任意 GitHub 仓库的智能化工具。本文档描述项目的架构设计和实施计划。

**核心目标**：

1. 自动分析 GitHub 仓库，生成 7 种学习文档
2. 提供辅助素材（架构图、代码图谱、示例代码）
3. AI 智能问答，帮助用户理解项目

***

## 2. 架构设计

### 2.1 整体架构

```
┌───────────────────────────────────────────────────────────────────────────┐
│                           Vue 3 前端 (Element Plus)                       │
│         Home (URL输入) / Documentation (文档展示) / Chat (AI问答)          │
└───────────────────────────────────────────────────────────────────────────┘
                              │ HTTP / WebSocket
                              ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                          FastAPI 后端                                     │
│  API: /analyze, /chat, /repositories, /favorites, /health                 │
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
│  │   状态管理 + 任务规划 + 并行调度 + 质量审核 + 结果整合                 │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                    │                                      │
│          ┌─────────────────────────┼───────────────────────────┐         │
│          ▼                         ▼                           ▼         │
│  ┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐  │
│  │   Analyzer Team   │   │   Generator Team  │   │     Chat Agent    │  │
│  │    (并行执行)      │   │    (并行执行)      │   │                   │  │
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
└───────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Agent 职责

| Agent 类型           | 组件                  | 职责                  |
| :----------------- | :------------------ | :------------------ |
| **编排层**            | Orchestrator        | 入口管理、仓库克隆、进度回调、资源清理 |
| <br />             | Workflow            | 状态管理、并行调度、质量审核、结果整合 |
| **Analyzer Team**  | TypeAnalyzer        | 项目类型识别、语言/框架/构建系统检测 |
| <br />             | StructureAnalyzer   | 目录结构分析、模块识别、入口点提取   |
| <br />             | DependencyAnalyzer  | 依赖关系分析、版本兼容性检查      |
| <br />             | CodePatternAnalyzer | 代码模式识别、架构风格分析       |
| **Generator Team** | QuickStartGen       | 快速入门文档              |
| <br />             | OverviewGen         | 项目概览文档              |
| <br />             | ArchitectureGen     | 架构设计文档              |
| <br />             | InstallGuideGen     | 安装部署文档              |
| <br />             | TutorialGen         | 使用教程文档              |
| <br />             | DevGuideGen         | 开发指南文档              |
| <br />             | TroubleshootGen     | 故障排查文档              |
| **Chat Agent**     | KnowledgeBuilder    | 构建仓库知识库             |
| <br />             | RAGRetriever        | 检索增强生成              |
| <br />             | ConversationManager | 多轮对话管理              |

### 2.3 工作流程

```
用户输入 GitHub URL
        │
        ▼
┌─────────────────┐
│   Orchestrator  │
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
│ Stage 2: 分析    │ ─── 并行执行 4 个 Analyzer
│ Stage 3: 生成    │ ─── 并行执行 7 个 Generator
│ Stage 4: 审核    │ ─── 内置质量检查
│ Stage 5: 输出    │ ─── 构建最终结果
└─────────────────┘
        │
        ▼
    最终输出
    • 7种文档
    • 质量评分
    • 辅助素材
```

***

## 3. 文件结构

```
GitGuide/
├── backend/                    # FastAPI 后端
│   ├── main.py                 # 入口
│   ├── api/                    # API 路由
│   ├── models/                 # Pydantic + SQLAlchemy
│   ├── database/               # 数据库配置和 CRUD
│   ├── services/               # 服务层
│   │   └── code_graph.py       # 代码分析服务
│   └── websocket/              # WebSocket 管理
│
├── frontend/                   # Vue 3 前端
│   ├── src/
│   │   ├── api/                # API 调用
│   │   ├── components/         # 组件
│   │   ├── views/              # 页面
│   │   ├── stores/             # Pinia 状态
│   │   └── i18n/               # 国际化
│   └── package.json
│
├── agents/                     # Multi-Agent 系统
│   ├── __init__.py
│   ├── orchestrator.py         # 入口编排器
│   ├── workflow.py             # 核心工作流
│   │
│   ├── analyzers/              # Analyzer Team
│   │   ├── type_analyzer.py
│   │   ├── structure_analyzer.py
│   │   ├── dependency_analyzer.py
│   │   └── code_pattern_analyzer.py
│   │
│   ├── generators/             # Generator Team
│   │   ├── quick_start_generator.py
│   │   ├── overview_generator.py
│   │   ├── architecture_generator.py
│   │   ├── install_guide_generator.py
│   │   ├── tutorial_generator.py
│   │   ├── dev_guide_generator.py
│   │   └── troubleshoot_generator.py
│   │
│   └── chat/                   # Chat Agent Team
│       ├── conversation_manager.py
│       ├── knowledge_builder.py
│       ├── rag_retriever.py
│       └── chat_agent.py
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

## 4. 实施计划

### 4.1 阶段规划

| 阶段     | 目标     | 主要内容                              |
| :----- | :----- | :-------------------------------- |
| V3.0.1 | 架构简化   | 移除 Supervisor Team，职责合并到 Workflow |
| V3.1   | 文档质量提升 | 7种文档类型、辅助素材生成、前端适配                |
| V3.2   | AI问答升级 | Chat Agent 团队、RAG 知识库、多轮对话        |

### 4.2 V3.0.1 架构简化

**目标**：简化 Agent 架构，确保代码与文档一致

**任务清单**：

- 删除 `agents/supervisor/` 目录
- 更新 `agents/__init__.py`
- 简化 `core/sop.py`
- 验证后端连接
- 验证前端连接
- 整体功能测试

### 4.3 V3.1 文档质量提升

**目标**：扩展文档类型，提升文档质量

**任务清单**：

- 实现 TutorialGenerator、DevGuideGenerator、TroubleshootGenerator
- 数据库模型更新（添加新文档字段）
- 实现架构图生成（Mermaid 格式）
- 实现示例代码提取器
- 前端多标签页文档展示
- 辅助素材展示组件

### 4.4 V3.2 AI 问答升级

**目标**：构建 Chat Agent 团队，实现智能问答

**两步迭代策略**：

```
┌─────────────────────────────────────────────────────────────┐
│              第一步：基础问答（无 RAG）                        │
│                                                              │
│  实现组件：ConversationManager                               │
│  特点：快速实现，复用现有工具，无需额外依赖                     │
│  上下文来源：GitHub工具 + 已生成文档 + 分析结果                │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              第二步：RAG 增强（方案 C）                        │
│                                                              │
│  实现组件：KnowledgeBuilder + RAGRetriever                   │
│  技术栈：Chroma + HuggingFaceEmbeddings（本地，零成本）        │
│  特点：精准检索，支持多轮对话，多语言支持                       │
└─────────────────────────────────────────────────────────────┘
```

**任务清单**：

**第一阶段**：

- 实现 ConversationManager（问题分类、上下文构建、多轮对话）
- 集成现有 GitHub 工具和已生成文档
- 后端 API 集成

**第二阶段**：

- 实现 KnowledgeBuilder（向量数据库构建）
- 实现 RAGRetriever（MMR 检索）
- Chat Agent 团队整合

***

## 5. 技术栈

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

## 6. 预期收益

| 维度           | 当前   | V3.1 后 | V3.2 后    |
| :----------- | :--- | :----- | :-------- |
| 文档类型         | 4种   | 7种     | 7种        |
| 辅助素材         | 无    | 5种     | 5种        |
| AI 问答        | 泛泛而谈 | 基于文档   | RAG 精准检索  |
| 多轮对话         | 不支持  | 不支持    | 支持        |
| Embedding 成本 | -    | -      | 零成本（本地模型） |

***

*Last updated: 2026-03-21*
