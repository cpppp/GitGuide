# GitGuide 项目实施计划

> **文档版本**：v3.0  
> **最后更新**：2026-03-20  
> **更新说明**：基于产品设计文档v3.0，新增数据持久化和Multi-Agent架构升级迭代

***

## 概述

本文档基于产品设计文档 v3.0，详细规划 GitGuide 项目的后续实施步骤。MVP 阶段已完成，后续将按照迭代阶段逐步推进。

**项目状态**：v2.1 已完成 ✅

**核心目标**：将 GitGuide 从 MVP 升级为功能完善、用户体验优秀的 GitHub 仓库分析工具。

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

| 功能     | 状态 | 说明                    |
| :----- | :- | :-------------------- |
| 进度反馈 | ✅  | 实时进度条、分阶段状态提示 |
| 错误处理 | ✅  | URL验证、API限流提示、自动重试 |
| 历史记录 | ✅

### 用户体验优化（v1.1 - 已完成）

| 功能     | 状态 | 说明                    |
| :----- | :- | :-------------------- |
| 进度反馈 | ✅  | 实时进度条和状态提示 |
| 错误处理 | ✅  | URL验证、API限流提示、重试机制 |
| 历史记录 | ✅  | 本地存储分析历史 |
| 收藏仓库 | ✅  | 收藏功能持久化 |

### 架构重构（v2.0 - 已完成）

| 功能     | 状态 | 说明                    |
| :----- | :- | :-------------------- |
| 前后端分离 | ✅  | Vue 3 + FastAPI |
| WebSocket | ✅  | 实时进度推送 |
| 任务取消 | ✅  | 可靠的取消功能 |

### 功能增强（v2.1 - 已完成）

| 功能     | 状态 | 说明                    |
| :----- | :- | :-------------------- |
| 导出功能 | ✅  | Markdown、PDF、HTML |
| 代码图谱 | ✅  | 目录树可视化 |
| 深色模式 | ✅  | 主题切换 |
| 多语言 | ✅  | 中英文支持 |

***

## 迭代三：数据持久化（v3.0 - 计划中）

**优先级**：高  
**预计工作量**：5 天  
**目标**：实现数据持久化，支持AI问答记录和仓库文档的长期存储

### 步骤 3.1：数据库集成

**任务**：

1. 引入 SQLAlchemy ORM
2. 设计数据库模型（repositories, chat_messages, favorites, analysis_history）
3. 实现数据库连接和会话管理
4. 配置 Alembic 数据库迁移

**实现方案**：

```python
# backend/models/database.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

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
```

**验证方法**：

- [ ] 数据库表创建成功
- [ ] CRUD 操作正常
- [ ] 数据迁移脚本可执行

***

### 步骤 3.2：AI问答记录持久化

**任务**：

1. 实现问答记录保存到数据库
2. 实现问答记录查询（按仓库ID）
3. 实现问答记录删除功能
4. 切换仓库时清空当前问答记录

**实现方案**：

```python
# backend/database/crud.py
from sqlalchemy.orm import Session
from backend.models.database import Repository, ChatMessage

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

**验证方法**：

- [ ] 用户提问自动保存到数据库
- [ ] 切换仓库时问答记录正确处理
- [ ] 删除功能正常工作

***

### 步骤 3.3：仓库文档持久化

**任务**：

1. 分析完成后自动保存文档到数据库
2. 重新分析时更新已有文档
3. 支持离线查看已分析仓库
4. 实现文档删除功能

**实现方案**：

```python
# backend/database/crud.py
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
    
    def get_all_repositories(self, db: Session) -> list:
        return db.query(Repository).order_by(Repository.updated_at.desc()).all()
```

**验证方法**：

- [ ] 分析完成后文档自动保存
- [ ] 重新分析时文档正确更新
- [ ] 离线查看功能正常

***

### 步骤 3.4：代码图谱可视化

**任务**：

1. 实现目录树可视化组件
2. 实现文件统计展示（文件类型分布、代码行数统计）
3. 实现依赖关系展示（import关系、模块依赖）
4. 创建代码图谱标签页

**实现方案**：

```python
# backend/services/code_graph.py
from collections import defaultdict
from pathlib import Path
import os

