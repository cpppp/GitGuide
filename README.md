# GitGuide

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Vue-3.4+-green.svg" alt="Vue">
  <img src="https://img.shields.io/badge/FastAPI-0.109+-red.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/LangChain-1.0+-green.svg" alt="LangChain">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</p>

<p align="center">
  <b>🚀 智能化 GitHub 仓库学习工具</b>
</p>

<p align="center">
  输入 GitHub 仓库 URL，自动生成结构化学习文档、详细启动指南，并提供 AI 智能问答，让你快速掌握任何项目
</p>

***

## 🎯 核心功能

- **智能仓库分析** - 自动识别项目结构、技术栈和核心模块
- **一键文档生成** - 快速生成包含项目概述、架构设计、安装指南的完整文档
- **交互式 AI 问答** - 针对项目细节提供智能解答，支持代码解释和功能查询
- **数据持久化** - AI 问答记录和仓库文档自动保存，支持离线查看
- **多项目类型支持** - 兼容 Python、Node.js、Java、Go 等多种技术栈
- **实时进度显示** - WebSocket 实时推送分析进度
- **现代化用户界面** - 基于 Vue 3 + Element Plus 的响应式界面
- **多语言支持** - 支持中英文界面切换
- **深色模式** - 支持深色/浅色主题切换

## 🛠️ 技术栈

| 组件       | 技术                  | 版本            | 用途                        |
| :------- | :------------------ | :------------ | :------------------------ |
| 前端       | Vue 3               | 3.4+          | 现代化 Web 界面              |
| 前端 UI    | Element Plus        | 2.5+          | UI 组件库                   |
| 前端构建   | Vite                | 5.0+          | 开发服务器和构建工具           |
| 状态管理    | Pinia               | 2.1+          | 前端状态管理                 |
| 后端       | FastAPI             | 0.109+        | REST API 服务               |
| 实时通信    | WebSocket           | -             | 实时进度推送                 |
| Agent 框架 | LangChain           | 1.0+          | 构建智能 Agent 系统           |
| Agent 框架 | LangGraph           | 0.2+          | 管理 Agent 间的工作流和状态       |
| LLM      | OpenAI API / 智谱 GLM | GPT-4 / glm-4 | 提供自然语言处理能力              |
| 数据库     | SQLite              | 3.0+          | 数据持久化存储                 |
| ORM      | SQLAlchemy          | 2.0+          | 数据库操作                    |
| 仓库分析     | PyGithub            | 2.1+          | 调用 GitHub API 获取仓库信息     |
| 仓库分析     | GitPython           | 3.1+          | 本地仓库克隆和分析               |

## 📁 项目结构

```
GitGuide/
├── backend/                    # FastAPI 后端
│   ├── main.py                 # FastAPI 入口
│   ├── api/                    # API 路由
│   │   ├── analyze.py          # 分析 API
│   │   ├── chat.py             # 问答 API
│   │   ├── repositories.py     # 仓库管理 API
│   │   ├── data.py             # 数据导出导入 API
│   │   └── health.py           # 健康检查
│   ├── models/
│   │   ├── database.py         # 数据库模型
│   │   └── schemas.py          # Pydantic 数据模型
│   ├── database/
│   │   ├── config.py           # 数据库配置
│   │   └── crud.py             # CRUD 操作
│   ├── services/
│   │   └── code_graph.py       # 代码图谱服务
│   └── websocket/
│       └── manager.py          # WebSocket 管理器
│
├── frontend/                   # Vue 3 前端
│   ├── src/
│   │   ├── api/                # API 调用
│   │   ├── views/              # 页面组件
│   │   │   ├── Home.vue
│   │   │   ├── Documentation.vue
│   │   │   ├── Chat.vue
│   │   │   └── Repositories.vue
│   │   ├── components/         # 组件
│   │   │   └── CodeGraph.vue
│   │   ├── stores/             # Pinia 状态管理
│   │   ├── router/             # 路由配置
│   │   └── i18n/               # 国际化
│   └── package.json
│
├── agents/                     # LangChain Agent
│   ├── orchestrator.py         # 协调器 - 管理多 Agent 工作流
│   ├── analyzer.py             # 分析器 - 仓库结构和技术栈分析
│   ├── doc_generator.py        # 文档生成器 - 生成学习文档和指南
│   └── chat.py                 # 聊天 Agent - 回答项目相关问题
│
├── tools/                      # 工具函数库
│   ├── github_tools.py         # GitHub API 交互工具
│   ├── git_tools.py            # Git 仓库操作工具
│   └── file_tools.py           # 文件读取和分析工具
│
├── core/                       # 核心模块
│   ├── config.py               # 配置管理
│   ├── utils.py                # 通用工具函数
│   ├── favorites.py            # 收藏管理
│   ├── history.py              # 历史记录管理
│   └── validators.py           # URL 验证
│
├── memory-bank/                # 项目文档
│   ├── architecture.md         # 架构设计文档
│   ├── product-design-document.md # 产品设计文档
│   ├── tech-stack.md           # 技术栈说明
│   ├── implementation-plan.md  # 实施计划
│   ├── process.md              # 项目进度跟踪
│   └── system-update.md        # 系统升级方案
│
├── requirements.txt            # Python 依赖包
├── .env.example                # 环境变量示例
└── README.md                   # 项目说明文档
```

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/your-username/GitGuide.git
cd GitGuide
```

### 2. 创建虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# Windows 激活环境
venv\Scripts\activate

# macOS/Linux 激活环境
source venv/bin/activate
```

