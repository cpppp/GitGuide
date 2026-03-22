"""ArchitectureGenerator - Architecture Design Document Generator

Generates system architecture design documentation
"""

from typing import Dict, Any, List
from agents.generators.base_generator import BaseGenerator


class ArchitectureGenerator(BaseGenerator):
    """Architecture Design Document Generator - High-quality documentation via LLM"""

    def __init__(self):
        super().__init__("ArchitectureGenerator", "architecture")

    def generate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate architecture design document"""
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
                "document_type": "architecture",
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
                "document_type": "architecture"
            }

    def generate_with_llm(self, context: Dict[str, Any], repo_path: str, analysis_results: Dict[str, Any]) -> str:
        """Generate architecture design document using LLM"""

        prompt = f"""You are a technical architecture expert. Based on the following project information, generate a high-quality architecture design document.

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

## Main Source Files
{self._format_main_files(context.get('main_files', []))}

## Main Dependencies
{chr(10).join(context.get('requirements', [])[:15]) or 'None'}

---

Please generate an architecture design document containing:

1. **Architecture Overview** - Overall architecture style and design philosophy
2. **Architecture Diagram** - Use Mermaid syntax to draw architecture diagram (flowchart or graph)
3. **Core Modules** - List core modules and their responsibilities
4. **Data Flow** - Describe main data flow
5. **Technology Selection Rationale** - Why these technologies were chosen
6. **Scalability Design** - How to support future expansion

Requirements:
- Use Markdown format
- Architecture diagrams should use Mermaid syntax in ```mermaid code blocks
- Content should be based on actual project information, do not fabricate
- If information is insufficient, indicate "Inferred from code analysis"
"""

        return self._call_llm(prompt)

    def generate_fallback(self, context: Dict[str, Any], repo_path: str, analysis_results: Dict[str, Any]) -> str:
        """Fallback generation - Template when LLM is unavailable"""
        lines = []

        lines.append("# Architecture Design")
        lines.append("")

        lines.append("## Architecture Overview")
        overview = self._generate_overview(context)
        lines.extend(overview)
        lines.append("")

        lines.append("## Architecture Diagram")
        diagram = self._generate_architecture_diagram(context)
        lines.append(diagram)
        lines.append("")

        lines.append("## Core Modules")
        modules = self._generate_modules(context)
        lines.extend(modules)
        lines.append("")

        lines.append("## Data Flow")
        data_flow = self._generate_data_flow(context)
        lines.extend(data_flow)

        return "\n".join(lines)

    def _format_main_files(self, main_files: List[Dict[str, str]]) -> str:
        """Format main source files"""
        if not main_files:
            return "None"

        result = []
        for f in main_files[:2]:
            result.append(f"### {f['name']}")
            result.append(f"```")
            result.append(f['content'][:300])
            result.append("```")
        return '\n'.join(result)

    def _generate_overview(self, context: Dict[str, Any]) -> List[str]:
        """Generate architecture overview"""
        lines = []
        language = context.get("language", "Unknown")
        frameworks = context.get("frameworks", [])
        project_type = context.get("project_type", "Unknown")

        lines.append(f"This project uses **{project_type}** architecture.")
        lines.append(f"Primarily developed using **{language}** language.")
        if frameworks:
            lines.append(f"Core framework: **{frameworks[0]}**.")

        return lines

    def _generate_architecture_diagram(self, context: Dict[str, Any]) -> str:
        """Generate architecture diagram (Mermaid format)"""
        language = context.get("language", "Unknown")
        frameworks = context.get("frameworks", [])

        lines = ["```mermaid", "flowchart TD"]
        lines.append("    User[User]")

        if language == "Python":
            lines.append("    API[API Layer]")
            lines.append("    Service[Service Layer]")
            lines.append("    Data[Data Layer]")
            lines.append("    User --> API")
            lines.append("    API --> Service")
            lines.append("    Service --> Data")
        elif language in ["JavaScript", "TypeScript"]:
            lines.append("    Frontend[Frontend Components]")
            lines.append("    Backend[Backend Services]")
            lines.append("    Database[Database]")
            lines.append("    User --> Frontend")
            lines.append("    Frontend --> Backend")
            lines.append("    Backend --> Database")
        else:
            lines.append("    App[Application Layer]")
            lines.append("    Core[Core Layer]")
            lines.append("    User --> App")
            lines.append("    App --> Core")

        lines.append("```")
        return "\n".join(lines)

    def _generate_modules(self, context: Dict[str, Any]) -> List[str]:
        """Generate module description"""
        modules = []
        directory_tree = context.get("directory_tree", "")
        main_files = context.get("main_files", [])

        if main_files:
            for f in main_files[:3]:
                modules.append(f"- **{f['name']}**: Main entry file")

        modules.append("")
        modules.append("Please refer to the directory structure for complete module organization.")

        return modules

    def _generate_data_flow(self, context: Dict[str, Any]) -> List[str]:
        """Generate data flow description"""
        language = context.get("language", "")

        if language == "Python":
            return [
                "1. User initiates HTTP request",
                "2. API layer receives and validates request",
                "3. Service layer processes business logic",
                "4. Data layer accesses database",
                "5. Result returns to user layer by layer"
            ]
        elif language in ["JavaScript", "TypeScript"]:
            return [
                "1. User interacts with frontend interface",
                "2. Frontend components handle user operations",
                "3. Call backend services via API",
                "4. Backend processes and returns data",
                "5. Frontend updates interface display"
            ]
        else:
            return [
                "1. User input",
                "2. Application processing",
                "3. Output result"
            ]

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()


# Global instance
architecture_generator = ArchitectureGenerator()
