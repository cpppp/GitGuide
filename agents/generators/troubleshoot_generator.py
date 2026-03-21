"""TroubleshootGenerator - 故障排查文档生成器

负责生成故障排查文档，包含常见错误、调试技巧、FAQ
"""

from typing import Dict, Any, List
from agents.generators.base_generator import BaseGenerator


class TroubleshootGenerator(BaseGenerator):
    """故障排查文档生成器 - 基于LLM生成高质量文档"""

    def __init__(self):
        super().__init__("TroubleshootGenerator", "troubleshooting")

    def generate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """生成故障排查文档"""
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
                "document_type": "troubleshooting",
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
                "document_type": "troubleshooting"
            }

    def generate_with_llm(self, context: Dict[str, Any], repo_path: str, analysis_results: Dict[str, Any]) -> str:
        """使用LLM生成故障排查文档"""
        
        prompt = f"""你是一个技术文档专家。请根据以下项目信息，生成一份高质量的故障排查文档。

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

## 主要依赖
{chr(10).join(context.get('requirements', [])[:15]) or '无'}

---

请生成一份故障排查文档，包含以下内容：
1. **常见错误** - 列出5-10个常见错误及其解决方案
2. **调试技巧** - 如何调试项目、查看日志
3. **环境问题** - 环境配置相关的问题
4. **依赖问题** - 依赖安装和版本冲突问题
5. **FAQ** - 常见问题解答

要求：
- 使用Markdown格式
- 错误信息要准确
- 解决方案要具体可操作
- 内容要基于实际项目信息
"""

        return self._call_llm(prompt)

    def generate_fallback(self, context: Dict[str, Any], repo_path: str, analysis_results: Dict[str, Any]) -> str:
        """降级生成 - 当LLM不可用时使用模板"""
        lines = []

        lines.append("# 故障排查指南")
        lines.append("")

        lines.append("## 常见错误")
        errors = self._generate_common_errors(context)
        lines.extend(errors)
        lines.append("")

        lines.append("## 调试技巧")
        debug = self._generate_debug_tips(context)
        lines.extend(debug)
        lines.append("")

        lines.append("## 环境问题")
        env = self._generate_env_issues(context)
        lines.extend(env)
        lines.append("")

        lines.append("## FAQ")
        faq = self._generate_faq(context)
        lines.extend(faq)

        return "\n".join(lines)

    def _generate_common_errors(self, context: Dict[str, Any]) -> List[str]:
        """生成常见错误说明"""
        lines = []
        language = context.get("language", "")

        if language == "Python":
            lines.append("### 1. ModuleNotFoundError")
            lines.append("**错误信息**: `ModuleNotFoundError: No module named 'xxx'`")
            lines.append("**解决方案**: 安装缺失的依赖")
            lines.append("```bash")
            lines.append("pip install xxx")
            lines.append("```")
            lines.append("")
            lines.append("### 2. ImportError")
            lines.append("**错误信息**: `ImportError: cannot import name 'xxx'`")
            lines.append("**解决方案**: 检查模块版本或重新安装")
            lines.append("```bash")
            lines.append("pip install --upgrade xxx")
            lines.append("```")
        elif language in ["JavaScript", "TypeScript"]:
            lines.append("### 1. Cannot find module")
            lines.append("**错误信息**: `Error: Cannot find module 'xxx'`")
            lines.append("**解决方案**: 安装缺失的依赖")
            lines.append("```bash")
            lines.append("npm install xxx")
            lines.append("```")
            lines.append("")
            lines.append("### 2. TypeError")
            lines.append("**错误信息**: `TypeError: xxx is not a function`")
            lines.append("**解决方案**: 检查导入方式和模块版本")

        return lines

    def _generate_debug_tips(self, context: Dict[str, Any]) -> List[str]:
        """生成调试技巧"""
        lines = []
        language = context.get("language", "")

        lines.append("### 日志调试")
        if language == "Python":
            lines.append("```python")
            lines.append("import logging")
            lines.append("")
            lines.append("logging.basicConfig(level=logging.DEBUG)")
            lines.append("logging.debug('Debug message')")
            lines.append("```")
        elif language in ["JavaScript", "TypeScript"]:
            lines.append("```javascript")
            lines.append("console.log('Debug message');")
            lines.append("console.debug('Debug info');")
            lines.append("```")

        return lines

    def _generate_env_issues(self, context: Dict[str, Any]) -> List[str]:
        """生成环境问题说明"""
        lines = []
        language = context.get("language", "")

        if language == "Python":
            lines.append("### Python 版本问题")
            lines.append("- 确保使用正确的 Python 版本")
            lines.append("- 使用 `python --version` 检查版本")
            lines.append("")
            lines.append("### 虚拟环境问题")
            lines.append("- 确保已激活虚拟环境")
            lines.append("- 使用 `which python` 检查当前 Python 路径")
        elif language in ["JavaScript", "TypeScript"]:
            lines.append("### Node.js 版本问题")
            lines.append("- 确保使用正确的 Node.js 版本")
            lines.append("- 使用 `node --version` 检查版本")
            lines.append("")
            lines.append("### npm/yarn 问题")
            lines.append("- 清除缓存: `npm cache clean --force`")
            lines.append("- 删除 node_modules 重新安装")

        return lines

    def _generate_faq(self, context: Dict[str, Any]) -> List[str]:
        """生成FAQ"""
        lines = []
        language = context.get("language", "")

        lines.append("### Q: 如何更新项目依赖？")
        if language == "Python":
            lines.append("A: 运行 `pip install --upgrade -r requirements.txt`")
        elif language in ["JavaScript", "TypeScript"]:
            lines.append("A: 运行 `npm update` 或 `yarn upgrade`")
        lines.append("")

        lines.append("### Q: 如何查看详细错误信息？")
        lines.append("A: 查看日志文件或启用调试模式")

        return lines

    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()


# 全局实例
troubleshoot_generator = TroubleshootGenerator()