### 3. 安装依赖

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 安装前端依赖
cd frontend
npm install
cd ..
```

### 4. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的 API Key
```

`.env` 文件配置示例：

```env
# OpenAI API（或兼容的 API，如智谱 GLM）
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.openai.com/v1  # 或其他兼容端点
OPENAI_MODEL=gpt-4

# GitHub API（可选，提高速率限制）
GITHUB_TOKEN=your_github_token

# 数据库配置（默认使用 SQLite）
DATABASE_URL=sqlite:///./gitguide.db
```

### 5. 启动应用

```bash
# 终端 1：启动后端
cd backend
python -m uvicorn main:app --reload --port 8000

# 终端 2：启动前端
cd frontend
npm run dev
```

应用将在 <http://localhost:5173> 启动。

## 📖 使用指南

1. **访问应用** - 打开浏览器访问 <http://localhost:5173>
2. **输入仓库 URL** - 在首页输入 GitHub 仓库 URL（例如：`https://github.com/vuejs/vue`）
3. **选择分析模式** - 快速模式（约30秒）或详细模式（约2分钟）
4. **生成文档** - 点击"生成文档"按钮，系统将自动分析仓库并生成文档
5. **查看学习文档** - 在文档页面浏览生成的项目概述、技术栈分析和启动指南
6. **AI 智能问答** - 切换到 Chat 页面，针对项目提出问题，获取智能解答
7. **查看已分析仓库** - 首页"已分析仓库"卡片显示历史记录，点击可查看已保存的文档

## 🆕 V3.0 新功能

### 数据持久化

- **AI 问答记录持久化** - 问答记录自动保存到数据库，刷新页面不丢失，支持清除历史记录
- **仓库文档持久化** - 分析结果自动保存，支持离线查看
- **已分析仓库列表** - 首页展示已分析仓库卡片，点击可快速查看历史文档
- **数据导出导入** - 支持导出和导入用户数据（JSON 格式）

### 数据库集成

- 使用 SQLite 作为默认数据库
- SQLAlchemy ORM 支持数据库操作
- 支持迁移到 PostgreSQL（生产环境）

### 新增 API

| 端点 | 方法 | 描述 |
|:---|:---|:---|
| `/api/repositories` | GET | 获取所有已分析仓库 |
| `/api/repositories/{url}` | GET | 获取指定仓库详情 |
| `/api/repositories/{url}` | DELETE | 删除指定仓库 |
| `/api/chat/history` | GET | 获取问答历史记录 |
| `/api/chat/history` | DELETE | 清除问答历史记录 |
| `/api/data/export` | GET | 导出所有数据 |
| `/api/data/import` | POST | 导入数据 |

## 📂 支持的项目类型

- **Node.js** - 基于 package.json 识别
- **Python** - 基于 requirements.txt 或 setup.py 识别
- **Java** - 基于 pom.xml 或 build.gradle 识别
- **Go** - 基于 go.mod 识别
- **Docker** - 基于 Dockerfile 识别

## 🏗️ 架构设计

GitGuide 采用前后端分离架构：

