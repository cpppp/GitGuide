# GitGuide 项目实施计划

## 概述

本文档将产品设计文档 (`product-design-document.md`) 和技术栈文档 (`tech-stack.md`) 转化为详细的、分步骤的实施计划。每个步骤都包含具体的验证方法，确保实现正确。

**MVP 核心目标**：用户输入 GitHub 仓库 URL，系统生成学习文档和启动指南，并提供 AI 问答功能。

---

## 技术决策（已确认）

| 决策项 | 选择 | 原因 |
|:---|:---|:---|
| Agent 构建方式 | `create_agent` 或 LangChain 1.0+ 推荐方式 | 快速上手，LangChain 1.0+ 官方推荐 |
| 工具调用方式 | 简单同步调用 | MVP 阶段快速实现功能验证 |
| 缓存策略 | Streamlit Session State | MVP 阶段无需额外依赖 |
| 测试仓库 | `https://github.com/666ghj/DeepSearchAgent-Demo` | 用户指定 |
| 错误处理 | 显示具体错误信息 | 便于调试和用户体验 |

---

## 阶段一：环境搭建与基础项目结构

### 步骤 1.1：创建虚拟环境并安装依赖

**任务**：
1. 在项目根目录创建 Python 虚拟环境
2. 创建 `requirements.txt` 文件，添加以下核心依赖：
   - `streamlit>=1.40.0`
   - `langchain>=1.0.0`
   - `langchain-openai>=0.3.0`
   - `langgraph>=0.2.0`
   - `openai>=1.57.0`
   - `GitPython>=3.1.41`
   - `PyGithub>=2.1.1`
   - `python-dotenv>=1.0.0`
   - `pydantic>=2.6.0`
3. 安装所有依赖：`pip install -r requirements.txt`

**注意**：LangChain 1.0.x 版本有重大变化：
- 使用 `langchain_core.tools` 替代 `langchain.tools`
- 使用 `langchain_core.messages` 替代 `langchain.schema`
- 推荐使用 `create_agent` 或 `AgentExecutor`

**验证方法**：运行 `pip list` 确认所有包已安装。

---

### 步骤 1.2：配置环境变量

**任务**：
1. 创建 `.env` 文件
2. 添加 `OPENAI_API_KEY=your_openai_api_key`
3. 可选：添加 `GITHUB_TOKEN=your_github_token` 提高 API 限流
4. 创建 `.env.example` 文件作为模板

**验证方法**：
```python
from dotenv import load_dotenv
import os
load_dotenv()
print(os.getenv("OPENAI_API_KEY"))  # 应输出非 None
```

---

### 步骤 1.3：创建项目目录结构

**任务**：创建以下目录和空 `__init__.py` 文件：
```
GitGuide/
├── app.py
├── pages/
│   ├── 1_🏠_Home.py
│   ├── 2_📚_Documentation.py
│   └── 3_💬_Chat.py
├── agents/
│   ├── __init__.py
│   ├── orchestrator.py
│   ├── analyzer.py
│   ├── doc_generator.py
│   └── chat.py
├── tools/
│   ├── __init__.py
│   ├── github_tools.py
│   ├── git_tools.py
│   └── file_tools.py
├── core/
│   ├── __init__.py
│   ├── config.py
│   └── utils.py
├── memory-bank/
├── requirements.txt
├── .env
└── .env.example
```

**验证方法**：`ls -R` 确认目录结构正确。

---

### 步骤 1.4：创建 Streamlit 基础页面

**任务**：
1. 在 `app.py` 中添加页面配置：
   ```python
   import streamlit as st
   st.set_page_config(page_title="GitGuide", page_icon="🚀")
   ```
2. 在 `pages/1_🏠_Home.py` 中创建简单首页，显示标题和说明文字
3. 确保 Streamlit 可以正常启动

**验证方法**：运行 `streamlit run app.py`，确认页面可以正常打开。

---

## 阶段二：GitHub API 工具层（同步调用）

### 步骤 2.1：实现 GitHub 仓库信息获取工具

**任务**：
1. 在 `tools/github_tools.py` 中实现 `get_repo_info(repo_url: str)` 函数
2. 使用 PyGithub 库（同步调用）
3. 返回以下信息：
   - 仓库名称
   - 仓库描述
   - 主要编程语言
   - Star 数量
   - README 内容（如果有）
4. 添加异常处理，捕获并显示具体错误：
   - `GithubException` - GitHub API 错误
   - `InvalidUrlException` - 无效 URL
   - 其他异常

**验证方法**：
```python
from tools.github_tools import get_repo_info
result = get_repo_info("https://github.com/666ghj/DeepSearchAgent-Demo")
print(result.keys())  # 应包含: name, description, language, stars, readme
```

---

