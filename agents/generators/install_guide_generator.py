"""InstallGuideGenerator - Installation and Deployment Document Generator

Generates installation and deployment documentation to help users run the project
"""

from typing import Dict, Any, List
from agents.generators.base_generator import BaseGenerator


class InstallGuideGenerator(BaseGenerator):
    """Installation and Deployment Document Generator - High-quality documentation via LLM"""

    def __init__(self):
        super().__init__("InstallGuideGenerator", "install_guide")

    def generate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate installation and deployment document"""
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
        """Generate installation and deployment document using LLM"""

        prompt = f"""You are a technical documentation expert. Based on the following project information, generate a high-quality installation and deployment document.

## Project Information
- Language: {context.get('language', 'Unknown')}
- Project Type: {context.get('project_type', 'Unknown')}
- Frameworks: {', '.join(context.get('frameworks', [])) or 'None'}
- Build System: {context.get('build_system', 'Unknown')}
- Package Manager: {context.get('package_manager', 'Unknown')}

## Directory Structure
```
{context.get('directory_tree', 'None')}
```

## README Content
{context.get('readme', 'No README')[:2000]}

## Main Dependencies
{chr(10).join(context.get('requirements', [])[:20]) or 'None'}

## Main Source Files
{self._format_main_files(context.get('main_files', []))}

---

Please generate an installation and deployment document containing:

1. **Environment Requirements** - Required software and versions
2. **Installation Steps** - Detailed installation commands, differentiated by operating system
3. **Configuration Instructions** - Environment variables, configuration files, etc.
4. **Running Commands** - How to run in development and production modes
5. **Common Issues** - Potential problems during installation and running and their solutions

Requirements:
- Use Markdown format
- Code blocks should specify language (bash, python, etc.)
- Commands should be directly copyable and executable
- Content should be specific and accurate, based on actual project information
"""

        return self._call_llm(prompt)

    def generate_fallback(self, context: Dict[str, Any], repo_path: str, analysis_results: Dict[str, Any]) -> str:
        """Fallback generation - Template when LLM is unavailable"""
        lines = []

        lines.append("# Installation and Deployment Guide")
        lines.append("")

        lines.append("## Environment Requirements")
        requirements = self._generate_requirements(context)
        lines.extend(requirements)
        lines.append("")

        lines.append("## Installation Steps")
        install_steps = self._generate_install_steps(context)
        lines.extend(install_steps)
        lines.append("")

        lines.append("## Configuration Instructions")
        configuration = self._generate_configuration(context)
        lines.extend(configuration)
        lines.append("")

        lines.append("## Running Commands")
        run_commands = self._generate_run_commands(context)
        lines.extend(run_commands)

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

    def _generate_requirements(self, context: Dict[str, Any]) -> List[str]:
        """Generate environment requirements"""
        requirements = []
        language = context.get("language", "Unknown")
        frameworks = context.get("frameworks", [])

        if language == "Python":
            requirements.append("- Python 3.8+")
            requirements.append("- pip (Python package manager)")
            if frameworks:
                requirements.append(f"- Main framework: {frameworks[0]}")
        elif language in ["JavaScript", "TypeScript"]:
            requirements.append("- Node.js 16+")
            requirements.append("- npm or yarn")
            if frameworks:
                requirements.append(f"- Main framework: {frameworks[0]}")
        else:
            requirements.append(f"- {language} runtime environment")

        return requirements

    def _generate_install_steps(self, context: Dict[str, Any]) -> List[str]:
        """Generate installation steps"""
        steps = []
        language = context.get("language", "Unknown")
        package_manager = context.get("package_manager", "")

        steps.append("### 1. Clone Repository")
        steps.append("```bash")
        steps.append("git clone <repository-url>")
        steps.append("cd <project-directory>")
        steps.append("```")
        steps.append("")

        if language == "Python":
            steps.append("### 2. Create Virtual Environment")
            steps.append("```bash")
            steps.append("python -m venv venv")
            steps.append("source venv/bin/activate  # Linux/Mac")
            steps.append("# venv\\Scripts\\activate  # Windows")
            steps.append("```")
            steps.append("")
            steps.append("### 3. Install Dependencies")
            steps.append("```bash")
            steps.append("pip install -r requirements.txt")
            steps.append("```")
        elif language in ["JavaScript", "TypeScript"]:
            steps.append("### 2. Install Dependencies")
            steps.append("```bash")
            if package_manager == "yarn":
                steps.append("yarn install")
            else:
                steps.append("npm install")
            steps.append("```")

        return steps

    def _generate_configuration(self, context: Dict[str, Any]) -> List[str]:
        """Generate configuration instructions"""
        configuration = []
        language = context.get("language", "")

        configuration.append("### Environment Variables")
        configuration.append("```bash")
        configuration.append("cp .env.example .env")
        configuration.append("# Edit .env file to configure necessary environment variables")
        configuration.append("```")

        return configuration

    def _generate_run_commands(self, context: Dict[str, Any]) -> List[str]:
        """Generate running commands"""
        commands = []
        language = context.get("language", "")
        main_files = context.get("main_files", [])

        commands.append("### Development Mode")
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
        commands.append("### Run Tests")
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
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()


# Global instance
install_guide_generator = InstallGuideGenerator()