```
┌─────────────────────────────────────────────────────────────────┐
│                    Vue 3 前端 (Port 5173)                        │
│  ┌──────────┐  ┌──────────────┐  ┌────────────┐  ┌──────────┐  │
│  │   Home   │  │ Documentation│  │    Chat    │  │Repositories│ │
│  └────┬─────┘  └──────┬───────┘  └─────┬──────┘  └────┬─────┘  │
│       │               │                 │              │        │
│       └───────────────┼─────────────────┼──────────────┘        │
│                       │                 │                       │
│              HTTP / WebSocket                                   │
└───────────────────────┼─────────────────┼───────────────────────┘
                        │                 │
                        ▼                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI 后端 (Port 8000)                      │
│  ┌─────────────┐  ┌────────────┐  ┌──────────────┐             │
│  │ /api/analyze│  │ /api/chat  │  │/api/repositories│            │
│  └──────┬──────┘  └─────┬──────┘  └──────┬───────┘             │
└─────────┼───────────────┼─────────────────┼──────────────────────┘
          │               │                 │
          └───────────────┼─────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    数据层                                        │
│  ┌─────────────┐  ┌────────────┐  ┌──────────────┐             │
│  │   SQLite    │  │ LangChain  │  │  GitHub API  │             │
│  │  Database   │  │   Agents   │  │              │             │
│  └─────────────┘  └────────────┘  └──────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

### Agent 职责说明

- **Orchestrator** - 负责协调各 Agent 工作流程，管理任务分发和状态跟踪
- **Analyzer Agent** - 分析仓库结构、识别技术栈、提取核心模块和依赖关系
- **DocGen Agent** - 根据分析结果生成结构化学习文档和详细启动指南
- **Chat Agent** - 基于生成的文档和仓库知识，回答用户关于项目的问题

## ⚙️ 环境变量配置

| 变量名               | 必填 | 说明                          | 默认值                     |
| :---------------- | :- | :-------------------------- | :---------------------- |
| `OPENAI_API_KEY`  | 是  | OpenAI API 密钥或兼容 API 密钥       | -                       |
| `OPENAI_BASE_URL` | 否  | API 端点 URL（默认 OpenAI）         | `https://api.openai.com/v1` |
| `OPENAI_MODEL`    | 否  | 模型名称（默认 gpt-4）              | `gpt-4`                 |
| `GITHUB_TOKEN`    | 否  | GitHub Token（提高 API 限额）        | -                       |
| `DATABASE_URL`    | 否  | 数据库连接字符串                    | `sqlite:///./gitguide.db` |

## ❓ 常见问题

### Q: API 调用失败怎么办？

A: 请检查 `.env` 文件中的 `OPENAI_API_KEY` 是否正确配置，确保 API Key 有效且未过期。

### Q: GitHub API 限流怎么办？

A: 配置 `GITHUB_TOKEN` 可将 API 调用限额从 60 次/小时提升到 5000 次/小时，显著提高分析速度。

### Q: 分析大型仓库需要多长时间？

A: 分析时间取决于仓库大小和网络速度，一般在 1-3 分钟内完成。大型仓库可能需要更长时间。

### Q: 前后端如何通信？

A: 前端通过 HTTP API 与后端通信，分析进度通过 WebSocket 实时推送。

### Q: 数据存储在哪里？

A: 数据默认存储在 `backend/gitguide.db` SQLite 数据库文件中，可以通过配置 `DATABASE_URL` 切换到 PostgreSQL。

## 📅 开发路线

### v2.0 ✅ 已完成
- [x] 前后端分离架构（Vue 3 + FastAPI）
- [x] WebSocket 实时进度推送
- [x] 可靠的任务取消功能
- [x] 现代化响应式界面

### v2.1 ✅ 已完成
- [x] 文档导出功能（Markdown、PDF、HTML）
- [x] 深色模式支持
- [x] 多语言界面支持

### v2.2 ✅ 已完成
- [x] 数据库集成（SQLite + SQLAlchemy）
- [x] AI 问答记录持久化
- [x] 仓库文档持久化
- [x] 数据导出导入功能
- [x] 已分析仓库列表页面
- [x] 收藏功能数据库迁移

### v3.0 计划中
- [ ] Multi-Agent 架构升级
- [ ] SOP 标准化流程
- [ ] 并行分析处理
- [ ] 分析效率提升 60%+

### v3.1 计划中
- [ ] 7 种文档类型（快速入门、项目概览、架构设计、安装部署、使用教程、开发指南、故障排查）
- [ ] 5 种辅助素材（架构图、目录树、代码图谱、示例代码、学习路径）
- [ ] 质量控制机制
- [ ] 文档质量评分系统

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

***

<p align="center">
  Made with ❤️ for HOMEWORK
</p>
