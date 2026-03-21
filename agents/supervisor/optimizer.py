"""Optimizer Agent - 文档优化器

负责根据反馈优化文档，实现迭代改进
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass


class OptimizerAgent:
    """优化器 Agent - 负责文档优化和迭代改进"""

    def __init__(self, max_iterations: int = 3, target_score: float = 85.0):
        self.name = "Optimizer"
        self.version = "1.0"
        self.max_iterations = max_iterations
        self.target_score = target_score

    async def optimize(
        self,
        documents: Dict[str, str],
        review_result: Dict[str, Any],
        iteration: int = 0
    ) -> Dict[str, Any]:
        """
        优化文档

        参数:
            documents: 文档字典
            review_result: 审核结果
            iteration: 当前迭代次数

        返回:
            Dict: 优化后的文档和建议
        """
        # 检查是否达到目标分数
        overall_score = review_result.get("overall_score", 0)
        if overall_score >= self.target_score:
            return {
                "success": True,
                "documents": documents,
                "optimized": False,
                "message": "文档质量已达标，无需优化",
                "final_score": overall_score
            }

        # 检查是否超过最大迭代次数
        if iteration >= self.max_iterations:
            return {
                "success": True,
                "documents": documents,
                "optimized": False,
                "message": f"已达到最大迭代次数 ({self.max_iterations})",
                "final_score": overall_score
            }

        # 应用优化建议
        optimized_docs = await self._apply_optimizations(documents, review_result)

        # 生成优化报告
        report = self._generate_optimization_report(review_result)

        return {
            "success": True,
            "documents": optimized_docs,
            "optimized": True,
            "iteration": iteration,
            "message": f"第 {iteration + 1} 次优化完成",
            "report": report,
            "final_score": overall_score  # 这里的分数是优化前的，需要重新审核
        }

    async def _apply_optimizations(
        self,
        documents: Dict[str, str],
        review_result: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        应用优化建议到文档

        目前实现简单的内容扩展，实际可以使用 LLM 进行更智能的优化
        """
        optimized_docs = {}
        issues = review_result.get("issues", [])

        # 按文档类别分组问题
        doc_issues = {}
        for issue in issues:
            location = issue.get("location", "")
            if location:
                if location not in doc_issues:
                    doc_issues[location] = []
                doc_issues[location].append(issue)

        # 对每个文档应用优化
        for doc_type, content in documents.items():
            optimized_content = content
            type_issues = doc_issues.get(doc_type, [])

            for issue in type_issues:
                optimized_content = self._apply_single_fix(optimized_content, issue)

            optimized_docs[doc_type] = optimized_content

        return optimized_docs

    def _apply_single_fix(self, content: str, issue: Dict[str, Any]) -> str:
        """应用单个修复"""
        category = issue.get("category", "")
        message = issue.get("message", "")
        suggestion = issue.get("suggestion", "")

        if category == "completeness" and "内容过短" in message:
            # 添加占位符内容来扩展
            if not content.strip().endswith("\n"):
                content += "\n"
            content += "\n### 补充信息\n\n[建议根据实际情况添加更多详细说明]\n"

        elif category == "readability" and "缺少markdown标题" in message:
            # 添加标题
            if not content.startswith("#"):
                content = "## 内容概述\n\n" + content

        elif category == "practicality":
            # 添加实用信息
            if "环境要求" in message:
                if "\n### 环境要求\n" not in content:
                    content += "\n\n### 环境要求\n\n[请根据项目填写环境要求]\n"

        return content

    def _generate_optimization_report(self, review_result: Dict[str, Any]) -> Dict[str, Any]:
        """生成优化报告"""
        score = review_result.get("score", {})
        issues = review_result.get("issues", [])
        suggestions = review_result.get("suggestions", [])

        return {
            "before_score": {
                "completeness": score.get("completeness", 0),
                "accuracy": score.get("accuracy", 0),
                "readability": score.get("readability", 0),
                "practicality": score.get("practicality", 0),
                "overall": review_result.get("overall_score", 0)
            },
            "issues_count": len(issues),
            "issues_by_severity": {
                "error": len([i for i in issues if i.get("severity") == "error"]),
                "warning": len([i for i in issues if i.get("severity") == "warning"]),
                "info": len([i for i in issues if i.get("severity") == "info"])
            },
            "suggestions_count": len(suggestions),
            "applied_suggestions": suggestions
        }

    async def optimize_with_iteration(
        self,
        documents: Dict[str, str],
        review_func: Any,  # 审核函数
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        带迭代的完整优化流程

        参数:
            documents: 初始文档
            review_func: 审核函数，接受 documents 并返回 review_result
            context: 上下文信息

        返回:
            Dict: 最终优化结果
        """
        current_docs = documents.copy()
        iteration = 0
        history = []

        while iteration < self.max_iterations:
            # 审核当前文档
            review_result = await review_func(current_docs, context)

            # 检查是否达标
            if review_result.get("overall_score", 0) >= self.target_score:
                return {
                    "success": True,
                    "documents": current_docs,
                    "iterations": iteration,
                    "final_score": review_result.get("overall_score", 0),
                    "message": f"文档质量达标（{iteration} 次迭代）",
                    "history": history
                }

            # 优化文档
            optimize_result = await self.optimize(
                current_docs,
                review_result,
                iteration
            )

            if not optimize_result.get("optimized", False):
                # 无法继续优化
                break

            current_docs = optimize_result.get("documents", current_docs)
            history.append({
                "iteration": iteration,
                "score": review_result.get("overall_score", 0),
                "report": optimize_result.get("report", {})
            })

            iteration += 1

        # 最终审核
        final_review = await review_func(current_docs, context)

        return {
            "success": True,
            "documents": current_docs,
            "iterations": iteration,
            "final_score": final_review.get("overall_score", 0),
            "message": f"优化完成（{iteration} 次迭代）",
            "history": history,
            "final_review": final_review
        }

    def get_status(self) -> Dict[str, Any]:
        """获取优化器状态"""
        return {
            "name": self.name,
            "version": self.version,
            "max_iterations": self.max_iterations,
            "target_score": self.target_score,
            "status": "ready"
        }


# 全局实例
optimizer_agent = OptimizerAgent()
