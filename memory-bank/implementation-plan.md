# GitGuide 项目实施计划

> **文档版本**：v3.2\
> **最后更新**：2026-03-20\
> **更新说明**：V3.1 Multi-Agent架构升级，V3.2 文档质量提升

***

## 概述

本文档基于产品设计文档 v3.2，详细规划 GitGuide 项目的后续实施步骤。MVP 阶段已完成，V3.0 数据持久化已完成，当前重点为 V3.1 Multi-Agent架构升级 和 V3.2 文档质量提升。

**项目状态**：v3.0 已完成 ✅

**核心目标**：

1. V3.1：升级 Multi-Agent 架构，实现并行处理，提高分析效率
2. V3.2：基于新学习者需求，全面提升文档质量和实用性

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

***

## 迭代四：Multi-Agent架构升级（v3.0 - 计划中）

**优先级**：高\
**预计工作量**：7 天\
**目标**：升级 Multi-Agent 架构，实现并行处理，提高分析效率

### 步骤 4.1：SOP标准化流程定义

**任务**：

1. 定义标准化的分析流程（Planning → Analysis → Generation → Review → Output）
2. 创建 SOP 配置文件
3. 实现流程状态机

**实现方案**：

```python
# core/sop.py
GITGUIDE_SOP = {
    "name": "GitHub Repository Analysis",
    "version": "3.1",
    "stages": [
        {
            "id": "planning",
            "name": "任务规划",
            "agent": "PlannerAgent",
            "timeout": 30,
            "outputs": ["task_list", "priority_order"]
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
            "timeout": 120
        },
        {
            "id": "generation",
            "name": "文档生成",
            "parallel": True,
            "sub_tasks": [
                {"id": "learning_doc", "agent": "LearningDocGenerator"},
                {"id": "setup_guide", "agent": "SetupGuideGenerator"}
            ],
            "timeout": 180
        },
        {
            "id": "review",
            "name": "质量审核",
            "agent": "ReviewerAgent",
            "outputs": ["quality_score", "issues"]
        }
    ]
}
```

**验证方法**：

- [ ] SOP 流程配置正确
- [ ] 状态机转换正常
- [ ] 各阶段输出符合预期

***

### 步骤 4.2：Supervisor Agent 实现

**任务**：

1. 实现 Planner（规划器）：任务分解和优先级排序
2. 实现 Scheduler（调度器）：并行任务调度
3. 实现 Reviewer（审核器）：文档质量审核
4. 实现 Optimizer（优化器）：文档优化建议

**实现方案**：

```python
# agents/supervisor.py
from langgraph.graph import StateGraph, END

class SupervisorAgent:
    def __init__(self):
        self.planner = PlannerAgent()
        self.scheduler = SchedulerAgent()
        self.reviewer = ReviewerAgent()
    
    async def run(self, context: SharedContext) -> dict:
        # 1. 规划阶段
        plan = await self.planner.plan(context)
        context.set_plan(plan)
        
        # 2. 调度执行
        results = await self.scheduler.execute_parallel(plan, context)
        context.set_results(results)
        
        # 3. 质量审核
        review = await self.reviewer.review(results)
        
        return results
```

**验证方法**：

- [ ] Planner 正确分解任务
- [ ] Scheduler 并行调度正常
- [ ] Reviewer 质量评分准确

***

### 步骤 4.3：Analyzer Team 实现

**任务**：

1. 实现 TypeAnalyzer：项目类型识别（Python/Node/Java/Go等）
2. 实现 StructureAnalyzer：目录结构分析、核心模块识别
3. 实现 DependencyAnalyzer：依赖关系分析、版本兼容性检查

**实现方案**：

```python
# agents/analyzers.py
class TypeAnalyzer:
    async def analyze(self, context: SharedContext) -> AnalysisResult:
        repo_path = context.repo_path
        
        project_type = self._detect_type(repo_path)
        frameworks = self._detect_frameworks(repo_path)
        
        return AnalysisResult(
            analyzer_id="type_analyzer",
            data={
                "project_type": project_type,
                "frameworks": frameworks
            }
        )

class StructureAnalyzer:
    async def analyze(self, context: SharedContext) -> AnalysisResult:
        repo_path = context.repo_path
        
        tree = self._build_tree(repo_path)
        core_modules = self._identify_core_modules(tree)
        
        return AnalysisResult(
            analyzer_id="structure_analyzer",
            data={
                "tree": tree,
                "core_modules": core_modules
            }
        )

class DependencyAnalyzer:
    async def analyze(self, context: SharedContext) -> AnalysisResult:
        repo_path = context.repo_path
        
        dependencies = self._parse_dependencies(repo_path)
        
        return AnalysisResult(
            analyzer_id="dependency_analyzer",
            data={"dependencies": dependencies}
        )
```

