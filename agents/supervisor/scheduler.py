"""Scheduler Agent - 任务调度器

负责任务调度、并行执行管理、进度监控
"""

import asyncio
import time
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed


@dataclass
class TaskResult:
    """任务执行结果"""
    task_id: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0


@dataclass
class ExecutionStats:
    """执行统计"""
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    total_time: float = 0.0
    parallel_efficiency: float = 0.0


class SchedulerAgent:
    """调度器 Agent - 负责任务调度和并行执行管理"""

    def __init__(self, max_workers: int = 4):
        self.name = "Scheduler"
        self.version = "1.0"
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.task_registry: Dict[str, Callable] = {}  # 任务注册表

    def register_task(self, task_id: str, task_func: Callable):
        """注册任务函数"""
        self.task_registry[task_id] = task_func

    async def execute(
        self,
        tasks: List[Dict[str, Any]],
        context: Dict[str, Any],
        progress_callback: Optional[Callable] = None,
        cancel_check: Optional[Callable[[], bool]] = None
    ) -> Dict[str, Any]:
        """
        执行任务列表

        参数:
            tasks: 任务列表
            context: 执行上下文
            progress_callback: 进度回调函数 (stage_key, progress, message)
            cancel_check: 取消检查函数

        返回:
            Dict: 包含所有任务结果和统计信息
        """
        results = {}
        stats = ExecutionStats(total_tasks=len(tasks))
        start_time = time.time()

        # 按阶段分组任务
        stage_groups = self._group_by_stage(tasks)

        # 串行执行各个阶段
        for stage_id, stage_tasks in stage_groups.items():
            if cancel_check and cancel_check():
                results["cancelled"] = True
                break

            # 检查是否是并行阶段
            is_parallel = stage_tasks[0].get("parallel", False)

            if is_parallel:
                # 并行执行
                stage_results = await self._execute_parallel(
                    stage_tasks,
                    context,
                    progress_callback,
                    cancel_check
                )
            else:
                # 串行执行
                stage_results = await self._execute_sequential(
                    stage_tasks,
                    context,
                    progress_callback,
                    cancel_check
                )

            results.update(stage_results)

            # 更新统计
            for task_result in stage_results.values():
                if isinstance(task_result, TaskResult):
                    if task_result.success:
                        stats.completed_tasks += 1
                    else:
                        stats.failed_tasks += 1

        # 计算总执行时间
        stats.total_time = time.time() - start_time

        # 计算并行效率
        stats.parallel_efficiency = self._calculate_efficiency(tasks, stats.total_time)

        return {
            "results": results,
            "stats": stats,
            "success": stats.failed_tasks == 0
        }

    def _group_by_stage(self, tasks: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """按阶段分组任务"""
        groups = {}
        for task in tasks:
            stage = task.get("stage", "default")
            if stage not in groups:
                groups[stage] = []
            groups[stage].append(task)
        return groups

    async def _execute_sequential(
        self,
        tasks: List[Dict[str, Any]],
        context: Dict[str, Any],
        progress_callback: Optional[Callable],
        cancel_check: Optional[Callable[[], bool]]
    ) -> Dict[str, TaskResult]:
        """串行执行任务"""
        results = {}
        total = len(tasks)

        for idx, task in enumerate(tasks):
            # 检查取消
            if cancel_check and cancel_check():
                break

            task_id = task.get("task_id")
            progress = int((idx / total) * 100)
            message = f"正在执行: {task.get('description', task_id)}"

            if progress_callback:
                await self._safe_callback(progress_callback, task.get("stage"), progress, message)

            # 执行任务
            result = await self._execute_single_task(task, context)

            results[task_id] = result

            # 更新任务状态
            task["status"] = "completed" if result.success else "failed"

        return results

    async def _execute_parallel(
        self,
        tasks: List[Dict[str, Any]],
        context: Dict[str, Any],
        progress_callback: Optional[Callable],
        cancel_check: Optional[Callable[[], bool]]
    ) -> Dict[str, TaskResult]:
        """并行执行任务"""
        results = {}
        total = len(tasks)
        completed = 0

        # 创建异步任务
        async_tasks = []
        for task in tasks:
            async_task = self._execute_single_task(task, context)
            async_tasks.append(async_task)

        # 等待所有任务完成
        for idx, future in enumerate(asyncio.as_completed(async_tasks)):
            # 检查取消
            if cancel_check and cancel_check():
                # 取消剩余任务
                for f in async_tasks[idx+1:]:
                    f.cancel()
                break

            result = await future
            task_id = tasks[idx].get("task_id")
            results[task_id] = result

            # 更新进度
            completed += 1
            progress = int((completed / total) * 100)
            message = f"并行执行进度: {completed}/{total}"

            if progress_callback:
                await self._safe_callback(progress_callback, tasks[idx].get("stage"), progress, message)

        return results

    async def _execute_single_task(
        self,
        task: Dict[str, Any],
        context: Dict[str, Any]
    ) -> TaskResult:
        """执行单个任务"""
        task_id = task.get("task_id")
        task_func = self.task_registry.get(task_id)

        if not task_func:
            return TaskResult(
                task_id=task_id,
                success=False,
                error=f"任务函数未注册: {task_id}"
            )

        start_time = time.time()

        try:
            # 在线程池中执行任务
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor,
                task_func,
                context
            )

            execution_time = time.time() - start_time

            return TaskResult(
                task_id=task_id,
                success=True,
                result=result,
                execution_time=execution_time
            )

        except Exception as e:
            execution_time = time.time() - start_time

            return TaskResult(
                task_id=task_id,
                success=False,
                error=str(e),
                execution_time=execution_time
            )

    async def _safe_callback(self, callback: Callable, *args):
        """安全地调用回调函数"""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(*args)
            else:
                callback(*args)
        except Exception as e:
            print(f"进度回调错误: {e}")

    def _calculate_efficiency(self, tasks: List[Dict[str, Any]], actual_time: float) -> float:
        """计算并行效率"""
        # 估算串行执行时间
        base_times = {
            "planning": 30,
            "type_analysis": 45,
            "structure_analysis": 60,
            "dependency_analysis": 45,
            "code_pattern_analysis": 60,
            "quickstart_generation": 60,
            "overview_generation": 90,
            "architecture_generation": 120,
            "install_guide_generation": 90,
            "tutorial_generation": 120,
            "dev_guide_generation": 90,
            "troubleshoot_generation": 60,
            "review": 60,
            "optimization": 90,
            "finalization": 30
        }

        serial_time = 0
        for task in tasks:
            task_id = task.get("task_id")
            serial_time += base_times.get(task_id, 60)

        if serial_time == 0:
            return 0.0

        # 效率 = (串行时间 - 并行时间) / 串行时间
        efficiency = (serial_time - actual_time) / serial_time
        return max(0.0, min(1.0, efficiency))

    def cleanup(self):
        """清理资源"""
        self.executor.shutdown(wait=False)

    def get_status(self) -> Dict[str, Any]:
        """获取调度器状态"""
        return {
            "name": self.name,
            "version": self.version,
            "max_workers": self.max_workers,
            "registered_tasks": list(self.task_registry.keys()),
            "status": "ready"
        }


# 全局实例
scheduler_agent = SchedulerAgent()
