# GitGuide 项目实施计划

> **文档版本**：v3.2\
> **最后更新**：2026-03-21\
> **更新说明**：新增 Chat Agent 两步迭代设计，第一阶段基础问答，第二阶段 RAG 增强

***

## 概述

本文档基于产品设计文档 v3.2，详细规划 GitGuide 项目的后续实施步骤。MVP 阶段已完成，V3.0 Multi-Agent架构升级已完成，当前重点为 V3.1 文档质量提升和 V3.2 AI 问答功能升级。

**项目状态**：v3.0 已完成 ✅

**核心目标**：

1. V3.1：扩展文档类型，提升文档质量（优先阶段）
2. V3.2：升级 AI 问答功能，实现真正理解仓库的智能问答（两步迭代）

***

## 已完成阶段回顾

### MVP 功能（v1.0 - 已完成）

| 功能     | 状态 | 说明                    |
| :----- | :- | :-------------------- |
| URL 输入 | ✅  | 支持公开 GitHub 仓库 URL 输入 |
| 一键生成   | ✅  | 点击按钮自动分析仓库            |
| 学习文档   | ✅  | 项目概述、技术栈、目录结构、依赖项     |
| 启动指南   | ✅  | 环境要求、安装命令、运行步骤        |
| AI 问答  | ✅  | 基于 LangChain 的智能问答    |

### 用户体验优化（v1.1 - 已完成）

| 功能   | 状态 | 说明                 |
| :--- | :- | :----------------- |
| 进度反馈 | ✅  | 实时进度条和状态提示         |
| 错误处理 | ✅  | URL验证、API限流提示、重试机制 |
| 历史记录 | ✅  | 本地存储分析历史           |
| 收藏仓库 | ✅  | 收藏功能持久化            |

### 架构重构（v2.0 - 已完成）

| 功能        | 状态 | 说明              |
| :-------- | :- | :-------------- |
| 前后端分离     | ✅  | Vue 3 + FastAPI |
| WebSocket | ✅  | 实时进度推送          |
| 任务取消      | ✅  | 可靠的取消功能         |

### 功能增强（v2.1 - 已完成）

| 功能   | 状态 | 说明                |
| :--- | :- | :---------------- |
| 导出功能 | ✅  | Markdown、PDF、HTML |
| 深色模式 | ✅  | 主题切换              |
| 多语言  | ✅  | 中英文支持             |

### 数据持久化（v2.2 - 已完成）

| 功能      | 状态 | 说明                  |
| :------ | :- | :------------------ |
| 数据库集成   | ✅  | SQLite + SQLAlchemy |
| AI问答持久化 | ✅  | 问答记录保存到数据库          |
| 仓库文档持久化 | ✅  | 分析结果自动保存            |
| 数据导出导入  | ✅  | JSON格式数据备份恢复        |
| 收藏功能迁移  | ✅  | 从JSON迁移到数据库         |

### Multi-Agent架构升级（v3.0 - 已完成）

| 功能               | 状态 | 说明                                   |
| :--------------- | :- | :----------------------------------- |
| SOP标准化流程         | ✅  | 定义标准化的分析流程                           |
| Supervisor Agent | ✅  | Planner、Scheduler、Reviewer、Optimizer |
| Analyzer Team    | ✅  | 4个分析器并行执行                            |
| Generator Team   | ✅  | 4个核心生成器                              |
| 并行执行引擎           | ✅  | LangGraph + asyncio                  |
| 共享上下文机制          | ✅  | Agent间状态共享                           |

***

## 迭代五：文档质量提升（v3.1 - 优先阶段）

**优先级**：高\
**预计工作量**：5 天\
**目标**：扩展文档类型，提升文档质量，满足新学习者需求

### 步骤 5.1：文档类型扩展

**预计时间**：3 天

#### 5.1.1 Generator Team 扩展

**任务**：

1. 实现 TutorialGenerator：使用教程文档
2. 实现 DevGuideGenerator：开发指南文档
3. 实现 TroubleshootGenerator：故障排查文档

**实现方案**：

