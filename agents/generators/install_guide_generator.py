"""InstallGuideGenerator - 安装部署文档生成器

负责生成安装部署文档，帮助用户运行项目
"""

from typing import Dict, Any, List
from agents.generators.base_generator import BaseGenerator


class InstallGuideGenerator(BaseGenerator):
    """安装部署文档生成器 - 基于LLM生成高质量文档"""

    def __init__(self):
        super().__init__("InstallGuideGenerator", "install_guide")

    def generate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """生成安装部署文档"""
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
                "document_type": "install_guide",
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
                "document_type": "install_guide"
            }

    def generate_with_llm(self, context: Dict[str, Any], repo_path: str, analysis_results: Dict[str, Any]) -> str:
        """使用LLM生成安装部署文档"""
        
        prompt = f"""你是一个技术文档专家。请根据以下项目信息，生成一份高质量的安装部署文档。

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

请生成一份安装部署文档，包含以下内容：
1. **环境要求** - 必需的软件和版本
2. **安装步骤** - 详细的安装命令，区分不同操作系统
3. **配置说明** - 环境变量、配置文件等
4. **运行命令** - 开发模式和生产模式的运行方法
5. **常见问题** - 安装和运行过程中可能遇到的问题及解决方案

要求：
- 使用Markdown格式
- 代码块要指定语言（bash, python等）
- 命令要可以直接复制执行
- 内容要具体、准确，基于实际项目信息
"""

        return self._call_llm(prompt)

    def generate_fallback(self, context: Dict[str, Any], repo_path: str, analysis_results: Dict[str, Any]) -> str:
        """降级生成 - 当LLM不可用时使用模板"""
        lines = []

        lines.append("# 安装部署指南")
        lines.append("")

        lines.append("## 环境要求")
        requirements = self._generate_requirements(context)
        lines.extend(requirements)
        lines.append("")

        lines.append("## 安装步骤")
        install_steps = self._generate_install_steps(context)
        lines.extend(install_steps)
        lines.append("")

        lines.append("## 配置说明")
        configuration = self._generate_configuration(context)
        lines.extend(configuration)
        lines.append("")

        lines.append("## 运行命令")
        run_commands = self._generate_run_commands(context)
        lines.extend(run_commands)

        return "\n".join(lines)

    def _format_main_files(self, main_files: List[Dict[str, str]]) -> str:
        """格式化主要源文件"""
        if not main_files:
            return "无"
        
        result = []
        for f in main_files[:2]:
            result.append(f"### {f['name']}")
            result.append(f"```")
            result.append(f['content'][:400])
            result.append("```")
        return '\n'.join(result)

    def _generate_requirements(self, context: Dict[str, Any]) -> List[str]:
        """生成环境要求说明"""
        requirements = []
        language = context.get("language", "Unknown")
        frameworks = context.get("frameworks", [])

        if language == "Python":
            requirements.append("- Python 3.8+")
            requirements.append("- pip (Python 包管理器)")
            if frameworks:
                requirements.append(f"- 主要框架: {frameworks[0]}")
        elif language in ["JavaScript", "TypeScript"]:
            requirements.append("- Node.js 16+")
            requirements.append("- npm 或 yarn")
            if frameworks:
                requirements.append(f"- 主要框架: {frameworks[0]}")
        else:
            requirements.append(f"- {language} 运行环境")

        return requirements

    def _generate_install_steps(self, context: Dict[str, Any]) -> List[str]:
        """生成安装步骤"""
        steps = []
        language = context.get("language", "Unknown")
        package_manager = context.get("package_manager", "")

        steps.append("### 1. 克隆仓库")
        steps.append("```bash")
        steps.append("git clone <repository-url>")
        steps.append("cd <project-directory>")
        steps.append("```")
        steps.append("")

        if language == "Python":
            steps.append("### 2. 创建虚拟环境")
            steps.append("```bash")
            steps.append("python -m venv venv")
            steps.append("source venv/bin/activate  # Linux/Mac")
            steps.append("# venv\\Scripts\\activate  # Windows")
            steps.append("```")
            steps.append("")
            steps.append("### 3. 安装依赖")
            steps.append("```bash")
            steps.append("pip install -r requirements.txt")
            steps.append("```")
        elif language in ["JavaScript", "TypeScript"]:
            steps.append("### 2. 安装依赖")
            steps.append("```bash")
            if package_manager == "yarn":
                steps.append("yarn install")
            else:
                steps.append("npm install")
            steps.append("```")

        return steps

    def _generate_configuration(self, context: Dict[str, Any]) -> List[str]:
        """生成配置说明"""
        configuration = []
        language = context.get("language", "")

        configuration.append("### 环境变量")
        configuration.append("```bash")
        configuration.append("cp .env.example .env")
        configuration.append("# 编辑 .env 文件配置必要的环境变量")
        configuration.append("```")

        return configuration

    def _generate_run_commands(self, context: Dict[str, Any]) -> List[str]:
        """生成运行命令"""
        commands = []
        language = context.get("language", "")
        main_files = context.get("main_files", [])

        commands.append("### 开发模式")
        if language == "Python":
            commands.append("```bash")
            if main_files:
                commands.append(f"python {main_files[0]['name']}")
            else:
                commands.append("python main.py")
            commands.append("```")
        elif language in ["JavaScript", "TypeScript"]:
            commands.append("```bash")
            commands.append("npm run dev")
            commands.append("```")

        commands.append("")
        commands.append("### 运行测试")
        if language == "Python":
            commands.append("```bash")
            commands.append("pytest")
            commands.append("```")
        elif language in ["JavaScript", "TypeScript"]:
            commands.append("```bash")
            commands.append("npm test")
            commands.append("```")

        return commands

    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()


# 全局实例
install_guide_generator = InstallGuideGenerator()
