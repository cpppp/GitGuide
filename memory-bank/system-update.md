# GitGuide Multi-Agent 系统升级方案

> **文档版本**：v1.0  
> **创建日期**：2026-03-20  
> **参考项目**：OpenMAIC (https://github.com/THU-MAIC/OpenMAIC)  
> **目标**：提升 GitHub 仓库分析能力和文档生成质量

---

## 一、现状分析

### 1.1 当前架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                     Orchestrator Agent                       │
│                   (串行协调、简单流程)                         │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
    ┌───────────┐   ┌───────────┐   ┌───────────┐
    │ Analyzer  │   │  DocGen   │   │   Chat    │
    │  Agent    │   │  Agent    │   │  Agent    │
    │ (全部分析) │   │ (生成文档) │   │  (问答)   │
    └───────────┘   └───────────┘   └───────────┘
```

### 1.2 核心问题诊断

| 问题类别 | 具体问题 | 影响 | 严重程度 |
|---------|---------|------|---------|
| **架构设计** | 串行执行，无并行处理 | 分析时间长（2-5分钟） | 🔴 高 |
| **职责划分** | Agent 职责过于宽泛 | 分析深度不足 | 🔴 高 |
| **流程管理** | 缺乏 SOP 标准化流程 | 质量不稳定 | 🔴 高 |
| **状态管理** | 无共享上下文机制 | 信息丢失 | 🟡 中 |
| **质量控制** | 无审核和优化机制 | 文档质量参差不齐 | 🟡 中 |
| **交互模式** | 单一问答模式 | 用户体验有限 | 🟢 低 |
| **可扩展性** | 架构耦合度高 | 难以添加新功能 | 🟡 中 |

### 1.3 现有代码分析

```python
# 当前 orchestrator.py 的问题
def run(repo_url: str) -> Dict[str, Any]:
    # 问题1: 串行执行
    analysis_result = run_analyzer(repo_url)  # 阻塞等待
    doc_result = run_docgen(repo_url, result["analysis"])  # 阻塞等待
    
    # 问题2: 无并行处理
    # 问题3: 无质量检查
    # 问题4: 无迭代优化
    
    return result
```

---

## 二、OpenMAIC 架构启示

### 2.1 核心设计理念

OpenMAIC 采用 **两阶段生成流水线 + 多Agent编排** 的架构：

```
┌─────────────────────────────────────────────────────────────┐
│                    Two-Stage Pipeline                        │
├─────────────────────────────────────────────────────────────┤
│  Stage 1: Outline Generation                                 │
│  - 分析用户输入                                               │
│  - 生成结构化大纲                                             │
│  - 规划内容类型                                               │
├─────────────────────────────────────────────────────────────┤
│  Stage 2: Scene Generation                                   │
│  - 每个大纲项生成具体场景                                      │
│  - 支持多种场景类型（Slides, Quiz, Interactive, PBL）         │
│  - 并行处理独立场景                                           │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 关键架构组件

| 组件 | 功能 | 技术实现 |
|------|------|---------|
| **Generation Pipeline** | 两阶段内容生成 | 分层生成策略 |
| **Multi-Agent Orchestration** | Agent 编排和协调 | LangGraph 状态机 |
| **Playback Engine** | 状态机驱动交互 | idle → playing → live |
| **Action Engine** | 执行多种动作类型 | 28+ 动作类型 |
| **Shared Context** | Agent 间状态共享 | Zustand Store |

### 2.3 多Agent交互模式

OpenMAIC 支持四种交互模式：

1. **Classroom Discussion** - Agent 主动发起讨论
2. **Roundtable Debate** - 多角色辩论
3. **Q&A Mode** - 自由问答
4. **Whiteboard** - 实时协作绘制

### 2.4 可借鉴的设计模式

```typescript
// OpenMAIC 的 LangGraph 编排模式
const directorGraph = new StateGraph({
  channels: {
    messages: { value: (x: any, y: any) => x.concat(y) },
    currentAgent: { value: null },
    context: { value: null }
  }
});

// 定义 Agent 节点
directorGraph.addNode("analyzer", analyzerNode);
directorGraph.addNode("generator", generatorNode);
directorGraph.addNode("reviewer", reviewerNode);

// 定义边和条件路由
directorGraph.addEdge("analyzer", "generator");
directorGraph.addConditionalEdges("generator", shouldReview, {
  true: "reviewer",
  false: END
});
```

---

## 三、升级方案设计

### 3.1 新架构总览

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Supervisor Agent                               │
│                    (任务规划、进度协调、质量控制)                           │
│                                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │   Planner   │  │  Scheduler  │  │  Reviewer   │  │  Optimizer  │   │
│  │  (规划器)   │  │  (调度器)   │  │  (审核器)   │  │  (优化器)   │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐
│   Analyzer Team   │   │   Generator Team  │   │   Research Team   │
│    (分析团队)      │   │    (生成团队)      │   │    (调研团队)      │
├───────────────────┤   ├───────────────────┤   ├───────────────────┤
│ ┌───────┐ ┌─────┐ │   │ ┌───────┐ ┌─────┐ │   │ ┌───────┐ ┌─────┐ │
│ │ Type  │ │Struc│ │   │ │Readme │ │Learn│ │   │ │ Code  │ │ API │ │
│ │Analyst│ │Analyst│   │ │ Gen   │ │DocGen│   │ │Analyst│ │Analyst│
│ └───────┘ └─────┘ │   │ └───────┘ └─────┘ │   │ └───────┘ └─────┘ │
│ ┌───────┐ ┌─────┐ │   │ ┌───────┐ ┌─────┐ │   │ ┌───────┐ ┌─────┐ │
│ │ Depend│ │Code │ │   │ │ Setup │ │Visual│ │   │ │ Test  │ │Perf │ │
│ │Analyst│ │Pattern│   │ │ Guide │ │ Gen  │ │   │ │Analyst│ │Analyst│
│ └───────┘ └─────┘ │   │ └───────┘ └─────┘ │   │ └───────┘ └─────┘ │
└───────────────────┘   └───────────────────┘   └───────────────────┘
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                │
                                ▼
                    ┌───────────────────┐
                    │   Shared Context  │
                    │    (共享上下文)    │
                    └───────────────────┘
```

### 3.2 两阶段生成流水线

借鉴 OpenMAIC 的两阶段设计：

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Stage 1: Analysis Planning                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  输入: GitHub Repository URL                                             │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     Planner Agent                                │   │
│  │  - 分析仓库类型和规模                                             │   │
│  │  - 制定分析策略                                                   │   │
│  │  - 分配分析任务                                                   │   │
│  │  - 生成分析大纲                                                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  输出: Analysis Plan (JSON)                                              │
│  {                                                                       │
│    "repo_type": "Python Web Application",                               │
│    "complexity": "medium",                                               │
│    "analysis_tasks": [                                                   │
│      {"agent": "TypeAnalyzer", "priority": "high"},                     │
│      {"agent": "StructureAnalyzer", "priority": "high"},                │
│      {"agent": "DependencyAnalyzer", "priority": "medium"}              │
│    ],                                                                    │
│    "doc_strategy": "detailed"                                            │
│  }                                                                       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    Stage 2: Parallel Execution                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    Scheduler Agent                                │  │
│  │  - 并行调度分析任务                                                │  │
│  │  - 管理任务依赖                                                    │  │
│  │  - 监控执行进度                                                    │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐       │
│  │    Type    │  │  Structure │  │ Dependency │  │   Code     │       │
│  │  Analyzer  │  │  Analyzer  │  │  Analyzer  │  │  Pattern   │       │
│  │  (并行)    │  │  (并行)    │  │  (并行)    │  │  (并行)    │       │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘       │
│        │               │               │               │               │
│        └───────────────┴───────────────┴───────────────┘               │
│                                    │                                    │
│                          Shared Context                                 │
│                                    │                                    │
└────────────────────────────────────┼────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    Stage 3: Document Generation                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  输入: Aggregated Analysis Results                                       │
│                                                                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐       │
│  │  Readme    │  │  Learning  │  │   Setup    │  │   Visual   │       │
│  │ Generator  │  │    Doc     │  │   Guide    │  │    Doc     │       │
│  │  (并行)    │  │  Generator │  │ Generator  │  │ Generator  │       │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘       │
│        │               │               │               │               │
│        └───────────────┴───────────────┴───────────────┘               │
│                                    │                                    │
└────────────────────────────────────┼────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    Stage 4: Quality Review                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     Reviewer Agent                                │   │
│  │  - 检查文档完整性                                                  │   │
│  │  - 验证技术准确性                                                  │   │
│  │  - 评估可读性                                                      │   │
│  │  - 生成改进建议                                                    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     Optimizer Agent                               │   │
│  │  - 根据反馈优化文档                                                │   │
│  │  - 迭代改进（最多3轮）                                             │   │
│  │  - 最终质量评分                                                    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  输出: Final Documentation Package                                       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2 SOP 标准化流程定义

```python
# GitGuide SOP - 标准作业程序
GITGUIDE_SOP = {
    "name": "GitHub Repository Analysis & Documentation",
    "version": "2.0",
    "description": "标准化 GitHub 仓库分析和文档生成流程",
    
    "stages": [
        {
            "id": "planning",
            "name": "任务规划",
            "agent": "PlannerAgent",
            "timeout": 30,
            "inputs": ["repo_url", "user_preferences"],
            "outputs": ["analysis_plan", "task_queue"],
            "validation": {
                "required_fields": ["repo_type", "complexity", "tasks"],
                "quality_checks": ["plan_completeness"]
            },
            "next": "analysis"
        },
        
        {
            "id": "analysis",
            "name": "仓库分析",
            "agent": "AnalyzerTeam",
            "parallel": True,
            "timeout": 120,
            "sub_tasks": [
                {
                    "id": "type_analysis",
                    "agent": "TypeAnalyzer",
                    "priority": "high",
                    "tools": ["detect_language", "detect_framework", "detect_build_system"]
                },
                {
                    "id": "structure_analysis",
                    "agent": "StructureAnalyzer",
                    "priority": "high",
                    "tools": ["get_tree", "get_file_list", "get_module_structure"]
                },
                {
                    "id": "dependency_analysis",
                    "agent": "DependencyAnalyzer",
                    "priority": "medium",
                    "tools": ["parse_requirements", "parse_package_json", "parse_go_mod"]
                },
                {
                    "id": "code_pattern_analysis",
                    "agent": "CodePatternAnalyzer",
                    "priority": "medium",
                    "tools": ["analyze_patterns", "extract_entry_points", "identify_modules"]
                }
            ],
            "merge_strategy": "aggregate",
            "outputs": ["analysis_results"],
            "next": "generation"
        },
        
        {
            "id": "generation",
            "name": "文档生成",
            "agent": "GeneratorTeam",
            "parallel": True,
            "timeout": 90,
            "sub_tasks": [
                {
                    "id": "readme_generation",
                    "agent": "ReadmeGenerator",
                    "depends_on": ["type_analysis", "structure_analysis"]
                },
                {
                    "id": "learning_doc_generation",
                    "agent": "LearningDocGenerator",
                    "depends_on": ["analysis_results"]
                },
                {
                    "id": "setup_guide_generation",
                    "agent": "SetupGuideGenerator",
                    "depends_on": ["dependency_analysis", "code_pattern_analysis"]
                },
                {
                    "id": "visual_doc_generation",
                    "agent": "VisualDocGenerator",
                    "depends_on": ["structure_analysis"]
                }
            ],
            "outputs": ["draft_documents"],
            "next": "review"
        },
        
        {
            "id": "review",
            "name": "质量审核",
            "agent": "ReviewerAgent",
            "timeout": 30,
            "inputs": ["draft_documents"],
            "outputs": ["review_result", "improvement_suggestions"],
            "validation": {
                "checklist": [
                    "document_completeness",
                    "technical_accuracy",
                    "readability_score",
                    "actionable_commands"
                ],
                "min_score": 0.8
            },
            "next": "optimization"
        },
        
        {
            "id": "optimization",
            "name": "迭代优化",
            "agent": "OptimizerAgent",
            "timeout": 60,
            "max_iterations": 3,
            "inputs": ["draft_documents", "improvement_suggestions"],
            "outputs": ["final_documents", "quality_score"],
            "exit_condition": "quality_score >= 0.9 or iterations >= max_iterations",
            "next": "finalization"
        },
        
        {
            "id": "finalization",
            "name": "整理输出",
            "agent": "SupervisorAgent",
            "timeout": 10,
            "inputs": ["final_documents"],
            "outputs": ["result_package"],
            "format": {
                "learning_doc": "markdown",
                "setup_guide": "markdown",
                "code_atlas": "json",
                "metadata": "json"
            }
        }
    ],
    
    "error_handling": {
        "retry_policy": {
            "max_retries": 2,
            "backoff": "exponential"
        },
        "fallback_strategy": {
            "on_analysis_failure": "use_fast_mode",
            "on_generation_failure": "use_template",
            "on_review_failure": "skip_optimization"
        }
    },
    
    "observability": {
        "logging": True,
        "progress_tracking": True,
        "performance_metrics": True
    }
}
```

### 3.3 Agent 详细设计

#### 3.3.1 Supervisor Agent（总监 Agent）

```python
class SupervisorAgent:
    """
    总监 Agent - 负责任务规划、进度协调、质量控制
    
    参考 OpenMAIC 的 Director Graph 设计
    """
    
    def __init__(self):
        self.planner = PlannerAgent()
        self.scheduler = SchedulerAgent()
        self.reviewer = ReviewerAgent()
        self.optimizer = OptimizerAgent()
        
    def plan(self, repo_url: str, preferences: dict) -> AnalysisPlan:
        """制定分析计划"""
        return self.planner.create_plan(repo_url, preferences)
    
    def schedule(self, plan: AnalysisPlan) -> TaskQueue:
        """调度任务执行"""
        return self.scheduler.create_queue(plan)
    
    def review(self, documents: dict) -> ReviewResult:
        """审核文档质量"""
        return self.reviewer.review(documents)
    
    def optimize(self, documents: dict, suggestions: list) -> dict:
        """优化文档"""
        return self.optimizer.optimize(documents, suggestions)
```

#### 3.3.2 Analyzer Team（分析团队）

```python
class AnalyzerTeam:
    """
    分析团队 - 并行执行多种分析任务
    
    参考 OpenMAIC 的并行场景生成设计
    """
    
    def __init__(self):
        self.type_analyzer = TypeAnalyzer()
        self.structure_analyzer = StructureAnalyzer()
        self.dependency_analyzer = DependencyAnalyzer()
        self.code_pattern_analyzer = CodePatternAnalyzer()
        
    async def analyze_parallel(self, repo_url: str, plan: AnalysisPlan) -> dict:
        """并行执行分析任务"""
        import asyncio
        
        # 创建并行任务
        tasks = []
        for task in plan.sub_tasks:
            if task.agent == "TypeAnalyzer":
                tasks.append(self.type_analyzer.analyze(repo_url))
            elif task.agent == "StructureAnalyzer":
                tasks.append(self.structure_analyzer.analyze(repo_url))
            elif task.agent == "DependencyAnalyzer":
                tasks.append(self.dependency_analyzer.analyze(repo_url))
            elif task.agent == "CodePatternAnalyzer":
                tasks.append(self.code_pattern_analyzer.analyze(repo_url))
        
        # 并行执行
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 合并结果
        return self._merge_results(results)


class TypeAnalyzer:
    """项目类型分析器"""
    
    tools = [
        "detect_language",        # 检测编程语言
        "detect_framework",       # 检测框架
        "detect_build_system",    # 检测构建系统
        "detect_runtime"          # 检测运行时环境
    ]
    
    def analyze(self, repo_url: str) -> TypeAnalysisResult:
        """分析项目类型"""
        # 检测关键文件
        key_files = self._detect_key_files(repo_url)
        
        # 识别项目类型
        project_type = self._identify_type(key_files)
        
        return TypeAnalysisResult(
            language=project_type.language,
            framework=project_type.framework,
            build_system=project_type.build_system,
            runtime=project_type.runtime,
            confidence=project_type.confidence
        )


class StructureAnalyzer:
    """目录结构分析器"""
    
    tools = [
        "get_tree",               # 获取目录树
        "get_file_list",          # 获取文件列表
        "get_module_structure",   # 获取模块结构
        "calculate_metrics"       # 计算代码指标
    ]
    
    def analyze(self, repo_url: str) -> StructureAnalysisResult:
        """分析目录结构"""
        # 获取目录树
        tree = self._get_tree(repo_url)
        
        # 识别模块
        modules = self._identify_modules(tree)
        
        # 计算指标
        metrics = self._calculate_metrics(tree)
        
        return StructureAnalysisResult(
            tree=tree,
            modules=modules,
            metrics=metrics,
            entry_points=self._find_entry_points(tree)
        )


class DependencyAnalyzer:
    """依赖关系分析器"""
    
    tools = [
        "parse_requirements",     # Python 依赖
        "parse_package_json",     # Node.js 依赖
        "parse_go_mod",          # Go 依赖
        "parse_pom_xml",         # Java 依赖
        "analyze_dependency_graph"  # 依赖图分析
    ]
    
    def analyze(self, repo_url: str) -> DependencyAnalysisResult:
        """分析依赖关系"""
        # 检测依赖文件
        dep_files = self._detect_dependency_files(repo_url)
        
        # 解析依赖
        dependencies = self._parse_dependencies(dep_files)
        
        # 构建依赖图
        graph = self._build_dependency_graph(dependencies)
        
        return DependencyAnalysisResult(
            dependencies=dependencies,
            graph=graph,
            critical_deps=self._identify_critical(dependencies)
        )


class CodePatternAnalyzer:
    """代码模式分析器"""
    
    tools = [
        "analyze_patterns",       # 分析代码模式
        "extract_entry_points",   # 提取入口点
        "identify_modules",       # 识别模块
        "analyze_architecture"    # 分析架构
    ]
    
    def analyze(self, repo_url: str) -> CodePatternResult:
        """分析代码模式"""
        # 识别架构模式
        architecture = self._identify_architecture(repo_url)
        
        # 提取入口点
        entry_points = self._extract_entry_points(repo_url)
        
        # 分析代码模式
        patterns = self._analyze_patterns(repo_url)
        
        return CodePatternResult(
            architecture=architecture,
            entry_points=entry_points,
            patterns=patterns,
            code_style=self._detect_style(repo_url)
        )
```

#### 3.3.3 Generator Team（生成团队）

```python
class GeneratorTeam:
    """
    文档生成团队 - 并行生成多种文档
    
    参考 OpenMAIC 的场景生成设计
    """
    
    def __init__(self):
        self.readme_generator = ReadmeGenerator()
        self.learning_doc_generator = LearningDocGenerator()
        self.setup_guide_generator = SetupGuideGenerator()
        self.visual_doc_generator = VisualDocGenerator()
        
    async def generate_parallel(self, analysis_results: dict) -> dict:
        """并行生成文档"""
        import asyncio
        
        tasks = [
            self.readme_generator.generate(analysis_results),
            self.learning_doc_generator.generate(analysis_results),
            self.setup_guide_generator.generate(analysis_results),
            self.visual_doc_generator.generate(analysis_results)
        ]
        
        results = await asyncio.gather(*tasks)
        
        return {
            "readme": results[0],
            "learning_doc": results[1],
            "setup_guide": results[2],
            "visual_doc": results[3]
        }
```

### 3.4 状态管理与上下文共享

```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph

class GitGuideState(TypedDict):
    """GitGuide 全局状态 - 参考 OpenMAIC 的状态管理"""
    
    # 输入
    repo_url: str
    user_preferences: dict
    
    # 分析阶段
    analysis_plan: dict
    type_result: dict
    structure_result: dict
    dependency_result: dict
    code_pattern_result: dict
    
    # 生成阶段
    readme_doc: str
    learning_doc: str
    setup_guide: str
    visual_doc: dict
    
    # 审核阶段
    review_result: dict
    quality_score: float
    improvement_suggestions: list
    
    # 最终输出
    final_result: dict
    
    # 元数据
    progress: int
    current_stage: str
    errors: list


class SharedContext:
    """
    共享上下文 - Agent 间状态共享
    
    参考 OpenMAIC 的 Zustand Store 设计
    """
    
    def __init__(self):
        self.state: GitGuideState = {}
        self.history: list = []
        self.subscribers: list = []
        
    def update(self, key: str, value: any, agent_id: str = None):
        """更新状态"""
        self.state[key] = value
        self.history.append({
            "timestamp": datetime.now(),
            "agent": agent_id,
            "key": key,
            "value": value
        })
        self._notify_subscribers(key, value)
        
    def get(self, key: str) -> any:
        """获取状态"""
        return self.state.get(key)
    
    def get_all_for_agent(self, agent_id: str) -> dict:
        """获取 Agent 需要的所有上下文"""
        # 根据 Agent 类型返回相关上下文
        return self.state
    
    def subscribe(self, callback: callable):
        """订阅状态变更"""
        self.subscribers.append(callback)
        
    def _notify_subscribers(self, key: str, value: any):
        """通知订阅者"""
        for callback in self.subscribers:
            callback(key, value)
```

### 3.5 LangGraph 工作流编排

```python
from langgraph.graph import StateGraph, END

def build_gitguide_graph():
    """
    构建 GitGuide 工作流图
    
    参考 OpenMAIC 的 Director Graph 设计
    """
    
    # 创建状态图
    graph = StateGraph(GitGuideState)
    
    # 添加节点
    graph.add_node("planner", planner_node)
    graph.add_node("type_analyzer", type_analyzer_node)
    graph.add_node("structure_analyzer", structure_analyzer_node)
    graph.add_node("dependency_analyzer", dependency_analyzer_node)
    graph.add_node("code_pattern_analyzer", code_pattern_analyzer_node)
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
    graph.add_edge("planner", "code_pattern_analyzer")
    
    # 并行分析后合并
    graph.add_edge("type_analyzer", "merger")
    graph.add_edge("structure_analyzer", "merger")
    graph.add_edge("dependency_analyzer", "merger")
    graph.add_edge("code_pattern_analyzer", "merger")
    
    # 合并后生成文档
    graph.add_edge("merger", "doc_generator")
    
    # 文档生成后审核
    graph.add_edge("doc_generator", "reviewer")
    
    # 条件路由：根据审核结果决定是否优化
    graph.add_conditional_edges(
        "reviewer",
        should_optimize,
        {
            True: "optimizer",
            False: END
        }
    )
    
    # 优化后可循环审核
    graph.add_conditional_edges(
        "optimizer",
        should_continue_optimization,
        {
            True: "reviewer",
            False: END
        }
    )
    
    return graph.compile()


def should_optimize(state: GitGuideState) -> bool:
    """判断是否需要优化"""
    return state["quality_score"] < 0.9


def should_continue_optimization(state: GitGuideState) -> bool:
    """判断是否继续优化"""
    iterations = state.get("optimization_iterations", 0)
    return iterations < 3 and state["quality_score"] < 0.9
```

### 3.6 质量控制机制

```python
class ReviewerAgent:
    """
    审核 Agent - 文档质量检查
    
    参考 OpenMAIC 的质量检查设计
    """
    
    QUALITY_CHECKLIST = [
        {
            "id": "completeness",
            "name": "完整性检查",
            "items": [
                "项目概述是否完整",
                "技术栈是否列出",
                "目录结构是否清晰",
                "启动命令是否正确"
            ]
        },
        {
            "id": "accuracy",
            "name": "准确性检查",
            "items": [
                "语言识别是否正确",
                "框架识别是否正确",
                "依赖版本是否准确"
            ]
        },
        {
            "id": "readability",
            "name": "可读性检查",
            "items": [
                "结构是否清晰",
                "语言是否流畅",
                "示例是否充分"
            ]
        },
        {
            "id": "actionability",
            "name": "可操作性检查",
            "items": [
                "安装步骤是否可执行",
                "运行命令是否正确",
                "配置说明是否完整"
            ]
        }
    ]
    
    def review(self, documents: dict) -> ReviewResult:
        """执行质量审核"""
        scores = {}
        issues = []
        
        for checklist in self.QUALITY_CHECKLIST:
            category_score, category_issues = self._check_category(
                documents, 
                checklist
            )
            scores[checklist["id"]] = category_score
            issues.extend(category_issues)
        
        overall_score = sum(scores.values()) / len(scores)
        
        return ReviewResult(
            scores=scores,
            overall_score=overall_score,
            issues=issues,
            passed=overall_score >= 0.8
        )


class OptimizerAgent:
    """
    优化 Agent - 迭代改进文档
    
    参考 OpenMAIC 的迭代优化设计
    """
    
    def __init__(self, max_iterations: int = 3):
        self.max_iterations = max_iterations
        self.llm = get_llm()
        
    def optimize(self, documents: dict, review_result: ReviewResult) -> dict:
        """优化文档"""
        optimized = documents.copy()
        
        for issue in review_result.issues:
            if issue.severity == "high":
                optimized = self._fix_issue(optimized, issue)
        
        return optimized
    
    def iterative_optimization(
        self, 
        documents: dict, 
        target_score: float = 0.9
    ) -> tuple:
        """迭代优化直到达到目标分数"""
        current_docs = documents
        iterations = 0
        
        while iterations < self.max_iterations:
            # 审核
            review = self.reviewer.review(current_docs)
            
            if review.overall_score >= target_score:
                break
            
            # 优化
            current_docs = self.optimize(current_docs, review)
            iterations += 1
        
        return current_docs, review.overall_score, iterations
```

---

## 四、性能优化策略

### 4.1 并行处理优化

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

### 4.2 缓存策略

```python
from functools import lru_cache
import hashlib

class AnalysisCache:
    """分析结果缓存"""
    
    def __init__(self, ttl: int = 3600):
        self.cache = {}
        self.ttl = ttl
        
    def get_cache_key(self, repo_url: str, analysis_type: str) -> str:
        """生成缓存键"""
        content = f"{repo_url}:{analysis_type}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, repo_url: str, analysis_type: str) -> any:
        """获取缓存"""
        key = self.get_cache_key(repo_url, analysis_type)
        return self.cache.get(key)
    
    def set(self, repo_url: str, analysis_type: str, result: any):
        """设置缓存"""
        key = self.get_cache_key(repo_url, analysis_type)
        self.cache[key] = {
            "result": result,
            "timestamp": datetime.now()
        }
```

### 4.3 超时与重试机制

```python
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

class RobustExecutor:
    """健壮的执行器 - 支持超时和重试"""
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def execute_with_retry(
        self, 
        task: callable, 
        timeout: int = 60
    ) -> any:
        """带重试的执行"""
        try:
            result = await asyncio.wait_for(
                task(),
                timeout=timeout
            )
            return result
        except asyncio.TimeoutError:
            raise TimeoutError(f"Task timed out after {timeout}s")
```

---

## 五、交互模式升级

### 5.1 多模式交互支持

参考 OpenMAIC 的四种交互模式：

```python
class InteractionMode:
    """交互模式枚举"""
    CLASSROOM = "classroom"      # 教学模式
    ROUNDTABLE = "roundtable"    # 圆桌讨论
    QA = "qa"                    # 问答模式
    WHITEBOARD = "whiteboard"    # 白板协作


class InteractionManager:
    """
    交互管理器 - 支持多种交互模式
    
    参考 OpenMAIC 的多模式交互设计
    """
    
    def __init__(self):
        self.current_mode = InteractionMode.QA
        self.agents = {}
        
    def switch_mode(self, mode: InteractionMode):
        """切换交互模式"""
        self.current_mode = mode
        
    async def handle_interaction(
        self, 
        user_input: str, 
        context: SharedContext
    ) -> dict:
        """处理交互"""
        if self.current_mode == InteractionMode.CLASSROOM:
            return await self._classroom_mode(user_input, context)
        elif self.current_mode == InteractionMode.ROUNDTABLE:
            return await self._roundtable_mode(user_input, context)
        elif self.current_mode == InteractionMode.QA:
            return await self._qa_mode(user_input, context)
        elif self.current_mode == InteractionMode.WHITEBOARD:
            return await self._whiteboard_mode(user_input, context)
```

### 5.2 圆桌讨论模式

```python
class RoundtableDiscussion:
    """
    圆桌讨论 - 多个 Agent 角色讨论
    
    参考 OpenMAIC 的 Roundtable Debate 设计
    """
    
    def __init__(self):
        self.roles = [
            {"name": "架构师", "perspective": "architecture"},
            {"name": "开发者", "perspective": "implementation"},
            {"name": "运维工程师", "perspective": "deployment"},
            {"name": "安全专家", "perspective": "security"}
        ]
        
    async def discuss(self, topic: str, context: SharedContext) -> list:
        """发起圆桌讨论"""
        discussions = []
        
        for role in self.roles:
            response = await self._get_role_perspective(
                role, 
                topic, 
                context
            )
            discussions.append({
                "role": role["name"],
                "perspective": role["perspective"],
                "content": response
            })
        
        return discussions
```

---

## 六、可观测性设计

### 6.1 进度追踪

```python
class ProgressTracker:
    """进度追踪器"""
    
    def __init__(self, websocket_manager):
        self.ws_manager = websocket_manager
        self.stages = {
            "planning": {"weight": 10, "status": "pending"},
            "analysis": {"weight": 40, "status": "pending"},
            "generation": {"weight": 30, "status": "pending"},
            "review": {"weight": 10, "status": "pending"},
            "optimization": {"weight": 10, "status": "pending"}
        }
        
    def update_stage(self, stage: str, status: str, message: str):
        """更新阶段状态"""
        self.stages[stage]["status"] = status
        
        # 计算总进度
        total_progress = sum(
            s["weight"] if s["status"] == "completed" 
            else s["weight"] * 0.5 if s["status"] == "running" 
            else 0
            for s in self.stages.values()
        )
        
        # 推送进度
        self.ws_manager.broadcast({
            "type": "progress",
            "stage": stage,
            "status": status,
            "message": message,
            "total_progress": total_progress
        })
```

### 6.2 性能监控

```python
class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics = {}
        
    def record_metric(
        self, 
        agent_id: str, 
        metric_name: str, 
        value: float
    ):
        """记录指标"""
        if agent_id not in self.metrics:
            self.metrics[agent_id] = {}
        self.metrics[agent_id][metric_name] = value
        
    def get_report(self) -> dict:
        """生成报告"""
        return {
            "total_time": self._calculate_total_time(),
            "agent_times": self._get_agent_times(),
            "parallel_efficiency": self._calculate_efficiency()
        }
```

---

## 七、实施计划

### 7.1 分阶段实施

| 阶段 | 任务 | 预计时间 | 优先级 |
|------|------|---------|--------|
| **Phase 1** | 基础架构重构 | 3 天 | 🔴 高 |
| - | 定义 SOP 流程 | 0.5 天 | |
| - | 实现状态管理 | 1 天 | |
| - | 构建工作流图 | 1.5 天 | |
| **Phase 2** | Agent 拆分与并行化 | 4 天 | 🔴 高 |
| - | 拆分 Analyzer | 1.5 天 | |
| - | 实现并行执行 | 1.5 天 | |
| - | 集成测试 | 1 天 | |
| **Phase 3** | 质量控制机制 | 3 天 | 🟡 中 |
| - | 实现 Reviewer | 1 天 | |
| - | 实现 Optimizer | 1 天 | |
| - | 迭代优化测试 | 1 天 | |
| **Phase 4** | 高级功能 | 4 天 | 🟢 低 |
| - | 交互模式升级 | 2 天 | |
| - | 可观测性完善 | 1 天 | |
| - | 性能优化 | 1 天 | |

### 7.2 技术选型

| 组件 | 当前技术 | 升级技术 | 原因 |
|------|---------|---------|------|
| Agent 框架 | LangChain | LangChain + LangGraph | 支持复杂工作流 |
| 状态管理 | 无 | TypedDict + StateGraph | 标准化状态 |
| 并行处理 | 无 | asyncio + ThreadPoolExecutor | 提升效率 |
| 缓存 | 无 | Redis / 内存缓存 | 减少重复计算 |

### 7.3 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| API 调用增加 | 成本上升 | 实现缓存、优化 Prompt |
| 复杂度增加 | 维护困难 | 完善文档、模块化设计 |
| 并发问题 | 结果不一致 | 实现锁机制、状态同步 |

---

## 八、预期收益

### 8.1 性能提升

| 指标 | 当前 | 升级后 | 提升 |
|------|------|--------|------|
| 分析时间 | 2-5 分钟 | 30秒-1分钟 | 70%↓ |
| 并行效率 | 0% | 80% | +80% |
| 文档质量 | 不稳定 | 稳定高质量 | SOP 保证 |

### 8.2 功能增强

| 功能 | 当前 | 升级后 |
|------|------|--------|
| 分析深度 | 表面分析 | 深度多维度分析 |
| 文档类型 | 2 种 | 4+ 种 |
| 交互模式 | 单一问答 | 多模式交互 |
| 质量保证 | 无 | 多轮审核优化 |

### 8.3 可维护性

| 维度 | 当前 | 升级后 |
|------|------|--------|
| 架构清晰度 | 中 | 高 |
| 扩展性 | 低 | 高 |
| 可观测性 | 低 | 高 |
| 文档完整性 | 中 | 高 |

---

## 九、总结

本升级方案充分借鉴了 OpenMAIC 项目的优秀设计理念，包括：

1. **两阶段生成流水线** - 先规划后执行，确保任务清晰
2. **多 Agent 并行编排** - 使用 LangGraph 实现高效并行处理
3. **SOP 标准化流程** - 定义清晰的工作流程和质量标准
4. **共享上下文机制** - Agent 间高效协作
5. **质量控制闭环** - 审核与迭代优化确保输出质量
6. **多模式交互** - 提升用户体验

通过本次升级，GitGuide 将从简单的串行分析工具进化为一个高效、智能、可扩展的 GitHub 仓库分析平台，为用户提供更快速、更深入、更高质量的仓库学习和文档生成服务。

---

*文档版本: v1.0*  
*创建日期: 2026-03-20*  
*参考项目: OpenMAIC (https://github.com/THU-MAIC/OpenMAIC)*
