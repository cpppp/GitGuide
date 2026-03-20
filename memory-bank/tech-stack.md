# 技术栈推荐文档：GitGuide

## 1. 推荐技术栈总览

基于产品设计文档的需求分析，推荐以下技术栈组合：

| 层级           | 技术选择                   | 版本建议                           |
| :----------- | :--------------------- | :----------------------------- |
| **前端框架**     | Vue 3 + Element Plus   | Vue 3.4+, Element Plus 2.5+    |
| **前端构建**     | Vite                   | 5.0+                           |
| **前端状态管理**   | Pinia                  | 2.1+                           |
| **Agent 框架** | LangChain + LangGraph  | LangChain 1.0+, LangGraph 0.2+ |
| **后端框架**     | FastAPI                | 0.109+                         |
| **AI 服务**    | OpenAI API / 智谱 GLM    | GPT-4 / glm-4.7                |
| **仓库分析**     | GitPython + GitHub API | GitPython 3.1+                 |
| **实时通信**     | WebSocket              | FastAPI 内置                     |
| **数据库**      | SQLite / PostgreSQL    | SQLite 3.x / PostgreSQL 14+    |
| **ORM**      | SQLAlchemy             | 2.0+                           |
| **缓存**       | Redis                  | 7.0+                           |
| **部署平台**     | Railway / 容器化部署        | -                              |

## 2. 详细技术选型理由

### 2.1 前端技术栈

#### Vue 3 + Element Plus

**推荐理由：**

- **Composition API**：Vue 3 的组合式 API 使代码组织更灵活
- **Element Plus**：国内生态最完善的 UI 组件库，文档友好
- **Vite**：极快的开发启动和热更新体验
- **Pinia**：轻量级状态管理，与 Vue 3 完美集成
- **前后端分离**：更灵活的架构，支持更好的并发处理

**技术架构：**

```
┌─────────────────────────────────────────────────────────────┐
│                      Vue 3 前端                              │
├─────────────────────────────────────────────────────────────┤
│  Views: Home | Documentation | Chat                         │
│  Components: UrlInput, ProgressPanel, DocViewer, ChatPanel │
│  Store: Pinia (analysis, chat history)                     │
│  API: Axios + WebSocket                                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ HTTP / WebSocket
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI 后端                             │
├─────────────────────────────────────────────────────────────┤
│  API Routes: /api/analyze, /api/chat, /api/history          │
│  WebSocket: /ws/analyze/{job_id}                            │
│  Models: Pydantic schemas                                   │
│  Database: SQLAlchemy ORM                                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    LangChain Agents                         │
├─────────────────────────────────────────────────────────────┤
│  Supervisor | Analyzer Team | Generator Team | Chat        │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Agent 框架

#### LangChain + LangGraph

**推荐理由：**

- **多 Agent 协作**：LangGraph 支持构建复杂的多 Agent 工作流
- **工具调用**：内置 Tool 机制，方便 Agent 调用外部 API 和函数
- **状态管理**：LangGraph 提供图状状态机，管理 Agent 间通信
- **可观测性**：LangSmith 集成，便于调试和监控 Agent 行为
- **生态丰富**：大量预置组件（文档加载器、向量存储、LLM 接口）

#### Multi-Agent 架构升级（v3.1）

借鉴 OpenMAIC 的设计理念，升级为分层多Agent架构：

```
┌─────────────────────────────────────────────────────────────┐
│                      用户输入 GitHub URL                      │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Supervisor Agent                          │
│              (任务规划、进度协调、质量控制)                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ Planner  │ │Scheduler │ │ Reviewer │ │Optimizer │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
└──────────┬──────────────────┬──────────────────┬────────────┘
           │                  │                  │
           ▼                  ▼                  ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│  Analyzer Team   │ │  Generator Team  │ │  Research Team   │
