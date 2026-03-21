"""DevGuideGenerator - 开发指南文档生成器

负责生成开发指南文档，包含目录结构、代码规范、测试指南、贡献指南
"""

from typing import Dict, Any, List
from agents.generators.base_generator import BaseGenerator


class DevGuideGenerator(BaseGenerator):
    """开发指南文档生成器 - 基于LLM生成高质量文档"""

    def __init__(self):
        super().__init__("DevGuideGenerator", "dev_guide")

    def generate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """生成开发指南文档"""
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
                "document_type": "dev_guide",
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
                "document_type": "dev_guide"
            }

    def generate_with_llm(self, context: Dict[str, Any], repo_path: str, analysis_results: Dict[str, Any]) -> str:
        """使用LLM生成开发指南文档"""
        
        prompt = f"""你是一个技术文档专家。请根据以下项目信息，生成一份高质量的开发指南文档。

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
{context.get('readme', '无README')[:1500]}

## 主要依赖
{chr(10).join(context.get('requirements', [])[:15]) or '无'}

## 主要源文件
{self._format_main_files(context.get('main_files', []))}

---

请生成一份开发指南文档，包含以下内容：
1. **项目结构** - 详细说明目录结构和各模块职责
2. **代码规范** - 编码风格、命名规范、注释规范
3. **开发环境** - 开发环境配置、IDE推荐
4. **测试指南** - 如何运行测试、编写测试
5. **贡献指南** - 如何提交PR、代码审查流程
6. **发布流程** - 版本管理、发布步骤

要求：
- 使用Markdown格式
- 内容要基于实际项目信息
- 代码示例要完整
"""

        return self._call_llm(prompt)

    def generate_fallback(self, context: Dict[str, Any], repo_path: str, analysis_results: Dict[str, Any]) -> str:
        """降级生成 - 当LLM不可用时使用模板"""
        lines = []

        lines.append("# 开发指南")
        lines.append("")

        lines.append("## 项目结构")
        structure = self._generate_structure(context)
        lines.extend(structure)
        lines.append("")

        lines.append("## 代码规范")
        code_style = self._generate_code_style(context)
        lines.extend(code_style)
        lines.append("")

        lines.append("## 开发环境")
        dev_env = self._generate_dev_env(context)
        lines.extend(dev_env)
        lines.append("")

        lines.append("## 测试指南")
        testing = self._generate_testing(context)
        lines.extend(testing)

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

    def _generate_structure(self, context: Dict[str, Any]) -> List[str]:
        """生成项目结构说明"""
        lines = []
        directory_tree = context.get("directory_tree", "")

        lines.append("```")
        lines.append(directory_tree[:1000] if directory_tree else "项目目录结构")
        lines.append("```")
        lines.append("")
        lines.append("### 主要目录说明")
        lines.append("- `src/`: 源代码目录")
        lines.append("- `tests/`: 测试代码目录")
        lines.append("- `docs/`: 文档目录")
        lines.append("- `config/`: 配置文件目录")

        return lines

    def _generate_code_style(self, context: Dict[str, Any]) -> List[str]:
        """生成代码规范说明"""
        lines = []
        language = context.get("language", "")

        if language == "Python":
            lines.append("### Python 代码规范")
            lines.append("- 遵循 PEP 8 编码规范")
            lines.append("- 使用 4 空格缩进")
            lines.append("- 函数和变量使用 snake_case")
            lines.append("- 类使用 PascalCase")
            lines.append("- 使用类型注解")
        elif language in ["JavaScript", "TypeScript"]:
            lines.append("### JavaScript/TypeScript 代码规范")
            lines.append("- 使用 ESLint 进行代码检查")
            lines.append("- 使用 2 空格缩进")
            lines.append("- 变量使用 camelCase")
            lines.append("- 组件使用 PascalCase")
            lines.append("- 优先使用 const/let，避免 var")

        return lines

    def _generate_dev_env(self, context: Dict[str, Any]) -> List[str]:
        """生成开发环境说明"""
        lines = []
        language = context.get("language", "")

        lines.append("### 推荐工具")
        if language == "Python":
            lines.append("- IDE: VS Code / PyCharm")
            lines.append("- 虚拟环境: venv / conda")
            lines.append("- 包管理: pip")
        elif language in ["JavaScript", "TypeScript"]:
            lines.append("- IDE: VS Code")
            lines.append("- 包管理: npm / yarn")
            lines.append("- 调试: Chrome DevTools")

        return lines

    def _generate_testing(self, context: Dict[str, Any]) -> List[str]:
        """生成测试指南"""
        lines = []
        language = context.get("language", "")

        lines.append("### 运行测试")
        if language == "Python":
            lines.append("```bash")
            lines.append("# 运行所有测试")
            lines.append("pytest")
            lines.append("")
            lines.append("# 运行特定测试文件")
            lines.append("pytest tests/test_main.py")
            lines.append("")
            lines.append("# 查看测试覆盖率")
            lines.append("pytest --cov=src")
            lines.append("```")
        elif language in ["JavaScript", "TypeScript"]:
            lines.append("```bash")
            lines.append("# 运行所有测试")
            lines.append("npm test")
            lines.append("")
            lines.append("# 运行特定测试文件")
            lines.append("npm test -- --grep 'test name'")
            lines.append("")
            lines.append("# 查看测试覆盖率")
            lines.append("npm run test:coverage")
            lines.append("```")

        return lines

    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()


# 全局实例
dev_guide_generator = DevGuideGenerator()
