"""TutorialGenerator - 使用教程文档生成器

负责生成使用教程文档，包含基础用法、进阶用法、API参考、示例代码
"""

from typing import Dict, Any, List
from agents.generators.base_generator import BaseGenerator


class TutorialGenerator(BaseGenerator):
    """使用教程文档生成器 - 基于LLM生成高质量文档"""

    def __init__(self):
        super().__init__("TutorialGenerator", "usage_tutorial")

    def generate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """生成使用教程文档"""
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
                "document_type": "usage_tutorial",
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
                "document_type": "usage_tutorial"
            }

    def generate_with_llm(self, context: Dict[str, Any], repo_path: str, analysis_results: Dict[str, Any]) -> str:
        """使用LLM生成使用教程文档"""
        
        prompt = f"""你是一个技术文档专家。请根据以下项目信息，生成一份高质量的使用教程文档。

## 项目信息
- 语言: {context.get('language', 'Unknown')}
- 项目类型: {context.get('project_type', 'Unknown')}
- 框架: {', '.join(context.get('frameworks', [])) or '无'}

## 目录结构
```
{context.get('directory_tree', '无')}
```

## README 内容
{context.get('readme', '无README')[:2000]}

## 主要依赖
{chr(10).join(context.get('requirements', [])[:15]) or '无'}

## 主要源文件
{self._format_main_files(context.get('main_files', []))}

---

请生成一份使用教程文档，包含以下内容：
1. **概述** - 本教程的目标和适用人群
2. **基础用法** - 最简单的使用方法，包含代码示例
3. **进阶用法** - 高级功能和配置选项
4. **API 参考** - 主要API和函数说明
5. **示例代码** - 完整的使用示例
6. **最佳实践** - 使用建议和注意事项

要求：
- 使用Markdown格式
- 代码示例要完整可运行
- 从简单到复杂，循序渐进
- 内容要基于实际项目信息
"""

        return self._call_llm(prompt)

    def generate_fallback(self, context: Dict[str, Any], repo_path: str, analysis_results: Dict[str, Any]) -> str:
        """降级生成 - 当LLM不可用时使用模板"""
        lines = []

        lines.append("# 使用教程")
        lines.append("")

        lines.append("## 概述")
        lines.append(self._generate_overview(context))
        lines.append("")

        lines.append("## 基础用法")
        basic = self._generate_basic_usage(context)
        lines.extend(basic)
        lines.append("")

        lines.append("## 进阶用法")
        advanced = self._generate_advanced_usage(context)
        lines.extend(advanced)
        lines.append("")

        lines.append("## 示例代码")
        examples = self._generate_examples(context)
        lines.extend(examples)

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

    def _generate_overview(self, context: Dict[str, Any]) -> str:
        """生成概述"""
        language = context.get("language", "Unknown")
        frameworks = context.get("frameworks", [])
        
        overview = f"本教程将帮助你快速上手这个 {language} 项目。"
        if frameworks:
            overview += f" 项目使用 {frameworks[0]} 框架。"
        return overview

    def _generate_basic_usage(self, context: Dict[str, Any]) -> List[str]:
        """生成基础用法"""
        lines = []
        language = context.get("language", "")
        main_files = context.get("main_files", [])

        lines.append("### 快速开始")
        if language == "Python":
            lines.append("```python")
            lines.append("# 导入模块")
            if main_files:
                lines.append(f"from {main_files[0]['name'].replace('.py', '')} import main")
            lines.append("")
            lines.append("# 运行主函数")
            lines.append("result = main()")
            lines.append("print(result)")
            lines.append("```")
        elif language in ["JavaScript", "TypeScript"]:
            lines.append("```javascript")
            lines.append("// 导入模块")
            lines.append("import { main } from './src/index'")
            lines.append("")
            lines.append("// 运行主函数")
            lines.append("main();")
            lines.append("```")

        return lines

    def _generate_advanced_usage(self, context: Dict[str, Any]) -> List[str]:
        """生成进阶用法"""
        lines = []
        language = context.get("language", "")

        lines.append("### 自定义配置")
        if language == "Python":
            lines.append("```python")
            lines.append("# 配置选项")
            lines.append("config = {")
            lines.append("    'debug': True,")
            lines.append("    'timeout': 30")
            lines.append("}")
            lines.append("```")
        elif language in ["JavaScript", "TypeScript"]:
            lines.append("```javascript")
            lines.append("// 配置选项")
            lines.append("const config = {")
            lines.append("  debug: true,")
            lines.append("  timeout: 30000")
            lines.append("};")
            lines.append("```")

        return lines

    def _generate_examples(self, context: Dict[str, Any]) -> List[str]:
        """生成示例代码"""
        lines = []
        language = context.get("language", "")

        lines.append("### 完整示例")
        if language == "Python":
            lines.append("```python")
            lines.append("#!/usr/bin/env python")
            lines.append('"""完整使用示例"""')
            lines.append("")
            lines.append("def main():")
            lines.append("    print('Hello, World!')")
            lines.append("")
            lines.append("if __name__ == '__main__':")
            lines.append("    main()")
            lines.append("```")
        elif language in ["JavaScript", "TypeScript"]:
            lines.append("```javascript")
            lines.append("// 完整使用示例")
            lines.append("function main() {")
            lines.append("  console.log('Hello, World!');")
            lines.append("}")
            lines.append("")
            lines.append("main();")
            lines.append("```")

        return lines

    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()


# 全局实例
tutorial_generator = TutorialGenerator()