```python
# agents/generators/tutorial_generator.py

class TutorialGenerator:
    """使用教程文档生成器"""
    
    TEMPLATE = """
    # 使用教程
    
    ## 基础用法
    {basic_usage}
    
    ## 进阶用法
    {advanced_usage}
    
    ## API 参考
    {api_reference}
    
    ## 最佳实践
    {best_practices}
    
    ## 示例代码
    {examples}
    """
    
    async def generate(self, context: SharedContext) -> str:
        analysis = context.get_analysis_results()
        
        basic_usage = await self._generate_basic_usage(analysis)
        advanced_usage = await self._generate_advanced_usage(analysis)
        api_reference = await self._extract_api_reference(analysis)
        best_practices = await self._generate_best_practices(analysis)
        examples = await self._extract_examples(analysis)
        
        return self.TEMPLATE.format(
            basic_usage=basic_usage,
            advanced_usage=advanced_usage,
            api_reference=api_reference,
            best_practices=best_practices,
            examples=examples
        )
```

**验证方法**：

- [ ] 3种新文档类型正确生成
- [ ] 文档内容完整、准确
- [ ] 文档格式统一

#### 5.1.2 数据库模型更新

**任务**：

1. 添加新文档字段到 repositories 表
2. 创建数据库迁移脚本

**SQL 更新**：

```sql
ALTER TABLE repositories ADD COLUMN usage_tutorial TEXT;
ALTER TABLE repositories ADD COLUMN dev_guide TEXT;
ALTER TABLE repositories ADD COLUMN troubleshooting TEXT;
```

**验证方法**：

- [ ] 数据库迁移成功
- [ ] 新字段正确存储文档

### 步骤 5.2：辅助素材生成

**预计时间**：2 天

#### 5.2.1 可视化素材生成

**任务**：

1. 实现架构图生成器（Mermaid 格式）
2. 实现目录树可视化
3. 实现代码图谱生成

**实现方案**：

```python
# services/visual_assets.py

class ArchitectureDiagramGenerator:
    """架构图生成器"""
    
    def generate(self, analysis_result: dict) -> dict:
        return {
            "type": "mermaid",
            "content": self._build_mermaid_diagram(analysis_result)
        }
    
    def _build_mermaid_diagram(self, analysis: dict) -> str:
        modules = analysis.get("modules", [])
        connections = analysis.get("connections", [])
        
        diagram = "graph TD\n"
        for module in modules:
            diagram += f"    {module['id']}[{module['name']}]\n"
        for conn in connections:
            diagram += f"    {conn['from']} --> {conn['to']}\n"
        
        return diagram


class DirectoryTreeGenerator:
    """目录树生成器"""
    
    def generate(self, repo_path: str) -> dict:
        return {
            "tree": self._build_tree(repo_path),
            "stats": self._get_file_stats(repo_path)
        }
```

**验证方法**：

- [ ] 架构图正确生成
- [ ] 目录树准确展示
- [ ] 代码图谱数据准确

### 步骤 5.3：前端界面适配

**预计时间**：2 天

#### 5.3.1 文档展示组件更新

**任务**：

1. 实现多标签页文档展示（7种文档类型）
2. 实现辅助素材展示组件
3. 实现质量评分展示

**组件更新**：

```vue
<!-- frontend/src/views/Documentation.vue -->

<template>
  <div class="documentation">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="快速入门" name="quick_start">
        <QuickStartDoc :content="result.quick_start" />
      </el-tab-pane>
      <el-tab-pane label="项目概览" name="overview">
        <OverviewDoc :content="result.overview_doc" />
      </el-tab-pane>
      <el-tab-pane label="架构设计" name="architecture">
        <ArchitectureDoc :content="result.architecture_doc" />
      </el-tab-pane>
      <el-tab-pane label="安装部署" name="install">
        <InstallGuideDoc :content="result.install_guide" />
      </el-tab-pane>
      <el-tab-pane label="使用教程" name="tutorial">
        <TutorialDoc :content="result.usage_tutorial" />
      </el-tab-pane>
      <el-tab-pane label="开发指南" name="dev">
        <DevGuideDoc :content="result.dev_guide" />
      </el-tab-pane>
      <el-tab-pane label="故障排查" name="troubleshoot">
        <TroubleshootDoc :content="result.troubleshooting" />
      </el-tab-pane>
    </el-tabs>
    
    <div class="quality-score">
      <span>文档质量评分: {{ result.quality_score }}分</span>
    </div>
    
    <div class="visual-assets">
      <ArchitectureDiagram :data="result.architecture_diagram" />
      <DirectoryTree :data="result.directory_tree" />
      <CodeGraph :data="result.code_graph" />
    </div>
  </div>
</template>
```

**验证方法**：

- 文档标签页切换正常
- 辅助素材正确展示
- 质量评分显示正确

***

## 迭代六：AI问答功能升级（v3.2 - 两步迭代）

**优先级**：高\
**预计工作量**：7 天\
**目标**：升级 AI 问答功能，实现真正理解仓库的智能问答
**依赖**：V3.1 文档质量提升完成

