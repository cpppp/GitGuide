"""TroubleshootGenerator - Troubleshooting Document Generator

Generates troubleshooting documentation, including common errors, debugging tips, and FAQ
"""

from typing import Dict, Any, List
from agents.generators.base_generator import BaseGenerator


class TroubleshootGenerator(BaseGenerator):
    """Troubleshooting Document Generator - High-quality documentation via LLM"""

    def __init__(self):
        super().__init__("TroubleshootGenerator", "troubleshooting")

    def generate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate troubleshooting document"""
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
        """Generate troubleshooting document using LLM"""

        prompt = f"""You are a technical documentation expert. Based on the following project information, generate a high-quality troubleshooting document.

## Project Information
- Language: {context.get('language', 'Unknown')}
- Project Type: {context.get('project_type', 'Unknown')}
- Frameworks: {', '.join(context.get('frameworks', [])) or 'None'}

## Directory Structure
```
{context.get('directory_tree', 'None')}
```

## README Content
{context.get('readme', 'No README')[:1500]}

## Main Dependencies
{chr(10).join(context.get('requirements', [])[:15]) or 'None'}

---

Please generate a troubleshooting document containing:

1. **Common Errors** - List 5-10 common errors and their solutions
2. **Debugging Tips** - How to debug the project, viewing logs
3. **Environment Issues** - Issues related to environment configuration
4. **Dependency Issues** - Dependency installation and version conflict issues
5. **FAQ** - Frequently asked questions and answers

Requirements:
- Use Markdown format
- Error messages should be accurate
- Solutions should be specific and actionable
- Content should be based on actual project information
"""

        return self._call_llm(prompt)

    def generate_fallback(self, context: Dict[str, Any], repo_path: str, analysis_results: Dict[str, Any]) -> str:
        """Fallback generation - Template when LLM is unavailable"""
        lines = []

        lines.append("# Troubleshooting Guide")
        lines.append("")

        lines.append("## Common Errors")
        errors = self._generate_common_errors(context)
        lines.extend(errors)
        lines.append("")

        lines.append("## Debugging Tips")
        debug = self._generate_debug_tips(context)
        lines.extend(debug)
        lines.append("")

        lines.append("## Environment Issues")
        env = self._generate_env_issues(context)
        lines.extend(env)
        lines.append("")

        lines.append("## FAQ")
        faq = self._generate_faq(context)
        lines.extend(faq)

        return "\n".join(lines)

    def _generate_common_errors(self, context: Dict[str, Any]) -> List[str]:
        """Generate common errors description"""
        lines = []
        language = context.get("language", "")

        if language == "Python":
            lines.append("### 1. ModuleNotFoundError")
            lines.append("**Error**: `ModuleNotFoundError: No module named 'xxx'`")
            lines.append("**Solution**: Install the missing dependency")
            lines.append("```bash")
            lines.append("pip install xxx")
            lines.append("```")
            lines.append("")
            lines.append("### 2. ImportError")
            lines.append("**Error**: `ImportError: cannot import name 'xxx'`")
            lines.append("**Solution**: Check module version or reinstall")
            lines.append("```bash")
            lines.append("pip install --upgrade xxx")
            lines.append("```")
        elif language in ["JavaScript", "TypeScript"]:
            lines.append("### 1. Cannot find module")
            lines.append("**Error**: `Error: Cannot find module 'xxx'`")
            lines.append("**Solution**: Install the missing dependency")
            lines.append("```bash")
            lines.append("npm install xxx")
            lines.append("```")
            lines.append("")
            lines.append("### 2. TypeError")
            lines.append("**Error**: `TypeError: xxx is not a function`")
            lines.append("**Solution**: Check import method and module version")

        return lines

    def _generate_debug_tips(self, context: Dict[str, Any]) -> List[str]:
        """Generate debugging tips"""
        lines = []
        language = context.get("language", "")

        lines.append("### Log Debugging")
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
        """Generate environment issues description"""
        lines = []
        language = context.get("language", "")

        if language == "Python":
            lines.append("### Python Version Issues")
            lines.append("- Ensure you are using the correct Python version")
            lines.append("- Use `python --version` to check the version")
            lines.append("")
            lines.append("### Virtual Environment Issues")
            lines.append("- Ensure the virtual environment is activated")
            lines.append("- Use `which python` to check the current Python path")
        elif language in ["JavaScript", "TypeScript"]:
            lines.append("### Node.js Version Issues")
            lines.append("- Ensure you are using the correct Node.js version")
            lines.append("- Use `node --version` to check the version")
            lines.append("")
            lines.append("### npm/yarn Issues")
            lines.append("- Clear cache: `npm cache clean --force`")
            lines.append("- Delete node_modules and reinstall")

        return lines

    def _generate_faq(self, context: Dict[str, Any]) -> List[str]:
        """Generate FAQ"""
        lines = []
        language = context.get("language", "")

        lines.append("### Q: How to update project dependencies?")
        if language == "Python":
            lines.append("A: Run `pip install --upgrade -r requirements.txt`")
        elif language in ["JavaScript", "TypeScript"]:
            lines.append("A: Run `npm update` or `yarn upgrade`")
        lines.append("")

        lines.append("### Q: How to view detailed error information?")
        lines.append("A: Check log files or enable debug mode")

        return lines

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()


# Global instance
troubleshoot_generator = TroubleshootGenerator()
