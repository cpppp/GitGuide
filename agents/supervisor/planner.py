"""Planner Agent - 任务规划器

负责任务分解、优先级排序、生成分析大纲
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from core.sop import GITGUIDE_SOP, AgentType, get_stage_config


@dataclass
class AnalysisPlan:
    """分析计划"""
    repo_url: str
    project_type: Optional[str] = None
    tasks: List[Dict[str, Any]] = field(default_factory=list)
    priority_order: List[str] = field(default_factory=list)
    estimated_time: int = 0
    analysis_outline: str = ""


class PlannerAgent:
    """规划器 Agent - 负责任务规划和分析策略制定"""

    def __init__(self):
        self.name = "Planner"
        self.version = "1.0"

    async def plan(self, context: Dict[str, Any]) -> AnalysisPlan:
        """
        制定分析计划

        参数:
            context: 包含 repo_url、repo_info 等上下文信息

        返回:
            AnalysisPlan: 分析计划对象
        """
        repo_url = context.get("repo_url", "")
        repo_info = context.get("repo_info", {})

        # 1. 分析项目类型
        project_type = self._detect_project_type(repo_info)
        context["project_type"] = project_type

        # 2. 生成任务列表
        tasks = self._generate_task_list(context)

        # 3. 制定优先级顺序
        priority_order = self._determine_priority(tasks, project_type)

        # 4. 估算执行时间
        estimated_time = self._estimate_time(tasks)

        # 5. 生成分析大纲
        analysis_outline = self._generate_outline(context, project_type, tasks)

        return AnalysisPlan(
            repo_url=repo_url,
            project_type=project_type,
            tasks=tasks,
            priority_order=priority_order,
            estimated_time=estimated_time,
            analysis_outline=analysis_outline
        )

    def _detect_project_type(self, repo_info: Dict[str, Any]) -> str:
        """检测项目类型"""
        language = repo_info.get("language", "").lower()

        # 语言映射到项目类型
        type_mapping = {
            "python": "Python",
            "javascript": "JavaScript",
            "typescript": "TypeScript",
            "java": "Java",
            "go": "Go",
            "rust": "Rust",
            "c++": "C++",
            "c": "C",
            "ruby": "Ruby",
            "php": "PHP",
            "swift": "Swift",
            "kotlin": "Kotlin",
        }

        return type_mapping.get(language, "Unknown")

    def _generate_task_list(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成任务列表"""
        tasks = []

        # 获取 SOP 中的阶段配置
        stages = GITGUIDE_SOP.get("stages", [])

        for stage in stages:
            stage_id = stage.get("id")
            stage_name = stage.get("name")
            is_parallel = stage.get("parallel", False)

            if is_parallel:
                # 并行阶段：展开子任务
                sub_tasks = stage.get("sub_tasks", [])
                for sub_task in sub_tasks:
                    tasks.append({
                        "stage": stage_id,
                        "stage_name": stage_name,
                        "task_id": sub_task.get("id"),
                        "agent": sub_task.get("agent"),
                        "description": sub_task.get("description"),
                        "status": "pending",
                        "parallel": True
                    })
            else:
                # 顺序阶段
                tasks.append({
                    "stage": stage_id,
                    "stage_name": stage_name,
                    "task_id": stage_id,
                    "agent": stage.get("agent"),
                    "description": stage.get("description"),
                    "status": "pending",
                    "parallel": False
                })

        return tasks

    def _determine_priority(self, tasks: List[Dict[str, Any]], project_type: str) -> List[str]:
        """确定任务执行优先级顺序"""
        # 基本优先级：按阶段顺序
        priority_order = [task["task_id"] for task in tasks]

        # 根据项目类型调整优先级
        # 例如：Python 项目可能需要更详细的依赖分析
        if project_type == "Python":
            # 确保 dependency_analysis 在其他分析器之前
            if "dependency_analysis" in priority_order:
                priority_order.remove("dependency_analysis")
                # 插入到第二位（在 type_analysis 之后）
                idx = priority_order.index("type_analysis") + 1
                priority_order.insert(idx, "dependency_analysis")

        return priority_order

    def _estimate_time(self, tasks: List[Dict[str, Any]]) -> int:
        """估算执行时间（秒）"""
        # 基础时间估算
        base_times = {
            # Planning 阶段
            "planning": 30,

            # Analysis 阶段（并行）
            "type_analysis": 45,
            "structure_analysis": 60,
            "dependency_analysis": 45,
            "code_pattern_analysis": 60,

            # Generation 阶段（并行）
            "quickstart_generation": 60,
            "overview_generation": 90,
            "architecture_generation": 120,
            "install_guide_generation": 90,
            "tutorial_generation": 120,
            "dev_guide_generation": 90,
            "troubleshoot_generation": 60,

            # Review 和 Optimization 阶段
            "review": 60,
            "optimization": 90,

            # Finalization 阶段
            "finalization": 30
        }

        total_time = 0

        # 计算串行任务的时间
        serial_time = 0
        # 计算并行任务的最大时间
        parallel_times = {}

        for task in tasks:
            task_id = task["task_id"]
            is_parallel = task.get("parallel", False)
            stage = task.get("stage")

            task_time = base_times.get(task_id, 60)

            if is_parallel:
                # 并行任务：同一阶段的任务一起运行
                if stage not in parallel_times:
                    parallel_times[stage] = []
                parallel_times[stage].append(task_time)
            else:
                # 串行任务
                serial_time += task_time

        # 并行阶段的时间取最大值
        max_parallel_time = 0
        for stage, times in parallel_times.items():
            max_parallel_time += max(times)

        total_time = serial_time + max_parallel_time

        return total_time

    def _generate_outline(self, context: Dict[str, Any], project_type: str, tasks: List[Dict[str, Any]]) -> str:
        """生成分析大纲"""
        repo_url = context.get("repo_url", "")
        repo_name = repo_url.split("/")[-1] if "/" in repo_url else repo_url

        outline = f"""# {repo_name} 分析大纲

## 项目信息
- 仓库 URL: {repo_url}
- 项目类型: {project_type}
- 语言: {context.get("repo_info", {}).get("language", "Unknown")}

## 分析计划

### 分析阶段
"""
        # 按阶段分组任务
        stages = {}
        for task in tasks:
            stage = task["stage_name"]
            if stage not in stages:
                stages[stage] = []
            stages[stage].append(task["description"])

        for stage_name, descriptions in stages.items():
            outline += f"\n#### {stage_name}\n"
            for desc in descriptions:
                outline += f"- {desc}\n"

        return outline

    def get_status(self) -> Dict[str, Any]:
        """获取规划器状态"""
        return {
            "name": self.name,
            "version": self.version,
            "status": "ready"
        }


# 全局实例
planner_agent = PlannerAgent()