### Chat Agent 两步迭代设计

```
┌─────────────────────────────────────────────────────────────┐
│                     Chat Agent 两步迭代                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              第一步：基础问答（无 RAG）                 │    │
│  │                                                       │    │
│  │  目标：快速实现可用的问答功能                          │    │
│  │                                                       │    │
│  │  架构：                                               │    │
│  │  用户问题 ──► 问题分类 ──► 上下文构建 ──► LLM 回答    │    │
│  │                    │                                  │    │
│  │                    ▼                                  │    │
│  │         ┌──────────────────────┐                     │    │
│  │         │   上下文来源：        │                     │    │
│  │         │ 1. GitHub 工具实时获取│                     │    │
│  │         │ 2. 已生成的文档内容   │                     │    │
│  │         │ 3. 分析结果数据       │                     │    │
│  │         └──────────────────────┘                     │    │
│  │                                                       │    │
│  │  特点：实现简单，无需额外依赖，快速上线                │    │
│  └─────────────────────────────────────────────────────┘    │
│                           │                                  │
│                           ▼                                  │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              第二步：RAG 增强（方案 C）                 │    │
│  │                                                       │    │
│  │  目标：精准检索，支持复杂问题                          │    │
│  │                                                       │    │
│  │  架构：                                               │    │
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

***

### 步骤 6.1：第一阶段 - 基础问答（无 RAG）

**状态**：⏳ 待开始\
**预计时间**：3 天

#### 6.1.1 设计目标

**核心思路**：利用现有的 GitHub 工具和已生成的文档，快速实现一个可用的问答功能。

| 特点 | 说明 |
|:---|:---|
| **快速实现** | 无需引入新的依赖，复用现有工具 |
| **实时获取** | 通过 GitHub 工具实时获取文件内容 |
| **文档利用** | 充分利用已生成的 7 种文档 |
| **上下文构建** | 智能组合多个来源构建回答上下文 |

#### 6.1.2 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│              第一阶段：基础问答架构                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  用户问题                                                    │
│      │                                                       │
│      ▼                                                       │
│  ┌─────────────────┐                                        │
│  │   问题分类器     │                                        │
│  │  - 项目理解类    │                                        │
│  │  - 代码解释类    │                                        │
│  │  - 运行指导类    │                                        │
│  │  - 问题排查类    │                                        │
│  └────────┬────────┘                                        │
│           │                                                  │
│           ▼                                                  │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                   上下文构建器                        │    │
│  │                                                       │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │    │
│  │  │ GitHub 工具 │  │ 文档检索器  │  │ 分析结果    │  │    │
│  │  │ - get_file  │  │ - README    │  │ - 项目类型  │  │    │
│  │  │ - get_dir   │  │ - 安装指南  │  │ - 依赖关系  │  │    │
│  │  │ - get_readme│  │ - 架构文档  │  │ - 入口点    │  │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │    │
│  │           │              │              │            │    │
│  │           └──────────────┼──────────────┘            │    │
│  │                          ▼                            │    │
│  │              ┌─────────────────────┐                 │    │
│  │              │    上下文组合器      │                 │    │
│  │              │  - 相关性排序        │                 │    │
│  │              │  - 长度截断          │                 │    │
│  │              │  - 格式化输出        │                 │    │
│  │              └─────────────────────┘                 │    │
│  └─────────────────────────────────────────────────────┘    │
│                          │                                   │
│                          ▼                                   │
│              ┌─────────────────────┐                        │
│              │      LLM 回答       │                        │
│              │  - GPT-4 / GLM-4    │                        │
│              │  - 多轮对话记忆      │                        │
│              └─────────────────────┘                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

#### 6.1.3 实现代码

```python
# agents/chat.py - 第一阶段实现

from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from typing import Dict, List, Any, Optional
from enum import Enum

from core.config import get_llm, get_settings
from tools.github_tools import get_file_content, get_readme, get_directory_structure


class QuestionType(Enum):
    PROJECT_UNDERSTANDING = "project_understanding"
    CODE_EXPLANATION = "code_explanation"
    RUN_GUIDANCE = "run_guidance"
    TROUBLESHOOTING = "troubleshooting"
    GENERAL = "general"


