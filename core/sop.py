"""SOP - 标准化操作流程定义

简化架构版本 V3.0.1
定义 GitGuide Multi-Agent 架构的标准化分析流程。

工作流程：初始化 → 分析(并行) → 生成(并行) → 审核 → 输出
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class Stage(Enum):
    """流程阶段枚举（简化版）"""
    INITIALIZATION = "initialization"
    ANALYSIS = "analysis"
    GENERATION = "generation"
    REVIEW = "review"
    OUTPUT = "output"


class AgentType(Enum):
    """Agent 类型枚举（简化版）"""
    # Analyzer Team
    TYPE_ANALYZER = "type_analyzer"
    STRUCTURE_ANALYZER = "structure_analyzer"
    DEPENDENCY_ANALYZER = "dependency_analyzer"
    CODE_PATTERN_ANALYZER = "code_pattern_analyzer"

    # Generator Team
    QUICKSTART_GEN = "quickstart_generator"
    OVERVIEW_GEN = "overview_generator"
    ARCHITECTURE_GEN = "architecture_generator"
    INSTALL_GUIDE_GEN = "install_guide_generator"
    TUTORIAL_GEN = "tutorial_generator"
    DEV_GUIDE_GEN = "dev_guide_generator"
    TROUBLESHOOT_GEN = "troubleshoot_generator"


@dataclass
class TaskSpec:
    """任务规格定义"""
    id: str
    name: str
    agent: AgentType
    description: str
    timeout: int = 60
    parallel: bool = False
    depends_on: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)


@dataclass
class StageSpec:
    """阶段规格定义"""
    id: Stage
    name: str
    description: str
    tasks: List[TaskSpec] = field(default_factory=list)
    timeout: int = 120
    parallel: bool = False


GITGUIDE_SOP: Dict[str, Any] = {
    "name": "GitHub Repository Analysis",
    "version": "3.0.1",
    "description": "简化架构的 GitHub 仓库分析标准流程",

    "stages": [
        {
            "id": Stage.INITIALIZATION.value,
            "name": "初始化",
            "description": "创建 WorkflowState，设置仓库路径",
            "timeout": 30,
            "outputs": ["repo_url", "repo_path"]
        },

        {
            "id": Stage.ANALYSIS.value,
            "name": "仓库分析",
            "description": "Analyzer Team 并行执行多维度分析",
            "parallel": True,
            "sub_tasks": [
                {
                    "id": "type_analysis",
                    "agent": AgentType.TYPE_ANALYZER.value,
                    "description": "识别项目类型（Python/Node/Java/Go等）"
                },
                {
                    "id": "structure_analysis",
                    "agent": AgentType.STRUCTURE_ANALYZER.value,
                    "description": "分析目录结构、识别核心模块、提取入口点"
                },
                {
                    "id": "dependency_analysis",
                    "agent": AgentType.DEPENDENCY_ANALYZER.value,
                    "description": "分析依赖关系、检查版本兼容性"
                },
                {
                    "id": "code_pattern_analysis",
                    "agent": AgentType.CODE_PATTERN_ANALYZER.value,
                    "description": "识别代码模式、分析架构风格"
                }
            ],
            "timeout": 120
        },

        {
            "id": Stage.GENERATION.value,
            "name": "文档生成",
            "description": "Generator Team 并行生成7种文档类型",
            "parallel": True,
            "sub_tasks": [
                {
                    "id": "quickstart_generation",
                    "agent": AgentType.QUICKSTART_GEN.value,
                    "description": "生成快速入门文档"
                },
                {
                    "id": "overview_generation",
                    "agent": AgentType.OVERVIEW_GEN.value,
                    "description": "生成项目概览文档"
                },
                {
                    "id": "architecture_generation",
                    "agent": AgentType.ARCHITECTURE_GEN.value,
                    "description": "生成架构设计文档"
                },
                {
                    "id": "install_guide_generation",
                    "agent": AgentType.INSTALL_GUIDE_GEN.value,
                    "description": "生成安装部署文档"
                },
                {
                    "id": "tutorial_generation",
                    "agent": AgentType.TUTORIAL_GEN.value,
                    "description": "生成使用教程文档"
                },
                {
                    "id": "dev_guide_generation",
                    "agent": AgentType.DEV_GUIDE_GEN.value,
                    "description": "生成开发指南文档"
                },
                {
                    "id": "troubleshoot_generation",
                    "agent": AgentType.TROUBLESHOOT_GEN.value,
                    "description": "生成故障排查文档"
                }
            ],
            "timeout": 180
        },

        {
            "id": Stage.REVIEW.value,
            "name": "质量审核",
            "description": "内置质量检查：完整性、准确性、可读性、实用性",
            "outputs": ["quality_score", "issues"],
            "timeout": 60
        },

        {
            "id": Stage.OUTPUT.value,
            "name": "最终输出",
            "description": "整合所有文档，生成最终结果",
            "outputs": ["final_result"],
            "timeout": 30
        }
    ],

    "quality_dimensions": {
        "completeness": {
            "weight": 0.30,
            "description": "文档类型是否齐全、各章节是否完整、必要信息是否覆盖"
        },
        "accuracy": {
            "weight": 0.30,
            "description": "技术信息是否正确、命令是否可执行、配置是否有效"
        },
        "readability": {
            "weight": 0.20,
            "description": "结构是否清晰、语言是否流畅、示例是否充分"
        },
        "practicality": {
            "weight": 0.20,
            "description": "是否解决实际问题、是否有可操作步骤、是否有故障排查"
        }
    }
}


def get_stage_config(stage_id: str) -> Optional[Dict[str, Any]]:
    """获取指定阶段的配置"""
    for stage in GITGUIDE_SOP["stages"]:
        if stage["id"] == stage_id:
            return stage
    return None


def get_agent_stage(agent_type: AgentType) -> Optional[Stage]:
    """获取 Agent 所属的阶段"""
    if agent_type in [
        AgentType.TYPE_ANALYZER,
        AgentType.STRUCTURE_ANALYZER,
        AgentType.DEPENDENCY_ANALYZER,
        AgentType.CODE_PATTERN_ANALYZER
    ]:
        return Stage.ANALYSIS

    if agent_type in [
        AgentType.QUICKSTART_GEN,
        AgentType.OVERVIEW_GEN,
        AgentType.ARCHITECTURE_GEN,
        AgentType.INSTALL_GUIDE_GEN,
        AgentType.TUTORIAL_GEN,
        AgentType.DEV_GUIDE_GEN,
        AgentType.TROUBLESHOOT_GEN
    ]:
        return Stage.GENERATION

    return None


def get_parallel_tasks(stage_id: str) -> List[str]:
    """获取可并行执行的任务列表"""
    stage = get_stage_config(stage_id)
    if stage and stage.get("parallel", False):
        return [task["id"] for task in stage.get("sub_tasks", [])]
    return []


def get_expected_outputs(stage_id: str) -> List[str]:
    """获取阶段预期输出"""
    stage = get_stage_config(stage_id)
    if stage:
        outputs = stage.get("outputs", [])
        if stage.get("parallel", False):
            sub_tasks = stage.get("sub_tasks", [])
            for task in sub_tasks:
                outputs.extend(task.get("outputs", []))
        return outputs
    return []


def validate_sop() -> bool:
    """验证 SOP 配置的完整性"""
    try:
        required_fields = ["name", "version", "stages"]
        for f in required_fields:
            if f not in GITGUIDE_SOP:
                raise ValueError(f"SOP 配置缺少必需字段: {f}")

        required_stages = [stage.value for stage in Stage]
        defined_stages = [stage["id"] for stage in GITGUIDE_SOP["stages"]]

        for stage_id in required_stages:
            if stage_id not in defined_stages:
                raise ValueError(f"SOP 配置缺少必需阶段: {stage_id}")

        quality_dims = GITGUIDE_SOP.get("quality_dimensions", {})
        total_weight = sum(dim["weight"] for dim in quality_dims.values())

        if abs(total_weight - 1.0) > 0.01:
            raise ValueError(f"质量评分权重总和应为 1.0，当前为: {total_weight}")

        return True

    except Exception as e:
        print(f"SOP 验证失败: {e}")
        return False


if __name__ != "__main__":
    validate_sop()
