# GitGuide 项目架构设计

## 1. 整体架构

GitGuide 采用基于 Streamlit + LangChain + LangGraph 的多 Agent 架构，通过有向图工作流协调多个专业化 Agent 来完成 GitHub 仓库的分析、文档生成和智能问答功能。

```
┌───────────────────────────────────────────────────────────────────────────┐
│                             Streamlit 前端                               │
├─────────────────────┬──────────────────────┬───────────────────────────────┤
│  🏠 Home 页面       │ 📚 Documentation 页面 │        💬 Chat 页面           │
│  (URL 输入)        │  (文档展示)         │     (AI 问答)                │
└─────────────────────┴──────────────────────┴───────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                      LangGraph 有向图工作流                             │
│                   (状态管理、任务协调、并行处理)                           │
└─────────────────────┬──────────────────────┬───────────────────────────────┘
                     │                      │
                     ▼                      ▼
┌────────────────────────┐      ┌──────────────────────────────┐
│   Analyzer Agent       │      │      DocGen Agent            │
│  (仓库分析专家)         │      │   (文档生成专家)             │
│ - 识别项目类型         │      │ - 生成学习文档              │
│ - 分析目录结构         │      │ - 生成启动指南              │
│ - 解析依赖关系         │      │ - 提取关键信息              │
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

### 1.1 LangGraph 工作流架构

为提升系统性能、可维护性和扩展性，引入了 LangGraph 有向图工作流：

```
┌───────────────────────────────────────────────────────────────────────────┐
│                    LangGraph 状态图                                │
│                   (显式状态管理、条件路由、并行执行)                   │
└─────────────────────┬──────────────────────┬───────────────────────────────┘
                     │                      │
                     ▼                      ▼
┌────────────────────────┐      ┌──────────────────────────────┐
│   分析节点           │      │      生成文档节点              │
│  (并行分析)          │      │   (并行生成)                │
│ - 仓库信息获取         │      │ - 学习文档生成               │
│ - 目录结构分析         │      │ - 启动指南生成               │
└──────────┬─────────────┘      └──────────────────────────────┘
           │
           ▼
┌────────────────────────┐
│   错误处理节点         │
│  (错误路由与恢复)       │
│ - 错误分类           │
│ - 重试逻辑           │
│ - 恢复机制           │
└────────────────────────┘
```

**组件说明：**

| 组件 | 文件 | 说明 |
|------|------|------|
| 状态定义 | `agents/workflow.py` | 定义工作流状态结构 |
| 节点函数 | `agents/workflow.py` | 实现各处理节点逻辑 |
| 并行处理 | `agents/parallel_workflow.py` | 并行执行优化 |
| 错误处理 | `agents/error_handling.py` | 错误路由和恢复机制 |
| 监控系统 | `core/monitoring.py` | 性能监控和日志记录 |
| 插件系统 | `agents/plugin_system.py` | 扩展性支持 |

**LangGraph 架构优势：**

1. **显式状态管理**：结构化状态定义，支持持久化和恢复
2. **条件路由**：支持复杂的分支逻辑和决策流程
3. **并行处理**：同时执行多个独立任务，提高性能
4. **错误恢复**：智能错误处理和自动恢复机制
5. **可观测性**：内置日志和追踪能力，便于调试
6. **模块化设计**：每个节点可独立开发和测试

## 2. 代码文件详细说明

### 2.1 核心配置模块 (core/)

#### core/config.py
**功能**: 应用程序配置管理和 LLM 客户端初始化

**主要功能**:
- 加载环境变量 (OPENAI_API_KEY, GITHUB_TOKEN 等)
- 初始化 ChatOpenAI 客户端，支持自定义 API 端点 (如智谱 GLM)
- 提供模型降级逻辑，当主模型失败时尝试备用模型

**关键函数**:
```python
class Config:  # 配置类
    - OPENAI_API_KEY: OpenAI API 密钥
    - OPENAI_MODEL: 使用的模型名称 (默认 glm-4.7)
    - OPENAI_BASE_URL: 自定义 API 端点
    - GITHUB_TOKEN: GitHub API Token

def get_llm():  # 获取 LLM 客户端
    - 返回 ChatOpenAI 实例
    - 支持自定义 base_url
    - 包含降级处理逻辑
