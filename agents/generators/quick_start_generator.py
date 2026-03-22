"""QuickStartGenerator - Quick Start Documentation Generator

Generates quick start documentation to help users understand a project in 5 minutes
"""

from typing import Dict, Any, List
from agents.generators.base_generator import BaseGenerator


class QuickStartGenerator(BaseGenerator):
    """Quick Start Documentation Generator - LLM-based high-quality documentation"""

    def __init__(self):
        super().__init__("QuickStartGenerator", "quick_start")

    def generate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate quick start documentation

        Args:
            context: Contains analysis results, repo info, etc.

        Returns:
            Dict: Contains generated document and quality info
        """
        repo_url = context.get("repo_url", "")
        repo_path = context.get("repo_path", "")
        analysis_results = context.get("analysis_results", {})

        try:
            # Use shared context (avoid redundant file reading)
            gen_context = self._get_shared_context(context)

            # Try to generate with LLM
            content = self.generate_with_llm(gen_context, repo_path, analysis_results)

            # If LLM fails, use fallback template
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
        """Generate quick start documentation using LLM"""

        prompt = f"""You are a technical documentation expert. Based on the following project information, generate a high-quality quick start documentation.

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

Please generate a quick start document with the following sections:
1. **One-Sentence Summary** - Briefly describe what the project is and what problem it solves
2. **Core Concepts** - List 3-5 core concepts, each explained in one sentence
3. **Environment Requirements** - Software and versions needed to run the project
4. **Installation Steps** - Detailed installation commands for different operating systems
5. **Minimal Run** - Simplest command to run and expected results
6. **Next Steps** - Suggestions for what users should do next

Requirements:
- Use Markdown format
- Code blocks should specify the language
- Commands should be copy-paste executable
- Content should be specific and accurate, not generic
"""

        return self._call_llm(prompt)

    def generate_fallback(self, context: Dict[str, Any], repo_path: str, analysis_results: Dict[str, Any]) -> str:
        """Fallback generation - use template when LLM is unavailable"""
        lines = []

        lines.append("# Quick Start")
        lines.append("")

        # One-sentence summary
        lines.append("## One-Sentence Summary")
        summary = self._generate_summary(context)
        lines.append(summary)
        lines.append("")

        # Core concepts
        lines.append("## Core Concepts")
        concepts = self._generate_concepts(context)
        lines.extend(concepts)
        lines.append("")

        # Environment requirements
        lines.append("## Environment Requirements")
        requirements = self._generate_requirements(context)
        lines.extend(requirements)
        lines.append("")

        # Installation steps
        lines.append("## Installation Steps")
        install = self._generate_install_steps(context)
        lines.extend(install)
        lines.append("")

        # Minimal run
        lines.append("## Minimal Run")
        quick_run = self._generate_quick_run(context)
        lines.extend(quick_run)

        return "\n".join(lines)

    def _format_main_files(self, main_files: List[Dict[str, str]]) -> str:
        """Format main source files"""
        if not main_files:
            return "None"

        result = []
        for f in main_files[:3]:
            result.append(f"### {f['name']}")
            result.append(f"```")
            result.append(f['content'][:500])
            result.append("```")
        return '\n'.join(result)

    def _generate_summary(self, context: Dict[str, Any]) -> str:
        """Generate project summary"""
        language = context.get("language", "Unknown")
        project_type = context.get("project_type", "Unknown")
        frameworks = context.get("frameworks", [])

        summary = f"This is a **{language}** project"
        if frameworks:
            summary += f", using **{frameworks[0]}** framework"
        summary += f", with type **{project_type}**."

        return summary

    def _generate_concepts(self, context: Dict[str, Any]) -> List[str]:
        """Generate core concepts"""
        concepts = []
        frameworks = context.get("frameworks", [])
        language = context.get("language", "")

        for fw in frameworks[:3]:
            concepts.append(f"- **{fw}**: Main framework")

        if language == "Python":
            concepts.append("- **pip**: Python package manager")
            if context.get("requirements"):
                concepts.append("- **Virtual Environment**: Recommended to use venv or conda")
        elif language in ["JavaScript", "TypeScript"]:
            concepts.append("- **npm/yarn**: Node.js package manager")
            concepts.append("- **Node.js**: JavaScript runtime")

        return concepts if concepts else ["- Please check the project documentation for more information"]

    def _generate_requirements(self, context: Dict[str, Any]) -> List[str]:
        """Generate environment requirements"""
        lines = []
        language = context.get("language", "")

        if language == "Python":
            lines.append("- Python 3.8+")
            lines.append("- pip (Python package manager)")
        elif language in ["JavaScript", "TypeScript"]:
            lines.append("- Node.js 16+")
            lines.append("- npm or yarn")
        elif language == "Go":
            lines.append("- Go 1.18+")
        elif language == "Java":
            lines.append("- JDK 11+")
            lines.append("- Maven or Gradle")
        else:
            lines.append("- Please check the project documentation for environment requirements")

        return lines

    def _generate_install_steps(self, context: Dict[str, Any]) -> List[str]:
        """Generate installation steps"""
        lines = []
        language = context.get("language", "")
        package_manager = context.get("package_manager", "")

        if language == "Python":
            lines.append("```bash")
            lines.append("# Clone the repository")
            lines.append("git clone <repository-url>")
            lines.append("cd <project-directory>")
            lines.append("")
            lines.append("# Create virtual environment (recommended)")
            lines.append("python -m venv venv")
            lines.append("source venv/bin/activate  # Linux/Mac")
            lines.append("# venv\\Scripts\\activate  # Windows")
            lines.append("")
            lines.append("# Install dependencies")
            lines.append("pip install -r requirements.txt")
            lines.append("```")
        elif language in ["JavaScript", "TypeScript"]:
            lines.append("```bash")
            lines.append("# Clone the repository")
            lines.append("git clone <repository-url>")
            lines.append("cd <project-directory>")
            lines.append("")
            lines.append("# Install dependencies")
            if package_manager == "yarn":
                lines.append("yarn install")
            else:
                lines.append("npm install")
            lines.append("```")
        else:
            lines.append("Please check the project README for installation instructions.")

        return lines

    def _generate_quick_run(self, context: Dict[str, Any]) -> List[str]:
        """Generate minimal run instructions"""
        lines = []
        language = context.get("language", "")
        main_files = context.get("main_files", [])

        if language == "Python":
            lines.append("```bash")
            if main_files:
                first_main = main_files[0]["name"]
                lines.append(f"python {first_main}")
            else:
                lines.append("python main.py  # or app.py")
            lines.append("```")
        elif language in ["JavaScript", "TypeScript"]:
            lines.append("```bash")
            lines.append("npm run dev  # or npm start")
            lines.append("```")
        else:
            lines.append("Please check the project documentation for run instructions.")

        return lines

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()


# Global instance
quick_start_generator = QuickStartGenerator()