│  (分析团队-并行)   │ │  (生成团队-并行)   │ │  (调研团队-并行)   │
├──────────────────┤ ├──────────────────┤ ├──────────────────┤
│ TypeAnalyzer     │ │ ReadmeGenerator  │ │ CodeAnalyzer     │
│ StructureAnalyzer│ │ LearningDocGen   │ │ APIAnalyzer      │
│ DependencyAnalyzer│ │ SetupGuideGen   │ │ TestAnalyzer     │
│ CodePatternAnalyst│ │ VisualDocGen   │ │ PerfAnalyzer     │
└──────────────────┘ └──────────────────┘ └──────────────────┘
           │                  │                  │
           └──────────────────┼──────────────────┘
                              ▼
                    ┌──────────────────┐
                    │   Shared Context │
                    │   (共享上下文)    │
                    └──────────────────┘
```

**Agent 职责划分：**

| Agent                    | 职责               | 输入     | 输出       | 执行方式 |
| :----------------------- | :--------------- | :----- | :------- | :--- |
| **Supervisor**           | 协调各 Agent，管理整体流程 | 用户 URL | 最终结果     | 串行   |
| **Planner**              | 制定分析策略，分配任务      | 仓库信息   | 分析计划     | 串行   |
| **Scheduler**            | 调度并行任务           | 分析计划   | 任务队列     | 串行   |
| **TypeAnalyzer**         | 识别项目类型、语言        | 仓库 URL | 项目类型     | 并行   |
| **StructureAnalyzer**    | 分析目录结构           | 仓库 URL | 目录树      | 并行   |
| **DependencyAnalyzer**   | 解析依赖关系           | 仓库 URL | 依赖列表     | 并行   |
| **CodePatternAnalyzer**  | 分析代码模式           | 仓库 URL | 代码模式     | 并行   |
| **ReadmeGenerator**      | 生成 README        | 分析结果   | README文档 | 并行   |
| **LearningDocGenerator** | 生成学习文档           | 分析结果   | 学习文档     | 并行   |
| **SetupGuideGenerator**  | 生成启动指南           | 分析结果   | 启动指南     | 并行   |
| **Reviewer**             | 文档质量审核           | 生成文档   | 审核结果     | 串行   |
| **Optimizer**            | 迭代优化文档           | 文档+反馈  | 优化后文档    | 串行   |

### 2.3 AI 服务

#### OpenAI API / 智谱 GLM

**推荐理由：**

- **效果最佳**：GPT-4 在代码理解和生成方面表现最优
- **LangChain 原生支持**：无缝集成，开箱即用
- **Function Calling**：支持 Agent 工具调用
- **成本可控**：按使用量计费，MVP 阶段成本较低

**替代方案：**

- Claude API：代码能力接近，LangChain 同样支持
- 开源模型（Ollama + LLaMA/Qwen）：本地部署，隐私性好，但性能略低

### 2.4 仓库分析

#### GitPython + GitHub API

**推荐理由：**

- **GitPython**：纯 Python 实现，无需依赖系统 git
- **GitHub API**：官方 API，稳定可靠
- **LangChain Tool 封装**：可作为 Agent 工具使用

### 2.5 数据库（v3.0新增）

#### SQLite / PostgreSQL

**推荐理由：**

- **SQLite**：
  - 零配置，无需独立服务器
  - 适合 MVP 和中小规模应用
  - 单文件存储，易于备份和迁移
- **PostgreSQL**：
  - 生产环境首选
  - 支持高并发和复杂查询
  - 丰富的数据类型和扩展

**数据库架构：**

```
┌─────────────────┐     ┌─────────────────┐
│  repositories   │     │  chat_messages  │
├─────────────────┤     ├─────────────────┤
│ id (PK)         │◄────│ repo_id (FK)    │
│ url             │     │ role            │
│ name            │     │ content         │
│ learning_doc    │     │ created_at      │
│ setup_guide     │     └─────────────────┘
│ analysis_result │
│ created_at      │     ┌─────────────────┐
│ updated_at      │     │    favorites    │
└────────┬────────┘     ├─────────────────┤
         │              │ repo_id (FK)    │
         └─────────────►│ created_at      │
                        └─────────────────┘