**验证方法**：

- [ ] 项目类型识别准确率 > 95%
- [ ] 目录结构分析正确
- [ ] 依赖关系解析完整

***

### 步骤 4.4：并行执行引擎实现

**任务**：

1. 使用 LangGraph 构建工作流图
2. 实现 asyncio + ThreadPoolExecutor 并行执行
3. 创建共享上下文机制

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
    
    graph.add_node("planner", planner_node)
    graph.add_node("type_analyzer", type_analyzer_node)
    graph.add_node("structure_analyzer", structure_analyzer_node)
    graph.add_node("dependency_analyzer", dependency_analyzer_node)
    graph.add_node("merger", merger_node)
    graph.add_node("doc_generator", doc_generator_node)
    
    graph.set_entry_point("planner")
    graph.add_edge("planner", "type_analyzer")
    graph.add_edge("planner", "structure_analyzer")
    graph.add_edge("planner", "dependency_analyzer")
    
    return graph.compile()
```

**验证方法**：

- [ ] 并行执行正常工作
- [ ] 分析时间显著减少（目标：减少60-80%）
- [ ] 共享上下文正确传递

***

### 步骤 4.5：集成测试与优化

**任务**：

1. 集成所有 Agent 组件
2. 端到端测试
3. 性能优化

**验证方法**：

- [ ] 完整流程测试通过
- [ ] 分析时间减少 60%+
- [ ] 并行效率 > 80%

***

## 迭代五：文档质量提升（v3.1 - 计划中）

**优先级**：高\
**预计工作量**：8 天\
**目标**：基于新学习者需求，全面提升文档质量和实用性

### 步骤 5.1：文档类型扩展

**任务**：

1. 实现快速入门文档生成器（QuickStartGenerator）
2. 实现项目概览文档生成器（OverviewGenerator）
3. 实现架构设计文档生成器（ArchitectureGenerator）
4. 实现安装部署文档生成器（InstallGuideGenerator）
5. 实现使用教程文档生成器（TutorialGenerator）
6. 实现开发指南文档生成器（DevGuideGenerator）
7. 实现故障排查文档生成器（TroubleshootingGenerator）

**文档内容规划**：

| 文档类型     | 核心内容                 |
| :------- | :------------------- |
| **快速入门** | 一句话概括、核心概念图解、最小化运行命令 |
| **项目概览** | 背景、功能列表、技术选型、适用场景    |
| **架构设计** | 架构图、模块说明、数据流、设计决策    |
| **安装部署** | 环境要求、安装步骤、配置说明、常见问题  |
| **使用教程** | 基础用法、进阶用法、API参考、示例代码 |
| **开发指南** | 目录结构、代码规范、开发环境、测试指南  |
| **故障排查** | 常见错误、调试技巧、日志说明、FAQ   |

**实现方案**：

````python
# agents/generators.py
class QuickStartGenerator:
    TEMPLATE = """
    # 快速入门
    
    ## 一句话概括
    {one_liner}
    
    ## 核心概念
    {core_concepts}
    
    ## 最小化运行
    ```bash
    {minimal_run}
    ```
    """
    
    async def generate(self, context: SharedContext) -> str:
        analysis = context.get_analysis_results()
        
        return await self._generate_with_llm(
            template=self.TEMPLATE,
            context=analysis
        )

class ArchitectureGenerator:
    async def generate(self, context: SharedContext) -> str:
        analysis = context.get_analysis_results()
        
        architecture = await self._analyze_architecture(analysis)
        modules = await self._identify_modules(analysis)
        data_flow = await self._trace_data_flow(analysis)
        
        return self._format_architecture_doc(architecture, modules, data_flow)
````

**验证方法**：

- [ ] 7种文档类型全部生成
- [ ] 文档内容完整、准确
- [ ] 文档格式统一

***

### 步骤 5.2：辅助素材生成

**任务**：

1. 实现架构图生成器
2. 实现目录树可视化
3. 实现代码图谱生成
4. 实现示例代码提取器

**实现方案**：

```python
# services/visual_assets.py
class ArchitectureDiagramGenerator:
    def generate(self, analysis_result: dict) -> dict:
        return {
            "type": "mermaid",
            "content": self._build_mermaid_diagram(analysis_result)
        }

class DirectoryTreeGenerator:
    def generate(self, repo_path: str) -> dict:
        return {
            "tree": self._build_tree(repo_path),
            "stats": self._get_file_stats(repo_path)
        }