### 步骤 2.2：实现文件内容获取工具

**任务**：
1. 在 `tools/github_tools.py` 中实现 `get_file_content(repo_url: str, file_path: str)` 函数
2. 返回指定文件的内容
3. 限制单个文件大小不超过 100KB（返回前 N 字符）
4. 添加异常处理

**验证方法**：获取项目的 `README.md` 或 `requirements.txt` 内容。

---

### 步骤 2.3：实现目录结构分析工具

**任务**：
1. 在 `tools/github_tools.py` 中实现 `get_repo_contents(repo_url: str, path: str = "")` 函数
2. 返回仓库目录结构（递归获取，深度限制为 2 层）
3. 过滤掉：`node_modules`, `__pycache__`, `.git`, `.venv`, `dist`, `build`
4. 返回结构化数据（如嵌套字典或列表）

**验证方法**：确认返回的目录结构包含主要目录且已过滤无关目录。

---

## 阶段三：LangChain Agent 实现

### 步骤 3.1：创建 LLM 客户端

**任务**：
1. 在 `core/config.py` 中：
   ```python
   from langchain_openai import ChatOpenAI
   from dotenv import load_dotenv
   import os

   load_dotenv()

   def get_llm(model: str = "gpt-4"):
       return ChatOpenAI(model=model)
   ```
2. 添加模型降级逻辑（可选）：如果 gpt-4 失败，尝试 gpt-3.5-turbo

**验证方法**：
```python
from core.config import get_llm
llm = get_llm()
response = llm.invoke("你好")
print(response.content)  # 应返回 AI 回复
```

---

### 步骤 3.2：定义 Agent 工具

**任务**：
1. 在 `tools/github_tools.py` 中使用 `langchain_core.tools` 装饰器：
   ```python
   from langchain_core.tools import tool

   @tool
   def get_repo_info(repo_url: str) -> str:
       """获取 GitHub 仓库的基本信息"""
       # 实现...
   ```
2. 将所有工具定义为 `@tool` 装饰器函数
3. 工具函数返回字符串（便于 Agent 处理）

**验证方法**：确认工具函数可以用 `.invoke()` 调用。

---

### 步骤 3.3：实现 Analyzer Agent

**任务**：
1. 在 `agents/analyzer.py` 中：
   ```python
   from langchain_openai import ChatOpenAI
   from langchain_core.tools import tool
   from langchain.agents import create_agent

   # 工具列表
   tools = [get_repo_info, get_file_content, get_repo_contents]

   # 创建 Agent
   llm = ChatOpenAI(model="gpt-4")
   agent = create_agent(llm, tools, prompt="你是一个仓库分析专家...")
   ```
2. Agent 的 prompt 应明确要求：
   - 识别项目类型（Node.js, Python, Java, Go, Docker）
   - 解析依赖关系
   - 分析目录结构
   - 输出结构化结果（JSON 格式）

**验证方法**：
```python
from agents.analyzer import agent
result = agent.invoke({"input": "分析 https://github.com/666ghj/DeepSearchAgent-Demo"})
print(result["output"])
```

---

### 步骤 3.4：实现 DocGen Agent

**任务**：
1. 在 `agents/doc_generator.py` 中创建 Agent
2. 输入：Analyzer 的输出 + 原始仓库信息
3. 输出：
   - **学习文档**：项目概述、技术栈、目录结构、核心模块
   - **启动指南**：环境要求、安装步骤、运行命令
4. 使用 `create_agent` 或直接使用 LLM + prompt

**验证方法**：输入测试项目，确认生成包含必要章节的文档。

---

### 步骤 3.5：实现 Chat Agent

**任务**：
1. 在 `agents/chat.py` 中创建 Agent
2. 输入：用户问题 + 项目上下文（README + 分析结果）
3. 输出：回答用户关于项目的问题

**验证方法**：
```python
from agents.chat import chat_agent
response = chat_agent.invoke({
    "input": "这个项目是用来做什么的？",
    "context": "项目是一个..."
})
print(response["output"])
```

---

### 步骤 3.6：实现 Orchestrator

**任务**：
1. 在 `agents/orchestrator.py` 中：
   ```python
   def run(repo_url: str) -> dict:
       # 1. 调用 Analyzer
       analysis = analyzer_agent.invoke({"input": f"分析 {repo_url}"})

       # 2. 调用 DocGen
       docs = docgen_agent.invoke({
           "input": f"生成文档，仓库信息: {analysis['output']}"
       })

       # 3. 返回结果
       return {
           "analysis": analysis["output"],
           "learning_doc": docs["learning_doc"],
           "setup_guide": docs["setup_guide"]
       }
   ```
2. 协调 Analyzer → DocGen 的工作流程
3. 添加异常处理，每步失败时显示具体错误

