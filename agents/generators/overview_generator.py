"""OverviewGenerator - 项目概览文档生成器

负责生成完整的项目概览文档
"""

from typing import Dict, Any, List, List


class OverviewGenerator:
    """项目概览文档生成器"""

    def __init__(self):
        self.name = "OverviewGenerator"
        self.version = "1.0"

    def generate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成项目概览文档

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
            dependency_result = analysis_results.get("dependency_result", {})
            code_pattern_result = analysis_results.get("code_pattern_result", {})

            # 构建文档内容
            content = self._build_overview_content(
                repo_url,
                type_result,
                dependency_result,
                code_pattern_result
            )

            return {
                "success": True,
                "document_type": "overview",
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
                "document_type": "overview"
            }

    def _build_overview_content(
        self,
        repo_url: str,
        type_result: Dict[str, Any],
        dependency_result: Dict[str, Any],
        code_pattern_result: Dict[str, Any]
    ) -> str:
        """构建项目概览文档内容"""
        lines = []

        # 标题
        lines.append("# 项目概览")
        lines.append("")

        # 项目背景
        lines.append("## 项目背景")
        background = self._generate_background(type_result, repo_url)
        lines.extend(background)
        lines.append("")

        # 功能列表
        lines.append("## 功能列表")
        features = self._generate_features(type_result, code_pattern_result)
        lines.extend(features)
        lines.append("")

        # 技术选型
        lines.append("## 技术选型")
        tech_stack = self._generate_tech_stack(type_result, dependency_result)
        lines.extend(tech_stack)
        lines.append("")

        # 适用场景
        lines.append("## 适用场景")
        scenarios = self._generate_scenarios(type_result)
        lines.extend(scenarios)

        return "\n".join(lines)

    def _generate_background(self, type_result: Dict[str, Any], repo_url: str) -> List[str]:
        """生成项目背景说明"""
        background = []

        project_type = type_result.get("project_type", "Unknown")
        language = type_result.get("language", "Unknown")

        background.append(f"本项目是一个 **{project_type}**")
        background.append(f"项目地址：{repo_url}")
        background.append("")
        background.append(f"使用 **{language}** 编程语言开发")

        return background

    def _generate_features(self, type_result: Dict[str, Any], code_pattern_result: Dict[str, Any]) -> List[str]:
        """生成功能列表"""
        features = []

        # 从代码模式分析中提取设计模式
        design_patterns = code_pattern_result.get("design_patterns", [])
        architecture_style = code_pattern_result.get("architecture_style", {})

        features.append("### 主要特性")

        if design_patterns:
            for pattern in design_patterns[:3]:
                features.append(f"- {pattern}")

        primary_style = architecture_style.get("primary_style", "")
        if primary_style and primary_style != "Unknown":
            features.append(f"- 采用 **{primary_style}** 架构风格")

        return features

    def _generate_tech_stack(self, type_result: Dict[str, Any], dependency_result: Dict[str, Any]) -> List[str]:
        """生成技术栈说明"""
        tech_stack = []

        language = type_result.get("language", "Unknown")
        framework = type_result.get("framework", "Unknown")
        build_system = type_result.get("build_system", "Unknown")

        tech_stack.append(f"- **编程语言**: {language}")
        tech_stack.append(f"- **主要框架**: {framework}")
        tech_stack.append(f"- **构建系统**: {build_system}")

        # 关键依赖
        key_deps = dependency_result.get("key_dependencies", [])
        if key_deps:
            tech_stack.append("")
            tech_stack.append("### 关键依赖")
            for dep in key_deps[:5]:
                tech_stack.append(f"- {dep}")

        return tech_stack

    def _generate_scenarios(self, type_result: Dict[str, Any]) -> List[str]:
        """生成适用场景说明"""
        scenarios = []

        project_type = type_result.get("project_type", "Unknown").lower()

        scenario_map = {
            "web application": [
                "- Web 应用程序开发",
                "- 前后端服务构建",
                "- RESTful API 开发"
            ],
            "python web application": [
                "- Python Web 应用开发",
                "- 数据驱动的应用",
                "- API 服务开发"
            ],
            "javascript": [
                "- 前端开发",
                "- 单页应用(SPA)",
                "- 组件化开发"
            ]
        }

        if project_type in scenario_map:
            scenarios.extend(scenario_map[project_type])
        else:
            scenarios.append("- 通用应用开发场景")

        return scenarios

    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()


# 全局实例
overview_generator = OverviewGenerator()
