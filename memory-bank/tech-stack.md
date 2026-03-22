# 技术栈文档：GitGuide

> **文档版本**：v3.2\
> **最后更新**：2026-03-22\
> **更新说明**：V3.2 完成，更新 AI 问答技术栈和前端依赖

***

## 1. 技术栈总览

| 层级            | 技术选择                  | 版本             |
| ------------- | --------------------- | -------------- |
| **前端框架**      | Vue 3                 | 3.4+           |
| **前端 UI**     | Element Plus          | 2.5+           |
| **前端构建**      | Vite                  | 5.0+           |
| **前端状态管理**    | Pinia                 | 2.1+           |
| **前端路由**      | Vue Router            | 4.2+           |
| **后端框架**      | FastAPI               | 0.109+         |
| **Agent 框架**  | LangChain             | 1.0+           |
| **LLM**       | OpenAI API / 智谱 GLM   | GPT-4 / glm-4  |
| **仓库分析**      | GitPython + PyGithub  | GitPython 3.1+ |
| **数据库**       | SQLite / PostgreSQL   | SQLite 3.x     |
| **ORM**       | SQLAlchemy            | 2.0+           |
| **实时通信**      | WebSocket             | FastAPI 内置     |
| **缓存**        | Redis                 | 7.0+           |
| **向量数据库**     | Chroma                | -              |
| **Embedding** | HuggingFaceEmbeddings | 本地模型           |

## 2. 前端技术栈

### 2.1 核心框架

#### Vue 3 + Element Plus

**选择理由：**

- **Composition API**：Vue 3 的组合式 API 使代码组织更灵活
- **Element Plus**：国内生态最完善的 UI 组件库，文档友好
- **Vite**：极快的开发启动和热更新体验
- **Pinia**：轻量级状态管理，与 Vue 3 完美集成

**技术架构：**

```
┌─────────────────────────────────────────────────────────────┐
│                      Vue 3 前端                              │
├─────────────────────────────────────────────────────────────┤
│  Views: Home | Documentation | Chat | Repositories          │
│  Components: CodeAtlas, CodeGraph                           │
│  Store: Pinia (analysis, settings)                          │
│  API: Axios + WebSocket                                     │
│  i18n: 多语言支持 (zh, en)                                   │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 前端依赖

```json
{
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.0",
    "pinia": "^2.1.0",
    "element-plus": "^2.5.0",
    "@element-plus/icons-vue": "^2.3.0",
    "axios": "^1.6.0",
    "marked": "^11.0.0",
    "highlight.js": "^11.9.0",
    "dompurify": "^3.3.3",
    "prismjs": "^1.29.0",
    "mermaid": "^11.0.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "@vitejs/plugin-vue": "^5.0.0"
  }
}
```

### 2.3 前端模块说明

| 依赖                      | 用途              |
| ----------------------- | --------------- |
| vue                     | 核心框架            |
| vue-router              | 路由管理            |
| pinia                   | 状态管理            |
| element-plus            | UI 组件库          |
| @element-plus/icons-vue | 图标库             |
| axios                   | HTTP 请求         |
| marked                  | Markdown 渲染     |
| highlight.js            | 代码高亮            |
| dompurify               | HTML 净化（XSS 防护） |
| prismjs                 | 代码语法高亮          |
| mermaid                 | 架构图渲染           |

## 3. 后端技术栈

### 3.1 核心框架

#### FastAPI

**选择理由：**

- **高性能**：基于 Starlette 和 Pydantic，性能接近 Node.js
- **异步支持**：原生支持 async/await
- **自动文档**：自动生成 OpenAPI 文档
- **类型安全**：Pydantic 模型提供数据验证

**技术架构：**

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI 后端                             │
├─────────────────────────────────────────────────────────────┤
│  API Routes: analyze, chat, repositories, data, health      │
│  WebSocket: /ws/analyze/{job_id}                            │
│  Models: Pydantic schemas + SQLAlchemy ORM                  │
│  Database: SQLite (开发) / PostgreSQL (生产)                 │
│  Services: code_graph                                       │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 后端依赖

```txt
# FastAPI
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
python-multipart>=0.0.6

# LangChain
langchain>=1.0.0
langchain-openai>=0.3.0
langchain-community>=0.2.0
langgraph>=0.2.0

# AI
openai>=1.57.0

