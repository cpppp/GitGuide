"""QuickStartGenerator - 快速入门文档生成器

负责生成快速入门文档，帮助用户5分钟了解项目
"""

from typing import Dict, Any, List


class QuickStartGenerator:
    """快速入门文档生成器"""

    def __init__(self):
        self.name = "QuickStartGenerator"
        self.version = "1.0"

    def generate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成快速入门文档

        参数:
            context: 包含分析结果、仓库信息等

        返回:
            Dict: 包含生成的文档和质量信息
        """
        repo_url = context.get("repo_url", "")
        analysis_results = context.get("analysis_results", {})

        try:
            # 从分析结果中提取信息
            type_result = analysis_results.get("type_result", {})
            structure_result = analysis_results.get("structure_result", {})
            dependency_result = analysis_results.get("dependency_result", {})

            # 构建文档内容
            content = self._build_quick_start_content(
                repo_url,
                type_result,
                structure_result,
                dependency_result
            )

            return {
                "success": True,
                "document_type": "quick_start",
                "content": content,
                "metadata": {
                    "repo_url": repo_url,
                    "generated_at": self._get_timestamp()
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "document_type": "quick_start"
            }

    def _build_quick_start_content(
        self,
        repo_url: str,
        type_result: Dict[str, Any],
        structure_result: Dict[str, Any],
        dependency_result: Dict[str, Any]
    ) -> str:
        """构建快速入门文档内容"""
        lines = []

        # 标题
        lines.append("# 快速入门")
        lines.append("")

        # 一句话概括
        lines.append("## 一句话概括")
        summary = self._generate_summary(type_result, structure_result)
        lines.append(summary)
        lines.append("")

        # 核心概念
        lines.append("## 核心概念")
        concepts = self._generate_concepts(type_result, structure_result)
        lines.extend(concepts)
        lines.append("")

        # 最小化运行
        lines.append("## 最小化运行")
        quick_run = self._generate_quick_run(dependency_result)
        lines.extend(quick_run)

        return "\n".join(lines)

    def _generate_summary(self, type_result: Dict[str, Any], structure_result: Dict[str, Any]) -> str:
        """生成项目概括"""
        language = type_result.get("language", "Unknown")
        framework = type_result.get("framework", "Unknown")
        project_type = type_result.get("project_type", "Unknown")

        summary = f"这是一个 **{language}** "

        if framework != "Unknown":
            summary += f"使用 **{framework}** 框架的 "

        summary += f"**{project_type}** 项目。"

        return summary

    def _generate_concepts(self, type_result: Dict[str, Any], structure_result: Dict[str, Any]) -> str:
        """生成核心概念说明"""
        concepts = []

        framework = type_result.get("framework", "")
        modules = structure_result.get("core_modules", [])

        if framework:
            concepts.append(f"- **{framework}**: 主要框架")

        for module in modules[:3]:  # 最多显示3个核心模块
            module_name = module.get("name", "")
            if module_name:
                concepts.append(f"- **{module_name}**: 核心功能模块")

        return concepts

    def _generate_quick_run(self, dependency_result: Dict[str, Any]) -> List[str]:
        """生成最小化运行说明"""
        quick_run = []
        language = dependency_result.get("language", "")

        if language == "Python":
            quick_run.append("```bash")
            quick_run.append("# 安装依赖")
            quick_run.append("pip install -r requirements.txt")
            quick_run.append("")
            quick_run.append("# 运行项目")
            quick_run.append("python main.py  # 或 python app.py")
            quick_run.append("```")
        elif language in ["JavaScript", "TypeScript"]:
            quick_run.append("```bash")
            quick_run.append("# 安装依赖")
            quick_run.append("npm install")
            quick_run.append("")
            quick_run.append("# 运行项目")
            quick_run.append("npm run dev")
            quick_run.append("```")
        else:
            quick_run.append("```bash")
            quick_run.append("# 请查看项目文档获取详细的运行说明")
            quick_run.append("```")

        return quick_run

    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()


# 全局实例
quick_start_generator = QuickStartGenerator()