```

#### core/utils.py
**功能**: 通用工具函数

**主要功能**:
- 解析 GitHub URL，提取 owner 和 repo
- 验证 GitHub URL 格式
- 截断过长文本
- 格式化目录结构为树形展示

**关键函数**:
```python
def parse_github_url(url: str) -> dict:
    # 解析 GitHub URL，返回 {"owner": "...", "repo": "...", "full_name": "..."}

def is_valid_github_url(url: str) -> bool:
    # 验证 URL 格式是否有效

def truncate_text(text: str, max_length: int = 5000) -> str:
    # 截断文本到指定长度

def format_directory_structure(structure: list, max_depth: int = 3, current_depth: int = 0) -> list:
    # 格式化目录结构为树形字符串列表
```

#### core/favorites.py
**功能**: 收藏仓库管理模块

**主要功能**:
- 管理用户收藏的仓库列表
- 提供添加、删除、查询收藏的功能
- 持久化存储收藏数据到本地文件

**关键函数**:
```python
def add_favorite(repo_url: str, repo_info: dict = None):
    # 添加仓库到收藏列表

def remove_favorite(repo_url: str):
    # 从收藏列表中移除仓库

def get_favorites() -> list:
    # 获取所有收藏的仓库

def is_favorite(repo_url: str) -> bool:
    # 检查仓库是否已收藏

def clear_favorites():
    # 清除所有收藏
```

#### core/history.py
**功能**: 历史记录管理模块

**主要功能**:
- 记录用户分析过的仓库历史
- 限制历史记录数量，保持最近的记录
- 提供添加、查询、删除历史记录的功能

**关键函数**:
```python
def add_history(repo_url: str, repo_info: dict = None):
    # 添加仓库到历史记录

def get_history() -> list:
    # 获取历史记录列表

def clear_history():
    # 清除所有历史记录

def remove_history_item(url: str):
    # 删除指定历史记录

def is_in_history(url: str) -> bool:
    # 检查 URL 是否在历史记录中
```

#### core/validators.py
**功能**: URL 验证和错误处理模块

**主要功能**:
- 验证 GitHub URL 格式是否正确
- 检查仓库是否存在（公开或私有）
- 处理 API 错误并返回友好的错误消息

**关键函数**:
```python
def validate_github_url(url: str) -> dict:
    # 验证 GitHub URL 并返回详细结果

def check_repo_exists(repo_url: str, github_token: str = None) -> dict:
    # 检查仓库是否存在

def handle_api_error(error: Exception) -> dict:
    # 处理 API 错误并返回友好的错误消息
```

### 2.2 工具层 (tools/)

#### tools/github_tools.py
**功能**: GitHub API 交互工具

**主要功能**:
- 通过 GitHub REST API 获取仓库基本信息
- 获取仓库 README 内容
- 获取指定文件的内容

**关键类与函数**:
```python
class GitHubTools:
    def __init__(self):
        # 初始化请求头，支持 Token 认证

    def get_repo_info(self, repo_url: str) -> dict:
        # 获取仓库名称、描述、语言、star 数、README
        # 返回: {"name", "description", "language", "stargazers_count", "full_name", "html_url", "readme"}

    def get_file_content(self, repo_url: str, file_path: str) -> str:
        # 获取指定文件内容，限制 5000 字符

# LangChain @tool 装饰器导出
@tool
def get_repo_info(repo_url: str) -> str:
    # LangChain 工具函数

@tool
def get_file_content(repo_url: str, file_path: str) -> str:
    # LangChain 工具函数
```

#### tools/git_tools.py
**功能**: Git 仓库克隆和本地分析工具

**主要功能**:
- 克隆 GitHub 仓库到临时目录
- 分析仓库目录结构
- 自动清理临时目录

**关键类与函数**:
```python
class GitTools:
    def __init__(self):
        # 维护临时目录列表

    def clone_repo(self, repo_url: str) -> str:
        # 克隆仓库到临时目录，返回路径

    def analyze_structure(self, repo_url: str) -> dict:
        # 递归分析目录结构 (最大深度 3 层)
        # 过滤忽略: .git, __pycache__, node_modules, venv 等
        # 返回: {"structure": [...], "formatted": "..."}

