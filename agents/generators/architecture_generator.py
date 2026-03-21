"""ArchitectureGenerator - 架构设计文档生成器

负责生成系统架构设计文档
"""

from typing import Dict, Any, List
from agents.generators.base_generator import BaseGenerator


class ArchitectureGenerator(BaseGenerator):
    """架构设计文档生成器 - 基于LLM生成高质量文档"""

    def __init__(self):
        super().__init__("ArchitectureGenerator", "architecture")

    def generate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """生成架构设计文档"""
        repo_url = context.get("repo_url", "")
        repo_path = context.get("repo_path", "")
        analysis_results = context.get("analysis_results", {})

        try:
            gen_context = self._get_shared_context(context)
            
            content = self.generate_with_llm(gen_context, repo_path, analysis_results)
            
            if not content:
                content = self.generate_fallback(gen_context, repo_path, analysis_results)

            return {
                "success": True,
                "document_type": "architecture",
                "content": content,
                "metadata": {
                    "repo_url": repo_url,
                    "generated_at": self._get_timestamp(),
                    "used_llm": self.llm is not None
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "document_type": "architecture"
            }

    def generate_with_llm(self, context: Dict[str, Any], repo_path: str, analysis_results: Dict[str, Any]) -> str:
        """使用LLM生成架构设计文档"""
        
        prompt = f"""你是一个技术架构专家。请根据以下项目信息，生成一份高质量的架构设计文档。

## 项目信息
- 语言: {context.get('language', 'Unknown')}
- 项目类型: {context.get('project_type', 'Unknown')}
- 框架: {', '.join(context.get('frameworks', [])) or '无'}

## 目录结构
```
{context.get('directory_tree', '无')}
```

## README 内容
{context.get('readme', '无README')[:1500]}

## 主要源文件
{self._format_main_files(context.get('main_files', []))}

## 主要依赖
{chr(10).join(context.get('requirements', [])[:15]) or '无'}

---

请生成一份架构设计文档，包含以下内容：
1. **架构概览** - 整体架构风格和设计理念
2. **架构图** - 使用Mermaid语法绘制架构图（flowchart或graph）
3. **核心模块** - 列出核心模块及其职责
4. **数据流** - 描述主要数据流向
5. **技术选型理由** - 为什么选择这些技术
6. **扩展性设计** - 如何支持未来扩展

要求：
- 使用Markdown格式
- 架构图使用Mermaid语法，放在```mermaid代码块中
- 内容要基于实际的项目信息，不要编造
- 如果信息不足，可以说明"根据代码分析推测"
"""

        return self._call_llm(prompt)

    def generate_fallback(self, context: Dict[str, Any], repo_path: str, analysis_results: Dict[str, Any]) -> str:
        """降级生成 - 当LLM不可用时使用模板"""
        lines = []

        lines.append("# 架构设计")
        lines.append("")

        lines.append("## 架构概览")
        overview = self._generate_overview(context)
        lines.extend(overview)
        lines.append("")

        lines.append("## 架构图")
        diagram = self._generate_architecture_diagram(context)
        lines.append(diagram)
        lines.append("")

        lines.append("## 核心模块")
        modules = self._generate_modules(context)
        lines.extend(modules)
        lines.append("")

        lines.append("## 数据流")
        data_flow = self._generate_data_flow(context)
        lines.extend(data_flow)

        return "\n".join(lines)

    def _format_main_files(self, main_files: List[Dict[str, str]]) -> str:
        """格式化主要源文件"""
        if not main_files:
            return "无"
        
        result = []
        for f in main_files[:2]:
            result.append(f"### {f['name']}")
            result.append(f"```")
            result.append(f['content'][:300])
            result.append("```")
        return '\n'.join(result)

    def _generate_overview(self, context: Dict[str, Any]) -> List[str]:
        """生成架构概览"""
        lines = []
        language = context.get("language", "Unknown")
        frameworks = context.get("frameworks", [])
        project_type = context.get("project_type", "Unknown")

        lines.append(f"本项目采用 **{project_type}** 架构。")
        lines.append(f"主要使用 **{language}** 语言开发。")
        if frameworks:
            lines.append(f"核心框架: **{frameworks[0]}**。")

        return lines

    def _generate_architecture_diagram(self, context: Dict[str, Any]) -> str:
        """生成架构图（Mermaid格式）"""
        language = context.get("language", "Unknown")
        frameworks = context.get("frameworks", [])

        lines = ["```mermaid", "flowchart TD"]
        lines.append("    User[用户]")
        
        if language == "Python":
            lines.append("    API[API层]")
            lines.append("    Service[服务层]")
            lines.append("    Data[数据层]")
            lines.append("    User --> API")
            lines.append("    API --> Service")
            lines.append("    Service --> Data")
        elif language in ["JavaScript", "TypeScript"]:
            lines.append("    Frontend[前端组件]")
            lines.append("    Backend[后端服务]")
            lines.append("    Database[数据库]")
            lines.append("    User --> Frontend")
            lines.append("    Frontend --> Backend")
            lines.append("    Backend --> Database")
        else:
            lines.append("    App[应用层]")
            lines.append("    Core[核心层]")
            lines.append("    User --> App")
            lines.append("    App --> Core")

        lines.append("```")
        return "\n".join(lines)

    def _generate_modules(self, context: Dict[str, Any]) -> List[str]:
        """生成模块说明"""
        modules = []
        directory_tree = context.get("directory_tree", "")
        main_files = context.get("main_files", [])

        if main_files:
            for f in main_files[:3]:
                modules.append(f"- **{f['name']}**: 主要入口文件")

        modules.append("")
        modules.append("请查看目录结构了解完整模块划分。")

        return modules

    def _generate_data_flow(self, context: Dict[str, Any]) -> List[str]:
        """生成数据流说明"""
        language = context.get("language", "")

        if language == "Python":
            return [
                "1. 用户发起HTTP请求",
                "2. API层接收并验证请求",
                "3. 服务层处理业务逻辑",
                "4. 数据层访问数据库",
                "5. 结果逐层返回用户"
            ]
        elif language in ["JavaScript", "TypeScript"]:
            return [
                "1. 用户与前端界面交互",
                "2. 前端组件处理用户操作",
                "3. 通过API调用后端服务",
                "4. 后端处理并返回数据",
                "5. 前端更新界面展示"
            ]
        else:
            return [
                "1. 用户输入",
                "2. 应用处理",
                "3. 输出结果"
            ]

    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()


# 全局实例
architecture_generator = ArchitectureGenerator()