class CodeGraphService:
    def analyze_structure(self, repo_path: str) -> dict:
        result = {
            "tree": self._build_tree(repo_path),
            "stats": self._get_file_stats(repo_path),
            "dependencies": self._analyze_dependencies(repo_path)
        }
        return result
    
    def _build_tree(self, repo_path: str, max_depth: int = 3) -> dict:
        tree = {"name": os.path.basename(repo_path), "children": []}
        self._traverse(Path(repo_path), tree, 0, max_depth)
        return tree
    
    def _get_file_stats(self, repo_path: str) -> dict:
        stats = defaultdict(lambda: {"count": 0, "lines": 0})
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                ext = Path(file).suffix or "other"
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = len(f.readlines())
                    stats[ext]["count"] += 1
                    stats[ext]["lines"] += lines
                except:
                    pass
        return dict(stats)
    
    def _analyze_dependencies(self, repo_path: str) -> dict:
        dependencies = {"imports": [], "modules": []}
        return dependencies
```

**验证方法**：

- [ ] 目录树正确显示
- [ ] 文件统计准确
- [ ] 依赖关系正确展示

***

### 步骤 3.5：数据导出导入

**任务**：

1. 实现用户数据导出（JSON格式）
2. 实现数据导入功能
3. 实现数据备份恢复

**验证方法**：

- [ ] 导出功能正常
- [ ] 导入功能正常
- [ ] 数据完整性验证

***

## 迭代四：Multi-Agent架构升级（v3.1 - 计划中）

**优先级**：高  
**预计工作量**：7 天  
**目标**：升级多Agent架构，实现并行处理和质量控制

### 步骤 4.1：SOP标准化流程定义

**任务**：

1. 定义标准化的分析流程
2. 创建 SOP 配置文件
3. 实现流程状态机

**实现方案**：

```python
# core/sop.py
GITGUIDE_SOP = {
    "name": "GitHub Repository Analysis",
    "version": "3.0",
    "stages": [
        {
            "id": "planning",
            "name": "任务规划",
            "agent": "PlannerAgent",
            "timeout": 30,
            "next": "analysis"
        },
        {
            "id": "analysis",
            "name": "仓库分析",
            "parallel": True,
            "sub_tasks": [
                {"id": "type_analysis", "agent": "TypeAnalyzer"},
                {"id": "structure_analysis", "agent": "StructureAnalyzer"},
                {"id": "dependency_analysis", "agent": "DependencyAnalyzer"}
            ],
            "next": "generation"
        },
        {
            "id": "generation",
            "name": "文档生成",
            "parallel": True,
            "sub_tasks": [
                {"id": "readme_generation", "agent": "ReadmeGenerator"},
                {"id": "learning_doc_generation", "agent": "LearningDocGenerator"},
                {"id": "setup_guide_generation", "agent": "SetupGuideGenerator"}
            ],
            "next": "review"
        },
        {
            "id": "review",
            "name": "质量审核",
            "agent": "ReviewerAgent",
            "next": "optimization"
        },
        {
            "id": "optimization",
            "name": "迭代优化",
            "agent": "OptimizerAgent",
            "max_iterations": 3,
            "next": "finalization"
        }
    ]
}
```

**验证方法**：

- [ ] SOP 流程配置正确
- [ ] 状态机转换正常

***

### 步骤 4.2：并行分析处理

**任务**：

1. 实现 Analyzer Team（TypeAnalyzer, StructureAnalyzer, DependencyAnalyzer, CodePatternAnalyzer）
2. 实现 Generator Team（ReadmeGenerator, LearningDocGenerator, SetupGuideGenerator, VisualDocGenerator）
3. 使用 LangGraph 构建并行工作流
4. 实现共享上下文机制

**实现方案**：

```python
# agents/workflow.py
from langgraph.graph import StateGraph, END
import asyncio
from concurrent.futures import ThreadPoolExecutor

class ParallelExecutor:
    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
    async def execute_parallel(self, tasks: list, context: SharedContext) -> list:
        loop = asyncio.get_event_loop()
        futures = [
            loop.run_in_executor(self.executor, task.run, context)
            for task in tasks
        ]
        results = await asyncio.gather(*futures, return_exceptions=True)
        return results

def build_gitguide_graph():
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
    
    # 设置并行边
    graph.set_entry_point("planner")
    graph.add_edge("planner", "type_analyzer")
    graph.add_edge("planner", "structure_analyzer")
    graph.add_edge("planner", "dependency_analyzer")
    
    return graph.compile()