# RAG (方案 C - 本地 Embeddings)
chromadb>=0.4.0
sentence-transformers>=2.2.0

# 仓库分析
GitPython>=3.1.41
PyGithub>=2.1.1

# 数据处理
pydantic>=2.6.0
python-dotenv>=1.0.0
httpx>=0.26.0

# 代码高亮
pygments>=2.17.2

# Markdown 渲染
markdown>=3.5.2

# 异步任务队列
redis>=5.0.0
rq>=1.16.0

# 数据库
sqlalchemy>=2.0.0
alembic>=1.13.0

# Streamlit (旧版兼容)
streamlit>=1.40.0
streamlit-extras>=0.4.0
```

### 3.3 后端模块说明

| 依赖                    | 用途              |
| --------------------- | --------------- |
| fastapi               | Web 框架          |
| uvicorn               | ASGI 服务器        |
| langchain             | Agent 框架        |
| langchain-openai      | OpenAI 集成       |
| langgraph             | 工作流图            |
| openai                | LLM API         |
| chromadb              | 向量数据库           |
| sentence-transformers | 本地 Embedding 模型 |
| GitPython             | Git 操作          |
| PyGithub              | GitHub API      |
| pydantic              | 数据验证            |
| sqlalchemy            | ORM             |
| alembic               | 数据库迁移           |
| redis                 | 缓存/任务队列         |
| rq                    | 任务队列            |

## 4. Agent 框架

### 4.1 LangChain + LangGraph （当前未应用）

**选择理由：**

- **多 Agent 协作**：LangGraph 支持构建复杂的多 Agent 工作流
- **工具调用**：内置 Tool 机制，方便 Agent 调用外部 API 和函数
- **状态管理**：LangGraph 提供图状状态机，管理 Agent 间通信
- **可观测性**：LangSmith 集成，便于调试和监控 Agent 行为
- **生态丰富**：大量预置组件（文档加载器、向量存储、LLM 接口）

### 4.2 Agent 架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Orchestrator Agent                        │
│              (工作流协调、任务分发)                            │
└─────────────────────┬───────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Analyzer   │ │   DocGen     │ │    Chat      │
│    Agent     │ │    Agent     │ │    Agent     │
├──────────────┤ ├──────────────┤ ├──────────────┤
│ - 项目类型   │ │ - 学习文档   │ │ - 问答服务   │
│ - 目录结构   │ │ - 启动指南   │ │ - 代码解释   │
│ - 依赖分析   │ │ - 关键信息   │ │ - 项目建议   │
└──────────────┘ └──────────────┘ └──────────────┘
```

### 4.3 Agent 职责

| Agent            | 职责               | 输入       | 输出   |
| ---------------- | ---------------- | -------- | ---- |
| **Orchestrator** | 协调各 Agent，管理整体流程 | 用户 URL   | 最终结果 |
| **Analyzer**     | 分析仓库结构、识别项目类型    | 仓库 URL   | 分析结果 |
| **DocGen**       | 生成学习文档、启动指南      | 分析结果     | 文档内容 |
| **Chat**         | 回答用户问题、解释代码      | 问题 + 上下文 | 回答内容 |

## 5. 数据库

### 5.1 SQLite / PostgreSQL

**选择理由：**

**SQLite：**

- 零配置，无需独立服务器
- 适合 MVP 和中小规模应用
- 单文件存储，易于备份和迁移

**PostgreSQL：**

- 生产环境首选
- 支持高并发和复杂查询
- 丰富的数据类型和扩展

### 5.2 数据库架构

```
┌─────────────────┐     ┌─────────────────┐
│  repositories   │     │  chat_messages  │
├─────────────────┤     ├─────────────────┤
│ id (PK)         │◄────│ repo_id (FK)    │
│ url (UNIQUE)    │     │ role            │
│ name            │     │ content         │
│ description     │     │ created_at      │
│ language        │     └─────────────────┘
│ stars           │
│ learning_doc    │     ┌─────────────────┐
│ setup_guide     │     │    favorites    │
│ analysis_result │     ├─────────────────┤
│ created_at      │◄────│ repo_id (FK)    │
│ updated_at      │     │ created_at      │
└─────────────────┘     └─────────────────┘
         │
         │              ┌─────────────────┐
         └─────────────►│ analysis_history│
                        ├─────────────────┤
                        │ repo_id (FK)    │
                        │ analyzed_at     │
                        └─────────────────┘
```