# LangChain @tool 装饰器导出
@tool
def clone_repo(repo_url: str) -> str:
    # LangChain 工具函数

@tool
def analyze_structure(repo_url: str) -> str:
    # LangChain 工具函数
```

#### tools/file_tools.py
**功能**: 文件读取和项目类型检测工具

**主要功能**:
- 从仓库读取文件内容 (优先 API，失败则克隆)
- 检测项目类型 (Node.js, Python, Java, Go 等)

**关键类与函数**:
```python
class FileTools:
    def read_file_from_repo(self, repo_url: str, file_path: str) -> str:
        # 优先使用 GitHub API，失败则克隆仓库后读取
        # 限制文件大小 5000 字符

    def detect_project_type(self, repo_url: str) -> str:
        # 通过检查关键文件判断项目类型
        # package.json -> Node.js
        # requirements.txt/setup.py/pyproject.toml -> Python
        # pom.xml -> Java (Maven)
        # build.gradle -> Java (Gradle)
        # go.mod -> Go
        # Cargo.toml -> Rust
        # Dockerfile -> Docker

# LangChain @tool 装饰器导出
@tool
def read_file_from_repo(repo_url: str, file_path: str) -> str:
    # LangChain 工具函数

@tool
def detect_project_type(repo_url: str) -> str:
    # LangChain 工具函数
```

### 2.3 Agent 层 (agents/)

#### agents/analyzer.py
**功能**: 仓库分析 Agent

**主要功能**:
- 使用 LangChain create_openai_functions_agent 创建
- 调用工具获取仓库信息、目录结构、文件内容
- 识别项目类型、语言、依赖、主要模块

**关键函数**:
```python
# 工具列表
analyzer_tools = [get_repo_info, get_file_content, analyze_structure, detect_project_type]

# 系统提示
ANALYZER_SYSTEM_PROMPT = """
你是一个仓库分析专家...
职责:
1. 识别项目类型
2. 分析目录结构
3. 解析依赖关系
4. 提取关键信息
"""

def create_analyzer_agent() -> AgentExecutor:
    # 使用 create_openai_functions_agent 创建 Agent
    # 配置 max_iterations=10, verbose=True

def run_analyzer(repo_url: str) -> dict:
    # 执行分析，返回 {"success": bool, "analysis": str, "repo_url": str}
```

#### agents/doc_generator.py
**功能**: 文档生成 Agent

**主要功能**:
- 生成学习文档 (项目概述、技术栈、目录结构、核心模块)
- 生成启动指南 (环境要求、安装步骤、运行命令、常见问题)

**关键函数**:
```python
# 系统提示
DOCGEN_SYSTEM_PROMPT = """
你是一个文档生成专家...
输出格式:
## 学习文档
### 项目概述
### 技术栈
### 目录结构
### 核心模块

## 启动指南
### 环境要求
### 安装步骤
### 运行命令
### 常见问题
"""

def create_docgen_agent() -> AgentExecutor:
    # 使用 create_openai_functions_agent 创建 Agent
    # 工具: [get_repo_info]

def run_docgen(repo_url: str, analysis_result: str = None) -> dict:
    # 获取仓库信息后生成文档
    # 返回 {"success": bool, "learning_doc": str, "setup_guide": str, "repo_info": dict}
```

#### agents/chat.py
**功能**: 问答 Agent

**主要功能**:
- 回答用户关于项目的问题
- 解释代码功能和用途
- 提供运行和开发建议

**关键函数**:
```python
# 系统提示
CHAT_SYSTEM_PROMPT = """
你是一个 GitHub 仓库问答助手...
工具:
- get_repo_info: 获取仓库信息
- get_file_content: 获取文件内容
"""

def create_chat_agent() -> AgentExecutor:
    # 使用 create_openai_functions_agent 创建 Agent
    # 工具: [get_repo_info, get_file_content]
    # max_iterations=10

def run_chat(query: str, repo_url: str, chat_history: list = None) -> dict:
    # 传入项目上下文，运行问答
    # 返回 {"success": bool, "response": str, "repo_url": str}
