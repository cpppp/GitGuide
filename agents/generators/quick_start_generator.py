"""QuickStartGenerator - 快速入门文档生成器

负责生成快速入门文档，帮助用户5分钟了解项目
"""

from typing import Dict, Any, List
from agents.generators.base_generator import BaseGenerator


class QuickStartGenerator(BaseGenerator):
    """快速入门文档生成器 - 基于LLM生成高质量文档"""

    def __init__(self):
        super().__init__("QuickStartGenerator", "quick_start")

    def generate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成快速入门文档

        参数:
            context: 包含分析结果、仓库信息等

        返回:
            Dict: 包含生成的文档和质量信息
        """
        repo_url = context.get("repo_url", "")
        repo_path = context.get("repo_path", "")
        analysis_results = context.get("analysis_results", {})

        try:
            # 使用共享上下文（避免重复文件读取）
            gen_context = self._get_shared_context(context)
            
            # 尝试使用LLM生成
            content = self.generate_with_llm(gen_context, repo_path, analysis_results)
            
            # 如果LLM失败，使用降级模板
            if not content:
                content = self.generate_fallback(gen_context, repo_path, analysis_results)

            return {
                "success": True,
                "document_type": "quick_start",
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
                "document_type": "quick_start"
            }

    def generate_with_llm(self, context: Dict[str, Any], repo_path: str, analysis_results: Dict[str, Any]) -> str:
        """使用LLM生成快速入门文档"""
        
        prompt = f"""你是一个技术文档专家。请根据以下项目信息，生成一份高质量的快速入门文档。

## 项目信息
- 语言: {context.get('language', 'Unknown')}
- 项目类型: {context.get('project_type', 'Unknown')}
- 框架: {', '.join(context.get('frameworks', [])) or '无'}
- 构建系统: {context.get('build_system', 'Unknown')}
- 包管理器: {context.get('package_manager', 'Unknown')}

## 目录结构
```
{context.get('directory_tree', '无')}
```

## README 内容
{context.get('readme', '无README')[:2000]}

## 主要依赖
{chr(10).join(context.get('requirements', [])[:20]) or '无'}

## 主要源文件
{self._format_main_files(context.get('main_files', []))}

---

请生成一份快速入门文档，包含以下内容：
1. **一句话概括** - 简洁描述项目是什么，解决什么问题
2. **核心概念** - 列出3-5个核心概念，每个用一句话解释
3. **环境要求** - 运行项目需要的软件和版本
4. **安装步骤** - 详细的安装命令，区分不同操作系统
5. **最小化运行** - 最简单的运行命令和预期结果
6. **下一步** - 建议用户接下来做什么