### 5.3 SQLAlchemy ORM

**选择理由：**

- **成熟稳定**：Python 最流行的 ORM 框架
- **类型安全**：2.0 版本支持完整的类型提示
- **异步支持**：支持 async/await 模式
- **迁移工具**：Alembic 提供数据库版本管理

## 6. 缓存与异步任务

### 6.1 Redis

**选择理由：**

- **高性能缓存**：内存数据库，读写速度极快
- **任务队列**：支持 RQ 后台任务处理
- **实时进度**：通过任务元数据实现真正的进度反馈
- **会话存储**：可存储用户会话和临时数据

**架构设计：**

```
用户请求 ──▶ FastAPI ──▶ Redis Queue ──▶ RQ Worker
                              │
                              ▼
                         任务状态存储
                              │
                              ▼
                    WebSocket 推送进度
```

## 7. AI 服务

### 7.1 OpenAI API / 智谱 GLM

**选择理由：**

- **效果最佳**：GPT-4 在代码理解和生成方面表现最优
- **LangChain 原生支持**：无缝集成，开箱即用
- **Function Calling**：支持 Agent 工具调用
- **成本可控**：按使用量计费，MVP 阶段成本较低

**替代方案：**

- Claude API：代码能力接近，LangChain 同样支持
- 开源模型（Ollama + LLaMA/Qwen）：本地部署，隐私性好

## 8. AI 问答技术栈（方案 C）

### 8.1 技术选型

| 组件            | 技术                                                          | 说明              |
| :------------ | :---------------------------------------------------------- | :-------------- |
| **向量数据库**     | Chroma                                                      | 轻量级本地存储，无需额外服务  |
| **Embedding** | HuggingFaceEmbeddings                                       | 本地模型，零 API 成本   |
| **模型选择**      | sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 | 多语言支持，中文友好      |
| **对话管理**      | ConversationBufferMemory                                    | 多轮对话历史管理        |
| **检索策略**      | MMR                                                         | 最大边际相关性，提高检索多样性 |

### 8.2 方案优势

| 优势           | 说明                        |
| :----------- | :------------------------ |
| **零 API 成本** | 无需 OpenAI Embeddings，本地运行 |
| **数据隐私**     | 所有向量化在本地完成，无需上传数据         |
| **响应更快**     | 无网络延迟，本地计算                |
| **中文支持**     | 多语言模型，中英文效果均衡             |
| **部署简单**     | 无需额外向量数据库服务               |

### 8.3 Chat Agent 架构

```
┌─────────────────────────────────────────────────────────────┐
│                     Chat Agent 架构                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              第一阶段：基础问答（无 RAG）              │    │
│  │                                                       │    │
│  │  用户问题 ──► GitHub 工具 ──► 文档检索 ──► LLM 回答    │    │
│  │                                                       │    │
│  │  特点：直接利用现有工具和文档，快速实现                │    │
│  └─────────────────────────────────────────────────────┘    │
│                           │                                  │
│                           ▼                                  │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              第二阶段：RAG 增强（方案 C）              │    │
│  │                                                       │    │
│  │  知识库构建：                                         │    │
│  │  分析结果 + 仓库文件 ──► HuggingFaceEmbeddings        │    │
│  │                          │                            │    │
│  │                          ▼                            │    │
│  │                    Chroma VectorStore                 │    │
│  │                                                       │    │
│  │  问答流程：                                           │    │
│  │  用户问题 ──► 向量检索 ──► 上下文构建 ──► LLM 回答    │    │
│  │                                                       │    │
│  │  特点：精准检索，支持多轮对话，零 API 成本            │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 8.4 Embedding 模型对比

| 模型                                    | 维度  | 语言支持 | 速度 | 适用场景      |
| :------------------------------------ | :-- | :--- | :- | :-------- |
| all-MiniLM-L6-v2                      | 384 | 英文为主 | 最快 | 速度优先，免费高效 |
| paraphrase-multilingual-MiniLM-L12-v2 | 384 | 多语言  | 快  | 通用场景，中文友好 |
| paraphrase-multilingual-mpnet-base-v2 | 768 | 多语言  | 中  | 高精度需求     |

### 8.5 当前使用模型

**V3.2 采用** **`all-MiniLM-L6-v2`**：

- HuggingFace sentence-transformers 模型
- 384 维度，6 层轻量级设计
- 免费、无需 API key、本地运行
- 速度最快，适合效率优先场景

## 9. 仓库分析

### 9.1 GitPython + GitHub API

**选择理由：**

- **GitPython**：纯 Python 实现，无需依赖系统 git
- **GitHub API**：官方 API，稳定可靠
- **LangChain Tool 封装**：可作为 Agent 工具使用

### 9.2 工具模块

```
tools/
├── github_tools.py          # GitHub API 工具
│   - get_repo_info()        # 获取仓库信息
│   - get_readme()           # 获取 README
│   - get_file_content()     # 获取文件内容
│   - get_directory_structure()  # 获取目录结构
│
├── git_tools.py             # GitPython 工具
│   - clone_repo()           # 克隆仓库
│   - get_commit_history()   # 获取提交历史
│   - get_branches()         # 获取分支列表
│
└── file_tools.py            # 文件读取工具
    - read_file()            # 读取文件
    - read_directory()       # 读取目录
    - get_file_extension()   # 获取文件扩展名