```

#### agents/orchestrator.py
**功能**: 工作流协调器

**主要功能**:
- 协调 Analyzer 和 DocGen 的工作流程
- 整合分析结果和生成的文档
- 提供简化版本 run_simple 直接生成文档

**关键函数**:
```python
def run(repo_url: str) -> dict:
    # 完整工作流:
    # 1. 调用 run_analyzer(repo_url) 分析仓库
    # 2. 调用 run_docgen(repo_url, analysis) 生成文档
    # 返回 {"repo_url", "analysis", "learning_doc", "setup_guide", "repo_info", "success", "error"}

def run_simple(repo_url: str) -> dict:
    # 简化版本，直接调用 DocGen 生成文档
    # 跳过详细分析步骤
```

### 2.4 前端层 (pages/)

#### pages/1_🏠_Home.py
**功能**: 首页 - URL 输入和示例仓库

**主要功能**:
- URL 输入框，验证 GitHub URL 格式
- 调用 Orchestrator 进行仓库分析
- 展示示例仓库列表，支持一键试用

**关键逻辑**:
```python
# 1. 显示标题和说明
# 2. URL 输入框 (st.text_input)
# 3. 验证 URL (is_valid_github_url)
# 4. 点击"生成文档"后:
#    - 调用 agents.orchestrator.run(repo_url)
#    - 保存结果到 st.session_state["analysis_result"]
#    - 跳转到 Documentation 页面
# 5. 示例仓库按钮，点击后直接分析
```

#### pages/2_📚_Documentation.py
**功能**: 文档展示页面

**主要功能**:
- 展示仓库基本信息 (名称、描述、语言、stars)
- 展示学习文档 (标签页)
- 展示启动指南 (标签页)

**关键逻辑**:
```python
# 从 session_state 获取分析结果
analysis_result = st.session_state.get("analysis_result")

# 显示仓库信息
repo_info = analysis_result.get("repo_info", {})
# - full_name, html_url
# - description
# - language
# - stargazers_count

# 标签页布局
tab1, tab2 = st.tabs(["学习文档", "启动指南"])
# tab1: learning_doc
# tab2: setup_guide
```

#### pages/3_💬_Chat.py
**功能**: AI 问答页面

**主要功能**:
- 集成 Chat Agent 进行问答
- 维护聊天历史
- 提供快捷问题按钮

**关键逻辑**:
```python
# 检查分析结果
if not analysis_result:
    st.warning("请先在首页生成文档")
    st.stop()

# 聊天界面
st.session_state.messages = []  # 初始化

# 显示历史消息
for message in st.session_state.messages:
    st.chat_message(message["role"])

# 聊天输入
if prompt := st.chat_input("问关于这个项目的问题..."):
    # 调用 agents.chat.run_chat(prompt, repo_url, chat_history)
    # 保存消息到 session_state

# 侧边栏
# - 清空聊天历史
# - 快捷问题按钮
```

### 2.5 入口文件

#### app.py
**功能**: Streamlit 应用主入口

**主要功能**:
- 设置页面配置
- 定义多页面结构
- 页面文件位于 pages/ 目录

## 3. 数据流

### 3.1 主要流程

```
用户输入 URL → Home 页面
       ↓
调用 orchestrator.run(url)
       ↓
┌──────────────────────────────────────────┐
│  orchestrator.run()                      │
│  1. run_analyzer(url) → analysis         │
│     ↓                                    │
│  2. run_docgen(url, analysis) → docs     │
└──────────────────────────────────────────┘
       ↓
保存到 session_state
       ↓
跳转到 Documentation 页面
       ↓
展示 learning_doc + setup_guide
       ↓
用户跳转到 Chat 页面
       ↓
输入问题 → run_chat(query, url, history)
       ↓