要求：
- 使用Markdown格式
- 代码块要指定语言
- 命令要可以直接复制执行
- 内容要具体、准确，不要泛泛而谈
"""

        return self._call_llm(prompt)

    def generate_fallback(self, context: Dict[str, Any], repo_path: str, analysis_results: Dict[str, Any]) -> str:
        """降级生成 - 当LLM不可用时使用模板"""
        lines = []
        
        lines.append("# 快速入门")
        lines.append("")
        
        # 一句话概括
        lines.append("## 一句话概括")
        summary = self._generate_summary(context)
        lines.append(summary)
        lines.append("")
        
        # 核心概念
        lines.append("## 核心概念")
        concepts = self._generate_concepts(context)
        lines.extend(concepts)
        lines.append("")
        
        # 环境要求
        lines.append("## 环境要求")
        requirements = self._generate_requirements(context)
        lines.extend(requirements)
        lines.append("")
        
        # 安装步骤
        lines.append("## 安装步骤")
        install = self._generate_install_steps(context)
        lines.extend(install)
        lines.append("")
        
        # 最小化运行
        lines.append("## 最小化运行")
        quick_run = self._generate_quick_run(context)
        lines.extend(quick_run)
        
        return "\n".join(lines)

    def _format_main_files(self, main_files: List[Dict[str, str]]) -> str:
        """格式化主要源文件"""
        if not main_files:
            return "无"
        
        result = []
        for f in main_files[:3]:
            result.append(f"### {f['name']}")
            result.append(f"```")
            result.append(f['content'][:500])
            result.append("```")
        return '\n'.join(result)

    def _generate_summary(self, context: Dict[str, Any]) -> str:
        """生成项目概括"""
        language = context.get("language", "Unknown")
        project_type = context.get("project_type", "Unknown")
        frameworks = context.get("frameworks", [])
        
        summary = f"这是一个 **{language}** 项目"
        if frameworks:
            summary += f"，使用 **{frameworks[0]}** 框架"
        summary += f"，类型为 **{project_type}**。"
        
        return summary

    def _generate_concepts(self, context: Dict[str, Any]) -> List[str]:
        """生成核心概念说明"""
        concepts = []
        frameworks = context.get("frameworks", [])
        language = context.get("language", "")
        
        for fw in frameworks[:3]:
            concepts.append(f"- **{fw}**: 主要框架")
        
        if language == "Python":
            concepts.append("- **pip**: Python 包管理器")
            if context.get("requirements"):
                concepts.append("- **虚拟环境**: 推荐使用 venv 或 conda")
        elif language in ["JavaScript", "TypeScript"]:
            concepts.append("- **npm/yarn**: Node.js 包管理器")
            concepts.append("- **Node.js**: JavaScript 运行时")
        
        return concepts if concepts else ["- 请查看项目文档了解更多"]

    def _generate_requirements(self, context: Dict[str, Any]) -> List[str]:
        """生成环境要求"""
        lines = []
        language = context.get("language", "")
        
        if language == "Python":
            lines.append("- Python 3.8+")
            lines.append("- pip (Python 包管理器)")
        elif language in ["JavaScript", "TypeScript"]:
            lines.append("- Node.js 16+")
            lines.append("- npm 或 yarn")
        elif language == "Go":
            lines.append("- Go 1.18+")
        elif language == "Java":
            lines.append("- JDK 11+")
            lines.append("- Maven 或 Gradle")
        else:
            lines.append("- 请查看项目文档获取环境要求")
        
        return lines

    def _generate_install_steps(self, context: Dict[str, Any]) -> List[str]:
        """生成安装步骤"""
        lines = []
        language = context.get("language", "")
        package_manager = context.get("package_manager", "")
        
        if language == "Python":
            lines.append("```bash")
            lines.append("# 克隆仓库")
            lines.append("git clone <repository-url>")
            lines.append("cd <project-directory>")
            lines.append("")
            lines.append("# 创建虚拟环境（推荐）")
            lines.append("python -m venv venv")
            lines.append("source venv/bin/activate  # Linux/Mac")
            lines.append("# venv\\Scripts\\activate  # Windows")
            lines.append("")
            lines.append("# 安装依赖")
            lines.append("pip install -r requirements.txt")
            lines.append("```")
        elif language in ["JavaScript", "TypeScript"]:
            lines.append("```bash")
            lines.append("# 克隆仓库")
            lines.append("git clone <repository-url>")
            lines.append("cd <project-directory>")
            lines.append("")
            lines.append("# 安装依赖")
            if package_manager == "yarn":
                lines.append("yarn install")
            else:
                lines.append("npm install")
            lines.append("```")
        else:
            lines.append("请查看项目 README 获取安装说明。")
        
        return lines

    def _generate_quick_run(self, context: Dict[str, Any]) -> List[str]:
        """生成最小化运行说明"""
        lines = []
        language = context.get("language", "")
        main_files = context.get("main_files", [])
        
        if language == "Python":
            lines.append("```bash")
            if main_files:
                first_main = main_files[0]["name"]
                lines.append(f"python {first_main}")
            else:
                lines.append("python main.py  # 或 app.py")
            lines.append("```")
        elif language in ["JavaScript", "TypeScript"]:
            lines.append("```bash")
            lines.append("npm run dev  # 或 npm start")
            lines.append("```")
        else:
            lines.append("请查看项目文档获取运行说明。")
        
        return lines

    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()


# 全局实例
quick_start_generator = QuickStartGenerator()