**验证方法**：传入测试仓库 URL，确认返回完整结果。

---

## 阶段四：Streamlit 页面实现

### 步骤 4.1：实现首页（URL 输入）

**任务**：
1. 在 `pages/1_🏠_Home.py` 中：
   ```python
   import streamlit as st
   from agents.orchestrator import run

   st.title("🚀 GitGuide")
   st.markdown("快速上手任意 GitHub 仓库")

   url = st.text_input("输入 GitHub 仓库 URL", placeholder="https://github.com/user/repo")

   if st.button("生成文档", type="primary"):
       if url:
           with st.spinner("正在分析仓库..."):
               try:
                   result = run(url)
                   st.session_state["analysis_result"] = result
                   st.switch_page("pages/2_📚_Documentation.py")
               except Exception as e:
                   st.error(f"分析失败: {str(e)}")
   ```

**验证方法**：输入 `https://github.com/666ghj/DeepSearchAgent-Demo`，确认跳转到文档页面。

---

### 步骤 4.2：实现文档展示页面

**任务**：
1. 在 `pages/2_📚_Documentation.py` 中：
   ```python
   import streamlit as st

   st.title("📚 学习文档")

   result = st.session_state.get("analysis_result")
   if not result:
       st.warning("请先从首页生成文档")
       st.stop()

   tab1, tab2 = st.tabs(["学习文档", "启动指南"])

   with tab1:
       st.markdown(result.get("learning_doc", ""))

   with tab2:
       setup = result.get("setup_guide", "")
       st.markdown(setup)
   ```

**验证方法**：从首页进入，确认两个标签页都显示内容。

---

### 步骤 4.3：实现 AI 问答页面

**任务**：
1. 在 `pages/3_💬_Chat.py` 中：
   ```python
   import streamlit as st
   from agents.chat import chat_agent

   st.title("💬 AI 问答")

   if "messages" not in st.session_state:
       st.session_state.messages = []

   for msg in st.session_state.messages:
       with st.chat_message(msg["role"]):
           st.markdown(msg["content"])

   if prompt := st.chat_input("问关于这个项目的问题..."):
       st.session_state.messages.append({"role": "user", "content": prompt})

       with st.chat_message("user"):
           st.markdown(prompt)

       with st.chat_message("assistant"):
       # 调用 Chat Agent
       ```

**验证方法**：提问"如何运行这个项目？"，确认 AI 返回回答。

---

## 阶段五：测试与验证

### 步骤 5.1：端到端流程测试

**任务**：
1. 使用测试仓库：`https://github.com/666ghj/DeepSearchAgent-Demo`
2. 完整运行：
   - 首页输入 URL
   - 点击生成
   - 跳转到文档页面
   - 查看学习文档和启动指南
3. 验证：
   - 分析是否成功完成
   - 文档内容是否完整
   - 启动指南命令是否正确

**验证方法**：记录测试结果，确认无报错。

---

### 步骤 5.2：AI 问答功能测试

**任务**：
1. 在问答页面提问：
   - "这个项目是用来做什么的？"
   - "如何在本地运行这个项目？"
   - "主要依赖有哪些？"
2. 验证回答是否基于仓库实际内容

**验证方法**：检查 AI 回答的相关性。

---

## 阶段六：MVP 完成

### 步骤 6.1：创建 README.md

**任务**：
1. 在项目根目录创建 README.md
2. 包含：项目简介、功能列表、技术栈、快速开始指南、环境变量说明

**验证方法**：README.md 完整可读。

---

### 步骤 6.2：部署到 Streamlit Cloud

**任务**：
1. 推送代码到 GitHub
2. 登录 Streamlit Cloud
3. 关联仓库并部署
4. 配置环境变量（OPENAI_API_KEY）

**验证方法**：通过公开 URL 访问应用，确认功能正常。

---

## 实施检查清单

- [ ] 环境变量正确配置
- [ ] Streamlit 应用可以启动
- [ ] 可以分析 GitHub 仓库 `https://github.com/666ghj/DeepSearchAgent-Demo`
- [ ] 文档页面正确显示学习文档和启动指南
- [ ] AI 问答功能正常工作
- [ ] 端到端流程测试通过
- [ ] README.md 已创建
- [ ] 已部署到 Streamlit Cloud

---

## 错误处理示例

所有 API 调用都应捕获异常并显示具体信息：

```python
try:
    result = get_repo_info(url)
except Exception as e:
    st.error(f"获取仓库信息失败: {type(e).__name__}: {str(e)}")
```

常见错误类型：
- `GithubException` - GitHub API 限流或权限问题
- `InvalidUrlException` - URL 格式不正确
- `AuthenticationError` - OpenAI API Key 无效
- `RateLimitError` - OpenAI API 限流