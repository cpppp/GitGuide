"""InstallGuideGenerator - 安装部署文档生成器

负责生成安装部署文档，帮助用户运行项目
"""

from typing import Dict, Any, List


class InstallGuideGenerator:
    """安装部署文档生成器"""

    def __init__(self):
        self.name = "InstallGuideGenerator"
        self.version = "1.0"

    def generate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成安装部署文档

        参数:
            context: 包含分析结果、仓库信息等

        返回:
            Dict: 包含生成的文档和质量信息
        """
        repo_url = context.get("repo_url", "")
        analysis = context.get("analysis_results", {})
        analysis_results = analysis.get("analysis_results", analysis)

        try:
            # 从分析结果中提取信息
            type_result = analysis_results.get("type_result", {})
            dependency_result = analysis_results.get("dependency_result", {})

            # 构建文档内容
            content = self._build_install_guide_content(
                repo_url,
                type_result,
                dependency_result
            )

            return {
                "success": True,
                "document_type": "install_guide",
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
                "document_type": "install_guide"
            }

    def _build_install_guide_content(
        self,
        repo_url: str,
        type_result: Dict[str, Any],
        dependency_result: Dict[str, Any]
    ) -> str:
        """构建安装部署文档内容"""
        lines = []

        # 标题
        lines.append("# 安装部署指南")
        lines.append("")

        # 环境要求
        lines.append("## 环境要求")
        requirements = self._generate_requirements(type_result)
        lines.extend(requirements)
        lines.append("")

        # 安装步骤
        lines.append("## 安装步骤")
        install_steps = self._generate_install_steps(type_result, dependency_result)
        lines.extend(install_steps)
        lines.append("")

        # 配置说明
        lines.append("## 配置说明")
        configuration = self._generate_configuration(type_result, dependency_result)
        lines.extend(configuration)
        lines.append("")

        # 运行命令
        lines.append("## 运行命令")
        run_commands = self._generate_run_commands(type_result)
        lines.extend(run_commands)
        lines.append("")

        # 常见问题
        lines.append("## 常见问题")
        common_issues = self._generate_common_issues(type_result, dependency_result)
        lines.extend(common_issues)

        return "\n".join(lines)

    def _generate_requirements(self, type_result: Dict[str, Any]) -> List[str]:
        """生成环境要求说明"""
        requirements = []

        language = type_result.get("language", "Unknown")
        framework = type_result.get("frameworks", [])

        requirements.append(f"- **编程语言**: {language}")
        requirements.append(f"- **框架**: {', '.join(framework) if framework else 'None'}")

        if language == "Python":
            requirements.append("- **Python 版本**: Python 3.8+")
            requirements.append("- **推荐工具**: pip, virtualenv/conda")
        elif language in ["JavaScript", "TypeScript"]:
            requirements.append("- **Node.js 版本**: Node.js 16+")
            requirements.append("- **推荐工具**: npm/yarn/pnpm")

        return requirements

    def _generate_install_steps(self, type_result: Dict[str, Any], dependency_result: Dict[str, Any]) -> List[str]:
        """生成安装步骤"""
        steps = []

        language = type_result.get("language", "Unknown")

        steps.append("### 1. 克隆仓库")
        steps.append("```bash")
        steps.append("git clone <your-repo-url>")
        steps.append("cd <your-repo-name>")
        steps.append("```")
        steps.append("")

        if language == "Python":
            steps.append("### 2. 创建虚拟环境")
            steps.append("```bash")
            steps.append("# 使用 virtualenv")
            steps.append("python -m venv venv")
            steps.append("source venv/bin/activate")
            steps.append("")
            steps.append("# 或使用 conda")
            steps.append("conda create -n myenv python=3.9")
            steps.append("conda activate myenv")
            steps.append("```")
            steps.append("")
            steps.append("### 3. 安装依赖")
            steps.append("```bash")
            steps.append("pip install -r requirements.txt")
            steps.append("# 或者如果使用 poetry")
            steps.append("poetry install")
            steps.append("```")
        elif language in ["JavaScript", "TypeScript"]:
            steps.append("### 2. 安装依赖")
            steps.append("```bash")
            steps.append("npm install")
            steps.append("# 或者使用 yarn")
            steps.append("yarn install")
            steps.append("```")

        return steps

    def _generate_configuration(self, type_result: Dict[str, Any], dependency_result: Dict[str, Any]) -> List[str]:
        """生成配置说明"""
        configuration = []

        language = type_result.get("language", "Unknown")

        if language == "Python":
            configuration.append("### 环境变量配置")
            configuration.append("```bash")
            configuration.append("# 复制示例配置文件")
            configuration.append("cp .env.example .env")
            configuration.append("")
            configuration.append("# 编辑配置文件")
            configuration.append("nano .env  # 或使用你喜欢的编辑器")
            configuration.append("```")
            configuration.append("")
            configuration.append("### 数据库配置（如需要）")
            configuration.append("- 确保数据库服务已启动")
            configuration.append("- 在 `.env` 文件中配置数据库连接信息")
        elif language in ["JavaScript", "TypeScript"]:
            configuration.append("### 环境变量配置")
            configuration.append("```bash")
            configuration.append("# 复制示例配置文件")
            configuration.append("cp .env.example .env")
            configuration.append("")
            configuration.append("# 编辑配置文件")
            configuration.append("nano .env")
            configuration.append("```")

        return configuration

    def _generate_run_commands(self, type_result: Dict[str, Any]) -> List[str]:
        """生成运行命令"""
        commands = []

        language = type_result.get("language", "Unknown")

        commands.append("### 开发模式运行")
        if language == "Python":
            commands.append("```bash")
            commands.append("# 查找入口文件")
            commands.append("ls *.py  # 列出所有 Python 文件")
            commands.append("")
            commands.append("# 运行应用")
            commands.append("python main.py  # 或 python app.py 或 python manage.py runserver")
            commands.append("```")
        elif language in ["JavaScript", "TypeScript"]:
            commands.append("```bash")
            commands.append("# 开发模式")
            commands.append("npm run dev")
            commands.append("")
            commands.append("# 生产模式")
            commands.append("npm run build && npm start")
            commands.append("```")

        commands.append("")
        commands.append("### 运行测试")
        if language == "Python":
            commands.append("```bash")
            commands.append("pytest tests/")
            commands.append("```")
        elif language in ["JavaScript", "TypeScript"]:
            commands.append("```bash")
            commands.append("npm test")
            commands.append("```")

        return commands

    def _generate_common_issues(self, type_result: Dict[str, Any], dependency_result: Dict[str, Any]) -> List[str]:
        """生成常见问题说明"""
        issues = []

        language = type_result.get("language", "Unknown")

        issues.append("### 常见问题及解决方案")

        if language == "Python":
            issues.append("**问题1**: 模块导入错误")
            issues.append("```")
            issues.append("ModuleNotFoundError: No module named 'xxx'")
            issues.append("```")
            issues.append("")
            issues.append("**解决方案**:")
            issues.append("- 检查虚拟环境是否已激活")
            issues.append("- 运行 `pip list` 确认依赖已安装")
            issues.append("- 检查 Python 版本是否兼容")
            issues.append("")
            issues.append("**问题2**: 数据库连接失败")
            issues.append("- 检查数据库服务是否运行")
            issues.append("- 检查 `.env` 文件中的数据库配置")
            issues.append("- 检查数据库用户名和密码是否正确")
        elif language in ["JavaScript", "TypeScript"]:
            issues.append("**问题1**: npm install 失败")
            issues.append("- 删除 node_modules 目录后重试: `rm -rf node_modules`")
            issues.append("- 清理 npm 缓存: `npm cache clean --force`")
            issues.append("- 使用淘宝镜像加速: `npm config set registry https://registry.npmmirror.com`")
            issues.append("")
            issues.append("**问题2**: 端口被占用")
            issues.append("- 检查端口是否被其他程序占用")
            issues.append("- 修改 `.env` 文件中的端口配置")
            issues.append("- 使用 `lsof -i :端口号` 查看端口占用情况")

        return issues

    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()


# 全局实例
install_guide_generator = InstallGuideGenerator()