返回回答 → 更新 UI
```

### 3.2 数据结构

**analysis_result (session_state)**:
```python
{
    "repo_url": "https://github.com/user/repo",
    "analysis": "项目分析结果...",
    "learning_doc": "## 学习文档\n\n...",
    "setup_guide": "## 启动指南\n\n...",
    "repo_info": {
        "name": "repo-name",
        "description": "项目描述",
        "language": "Python",
        "stargazers_count": 1000,
        "full_name": "user/repo",
        "html_url": "https://github.com/user/repo"
    },
    "success": True,
    "error": None
}
```

## 4. 技术栈

| 类别 | 技术 | 版本 | 用途 |
|------|------|------|------|
| **前端** | Streamlit | 1.40+ | 用户界面 |
| **Agent 框架** | LangChain | 1.0+ | Agent 构建 |
| **Agent 框架** | LangGraph | 0.2+ | 工作流协调 |
| **LLM** | OpenAI API | GPT-4 | 智能分析和生成 |
| **仓库分析** | HTTP Requests | - | GitHub API 交互 |
| **仓库分析** | GitPython | 3.1+ | Git 仓库操作 |
| **配置管理** | python-dotenv | 1.0+ | 环境变量 |
| **数据验证** | Pydantic | 2.6+ | 数据模型 |

## 5. 项目结构

```
GitGuide/
├── app.py                      # Streamlit 主入口
├── pages/                      # Streamlit 多页面
│   ├── 1_🏠_Home.py           # 首页（URL 输入）
│   ├── 2_📚_Documentation.py  # 文档展示页
│   └── 3_💬_Chat.py           # AI 问答页
│
├── agents/                     # LangChain Agent
│   ├── __init__.py
│   ├── orchestrator.py        # 协调器 Agent
│   ├── analyzer.py            # 仓库分析 Agent
│   ├── doc_generator.py       # 文档生成 Agent
│   └── chat.py                # 问答 Agent
│
├── tools/                      # 工具函数
│   ├── __init__.py
│   ├── github_tools.py        # GitHub API 工具
│   ├── git_tools.py           # GitPython 工具
│   └── file_tools.py          # 文件读取工具
│
├── core/                       # 核心模块
│   ├── __init__.py
│   ├── config.py              # 配置管理
│   ├── utils.py               # 工具函数
│   ├── favorites.py           # 收藏仓库管理
│   ├── history.py             # 历史记录管理
│   └── validators.py          # URL 验证和错误处理
│
├── data/                       # 数据存储
│   ├── favorites.json         # 收藏仓库数据
│   └── history.json           # 历史记录数据
│
├── memory-bank/                # 项目文档
│   ├── architecture.md        # 架构设计文档
│   ├── product-design-document.md # 产品设计文档
│   ├── tech-stack.md          # 技术栈文档
│   ├── implementation-plan.md # 实施计划
│   └── process.md             # 进度跟踪
│
├── requirements.txt            # Python 依赖
├── .env                       # 环境变量
├── .env.example               # 环境变量示例
├── .gitignore                 # Git 忽略文件
├── CLAUDE.md                  # Claude 配置指南
├── LICENSE                    # 许可证文件
└── README.md                  # 项目说明
```

## 6. 错误处理

### 6.1 常见错误类型

| 错误类型 | 来源 | 处理方式 |
|----------|------|----------|
| Invalid URL | core/utils.py | 显示错误提示，要求重新输入 |
| GitHub API 错误 | tools/github_tools.py | 返回 error 字典，显示具体错误 |
| 仓库克隆失败 | tools/git_tools.py | 返回错误，清理临时目录 |
| LLM 调用失败 | agents/*.py | 返回 success=False，包含错误信息 |
| 文件不存在 | tools/file_tools.py | 返回 "error": "File not found" |

### 6.2 Agent 错误处理

- **Analyzer Agent**: max_iterations=10，超过则返回部分结果
- **DocGen Agent**: max_iterations=5，主要依赖 LLM 能力
- **Chat Agent**: max_iterations=10，支持工具调用超时

## 7. 扩展性

### 7.1 添加新 Agent

1. 在 `agents/` 目录创建新文件
2. 使用 `create_openai_functions_agent` 创建 Agent
3. 在 `orchestrator.py` 中集成

### 7.2 添加新工具

1. 在对应 `tools/` 文件中添加类方法
2. 使用 `@tool` 装饰器导出
3. 在 Agent 的工具列表中添加

### 7.3 支持更多项目类型

修改 `tools/file_tools.py` 中的 `detect_project_type` 方法，添加新的文件类型检测。

---

*Last updated: 2026-03-19 17:00 PM*