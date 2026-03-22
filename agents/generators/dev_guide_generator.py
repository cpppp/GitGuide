"""DevGuideGenerator - Development Guide Document Generator

Generates development guide documentation, including directory structure, code standards, testing guide, and contribution guide
"""

from typing import Dict, Any, List
from agents.generators.base_generator import BaseGenerator


class DevGuideGenerator(BaseGenerator):
    """Development Guide Document Generator - High-quality documentation via LLM"""

    def __init__(self):
        super().__init__("DevGuideGenerator", "dev_guide")

    def generate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate development guide document"""
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
        """Generate development guide document using LLM"""

        prompt = f"""You are a technical documentation expert. Based on the following project information, generate a high-quality development guide document.

## Project Information
- Language: {context.get('language', 'Unknown')}
- Project Type: {context.get('project_type', 'Unknown')}
- Frameworks: {', '.join(context.get('frameworks', [])) or 'None'}
- Build System: {context.get('build_system', 'Unknown')}

## Directory Structure
```
{context.get('directory_tree', 'None')}
```

## README Content
{context.get('readme', 'No README')[:1500]}

## Main Dependencies
{chr(10).join(context.get('requirements', [])[:15]) or 'None'}

## Main Source Files
{self._format_main_files(context.get('main_files', []))}

---

Please generate a development guide document containing:

1. **Project Structure** - Detailed explanation of directory structure and module responsibilities
2. **Code Standards** - Coding style, naming conventions, comment standards
3. **Development Environment** - Development environment configuration, recommended IDEs
4. **Testing Guide** - How to run tests, how to write tests
5. **Contributing Guide** - How to submit PRs, code review process
6. **Release Process** - Version management, release steps

Requirements:
- Use Markdown format
- Content should be based on actual project information
- Code examples should be complete
"""

        return self._call_llm(prompt)

    def generate_fallback(self, context: Dict[str, Any], repo_path: str, analysis_results: Dict[str, Any]) -> str:
        """Fallback generation - Template when LLM is unavailable"""
        lines = []

        lines.append("# Development Guide")
        lines.append("")

        lines.append("## Project Structure")
        structure = self._generate_structure(context)
        lines.extend(structure)
        lines.append("")

        lines.append("## Code Standards")
        code_style = self._generate_code_style(context)
        lines.extend(code_style)
        lines.append("")

        lines.append("## Development Environment")
        dev_env = self._generate_dev_env(context)
        lines.extend(dev_env)
        lines.append("")

        lines.append("## Testing Guide")
        testing = self._generate_testing(context)
        lines.extend(testing)

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

    def _generate_structure(self, context: Dict[str, Any]) -> List[str]:
        """Generate project structure description"""
        lines = []
        directory_tree = context.get("directory_tree", "")

        lines.append("```")
        lines.append(directory_tree[:1000] if directory_tree else "Project directory structure")
        lines.append("```")
        lines.append("")
        lines.append("### Main Directory Description")
        lines.append("- `src/`: Source code directory")
        lines.append("- `tests/`: Test code directory")
        lines.append("- `docs/`: Documentation directory")
        lines.append("- `config/`: Configuration files directory")

        return lines

    def _generate_code_style(self, context: Dict[str, Any]) -> List[str]:
        """Generate code standards description"""
        lines = []
        language = context.get("language", "")

        if language == "Python":
            lines.append("### Python Code Standards")
            lines.append("- Follow PEP 8 coding standards")
            lines.append("- Use 4-space indentation")
            lines.append("- Functions and variables use snake_case")
            lines.append("- Classes use PascalCase")
            lines.append("- Use type annotations")
        elif language in ["JavaScript", "TypeScript"]:
            lines.append("### JavaScript/TypeScript Code Standards")
            lines.append("- Use ESLint for linting")
            lines.append("- Use 2-space indentation")
            lines.append("- Variables use camelCase")
            lines.append("- Components use PascalCase")
            lines.append("- Prefer const/let, avoid var")

        return lines

    def _generate_dev_env(self, context: Dict[str, Any]) -> List[str]:
        """Generate development environment description"""
        lines = []
        language = context.get("language", "")

        lines.append("### Recommended Tools")
        if language == "Python":
            lines.append("- IDE: VS Code / PyCharm")
            lines.append("- Virtual environment: venv / conda")
            lines.append("- Package management: pip")
        elif language in ["JavaScript", "TypeScript"]:
            lines.append("- IDE: VS Code")
            lines.append("- Package management: npm / yarn")
            lines.append("- Debugging: Chrome DevTools")

        return lines

    def _generate_testing(self, context: Dict[str, Any]) -> List[str]:
        """Generate testing guide"""
        lines = []
        language = context.get("language", "")

        lines.append("### Running Tests")
        if language == "Python":
            lines.append("```bash")
            lines.append("# Run all tests")
            lines.append("pytest")
            lines.append("")
            lines.append("# Run specific test file")
            lines.append("pytest tests/test_main.py")
            lines.append("")
            lines.append("# View test coverage")
            lines.append("pytest --cov=src")
            lines.append("```")
        elif language in ["JavaScript", "TypeScript"]:
            lines.append("```bash")
            lines.append("# Run all tests")
            lines.append("npm test")
            lines.append("")
            lines.append("# Run specific test file")
            lines.append("npm test -- --grep 'test name'")
            lines.append("")
            lines.append("# View test coverage")
            lines.append("npm run test:coverage")
            lines.append("```")

        return lines

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()


# Global instance
dev_guide_generator = DevGuideGenerator()
