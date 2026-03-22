"""OverviewGenerator - Project Overview Document Generator

Generates comprehensive project overview documentation
"""

from typing import Dict, Any, List
from agents.generators.base_generator import BaseGenerator


class OverviewGenerator(BaseGenerator):
    """Project Overview Document Generator - High-quality documentation via LLM"""

    def __init__(self):
        super().__init__("OverviewGenerator", "overview")

    def generate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate project overview document

        Args:
            context: Contains analysis results, repository info, etc.

        Returns:
            Dict: Contains generated document and quality info
        """
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
                "document_type": "overview",
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
                "document_type": "overview"
            }

    def generate_with_llm(self, context: Dict[str, Any], repo_path: str, analysis_results: Dict[str, Any]) -> str:
        """Generate project overview document using LLM"""

        prompt = f"""You are a technical documentation expert. Based on the following project information, generate a high-quality project overview document.

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
{context.get('readme', 'No README')[:2000]}

## Main Dependencies
{chr(10).join(context.get('requirements', [])[:20]) or 'None'}

---

Please generate a project overview document containing:

1. **Project Background** - What is this project, what problem does it solve, who is the target audience
2. **Core Features** - List 5-8 core features
3. **Technical Architecture** - Tech stack, architecture style, design patterns
4. **Use Cases** - What types of projects and developers is this suitable for
5. **Project Highlights** - Advantages compared to similar projects

Requirements:
- Use Markdown format
- Content should be specific and accurate, based on the provided project information
- Do not fabricate features that do not exist
- If information is insufficient, indicate "Based on project code analysis"
"""

        return self._call_llm(prompt)

    def generate_fallback(self, context: Dict[str, Any], repo_path: str, analysis_results: Dict[str, Any]) -> str:
        """Fallback generation - Template when LLM is unavailable"""
        lines = []

        lines.append("# Project Overview")
        lines.append("")

        lines.append("## Project Background")
        background = self._generate_background(context)
        lines.extend(background)
        lines.append("")

        lines.append("## Core Features")
        features = self._generate_features(context)
        lines.extend(features)
        lines.append("")

        lines.append("## Technical Architecture")
        tech_stack = self._generate_tech_stack(context)
        lines.extend(tech_stack)
        lines.append("")

        lines.append("## Use Cases")
        scenarios = self._generate_scenarios(context)
        lines.extend(scenarios)

        return "\n".join(lines)

    def _generate_background(self, context: Dict[str, Any]) -> List[str]:
        """Generate project background description"""
        background = []

        project_type = context.get("project_type", "Unknown")
        language = context.get("language", "Unknown")
        frameworks = context.get("frameworks", [])

        background.append(f"This is a **{project_type}** project.")
        background.append(f"Developed using **{language}** programming language.")
        if frameworks:
            background.append(f"Primarily uses **{frameworks[0]}** framework.")

        return background

    def _generate_features(self, context: Dict[str, Any]) -> List[str]:
        """Generate feature list"""
        features = []
        frameworks = context.get("frameworks", [])
        language = context.get("language", "")

        features.append("### Main Features")
        features.append("")

        for fw in frameworks[:3]:
            features.append(f"- Based on {fw} framework")

        if language == "Python":
            features.append("- Python backend services")
            features.append("- Modular design")
        elif language in ["JavaScript", "TypeScript"]:
            features.append("- Frontend/full-stack development")
            features.append("- Component-based architecture")

        return features if len(features) > 2 else ["- Please refer to project documentation for more features"]

    def _generate_tech_stack(self, context: Dict[str, Any]) -> List[str]:
        """Generate tech stack description"""
        tech_stack = []

        language = context.get("language", "Unknown")
        frameworks = context.get("frameworks", [])
        build_system = context.get("build_system", "Unknown")

        tech_stack.append(f"- **Programming Language**: {language}")
        if frameworks:
            tech_stack.append(f"- **Main Framework**: {frameworks[0]}")
        tech_stack.append(f"- **Build System**: {build_system}")

        requirements = context.get("requirements", [])
        if requirements:
            tech_stack.append("")
            tech_stack.append("### Key Dependencies")
            for dep in requirements[:5]:
                if dep:
                    tech_stack.append(f"- {dep}")

        return tech_stack

    def _generate_scenarios(self, context: Dict[str, Any]) -> List[str]:
        """Generate use case description"""
        scenarios = []
        project_type = context.get("project_type", "").lower()

        if "web" in project_type or "api" in project_type:
            scenarios.append("- Web application development")
            scenarios.append("- RESTful API services")
        elif "react" in project_type or "vue" in project_type:
            scenarios.append("- Single Page Application (SPA) development")
            scenarios.append("- Frontend component development")
        else:
            scenarios.append("- General application development")

        return scenarios

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()


# Global instance
overview_generator = OverviewGenerator()