class BasicChatAgent:
    """第一阶段：基础问答 Agent（无 RAG）"""
    
    def __init__(self):
        self.llm = get_llm()
        self.memories: Dict[str, ConversationBufferMemory] = {}
        
    def _classify_question(self, query: str) -> QuestionType:
        """问题分类"""
        keywords = {
            QuestionType.PROJECT_UNDERSTANDING: ["做什么", "功能", "用途", "介绍"],
            QuestionType.CODE_EXPLANATION: ["函数", "代码", "实现", "原理"],
            QuestionType.RUN_GUIDANCE: ["运行", "安装", "启动", "配置"],
            QuestionType.TROUBLESHOOTING: ["报错", "错误", "问题", "失败"],
        }
        
        query_lower = query.lower()
        for q_type, words in keywords.items():
            if any(word in query_lower for word in words):
                return q_type
        return QuestionType.GENERAL
    
    def _build_context(
        self,
        repo_url: str,
        query: str,
        question_type: QuestionType,
        analysis_result: Dict[str, Any],
        generated_docs: Dict[str, str]
    ) -> str:
        """构建上下文"""
        context_parts = []
        
        # 1. 基础项目信息
        context_parts.append(f"项目类型: {analysis_result.get('project_type', 'Unknown')}")
        context_parts.append(f"主要语言: {analysis_result.get('language', 'Unknown')}")
        
        # 2. 根据问题类型选择上下文来源
        if question_type == QuestionType.PROJECT_UNDERSTANDING:
            context_parts.append(f"\n项目描述:\n{analysis_result.get('description', '')}")
            context_parts.append(f"\nREADME:\n{generated_docs.get('readme', '')}")
            context_parts.append(f"\n项目概览:\n{generated_docs.get('overview_doc', '')}")
            
        elif question_type == QuestionType.RUN_GUIDANCE:
            context_parts.append(f"\n安装指南:\n{generated_docs.get('install_guide', '')}")
            context_parts.append(f"\n快速入门:\n{generated_docs.get('quick_start', '')}")
            if "entry_points" in analysis_result:
                context_parts.append(f"\n入口点: {', '.join(analysis_result['entry_points'])}")
                
        elif question_type == QuestionType.CODE_EXPLANATION:
            context_parts.append(f"\n架构设计:\n{generated_docs.get('architecture_doc', '')}")
            if "code_patterns" in analysis_result:
                for pattern in analysis_result["code_patterns"][:3]:
                    context_parts.append(f"\n代码模式 [{pattern['type']}]:\n{pattern['description']}")
                    
        elif question_type == QuestionType.TROUBLESHOOTING:
            context_parts.append(f"\n故障排查:\n{generated_docs.get('troubleshooting', '')}")
            context_parts.append(f"\n安装指南:\n{generated_docs.get('install_guide', '')}")
        
        # 3. 如果问题涉及特定文件，尝试获取
        import re
        file_match = re.search(r'(\S+\.(py|js|ts|java|go|rs))', query)
        if file_match:
            file_path = file_match.group(1)
            try:
                file_content = get_file_content(repo_url, file_path)
                if file_content:
                    context_parts.append(f"\n文件 {file_path} 内容:\n{file_content[:2000]}")
            except:
                pass
        
        return "\n".join(context_parts)
    
    def run_chat(
        self,
        repo_url: str,
        query: str,
        analysis_result: Dict[str, Any],
        generated_docs: Dict[str, str],
        history: Optional[List[Dict]] = None
    ) -> str:
        """处理用户问答"""
        # 初始化对话记忆
        if repo_url not in self.memories:
            self.memories[repo_url] = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
        
        memory = self.memories[repo_url]
        
        # 恢复历史对话
        if history:
            for msg in history:
                if msg["role"] == "user":
                    memory.chat_memory.add_user_message(msg["content"])
                elif msg["role"] == "assistant":
                    memory.chat_memory.add_ai_message(msg["content"])
        
        # 问题分类
        question_type = self._classify_question(query)
        
        # 构建上下文
        context = self._build_context(
            repo_url, query, question_type, analysis_result, generated_docs
        )
        
        # 构建 Prompt
        from langchain_core.prompts import ChatPromptTemplate
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个专业的代码助手，帮助用户理解 GitHub 仓库。
            
基于以下项目上下文回答用户问题。如果上下文中没有足够信息，请诚实说明。

项目上下文:
{context}