```

#### SQLAlchemy ORM

**推荐理由：**

- **成熟稳定**：Python 最流行的 ORM 框架
- **类型安全**：2.0 版本支持完整的类型提示
- **异步支持**：支持 async/await 模式
- **迁移工具**：Alembic 提供数据库版本管理

### 2.6 缓存与异步任务

#### Redis

**推荐理由：**

- **高性能缓存**：内存数据库，读写速度极快
- **任务队列**：支持 RQ/Celery 后台任务处理
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

### 2.7 部署平台

#### Railway / 容器化部署

**推荐理由：**

- **Railway**：
  - 支持 FastAPI + PostgreSQL 一键部署
  - 自动 HTTPS 和域名
  - 简单的环境变量管理
- **Docker**：
  - 完全自主控制
  - 易于扩展和迁移
  - 支持 Kubernetes 编排

## 3. 项目结构建议

```
GitGuide/
├── app.py                      # Streamlit 主入口（旧版兼容）
├── pages/                      # Streamlit 页面（旧版）
│
├── backend/                    # FastAPI 后端
│   ├── main.py                 # FastAPI 入口
│   ├── api/                    # API 路由
│   │   ├── analyze.py          # 分析 API
│   │   ├── chat.py             # 问答 API
│   │   ├── history.py          # 历史 API
│   │   └── health.py           # 健康检查
│   ├── models/                 # 数据模型
│   │   ├── schemas.py          # Pydantic 模型
│   │   └── database.py         # SQLAlchemy 模型
│   ├── database/               # 数据库相关
│   │   ├── connection.py       # 数据库连接
│   │   ├── crud.py             # CRUD 操作
│   │   └── migrations/         # Alembic 迁移
│   ├── websocket/
│   │   └── manager.py          # WebSocket 管理器
│   └── tasks.py                # RQ 任务队列
│
├── frontend/                   # Vue 3 前端
│   ├── src/
│   │   ├── api/                # API 调用
│   │   ├── views/              # 页面组件
│   │   ├── stores/             # Pinia 状态管理
│   │   ├── router/             # 路由配置
│   │   └── i18n/               # 多语言配置
│   ├── package.json
│   └── vite.config.js
│
├── agents/                     # LangChain Agent 定义
│   ├── __init__.py
│   ├── supervisor.py           # 总监 Agent（v3.1新增）
│   ├── planner.py              # 规划器 Agent（v3.1新增）
│   ├── scheduler.py            # 调度器 Agent（v3.1新增）
│   ├── reviewer.py             # 审核器 Agent（v3.1新增）
│   ├── optimizer.py            # 优化器 Agent（v3.1新增）
│   ├── analyzer/               # 分析团队（v3.1重构）
│   │   ├── type_analyzer.py
│   │   ├── structure_analyzer.py
│   │   ├── dependency_analyzer.py
│   │   └── code_pattern_analyzer.py
│   ├── generators/             # 生成团队（v3.1重构）
│   │   ├── readme_generator.py
│   │   ├── learning_doc_generator.py
│   │   ├── setup_guide_generator.py
│   │   └── visual_doc_generator.py
│   ├── orchestrator.py         # 协调器 Agent（旧版保留）
│   ├── analyzer.py             # 仓库分析 Agent（旧版保留）
│   ├── doc_generator.py        # 文档生成 Agent（旧版保留）
│   └── chat.py                 # 问答 Agent
│
├── tools/                      # Agent 工具
│   ├── __init__.py
│   ├── github_tools.py         # GitHub API 工具
│   ├── git_tools.py            # GitPython 工具
│   ├── file_tools.py           # 文件读取工具
│   └── code_tools.py           # 代码解析工具
│
├── core/                       # 核心业务逻辑
│   ├── __init__.py
│   ├── config.py               # 配置管理
│   ├── utils.py                # 工具函数
│   ├── favorites.py            # 收藏管理
│   ├── history.py              # 历史记录管理
│   ├── validators.py           # URL 验证
│   └── context.py              # 共享上下文（v3.1新增）
│
├── memory-bank/                # 项目文档
├── requirements.txt            # Python 依赖
├── .env.example                # 环境变量示例
└── README.md
```

## 4. 核心依赖清单

### requirements.txt

```txt
# FastAPI
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
python-multipart>=0.0.6