```

**验证方法**：

- [ ] 并行分析任务正常执行
- [ ] 分析时间显著减少
- [ ] 结果正确合并

***

### 步骤 4.3：质量控制机制

**任务**：

1. 实现 Reviewer Agent（文档质量审核）
2. 实现 Optimizer Agent（迭代优化）
3. 定义质量检查清单
4. 实现多轮优化循环

**实现方案**：

```python
# agents/reviewer.py
class ReviewerAgent:
    QUALITY_CHECKLIST = [
        {
            "id": "completeness",
            "name": "完整性检查",
            "items": ["项目概述是否完整", "技术栈是否列出", "启动命令是否正确"]
        },
        {
            "id": "accuracy",
            "name": "准确性检查",
            "items": ["语言识别是否正确", "框架识别是否正确", "依赖版本是否准确"]
        },
        {
            "id": "readability",
            "name": "可读性检查",
            "items": ["结构是否清晰", "语言是否流畅", "示例是否充分"]
        }
    ]
    
    def review(self, documents: dict) -> ReviewResult:
        scores = {}
        issues = []
        
        for checklist in self.QUALITY_CHECKLIST:
            category_score, category_issues = self._check_category(documents, checklist)
            scores[checklist["id"]] = category_score
            issues.extend(category_issues)
        
        overall_score = sum(scores.values()) / len(scores)
        
        return ReviewResult(
            scores=scores,
            overall_score=overall_score,
            issues=issues,
            passed=overall_score >= 0.8
        )

# agents/optimizer.py
class OptimizerAgent:
    def __init__(self, max_iterations: int = 3):
        self.max_iterations = max_iterations
        
    def iterative_optimization(self, documents: dict, target_score: float = 0.9) -> tuple:
        current_docs = documents
        iterations = 0
        
        while iterations < self.max_iterations:
            review = self.reviewer.review(current_docs)
            
            if review.overall_score >= target_score:
                break
            
            current_docs = self.optimize(current_docs, review)
            iterations += 1
        
        return current_docs, review.overall_score, iterations
```

**验证方法**：

- [ ] 质量审核正常执行
- [ ] 迭代优化有效提升文档质量
- [ ] 质量评分准确

***

### 步骤 4.4：深度代码分析

**任务**：

1. 实现函数/类关系分析
2. 实现代码质量评分
3. 实现潜在问题检测
4. 实现最佳实践建议

**验证方法**：

- [ ] 函数/类分析正确
- [ ] 质量评分合理
- [ ] 问题检测准确

***

### 步骤 4.5：API文档生成

**任务**：

1. 识别 REST API 端点
2. 提取函数签名和文档字符串
3. 生成 OpenAPI/Swagger 规范

**验证方法**：

- [ ] API端点识别正确
- [ ] OpenAPI规范生成正确

***

## 迭代五：协作与分享（v3.2 - 计划中）

**优先级**：中  
**预计工作量**：3 天

### 步骤 5.1：分享功能

**任务**：

1. 生成分享链接
2. 生成二维码
3. 添加社交媒体分享按钮

**验证方法**：

- [ ] 分享链接可访问
- [ ] 二维码可扫描

***

### 步骤 5.2：用户反馈系统

**任务**：

1. 文档质量评分
2. AI 回答满意度反馈
3. 问题报告功能

**验证方法**：

- [ ] 评分功能正常
- [ ] 反馈数据保存

***

## 迭代六：技术改进（v3.3 - 计划中）

**优先级**：中  
**预计工作量**：4 天

### 步骤 6.1：缓存优化

**任务**：

1. Redis 缓存集成
2. 分析结果持久化
3. 智能缓存失效

**验证方法**：

- [ ] 缓存命中时响应更快
- [ ] 缓存失效逻辑正确

***

### 步骤 6.2：多 LLM 支持

**任务**：

1. 支持 Claude API
2. 支持本地模型（Ollama）
3. 支持更多国产模型

**验证方法**：

- [ ] 模型切换正常
- [ ] 各模型回答质量

***

## 实施检查清单

### 迭代三检查项（v3.0）

- [ ] 数据库表创建成功
- [ ] AI问答记录持久化正常
- [ ] 仓库文档持久化正常
- [ ] 代码图谱可视化功能正常
- [ ] 数据导出导入功能正常

### 迭代四检查项（v3.1）

- [ ] SOP流程配置正确
- [ ] 并行分析正常执行
- [ ] 质量审核机制有效
- [ ] 深度代码分析功能
- [ ] API文档生成功能

### 迭代五检查项（v3.2）

- [ ] 分享功能
- [ ] 反馈系统

### 迭代六检查项（v3.3）

- [ ] 缓存优化
- [ ] 多 LLM 支持

***

*本实施计划将根据实际开发进度和用户反馈持续更新*

*Last updated: 2026-03-20*