class CodeGraphGenerator:
    def generate(self, repo_path: str) -> dict:
        return {
            "file_types": self._analyze_file_types(repo_path),
            "lines_of_code": self._count_lines(repo_path),
            "dependencies": self._analyze_dependencies(repo_path)
        }

class ExampleExtractor:
    def extract(self, repo_path: str) -> list:
        examples = []
        for file_path in self._find_example_files(repo_path):
            example = self._extract_example(file_path)
            examples.append(example)
        return examples
```

**验证方法**：

- [ ] 架构图正确生成
- [ ] 目录树准确展示
- [ ] 代码图谱数据准确
- [ ] 示例代码有效提取

***

### 步骤 5.3：质量控制机制

**任务**：

1. 实现质量评分系统
2. 实现多轮审核优化机制
3. 定义文档模板标准

**质量评分维度**：

| 维度  | 权重  | 评估内容                      |
| :-- | :-- | :------------------------ |
| 完整性 | 30% | 文档类型是否齐全、各章节是否完整、必要信息是否覆盖 |
| 准确性 | 30% | 技术信息是否正确、命令是否可执行、配置是否有效   |
| 可读性 | 20% | 结构是否清晰、语言是否流畅、示例是否充分      |
| 实用性 | 20% | 是否解决实际问题、是否有可操作步骤、是否有故障排查 |

**实现方案**：

```python
# agents/quality.py
class QualityScorer:
    DIMENSIONS = {
        "completeness": {"weight": 0.30, "checks": [...]},
        "accuracy": {"weight": 0.30, "checks": [...]},
        "readability": {"weight": 0.20, "checks": [...]},
        "practicality": {"weight": 0.20, "checks": [...]}
    }
    
    async def score(self, documents: dict) -> QualityScore:
        scores = {}
        for dimension, config in self.DIMENSIONS.items():
            scores[dimension] = await self._evaluate_dimension(documents, config)
        
        return QualityScore(
            completeness=scores["completeness"],
            accuracy=scores["accuracy"],
            readability=scores["readability"],
            practicality=scores["practicality"],
            overall=sum(scores.values())
        )

class DocOptimizer:
    def __init__(self, max_iterations: int = 3, target_score: float = 0.85):
        self.max_iterations = max_iterations
        self.target_score = target_score
    
    async def optimize(self, documents: dict, review: ReviewResult) -> dict:
        iteration = 0
        current_docs = documents
        
        while iteration < self.max_iterations:
            if review.overall_score >= self.target_score:
                break
            
            current_docs = await self._apply_suggestions(current_docs, review.issues)
            review = await self.reviewer.review(current_docs)
            iteration += 1
        
        return current_docs
```

**验证方法**：

- [ ] 质量评分准确反映文档质量
- [ ] 多轮优化有效提升文档质量
- [ ] 文档模板统一规范

***

### 步骤 5.4：前端界面适配

**任务**：

1. 实现多标签页文档展示
2. 实现辅助素材展示组件
3. 实现质量评分展示
4. 更新数据库模型

**数据库模型更新**：

```sql
-- 扩展 repositories 表
ALTER TABLE repositories ADD COLUMN quick_start TEXT;
ALTER TABLE repositories ADD COLUMN architecture_doc TEXT;
ALTER TABLE repositories ADD COLUMN usage_tutorial TEXT;
ALTER TABLE repositories ADD COLUMN dev_guide TEXT;
ALTER TABLE repositories ADD COLUMN troubleshooting TEXT;
ALTER TABLE repositories ADD COLUMN quality_score INTEGER DEFAULT 0;
```

**验证方法**：

- [ ] 文档标签页切换正常
- [ ] 辅助素材正确展示
- [ ] 质量评分显示正确
- [ ] 数据库迁移成功

***

### 步骤 5.5：集成测试与优化

**任务**：

1. 端到端测试
2. 文档质量评估
3. 用户体验优化

**验证方法**：

- [ ] 完整流程测试通过
- [ ] 文档质量评分 > 85 分
- [ ] 用户反馈收集

***

## 实施检查清单

### V3.1 检查项（Multi-Agent架构升级）

- [ ] SOP流程配置正确
- [ ] Supervisor Agent 正常工作
- [ ] Analyzer Team 并行执行
- [ ] 并行执行引擎正常
- [ ] 分析时间减少 60%+
- [ ] 并行效率 > 80%

### V3.2 检查项（文档质量提升）

- [ ] 7种文档类型全部生成
- [ ] 辅助素材正确生成
- [ ] 质量评分系统准确
- [ ] 多轮优化有效
- [ ] 前端界面适配完成
- [ ] 文档质量评分 > 85 分

***

*本实施计划将根据实际开发进度和用户反馈持续更新*

*Last updated: 2026-03-20*