# LangChain 1.0+
langchain>=1.0.0
langchain-openai>=0.3.0
langchain-community>=0.3.0
langgraph>=0.2.0

# AI
openai>=1.57.0

# 仓库分析
GitPython>=3.1.41
PyGithub>=2.1.1

# 数据库（v3.0新增）
sqlalchemy>=2.0.0
alembic>=1.13.0
aiosqlite>=0.19.0

# 数据处理
pydantic>=2.6.0
python-dotenv>=1.0.0
httpx>=0.27.0

# 代码高亮
pygments==2.17.2

# 缓存与异步任务
redis>=5.0.0
rq>=1.16.0

# Markdown 渲染
markdown==3.5.2

# PDF 导出
reportlab>=4.0.0
weasyprint>=60.0
```

## 5. Agent 工作流实现

### 5.1 LangGraph 工作流（v3.1升级）

```python
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from typing import TypedDict, Annotated

class GitGuideState(TypedDict):
    """GitGuide 全局状态"""
    repo_url: str
    analysis_plan: dict
    type_result: dict
    structure_result: dict
    dependency_result: dict
    learning_doc: str
    setup_guide: str
    quality_score: float
    final_result: dict
    progress: int
    current_stage: str

def build_gitguide_graph():
    """构建 GitGuide 工作流图"""
    graph = StateGraph(GitGuideState)
    
    # 添加节点
    graph.add_node("planner", planner_node)
    graph.add_node("type_analyzer", type_analyzer_node)
    graph.add_node("structure_analyzer", structure_analyzer_node)
    graph.add_node("dependency_analyzer", dependency_analyzer_node)
    graph.add_node("merger", merger_node)
    graph.add_node("doc_generator", doc_generator_node)
    graph.add_node("reviewer", reviewer_node)
    graph.add_node("optimizer", optimizer_node)
    
    # 设置入口
    graph.set_entry_point("planner")
    
    # 定义边 - 规划后并行分析
    graph.add_edge("planner", "type_analyzer")
    graph.add_edge("planner", "structure_analyzer")
    graph.add_edge("planner", "dependency_analyzer")
    
    # 并行分析后合并
    graph.add_edge("type_analyzer", "merger")
    graph.add_edge("structure_analyzer", "merger")
    graph.add_edge("dependency_analyzer", "merger")
    
    # 合并后生成文档
    graph.add_edge("merger", "doc_generator")
    
    # 文档生成后审核
    graph.add_edge("doc_generator", "reviewer")
    
    # 条件路由
    graph.add_conditional_edges(
        "reviewer",
        should_optimize,
        {True: "optimizer", False: END}
    )
    
    return graph.compile()
```

### 5.2 并行执行实现

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class ParallelExecutor:
    """并行执行器"""
    
    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
    async def execute_parallel(
        self, 
        tasks: list, 
        context: SharedContext
    ) -> list:
        """并行执行任务"""
        loop = asyncio.get_event_loop()
        
        futures = [
            loop.run_in_executor(
                self.executor,
                task.run,
                context
            )
            for task in tasks
        ]
        
        results = await asyncio.gather(*futures, return_exceptions=True)
        
        return results
```

## 6. 数据库操作实现（v3.0新增）

### 6.1 SQLAlchemy 模型定义

```python
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.models.database import Base

class Repository(Base):
    __tablename__ = "repositories"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(500), unique=True, nullable=False)
    name = Column(String(200))
    description = Column(Text)
    language = Column(String(50))
    stars = Column(Integer, default=0)
    learning_doc = Column(Text)
    setup_guide = Column(Text)
    analysis_result = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    chat_messages = relationship("ChatMessage", back_populates="repository")
    favorites = relationship("Favorite", back_populates="repository")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, ForeignKey("repositories.id"))
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    repository = relationship("Repository", back_populates="chat_messages")

class Favorite(Base):
    __tablename__ = "favorites"
    
    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, ForeignKey("repositories.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    repository = relationship("Repository", back_populates="favorites")
```

### 6.2 CRUD 操作

