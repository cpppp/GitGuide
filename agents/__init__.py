"""GitGuide Multi-Agent System

简化架构版本 V3.0.1
- Orchestrator: 入口编排器
- Workflow: 核心工作流（状态管理+并行调度+质量审核）
- Analyzer Team: 4个分析器
- Generator Team: 7个生成器
"""

from .orchestrator import run_fast, run_with_progress

__all__ = [
    "run_fast",
    "run_with_progress",
]
