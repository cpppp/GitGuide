"""OverviewGenerator - 项目概览文档生成器

负责生成完整的项目概览文档
"""

from typing import Dict, Any, List
from agents.generators.base_generator import BaseGenerator


class OverviewGenerator(BaseGenerator):
    """项目概览文档生成器 - 基于LLM生成高质量文档"""

    def __init__(self):
        super().__init__("OverviewGenerator", "overview")

    def generate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成项目概览文档

        参数:
            context: 包含分析结果、仓库信息等

        返回:
            Dict: 包含生成的文档和质量信息
        """
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
                "document_type": "overview",
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
                "document_type": "overview"
            }

    def generate_with_llm(self, context: Dict[str, Any], repo_path: str, analysis_results: Dict[str, Any]) -> str:
        """使用LLM生成项目概览文档"""
        
        prompt = f"""你是一个技术文档专家。请根据以下项目信息，生成一份高质量的项目概览文档。

## 项目信息
- 语言: {context.get('language', 'Unknown')}
- 项目类型: {context.get('project_type', 'Unknown')}
- 框架: {', '.join(context.get('frameworks', [])) or '无'}
- 构建系统: {context.get('build_system', 'Unknown')}

## 目录结构
```
{context.get('directory_tree', '无')}
```

## README 内容
{context.get('readme', '无README')[:2000]}

## 主要依赖
{chr(10).join(context.get('requirements', [])[:20]) or '无'}

---

请生成一份项目概览文档，包含以下内容：
1. **项目背景** - 项目是什么，解决什么问题，目标用户是谁
2. **核心功能** - 列出5-8个核心功能点
3. **技术架构** - 技术栈、架构风格、设计模式
4. **适用场景** - 适合什么类型的项目和开发者
5. **项目特色** - 与同类项目相比的优势

要求：
- 使用Markdown格式
- 内容要具体、准确，基于提供的项目信息
- 不要编造不存在的功能
- 如果信息不足，可以说明"根据项目代码分析"
"""

        return self._call_llm(prompt)

    def generate_fallback(self, context: Dict[str, Any], repo_path: str, analysis_results: Dict[str, Any]) -> str:
        """降级生成 - 当LLM不可用时使用模板"""
        lines = []

        lines.append("# 项目概览")
        lines.append("")

        lines.append("## 项目背景")
        background = self._generate_background(context)
        lines.extend(background)
        lines.append("")

        lines.append("## 核心功能")
        features = self._generate_features(context)
        lines.extend(features)
        lines.append("")

        lines.append("## 技术架构")
        tech_stack = self._generate_tech_stack(context)
        lines.extend(tech_stack)
        lines.append("")

        lines.append("## 适用场景")
        scenarios = self._generate_scenarios(context)
        lines.extend(scenarios)

        return "\n".join(lines)

    def _generate_background(self, context: Dict[str, Any]) -> List[str]:
        """生成项目背景说明"""
        background = []

        project_type = context.get("project_type", "Unknown")
        language = context.get("language", "Unknown")
        frameworks = context.get("frameworks", [])

        background.append(f"本项目是一个 **{project_type}** 项目。")
        background.append(f"使用 **{language}** 编程语言开发。")
        if frameworks:
            background.append(f"主要使用 **{frameworks[0]}** 框架。")

        return background

    def _generate_features(self, context: Dict[str, Any]) -> List[str]:
        """生成功能列表"""
        features = []
        frameworks = context.get("frameworks", [])
        language = context.get("language", "")

        features.append("### 主要特性")
        features.append("")

        for fw in frameworks[:3]:
            features.append(f"- 基于 {fw} 框架")

        if language == "Python":
            features.append("- Python 后端服务")
            features.append("- 模块化设计")
        elif language in ["JavaScript", "TypeScript"]:
            features.append("- 前端/全栈开发")
            features.append("- 组件化架构")

        return features if len(features) > 2 else ["- 请查看项目文档了解更多功能"]

    def _generate_tech_stack(self, context: Dict[str, Any]) -> List[str]:
        """生成技术栈说明"""
        tech_stack = []

        language = context.get("language", "Unknown")
        frameworks = context.get("frameworks", [])
        build_system = context.get("build_system", "Unknown")

        tech_stack.append(f"- **编程语言**: {language}")
        if frameworks:
            tech_stack.append(f"- **主要框架**: {frameworks[0]}")
        tech_stack.append(f"- **构建系统**: {build_system}")

        requirements = context.get("requirements", [])
        if requirements:
            tech_stack.append("")
            tech_stack.append("### 关键依赖")
            for dep in requirements[:5]:
                if dep:
                    tech_stack.append(f"- {dep}")

        return tech_stack

    def _generate_scenarios(self, context: Dict[str, Any]) -> List[str]:
        """生成适用场景说明"""
        scenarios = []
        project_type = context.get("project_type", "").lower()

        if "web" in project_type or "api" in project_type:
            scenarios.append("- Web 应用程序开发")
            scenarios.append("- RESTful API 服务")
        elif "react" in project_type or "vue" in project_type:
            scenarios.append("- 单页应用(SPA)开发")
            scenarios.append("- 前端组件开发")
        else:
            scenarios.append("- 通用应用开发")

        return scenarios

    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()


# 全局实例
overview_generator = OverviewGenerator()