```python
from sqlalchemy.orm import Session
from backend.models.database import Repository, ChatMessage, Favorite

class RepositoryCRUD:
    def create_repository(self, db: Session, repo_data: dict) -> Repository:
        db_repo = Repository(**repo_data)
        db.add(db_repo)
        db.commit()
        db.refresh(db_repo)
        return db_repo
    
    def get_by_url(self, db: Session, url: str) -> Repository:
        return db.query(Repository).filter(Repository.url == url).first()
    
    def update_repository(self, db: Session, url: str, update_data: dict) -> Repository:
        db_repo = self.get_by_url(db, url)
        if db_repo:
            for key, value in update_data.items():
                setattr(db_repo, key, value)
            db.commit()
            db.refresh(db_repo)
        return db_repo

class ChatMessageCRUD:
    def create_message(self, db: Session, repo_id: int, role: str, content: str) -> ChatMessage:
        db_message = ChatMessage(
            repo_id=repo_id,
            role=role,
            content=content
        )
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        return db_message
    
    def get_messages_by_repo(self, db: Session, repo_id: int) -> list:
        return db.query(ChatMessage).filter(
            ChatMessage.repo_id == repo_id
        ).order_by(ChatMessage.created_at).all()
    
    def delete_messages_by_repo(self, db: Session, repo_id: int) -> int:
        deleted = db.query(ChatMessage).filter(
            ChatMessage.repo_id == repo_id
        ).delete()
        db.commit()
        return deleted
```

## 7. 环境变量配置

### .env

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

# 数据库配置（v3.0新增）
DATABASE_URL=sqlite:///./gitguide.db
# 或 PostgreSQL: postgresql://user:password@localhost/gitguide

# Redis
REDIS_URL=redis://localhost:6379/0

# 应用配置
APP_ENV=development
DEBUG=true
SECRET_KEY=your_secret_key_here
```

## 8. 技术风险与应对

| 风险            | 影响       | 应对方案                             |
| :------------ | :------- | :------------------------------- |
| OpenAI API 限流 | AI 功能不可用 | 实现请求队列、降级到 GPT-3.5、支持智谱GLM       |
| GitHub API 限流 | 仓库分析失败   | 使用 Token 认证、缓存结果                 |
| 大仓库分析慢        | 用户体验差    | 显示进度条、并行处理、限制文件大小                |
| 数据库性能瓶颈       | 查询变慢     | 添加索引、使用连接池、考虑分库分表                |
| Agent 输出不稳定   | 文档质量波动   | 使用 structured output、添加校验逻辑、多轮优化 |
| 并发问题          | 数据不一致    | 使用数据库事务、乐观锁                      |

## 9. 技术栈优势总结

### 当前版本优势

1. **前后端分离**：Vue 3 + FastAPI 架构清晰，易于维护
2. **AI 能力强大**：LangChain 多 Agent 架构，功能扩展灵活
3. **数据持久化**：SQLite/PostgreSQL 支持数据长期存储
4. **实时通信**：WebSocket 实现真正的实时进度反馈

### v3.1 升级后优势

1. **并行处理**：多Agent并行执行，分析效率提升70%+
2. **质量保证**：SOP标准化流程 + 多轮审核优化
3. **深度分析**：多维度代码分析能力
4. **可扩展性**：模块化设计，易于添加新Agent

## 10. 后续优化方向

### v3.0 数据持久化

- **数据库集成**：SQLite → PostgreSQL（生产环境）
- **数据迁移**：Alembic 版本管理
- **缓存策略**：Redis 缓存分析结果

### v3.1 Multi-Agent 升级

- **并行处理**：asyncio + ThreadPoolExecutor
- **状态管理**：LangGraph StateGraph
- **质量控制**：Reviewer + Optimizer Agent

### v3.2+ 高级功能

- **向量存储**：集成向量数据库支持语义搜索
- **多 LLM 支持**：Claude、开源模型
- **私有仓库**：OAuth 授权支持
- **容器化**：Docker + Kubernetes 部署

***

本技术栈推荐基于 **Vue 3 + FastAPI + LangChain** 架构，支持数据持久化和 Multi-Agent 并行处理，为 GitGuide 提供高性能、高可扩展性的技术基础。

*Last updated: 2026-03-20*
