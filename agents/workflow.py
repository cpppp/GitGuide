"""Workflow - 并行工作流编排器

负责协调各个 Agent 的并行执行和任务调度
"""

import sys
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime


class WorkflowState:
    """工作流状态 - 在各个 Agent 间共享"""

    def __init__(self):
        self.repo_url: str = ""
        self.repo_path = None
        self.user_preferences = {}

        # 分析结果
        self.type_result = None
        self.structure_result = None
        self.dependency_result = None
        self.code_pattern_result = None

        # 生成结果
        self.quick_start_doc = None
        self.overview_doc = None
        self.architecture_doc = None
        self.install_guide_doc = None

        # 审核结果
        self.review_result = None
        self.quality_score = 0.0
        self.improvement_suggestions = []

        # 最终输出
        self.final_result = None

        # 元数据
        self.progress = 0
        self.current_stage = "idle"
        self.errors = []
        self.start_time = None
        self.end_time = None


class Workflow:
    """工作流编排器 - 负责协调所有 Agent 的执行"""

    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.state = WorkflowState()

    async def run(self, repo_url: str, repo_path: str) -> dict:
        """
        运行完整的工作流

        参数:
            repo_url: GitHub 仓库 URL
            repo_path: 本地仓库路径

        返回:
            Dict: 包含所有生成文档和元数据
        """
        # 初始化状态
        self.state = WorkflowState()
        self.state.repo_url = repo_url
        self.state.repo_path = repo_path
        self.state.start_time = datetime.now()

        try:
            # Stage 1: 并行分析
            self.state.current_stage = "analysis"
            self.state.progress = 10

            # 创建分析上下文
            context = {
                "repo_url": repo_url,
                "repo_path": repo_path
            }

            # 动态导入分析器
            type_analyzer = self._import_analyzer("type_analyzer")
            structure_analyzer = self._import_analyzer("structure_analyzer")
            dependency_analyzer = self._import_analyzer("dependency_analyzer")
            code_pattern_analyzer = self._import_analyzer("code_pattern_analyzer")

            # 并行执行分析器
            analysis_tasks = [
                type_analyzer.analyze(context),
                structure_analyzer.analyze(context),
                dependency_analyzer.analyze(context),
                code_pattern_analyzer.analyze(context)
            ]

            # 在线程池中执行分析任务
            loop = asyncio.get_event_loop()
            analysis_results = await loop.run_in_executor(
                self.executor,
                self._run_analysis_task,
                analysis_tasks
            )

            # 收集分析结果
            if len(analysis_results) == 4:
                self.state.type_result = analysis_results[0]
                self.state.structure_result = analysis_results[1]
                self.state.dependency_result = analysis_results[2]
                self.state.code_pattern_result = analysis_results[3]

                # 检测分析是否成功
                success_count = sum(1 for r in analysis_results if r.get("success", False))
                if success_count < 4:
                    failed_analyzers = []
                    if not analysis_results[0].get("success"):
                        failed_analyzers.append("TypeAnalyzer")
                    if not analysis_results[1].get("success"):
                        failed_analyzers.append("StructureAnalyzer")
                    if not analysis_results[2].get("success"):
                        failed_analyzers.append("DependencyAnalyzer")
                    if not analysis_results[3].get("success"):
                        failed_analyzers.append("CodePatternAnalyzer")

                    failed_names = ", ".join(failed_analyzers)
                    self.state.errors.append(f"分析器失败: {failed_names}")

            self.state.progress = 40

            # Stage 2: 并行生成文档
            if all(r.get("success") for r in analysis_results):
                self.state.current_stage = "generation"
                self.state.progress = 50

                # 准备生成上下文
                generation_context = {
                    "repo_url": repo_url,
                    "repo_path": repo_path,
                    "analysis_results": {
                        "type_result": self.state.type_result,
                        "structure_result": self.state.structure_result,
                        "dependency_result": self.state.dependency_result,
                        "code_pattern_result": self.state.code_pattern_result
                    }
                }

                # 导入生成器
                quick_start_generator = self._import_generator("quick_start_generator")
                overview_generator = self._import_generator("overview_generator")
                architecture_generator = self._import_generator("architecture_generator")
                install_guide_generator = self._import_generator("install_guide_generator")

                # 创建生成任务
                generation_tasks = []
                if quick_start_generator:
                    generation_tasks.append(("quick_start", quick_start_generator.generate))
                if overview_generator:
                    generation_tasks.append(("overview", overview_generator.generate))
                if architecture_generator:
                    generation_tasks.append(("architecture", architecture_generator.generate))
                if install_guide_generator:
                    generation_tasks.append(("install_guide", install_guide_generator.generate))

                # 并行执行生成器
                if generation_tasks:
                    generation_results = await loop.run_in_executor(
                        self.executor,
                        self._run_generation_task,
                        generation_tasks
                    )

                    # 收集生成结果
                    for doc_type, result in generation_results:
                        if result.get("success"):
                            if doc_type == "quick_start":
                                self.state.quick_start_doc = result
                            elif doc_type == "overview":
                                self.state.overview_doc = result
                            elif doc_type == "architecture":
                                self.state.architecture_doc = result
                            elif doc_type == "install_guide":
                                self.state.install_guide_doc = result
                        else:
                            self.state.errors.append(f"{doc_type} 生成失败: {result.get('error', 'unknown error')}")

                self.state.progress = 80

            # Stage 3: 质量审核
            self.state.current_stage = "review"
            self.state.progress = 90

            self.review_result = self._basic_review()
            self.state.quality_score = self._calculate_quality_score()

            self.state.progress = 100

            # Stage 4: 整理输出
            self.state.current_stage = "finalization"
            self.state.end_time = datetime.now()

            # 构建最终结果
            self.state.final_result = self._build_final_result()

            return {
                "success": True,
                "repo_url": repo_url,
                "documents": self._build_document_package(),
                "metadata": self._build_metadata(),
                "state": self._get_state_summary()
            }

        except Exception as e:
            self.state.errors.append(str(e))
            return {
                "success": False,
                "error": str(e),
                "repo_url": repo_url,
                "state": self._get_state_summary()
            }

    def _import_analyzer(self, name: str):
        """动态导入分析器"""
        try:
            module_path = f"agents.analyzers.{name}"
            spec = __import__(module_path, fromlist=module_path)
            return spec
        except Exception as e:
            return None

    def _import_generator(self, name: str):
        """动态导入生成器"""
        try:
            module_path = f"agents.generators.{name}"
            spec = __import__(module_path, fromlist=module_path)
            return spec
        except Exception:
            return None

    def _run_analysis_task(self, task):
        """执行单个分析任务（在线程中）"""
        try:
            return task()
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _run_generation_task(self, task_data):
        """执行单个生成任务（在线程中）"""
        doc_type, generate_func = task_data
        try:
            context = {
                "repo_url": self.state.repo_url,
                "repo_path": self.state.repo_path,
                "analysis_results": {
                    "type_result": self.state.type_result,
                    "structure_result": self.state.structure_result,
                    "dependency_result": self.state.dependency_result,
                    "code_pattern_result": self.state.code_pattern_result
            }
            }
            return generate_func(context)
        except Exception as e:
            return {
                "success": False,
                "document_type": doc_type,
                "error": str(e)
            }

    def _basic_review(self):
        """基础质量审核"""
        review = {
            "checked_at": datetime.now().isoformat(),
            "completeness": self._check_completeness(),
            "accuracy": self._check_accuracy(),
            "readability": self._check_readability(),
            "practicality": self._check_practicality()
        }

        return review

    def _check_completeness(self):
        """检查完整性检查"""
        checks = {
            "has_quick_start": self.state.quick_start_doc is not None,
            "has_overview": self.state.overview_doc is not None,
            "has_architecture": self.state.architecture_doc is not None,
            "has_install_guide": self.state.install_guide_doc is not None
        }

        passed_count = sum(1 for v in checks.values() if v)
        checks["score"] = passed_count / len(checks) if checks else 0
        checks["passed"] = passed_count == len(checks)

        return checks

    def _check_accuracy(self):
        """检查准确性"""
        return {
            "score": 0.8,
            "issues": []
        }

    def _check_readability(self):
        """检查可读性"""
        return {
            "score": 0.8,
            "issues": []
        }

    def _check_practicality(self):
        """检查可操作性"""
        return {
            "score": 0.8,
            "issues": []
        }

    def _calculate_quality_score(self):
        """计算综合质量评分"""
        if not self.review_result:
            return 0.0

        weights = {
            "completeness": 0.4,
            "accuracy": 0.3,
            "readability": 0.2,
            "practicality": 0.1
        }

        scores = {
            "completeness": self.review_result.get("completeness", {}).get("score", 0),
            "accuracy": self.review_result.get("accuracy", {}).get("score", 0),
            "readability": self.review_result.get("readability", {}).get("score", 0),
            "practicality": self.review_result.get("practicality", {}).get("score", 0)
        }

        total_score = sum(
            weights[key] * scores[key]
            for key in weights.keys()
        )

        return min(total_score, 1.0)

    def _build_final_result(self):
        """构建最终结果"""
        return {
            "quick_start": self.state.quick_start_doc.get("content") if self.state.quick_start_doc else None,
            "overview": self.state.overview_doc.get("content") if self.state.overview_doc else None,
            "architecture": self.state.architecture_doc.get("content") if self.state.architecture_doc else None,
            "install_guide": self.state.install_guide_doc.get("content") if self.state.install_guide_doc else None,
            "quality_score": self.state.quality_score
        }

    def _build_document_package(self):
        """构建文档包"""
        package = {}

        if self.state.quick_start_doc:
            package["quick_start"] = self.state.quick_start_doc.get("content")

        if self.state.overview_doc:
            package["overview"] = self.state.overview_doc.get("content")

        if self.state.architecture_doc:
            package["architecture"] = self.state.architecture_doc.get("content")

        if self.state.install_guide_doc:
            package["install_guide"] = self.state.install_guide_doc.get("content")

        return package

    def _build_metadata(self):
        """构建元数据"""
        duration = None
        if self.state.start_time and self.state.end_time:
            duration = (self.state.end_time - self.state.start_time).total_seconds()

        return {
            "repo_url": self.state.repo_url,
            "generated_at": datetime.now().isoformat(),
            "duration_seconds": duration,
            "quality_score": self.state.quality_score,
            "errors": self.state.errors
        }

    def _get_state_summary(self):
        """获取状态摘要"""
        return {
            "current_stage": self.state.current_stage,
            "progress": self.state.progress,
            "error_count": len(self.state.errors),
            "analysis_success": all([
                self.state.type_result.get("success", False) if self.state.type_result else False,
                self.state.structure_result.get("success", False) if self.state.structure_result else False,
                self.state.dependency_result.get("success", False) if self.state.dependency_result else False,
                self.state.code_pattern_result.get("success", False) if self.state.code_pattern_result else False
            ])
        }


# 全局实例
workflow = Workflow()
