"""ArchitectureGenerator - 架构设计文档生成器

负责生成系统架构设计文档
"""

from typing import Dict, Any, List, List


class ArchitectureGenerator:
    """架构设计文档生成器"""

    def __init__(self):
        self.name = "ArchitectureGenerator"
        self.version = "1.0"

    def generate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成架构设计文档

        参数:
            context: 包含分析结果、仓库信息等

        返回:
            Dict: 包含生成的文档和质量信息
        """
        repo_url = context.get("repo_url", "")
        analysis_results = context.get("analysis_results", {})

        try:
            # 从分析结果中提取信息
            structure_result = analysis_results.get("structure_result", {})
            code_pattern_result = analysis_results.get("code_pattern_result", {})

            # 构建文档内容
            content = self._build_architecture_content(
                repo_url,
                structure_result,
                code_pattern_result
            )

            return {
                "success": True,
                "document_type": "architecture",
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
                "document_type": "architecture"
            }

    def _build_architecture_content(
        self,
        repo_url: str,
        structure_result: Dict[str, Any],
        code_pattern_result: Dict[str, Any]
    ) -> str:
        """构建架构设计文档内容"""
        lines = []

        # 标题
        lines.append("# 架构设计")
        lines.append("")

        # 架构图
        lines.append("## 架构图")
        architecture_diagram = self._generate_architecture_diagram(code_pattern_result)
        lines.append(architecture_diagram)
        lines.append("")

        # 模块说明
        lines.append("## 模块说明")
        modules = self._generate_modules(structure_result)
        lines.extend(modules)
        lines.append("")

        # 数据流
        lines.append("## 数据流")
        data_flow = self._generate_data_flow(structure_result)
        lines.extend(data_flow)
        lines.append("")

        # 设计决策
        lines.append("## 设计决策")
        design_decisions = self._generate_design_decisions(code_pattern_result)
        lines.extend(design_decisions)

        return "\n".join(lines)

    def _generate_architecture_diagram(self, code_pattern_result: Dict[str, Any]) -> str:
        """生成架构图（文本形式）"""
        architecture_style = code_pattern_result.get("architecture_style", {})
        detected_patterns = architecture_style.get("detected_patterns", [])

        if not detected_patterns:
            return "```\n[通用架构图未检测到特定模式]\n```"

        diagram_parts = ["```", "┌─────────────────────────┐"]

        for pattern in detected_patterns[:2]:
            pattern_name = pattern.get("pattern", "Unknown")
            description = pattern.get("description", "")
            diagram_parts.append(f"│     {pattern_name}     │")

        diagram_parts.append("├─────────────────────────────────┤")
        diagram_parts.append("│        数据层              │")

        diagram_parts.append("├─────────────────────────────────┤")
        diagram_parts.append("│       业务逻辑层            │")
        diagram_parts.append("├─────────────────────────────────┤")
        diagram_parts.append("│        表现层              │")
        diagram_parts.append("└─────────────────────────────────┘")
        diagram_parts.append("│        数据层返回结果            │")
        diagram_parts.append("└arez────────────────────────────────┘")
        diagram_parts.append("```")

        return "\n".join(diagram_parts)

    def _generate_modules(self, structure_result: Dict[str, Any]) -> List[str]:
        """生成模块说明"""
        modules = []

        core_modules = structure_result.get("core_modules", [])
        entry_points = structure_result.get("entry_points", [])

        if core_modules:
            modules.append("### 核心模块")
            for module in core_modules:
                name = module.get("name", "")
                module_type = module.get("type", "")
                path = module.get("path", "")

                if module_type == "directory":
                    modules.append(f"- **{name}** (目录)")
                    modules.append(f"  - 路径: {path}")
                else:
                    modules.append(f"- **{name}** (文件)")
                    modules.append(f"  - 路径: {path}")

        if entry_points:
            modules.append("")
            modules.append("### 入口点")
            for entry in entry_points:
                name = entry.get("name", "")
                description = entry.get("description", "")
                modules.append(f"- **{name}**: {description}")

        return modules

    def _generate_data_flow(self, structure_result: Dict[str, Any]) -> List[str]:
        """生成数据流说明"""
        data_flow = []

        data_flow.append("### 主要数据流")
        data_flow.append("1. **用户请求 → 表现层**")
        data_flow.append("   - 用户通过前端界面发起请求")
        data_flow.append("")
        data_flow.append("2. **表现层 → 业务逻辑层**")
        data_flow.append("   - 表现层将请求传递给后端业务逻辑")
        data_flow.append("")
        data_flow.append("3. **业务逻辑层 → 数据层**")
        data_flow.append("   - 业务逻辑层处理数据并访问数据库")
        data_flow.append("")
        data_flow.append("4. **数据层返回结果**")
        data_flow.append("   - 数据层返回处理后的数据")
        data_flow.append("")
        data_flow.append("5. **结果返回用户**")
        data_flow.append("   - 最终结果返回给用户界面")

        return data_flow

    def _generate_design_decisions(self, code_pattern_result: Dict[str, Any]) -> List[str]:
        """生成设计决策说明"""
        decisions = []

        architecture_style = code_pattern_result.get("architecture_style", {})
        design_patterns = code_pattern_result.get("design_patterns", [])

        decisions.append("### 架构选择")
        primary_style = architecture_style.get("primary_style", "Unknown")
        decisions.append(f"- 选择 **{primary_style}** 架构风格")

        if design_patterns:
            decisions.append("")
            decisions.append("### 应用的设计模式")
            for pattern in design_patterns:
                decisions.append(f"- **{pattern}**: 提高代码的可维护性和扩展性")

        decisions.append("")
        decisions.append("### 代码组织")
        code_org = code_pattern_result.get("code_organization", {})
        structure_type = code_org.get("structure_type", "unknown")
        decisions.append(f"- 采用 **{structure_type}** 目录结构")

        return decisions

    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()


# 全局实例
architecture_generator = ArchitectureGenerator()