```

## 10. 环境变量配置

### 10.1 .env 配置

```env
# OpenAI API
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4

# 智谱 GLM（可选）
ZHIPU_API_KEY=your_zhipu_api_key

# GitHub API (可选，提高速率限制)
GITHUB_TOKEN=your_github_token

# LangChain (可选，用于 LangSmith 调试)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langchain_api_key

# 数据库配置
DATABASE_URL=sqlite:///./gitguide.db
# 或 PostgreSQL: postgresql://user:password@localhost/gitguide

# Redis
REDIS_URL=redis://localhost:6379/0

# 应用配置
APP_ENV=development
DEBUG=true
SECRET_KEY=your_secret_key_here

# Embedding 模型配置（方案 C）
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
CHROMA_PERSIST_DIR=./chroma_db
```

## 11. 技术风险与应对

| 风险              | 影响       | 应对方案                        |
| --------------- | -------- | --------------------------- |
| OpenAI API 限流   | AI 功能不可用 | 实现请求队列、降级到 GPT-3.5、支持智谱 GLM |
| GitHub API 限流   | 仓库分析失败   | 使用 Token 认证、缓存结果            |
| 大仓库分析慢          | 用户体验差    | 显示进度条、并行处理、限制文件大小           |
| 数据库性能瓶颈         | 查询变慢     | 添加索引、使用连接池、考虑分库分表           |
| Agent 输出不稳定     | 文档质量波动   | 使用 structured output、添加校验逻辑 |
| 并发问题            | 数据不一致    | 使用数据库事务、乐观锁                 |
| Embedding 模型加载慢 | 首次响应慢    | 模型预加载、缓存机制                  |

## 12. 部署方案

### 12.1 开发环境

```bash
# 后端
pip install -r requirements.txt
cd backend && uvicorn main:app --reload --port 8000

# 前端
cd frontend && npm install && npm run dev
```

### 12.2 生产环境

**Railway / 容器化部署：**

- **Railway**：
  - 支持 FastAPI + PostgreSQL 一键部署
  - 自动 HTTPS 和域名
  - 简单的环境变量管理
- **Docker**：
  - 完全自主控制
  - 易于扩展和迁移
  - 支持 Kubernetes 编排

## 13. 技术栈优势总结

### 当前版本优势

1. **前后端分离**：Vue 3 + FastAPI 架构清晰，易于维护
2. **AI 能力强大**：LangChain 多 Agent 架构，功能扩展灵活
3. **数据持久化**：SQLite/PostgreSQL 支持数据长期存储
4. **实时通信**：WebSocket 实现真正的实时进度反馈
5. **多语言支持**：中英文切换，国际化友好
6. **主题切换**：浅色/深色主题，用户体验好
7. **零成本 Embedding**：本地模型，无需 API 费用

### 可扩展性

1. **模块化设计**：Agent、工具、API 各层独立
2. **插件化工具**：易于添加新的分析工具
3. **多 LLM 支持**：可切换不同的 LLM 提供商
4. **数据库迁移**：Alembic 支持平滑升级
5. **向量存储可替换**：Chroma 可替换为 Pinecone、Weaviate 等

***

*Last updated: 2026-03-21*
