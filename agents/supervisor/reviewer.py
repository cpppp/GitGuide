"""Reviewer Agent - 文档审核器

负责文档完整性检查、技术准确性验证、质量评分
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from core.sop import GITGUIDE_SOP


@dataclass
class QualityIssue:
    """质量问题"""
    issue_id: str
    severity: str  # "error", "warning", "info"
    category: str  # "completeness", "accuracy", "readability", "practicality"
    message: str
    suggestion: str = ""
    location: str = ""


@dataclass
class QualityScore:
    """质量评分"""
    completeness: float = 0.0
    accuracy: float = 0.0
    readability: float = 0.0
    practicality: float = 0.0
    overall: float = 0.0


class ReviewerAgent:
    """审核器 Agent - 负责文档质量审核和评分"""

    def __init__(self):
        self.name = "Reviewer"
        self.version = "1.0"
        self.quality_dimensions = GITGUIDE_SOP.get("quality_dimensions", {})

    async def review(
        self,
        documents: Dict[str, str],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        审核文档质量

        参数:
            documents: 文档字典，键为文档类型，值为文档内容
            context: 上下文信息

        返回:
            Dict: 包含质量评分、问题列表和建议
        """
        issues: List[QualityIssue] = []
        suggestions: List[str] = []

        # 1. 检查完整性
        completeness_issues = self._check_completeness(documents)
        issues.extend(completeness_issues)

        # 2. 检查准确性
        accuracy_issues = await self._check_accuracy(documents, context)
        issues.extend(accuracy_issues)

        # 3. 检查可读性
        readability_issues = self._check_readability(documents)
        issues.extend(readability_issues)

        # 4. 检查实用性
        practicality_issues = await self._check_practicality(documents, context)
        issues.extend(practicality_issues)

        # 5. 生成建议
        suggestions = self._generate_suggestions(issues)

        # 6. 计算质量评分
        score = self._calculate_score(documents, issues)

        return {
            "score": score,
            "issues": [self._issue_to_dict(issue) for issue in issues],
            "suggestions": suggestions,
            "overall_score": score.overall,
            "pass_threshold": score.overall >= 85.0
        }

    def _check_completeness(self, documents: Dict[str, str]) -> List[QualityIssue]:
        """检查文档完整性"""
        issues = []

        # 检查必需的文档类型

        required_docs = {
            "learning_doc": "学习文档",
            "setup_guide": "启动指南"
        }

        for doc_type, doc_name in required_docs.items():
            if doc_type not in documents or not documents[doc_type].strip():
                issues.append(QualityIssue(
                    issue_id=f"missing_{doc_type}",
                    severity="error",
                    category="completeness",
                    message=f"缺少必需的文档: {doc_name}",
                    suggestion=f"请生成{doc_name}"
                ))
            else:
                # 检查文档内容是否过短
                content = documents[doc_type]
                if len(content.strip()) < 100:
                    issues.append(QualityIssue(
                        issue_id=f"short_{doc_type}",
                        severity="warning",
                        category="completeness",
                        message=f"{doc_name}内容过短",
                        suggestion=f"请扩展{doc_name}的内容"
                    ))

        return issues

    async def _check_accuracy(
        self,
        documents: Dict[str, str],
        context: Optional[Dict[str, Any]]
    ) -> List[QualityIssue]:
        """检查技术准确性"""
        issues = []

        # 检查启动指南中的命令
        setup_guide = documents.get("setup_guide", "")

        # 检查是否包含可执行的命令
        if "```" not in setup_guide:
            issues.append(QualityIssue(
                issue_id="no_code_blocks",
                severity="warning",
                category="accuracy",
                message="启动指南缺少代码块",
                suggestion="请使用 markdown 代码块展示命令"
            ))

        # 检查是否包含常见命令格式
        if "npm install" in setup_guide or "pip install" in setup_guide:
            # 命令存在，无需警告
            pass
        else:
            issues.append(QualityIssue(
                issue_id="no_install_command",
                severity="warning",
                category="accuracy",
                message="启动指南可能缺少安装命令",
                suggestion="请确保包含依赖安装命令"
            ))

        return issues

    def _check_readability(self, documents: Dict[str, str]) -> List[QualityIssue]:
        """检查文档可读性"""
        issues = []

        for doc_type, content in documents.items():
            if not content.strip():
                continue

            # 检查是否使用了markdown标题
            if "##" not in content:
                issues.append(QualityIssue(
                    issue_id=f"no_headers_{doc_type}",
                    severity="warning",
                    category="readability",
                    message=f"{doc_type}缺少markdown标题",
                    suggestion="请使用 markdown 标题组织内容"
                ))

            # 检查段落长度
            paragraphs = content.split("\n\n")
            long_paragraphs = [p for p in paragraphs if len(p) > 500]
            if long_paragraphs:
                issues.append(QualityIssue(
                    issue_id=f"long_paragraphs_{doc_type}",
                    severity="info",
                    category="readability",
                    message=f"{doc_type}存在过长的段落",
                    suggestion="建议将长段落拆分成多个短段落"
                ))

        return issues

    async def _check_practicality(
        self,
        documents: Dict[str, str],
        context: Optional[Dict[str, Any]]
    ) -> List[QualityIssue]:
        """检查实用性"""
        issues = []

        setup_guide = documents.get("setup_guide", "")

        # 检查是否包含环境要求
        if "环境" not in setup_guide and "requirements" not in setup_guide.lower():
            issues.append(QualityIssue(
                issue_id="no_environment_info",
                severity="warning",
                category="practicality",
                message="启动指南缺少环境要求说明",
                suggestion="请添加环境要求部分"
            ))

        # 检查是否包含运行步骤
        if "运行" not in setup_guide and "run" not in setup_guide.lower():
            issues.append(QualityIssue(
                issue_id="no_run_steps",
                severity="warning",
                category="practicality",
                message="启动指南缺少运行步骤",
                suggestion="请添加项目运行步骤"
            ))

        return issues

    def _generate_suggestions(self, issues: List[QualityIssue]) -> List[str]:
        """生成改进建议"""
        suggestions = []

        # 按严重程度和类别分组
        error_issues = [i for i in issues if i.severity == "error"]
        warning_issues = [i for i in issues if i.severity == "warning"]

        if error_issues:
            suggestions.append("优先处理以下错误：")
            for issue in error_issues:
                suggestions.append(f"  - {issue.message}")

        if warning_issues:
            suggestions.append("\n建议改进以下警告：")
            for issue in warning_issues[:3]:  # 只显示前3个
                suggestions.append(f"  - {issue.message}")

        return suggestions

    def _calculate_score(
        self,
        documents: Dict[str, str],
        issues: List[QualityIssue]
    ) -> QualityScore:
        """计算质量评分"""
        # 按类别统计问题
        issues_by_category = {
            "completeness": [i for i in issues if i.category == "completeness"],
            "accuracy": [i for i in issues if i.category == "accuracy"],
            "readability": [i for i in issues if i.category == "readability"],
            "practicality": [i for i in issues if i.category == "practicality"]
        }

        # 计算各维度分数（基础分100，根据问题扣分）
        scores = {}
        for category, category_issues in issues_by_category.items():
            base_score = 100.0

            # 根据严重程度扣分
            for issue in category_issues:
                if issue.severity == "error":
                    base_score -= 30
                elif issue.severity == "warning":
                    base_score -= 10
                elif issue.severity == "info":
                    base_score -= 5

            scores[category] = max(0.0, min(100.0, base_score))

        # 计算加权总分
        weights = self.quality_dimensions
        overall = (
            scores["completeness"] * weights["completeness"]["weight"] +
            scores["accuracy"] * weights["accuracy"]["weight"] +
            scores["readability"] * weights["readability"]["weight"] +
            scores["practicality"] * weights["practicality"]["weight"]
        )

        return QualityScore(
            completeness=scores["completeness"],
            accuracy=scores["accuracy"],
            readability=scores["readability"],
            practicality=scores["practicality"],
            overall=overall
        )

    def _issue_to_dict(self, issue: QualityIssue) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "issue_id": issue.issue_id,
            "severity": issue.severity,
            "category": issue.category,
            "message": issue.message,
            "suggestion": issue.suggestion,
            "location": issue.location
        }

    def get_status(self) -> Dict[str, Any]:
        """获取审核器状态"""
        return {
            "name": self.name,
            "version": self.version,
            "status": "ready"
        }


# 全局实例
reviewer_agent = ReviewerAgent()
