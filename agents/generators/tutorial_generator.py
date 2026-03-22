"""TutorialGenerator - Usage Tutorial Document Generator

Generates usage tutorial documentation, including basic usage, advanced usage, API reference, and example code
"""

from typing import Dict, Any, List
from agents.generators.base_generator import BaseGenerator


class TutorialGenerator(BaseGenerator):
    """Usage Tutorial Document Generator - High-quality documentation via LLM"""

    def __init__(self):
        super().__init__("TutorialGenerator", "usage_tutorial")

    def generate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate usage tutorial document"""
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
        """Generate usage tutorial document using LLM"""

        prompt = f"""You are a technical documentation expert. Based on the following project information, generate a high-quality usage tutorial document.

## Project Information
- Language: {context.get('language', 'Unknown')}
- Project Type: {context.get('project_type', 'Unknown')}
- Frameworks: {', '.join(context.get('frameworks', [])) or 'None'}

## Directory Structure
```
{context.get('directory_tree', 'None')}
```

## README Content
{context.get('readme', 'No README')[:2000]}

## Main Dependencies
{chr(10).join(context.get('requirements', [])[:15]) or 'None'}

## Main Source Files
{self._format_main_files(context.get('main_files', []))}

---

Please generate a usage tutorial document containing:

1. **Overview** - Goals of this tutorial and target audience
2. **Basic Usage** - Simplest usage method, with code examples
3. **Advanced Usage** - Advanced features and configuration options
4. **API Reference** - Main API and function descriptions
5. **Example Code** - Complete usage examples
6. **Best Practices** - Usage suggestions and precautions

Requirements:
- Use Markdown format
- Code examples should be complete and runnable
- Progress from simple to complex, step by step
- Content should be based on actual project information
"""

        return self._call_llm(prompt)

    def generate_fallback(self, context: Dict[str, Any], repo_path: str, analysis_results: Dict[str, Any]) -> str:
        """Fallback generation - Template when LLM is unavailable"""
        lines = []

        lines.append("# Usage Tutorial")
        lines.append("")

        lines.append("## Overview")
        lines.append(self._generate_overview(context))
        lines.append("")

        lines.append("## Basic Usage")
        basic = self._generate_basic_usage(context)
        lines.extend(basic)
        lines.append("")

        lines.append("## Advanced Usage")
        advanced = self._generate_advanced_usage(context)
        lines.extend(advanced)
        lines.append("")

        lines.append("## Example Code")
        examples = self._generate_examples(context)
        lines.extend(examples)

        return "\n".join(lines)

    def _format_main_files(self, main_files: List[Dict[str, str]]) -> str:
        """Format main source files"""
        if not main_files:
            return "None"

        result = []
        for f in main_files[:2]:
            result.append(f"### {f['name']}")
            result.append(f"```")
            result.append(f['content'][:400])
            result.append("```")
        return '\n'.join(result)

    def _generate_overview(self, context: Dict[str, Any]) -> str:
        """Generate overview"""
        language = context.get("language", "Unknown")
        frameworks = context.get("frameworks", [])

        overview = f"This tutorial will help you quickly get started with this {language} project."
        if frameworks:
            overview += f" The project uses {frameworks[0]} framework."
        return overview

    def _generate_basic_usage(self, context: Dict[str, Any]) -> List[str]:
        """Generate basic usage"""
        lines = []
        language = context.get("language", "")
        main_files = context.get("main_files", [])

        lines.append("### Quick Start")
        if language == "Python":
            lines.append("```python")
            lines.append("# Import module")
            if main_files:
                lines.append(f"from {main_files[0]['name'].replace('.py', '')} import main")
            lines.append("")
            lines.append("# Run main function")
            lines.append("result = main()")
            lines.append("print(result)")
            lines.append("```")
        elif language in ["JavaScript", "TypeScript"]:
            lines.append("```javascript")
            lines.append("// Import module")
            lines.append("import { main } from './src/index'")
            lines.append("")
            lines.append("// Run main function")
            lines.append("main();")
            lines.append("```")

        return lines

    def _generate_advanced_usage(self, context: Dict[str, Any]) -> List[str]:
        """Generate advanced usage"""
        lines = []
        language = context.get("language", "")

        lines.append("### Custom Configuration")
        if language == "Python":
            lines.append("```python")
            lines.append("# Configuration options")
            lines.append("config = {")
            lines.append("    'debug': True,")
            lines.append("    'timeout': 30")
            lines.append("}")
            lines.append("```")
        elif language in ["JavaScript", "TypeScript"]:
            lines.append("```javascript")
            lines.append("// Configuration options")
            lines.append("const config = {")
            lines.append("  debug: true,")
            lines.append("  timeout: 30000")
            lines.append("};")
            lines.append("```")

        return lines

    def _generate_examples(self, context: Dict[str, Any]) -> List[str]:
        """Generate example code"""
        lines = []
        language = context.get("language", "")

        lines.append("### Complete Example")
        if language == "Python":
            lines.append("```python")
            lines.append("#!/usr/bin/env python")
            lines.append('"""Complete usage example"""')
            lines.append("")
            lines.append("def main():")
            lines.append("    print('Hello, World!')")
            lines.append("")
            lines.append("if __name__ == '__main__':")
            lines.append("    main()")
            lines.append("```")
        elif language in ["JavaScript", "TypeScript"]:
            lines.append("```javascript")
            lines.append("// Complete usage example")
            lines.append("function main() {")
            lines.append("  console.log('Hello, World!');")
            lines.append("}")
            lines.append("")
            lines.append("main();")
            lines.append("```")

        return lines

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()


# Global instance
tutorial_generator = TutorialGenerator()