请用中文回答，保持简洁专业。"""),
            ("placeholder", "{chat_history}"),
            ("human", "{query}")
        ])
        
        # 构建链
        chain = prompt | self.llm
        
        # 获取对话历史
        chat_history = memory.load_memory_variables({}).get("chat_history", [])
        
        # 执行问答
        response = chain.invoke({
            "context": context,
            "chat_history": chat_history,
            "query": query
        })
        
        # 保存对话
        memory.chat_memory.add_user_message(query)
        memory.chat_memory.add_ai_message(response.content)
        
        return response.content


def run_basic_chat(
    repo_url: str,
    query: str,
    analysis_result: Dict[str, Any],
    generated_docs: Dict[str, str],
    history: Optional[List[Dict]] = None
) -> str:
    """基础问答接口"""
    agent = BasicChatAgent()
    return agent.run_chat(repo_url, query, analysis_result, generated_docs, history)
```

#### 6.1.4 API 集成

```python
# backend/api/chat.py - 第一阶段

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional, Dict
from agents.chat import run_basic_chat
from backend.database.crud import RepositoryCRUD, ChatMessageCRUD
from backend.database.config import get_db

router = APIRouter()


class ChatRequest(BaseModel):
    repo_url: str
    query: str
    history: Optional[List[dict]] = []


class ChatResponse(BaseModel):
    response: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """处理用户问答 - 第一阶段：基础问答"""
    db = next(get_db())
    
    # 获取仓库信息
    repo = RepositoryCRUD.get_by_url(db, request.repo_url)
    if not repo:
        return ChatResponse(response="请先分析此仓库。")
    
    # 构建分析结果
    analysis_result = {
        "project_type": repo.language,
        "language": repo.language,
        "description": repo.description,
        "entry_points": repo.analysis_result.get("entry_points", []) if repo.analysis_result else [],
        "code_patterns": repo.analysis_result.get("code_patterns", []) if repo.analysis_result else [],
    }
    
    # 构建已生成文档
    generated_docs = {
        "readme": repo.analysis_result.get("readme", "") if repo.analysis_result else "",
        "quick_start": repo.quick_start or "",
        "overview_doc": repo.overview_doc or "",
        "architecture_doc": repo.architecture_doc or "",
        "install_guide": repo.install_guide or "",
        "troubleshooting": repo.troubleshooting or "",
    }
    
    # 保存用户消息
    ChatMessageCRUD.create(db, repo.id, "user", request.query)
    
    # 调用基础问答
    response = run_basic_chat(
        repo_url=request.repo_url,
        query=request.query,
        analysis_result=analysis_result,
        generated_docs=generated_docs,
        history=request.history
    )
    
    # 保存 AI 回复
    ChatMessageCRUD.create(db, repo.id, "assistant", response)
    
    return ChatResponse(response=response)
```

#### 6.1.5 验证方法

- [ ] 问题分类器正确工作
- [ ] 上下文构建器能组合多个来源
- [ ] GitHub 工具能实时获取文件
- [ ] 多轮对话历史正确保存
- [ ] API 接口正常工作

***

### 步骤 6.2：第二阶段 - RAG 增强（方案 C）

**状态**：⏳ 待开始\
**预计时间**：4 天

#### 6.2.1 设计目标

**核心思路**：引入向量数据库和本地 Embedding 模型，实现精准的语义检索。

| 特点 | 说明 |
|:---|:---|
| **精准检索** | 基于语义相似度，而非关键词匹配 |
| **零 API 成本** | 使用 HuggingFace 本地模型 |
| **多语言支持** | 多语言模型，中英文效果均衡 |
| **知识库持久化** | 向量数据库本地存储 |

#### 6.2.2 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│              第二阶段：RAG 增强架构                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                 知识库构建（一次性）                    │    │
│  │                                                       │    │
│  │  输入来源：                                           │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │    │
│  │  │ 分析结果    │  │ 仓库文件    │  │ 生成文档    │  │    │
│  │  │ - 项目类型  │  │ - README    │  │ - 快速入门  │  │    │
│  │  │ - 依赖关系  │  │ - 配置文件  │  │ - 架构设计  │  │    │
│  │  │ - 代码模式  │  │ - 核心代码  │  │ - 安装指南  │  │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │    │
│  │           │              │              │            │    │
│  │           └──────────────┼──────────────┘            │    │
│  │                          ▼                            │    │
│  │              ┌─────────────────────┐                 │    │
│  │              │    文本分块器        │                 │    │
│  │              │  - 按段落/函数分割   │                 │    │
│  │              │  - 保留元数据        │                 │    │
│  │              └─────────────────────┘                 │    │
│  │                          │                            │    │
│  │                          ▼                            │    │
│  │              ┌─────────────────────┐                 │    │
│  │              │ HuggingFaceEmbeddings│                │    │
│  │              │ (本地模型，零成本)    │                │    │
│  │              └─────────────────────┘                 │    │
│  │                          │                            │    │
│  │                          ▼                            │    │
│  │              ┌─────────────────────┐                 │    │
│  │              │   Chroma VectorStore │                │    │
│  │              │   (本地持久化存储)    │                │    │
│  │              └─────────────────────┘                 │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                   问答流程                            │    │
│  │                                                       │    │
│  │  用户问题                                             │    │
│  │      │                                                │    │
│  │      ▼                                                │    │
│  │  ┌─────────────────────┐                             │    │
│  │  │   问题向量化         │                             │    │
│  │  │ (HuggingFaceEmbeddings)│                          │    │
│  │  └─────────────────────┘                             │    │
│  │      │                                                │    │
│  │      ▼                                                │    │
│  │  ┌─────────────────────┐                             │    │
│  │  │   向量检索 (MMR)     │                             │    │
│  │  │  - k=5, fetch_k=10   │                             │    │
│  │  │  - 多样性优化        │                             │    │
│  │  └─────────────────────┘                             │    │
│  │      │                                                │    │
│  │      ▼                                                │    │
│  │  ┌─────────────────────┐                             │    │
│  │  │   上下文构建         │                             │    │
│  │  │  - 检索结果排序      │                             │    │
│  │  │  - 长度控制          │                             │    │
│  │  └─────────────────────┘                             │    │
│  │      │                                                │    │
│  │      ▼                                                │    │
│  │  ┌─────────────────────┐                             │    │
│  │  │   LLM 生成回答       │                             │    │
│  │  │  + 多轮对话记忆      │                             │    │
│  │  └─────────────────────┘                             │    │
│  │                                                       │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

#### 6.2.3 实现代码

```python
# agents/chat_rag.py - 第二阶段实现

from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import Dict, List, Any, Optional
import os

from core.config import get_llm, get_settings


class KnowledgeBuilder:
    """构建仓库知识库（使用 HuggingFace 本地 Embeddings）"""
    
    def __init__(self, persist_dir: str = "./chroma_db"):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        self.persist_dir = persist_dir
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
        
    def build_from_analysis(
        self,
        repo_url: str,
        analysis_result: Dict[str, Any],
        generated_docs: Dict[str, str],
        repo_files: Dict[str, str]
    ) -> Chroma:
        """从分析结果构建知识库"""
        documents = []
        
        # 1. 项目基础信息
        if "project_type" in analysis_result:
            documents.append({
                "content": f"项目类型: {analysis_result['project_type']}",
                "metadata": {"type": "project_info", "source": "analysis"}
            })
        
        if "language" in analysis_result:
            documents.append({
                "content": f"主要语言: {analysis_result['language']}",
                "metadata": {"type": "project_info", "source": "analysis"}
            })
        
        if "description" in analysis_result:
            documents.append({
                "content": f"项目描述: {analysis_result['description']}",
                "metadata": {"type": "project_info", "source": "analysis"}
            })
        
        # 2. 依赖关系
        if "dependencies" in analysis_result:
            deps_text = "\n".join([
                f"- {dep.get('name', 'unknown')}: {dep.get('version', 'unknown')}"
                for dep in analysis_result["dependencies"]
            ])
            documents.append({
                "content": f"项目依赖:\n{deps_text}",
                "metadata": {"type": "dependencies", "source": "analysis"}
            })
        
        # 3. 入口点
        if "entry_points" in analysis_result:
            documents.append({
                "content": f"入口点: {', '.join(analysis_result['entry_points'])}",
                "metadata": {"type": "entry_points", "source": "analysis"}
            })
        
        # 4. 代码模式
        if "code_patterns" in analysis_result:
            for pattern in analysis_result["code_patterns"]:
                documents.append({
                    "content": f"代码模式 [{pattern.get('type', 'unknown')}]:\n{pattern.get('description', '')}",
                    "metadata": {
                        "type": "code_pattern",
                        "source": "analysis",
                        "file": pattern.get("file", "")
                    }
                })
        
        # 5. 生成的文档
        doc_mapping = {
            "quick_start": "快速入门",
            "overview_doc": "项目概览",
            "architecture_doc": "架构设计",
            "install_guide": "安装部署",
            "usage_tutorial": "使用教程",
            "dev_guide": "开发指南",
            "troubleshooting": "故障排查"
        }
        
        for doc_key, doc_name in doc_mapping.items():
            if doc_key in generated_docs and generated_docs[doc_key]:
                # 分块处理长文档
                chunks = self.text_splitter.split_text(generated_docs[doc_key])
                for i, chunk in enumerate(chunks):
                    documents.append({
                        "content": chunk,
                        "metadata": {
                            "type": "generated_doc",
                            "doc_name": doc_name,
                            "chunk_index": i,
                            "source": doc_key
                        }
                    })
        
        # 6. 仓库文件
        for file_path, file_content in repo_files.items():
            if file_content and len(file_content) > 100:
                chunks = self.text_splitter.split_text(file_content)
                for i, chunk in enumerate(chunks):
                    documents.append({
                        "content": chunk,
                        "metadata": {
                            "type": "source_code",
                            "file_path": file_path,
                            "chunk_index": i,
                            "source": "repo_file"
                        }
                    })
        
        # 构建向量数据库
        texts = [doc["content"] for doc in documents]
        metadatas = [doc["metadata"] for doc in documents]
        
        # 创建持久化目录
        repo_dir = os.path.join(self.persist_dir, repo_url.replace("/", "_").replace(":", "_"))
        os.makedirs(repo_dir, exist_ok=True)
        
        vectorstore = Chroma.from_texts(
            texts=texts,
            embedding=self.embeddings,
            metadatas=metadatas,
            persist_directory=repo_dir
        )
        
        return vectorstore


class RAGChatAgent:
    """第二阶段：RAG 增强 Chat Agent"""
    
    def __init__(self, persist_dir: str = "./chroma_db"):
        self.llm = get_llm()
        self.knowledge_builder = KnowledgeBuilder(persist_dir)
        self.vectorstores: Dict[str, Chroma] = {}
        self.memories: Dict[str, ConversationBufferMemory] = {}
        
    def initialize(
        self,
        repo_url: str,
        analysis_result: Dict[str, Any],
        generated_docs: Dict[str, str],
        repo_files: Dict[str, str]
    ):
        """初始化仓库知识库"""
        self.vectorstores[repo_url] = self.knowledge_builder.build_from_analysis(
            repo_url, analysis_result, generated_docs, repo_files
        )
        self.memories[repo_url] = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
    def run_chat(
        self,
        repo_url: str,
        query: str,
        history: Optional[List[Dict]] = None
    ) -> str:
        """处理用户问答 - RAG 增强"""
        if repo_url not in self.vectorstores:
            return "请先分析此仓库，我才能回答相关问题。"
        
        vectorstore = self.vectorstores[repo_url]
        memory = self.memories[repo_url]
        
        # 恢复历史对话
        if history:
            for msg in history:
                if msg["role"] == "user":
                    memory.chat_memory.add_user_message(msg["content"])
                elif msg["role"] == "assistant":
                    memory.chat_memory.add_ai_message(msg["content"])
        
        # 创建对话检索链
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=vectorstore.as_retriever(
                search_type="mmr",
                search_kwargs={"k": 5, "fetch_k": 10}
            ),
            memory=memory,
            return_source_documents=True,
            verbose=True
        )
        
        # 执行问答
        result = qa_chain({"question": query})
        
        return result["answer"]


def run_rag_chat(
    repo_url: str,
    query: str,
    analysis_result: Optional[Dict[str, Any]] = None,
    generated_docs: Optional[Dict[str, str]] = None,
    repo_files: Optional[Dict[str, str]] = None,
    history: Optional[List[Dict]] = None
) -> str:
    """RAG 问答接口"""
    agent = RAGChatAgent()
    
    if analysis_result and generated_docs:
        agent.initialize(repo_url, analysis_result, generated_docs, repo_files or {})
    
    return agent.run_chat(repo_url, query, history)
```

#### 6.2.4 API 集成

```python
# backend/api/chat.py - 第二阶段升级

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional, Dict
from agents.chat import run_basic_chat
from agents.chat_rag import run_rag_chat
from backend.database.crud import RepositoryCRUD, ChatMessageCRUD
from backend.database.config import get_db

router = APIRouter()


class ChatRequest(BaseModel):
    repo_url: str
    query: str
    history: Optional[List[dict]] = []
    use_rag: bool = True  # 是否使用 RAG


class ChatResponse(BaseModel):
    response: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """处理用户问答 - 支持基础问答和 RAG 增强"""
    db = next(get_db())
    
    # 获取仓库信息
    repo = RepositoryCRUD.get_by_url(db, request.repo_url)
    if not repo:
        return ChatResponse(response="请先分析此仓库。")
    
    # 构建分析结果
    analysis_result = {
        "project_type": repo.language,
        "language": repo.language,
        "description": repo.description,
        "dependencies": repo.analysis_result.get("dependencies", []) if repo.analysis_result else [],
        "entry_points": repo.analysis_result.get("entry_points", []) if repo.analysis_result else [],
        "code_patterns": repo.analysis_result.get("code_patterns", []) if repo.analysis_result else [],
    }
    
    # 构建已生成文档
    generated_docs = {
        "quick_start": repo.quick_start or "",
        "overview_doc": repo.overview_doc or "",
        "architecture_doc": repo.architecture_doc or "",
        "install_guide": repo.install_guide or "",
        "usage_tutorial": repo.usage_tutorial or "",
        "dev_guide": repo.dev_guide or "",
        "troubleshooting": repo.troubleshooting or "",
    }
    
    # 保存用户消息
    ChatMessageCRUD.create(db, repo.id, "user", request.query)
    
    # 选择问答模式
    if request.use_rag:
        response = run_rag_chat(
            repo_url=request.repo_url,
            query=request.query,
            analysis_result=analysis_result,
            generated_docs=generated_docs,
            history=request.history
        )
    else:
        response = run_basic_chat(
            repo_url=request.repo_url,
            query=request.query,
            analysis_result=analysis_result,
            generated_docs=generated_docs,
            history=request.history
        )
    
    # 保存 AI 回复
    ChatMessageCRUD.create(db, repo.id, "assistant", response)
    
    return ChatResponse(response=response)
```

#### 6.2.5 验证方法

- [ ] KnowledgeBuilder 正确构建向量数据库
- [ ] HuggingFaceEmbeddings 本地模型加载成功
- [ ] Chroma 向量数据库持久化正常
- [ ] MMR 检索返回相关上下文
- [ ] 多轮对话历史正确保存
- [ ] API 接口正常工作
- [ ] AI 回答基于仓库上下文

***

### 步骤 6.3：前端界面适配

**状态**：⏳ 待开始\
**预计时间**：2 天

**任务**：

- [ ] 实现多标签页文档展示（7种文档类型）
- [ ] 实现辅助素材展示组件
- [ ] 实现质量评分展示
- [ ] 更新数据库模型（添加新文档字段）

**预期产出**：

- 更新 `frontend/src/views/Documentation.vue`

**验证方法**：

- [ ] 文档标签页切换正常
- [ ] 辅助素材正确展示
- [ ] 质量评分显示正确

***

## 实施检查清单

### V3.1 检查项（文档质量提升）

**文档类型扩展**：

- [ ] 7种文档类型全部生成
- [ ] 文档内容完整、准确
- [ ] 数据库迁移成功

**辅助素材**：

- [ ] 架构图正确生成
- [ ] 目录树准确展示
- [ ] 代码图谱数据准确

**前端界面**：

- 文档标签页切换正常
- 辅助素材正确展示
- 质量评分显示正确

### V3.2 检查项（AI问答功能升级）

**第一阶段：基础问答**：

- [ ] 问题分类器正确工作
- [ ] 上下文构建器能组合多个来源
- [ ] GitHub 工具能实时获取文件
- [ ] 多轮对话历史正确保存
- [ ] API 接口正常工作

**第二阶段：RAG 增强**：

- [ ] KnowledgeBuilder 正确构建向量数据库
- [ ] HuggingFaceEmbeddings 本地模型加载成功
- [ ] Chroma 向量数据库持久化正常
- [ ] MMR 检索返回相关上下文
- [ ] AI 回答基于仓库上下文

**整体质量**：

- [ ] 文档质量评分 > 85 分
- [ ] AI 问答准确性 > 90%
- [ ] 用户满意度 > 90%

***

## 预期收益

| 维度 | V3.0 | V3.1 | V3.2 第一阶段 | V3.2 第二阶段 |
|:---|:---|:---|:---|:---|
| AI 问答可用性 | ❌ 功能不足 | ❌ 功能不足 | ✅ 基础问答 | ✅ RAG 精准检索 |
| 问答准确性 | 泛泛而谈 | 泛泛而谈 | 基于文档上下文 | 基于语义检索 |
| 多轮对话 | ❌ 不支持 | ❌ 不支持 | ✅ 支持 | ✅ 支持 |
| 文档类型 | 4种 | 7种 | 7种 | 7种 |
| 辅助素材 | 无 | 5种 | 5种 | 5种 |
| 文档质量 | 不稳定 | SOP保证稳定 | SOP保证稳定 | SOP保证稳定 |
| API 成本 | 需要 OpenAI | 需要 OpenAI | 需要 OpenAI | Embedding 零成本 |

***

*本实施计划将根据实际开发进度和用户反馈持续更新*

*Last updated: 2026-03-21*
