"""BaseGenerator - 文档生成器基类

提供基于LLM的文档生成能力
"""

from typing import Dict, Any, List, Optional
import os
import json


class BaseGenerator:
    """文档生成器基类 - 提供LLM支持"""

    def __init__(self, name: str, doc_type: str):
        self.name = name
        self.doc_type = doc_type
        self.llm = None
        self._init_llm()

    def _init_llm(self):
        """初始化LLM"""
        try:
            from core.config import get_llm
            self.llm = get_llm()
        except Exception as e:
            print(f"LLM initialization failed: {e}")
            self.llm = None

    def _get_shared_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """获取共享上下文（优先使用预构建的上下文）"""
        # 如果已有共享上下文，直接返回
        if "shared_context" in context:
            return context["shared_context"]
        
        # 否则构建上下文（兼容旧调用方式）
        repo_path = context.get("repo_path", "")
        analysis_results = context.get("analysis_results", {})
        return self._build_context(repo_path, analysis_results)

    def _build_context(self, repo_path: str, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """构建生成上下文（仅在共享上下文不存在时使用）"""
        type_result = analysis_results.get("type_result", {})
        structure_result = analysis_results.get("structure_result", {})
        dependency_result = analysis_results.get("dependency_result", {})
        code_pattern_result = analysis_results.get("code_pattern_result", {})

        language = type_result.get("language", "Unknown")
        
        return {
            "language": language,
            "project_type": type_result.get("project_type", "Unknown"),
            "frameworks": type_result.get("frameworks", []),
            "build_system": type_result.get("build_system", ""),
            "package_manager": type_result.get("package_manager", ""),
            "readme": self._get_readme_content(repo_path),
            "directory_tree": self._get_directory_tree(repo_path),
            "main_files": self._get_main_files(repo_path, language),
            "requirements": self._get_requirements(repo_path),
            "package_json": self._get_package_json(repo_path),
            "core_modules": structure_result.get("core_modules", []),
            "entry_points": structure_result.get("entry_points", []),
            "dependencies": dependency_result.get("dependencies", []),
            "patterns": code_pattern_result.get("patterns", [])
        }

    def _read_file_content(self, repo_path: str, file_path: str, max_lines: int = 100) -> str:
        """读取文件内容"""
        try:
            full_path = os.path.join(repo_path, file_path)
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()[:max_lines]
                    return ''.join(lines)
        except Exception:
            pass
        return ""

    def _get_readme_content(self, repo_path: str) -> str:
        """获取README内容"""
        readme_files = ['README.md', 'README.rst', 'README.txt', 'readme.md', 'Readme.md']
        for readme in readme_files:
            content = self._read_file_content(repo_path, readme, 200)
            if content:
                return content
        return ""

    def _get_package_json(self, repo_path: str) -> Dict[str, Any]:
        """获取package.json内容"""
        try:
            import json
            content = self._read_file_content(repo_path, 'package.json', 50)
            if content:
                return json.loads(content)
        except Exception:
            pass
        return {}

    def _get_requirements(self, repo_path: str) -> List[str]:
        """获取requirements.txt内容"""
        content = self._read_file_content(repo_path, 'requirements.txt', 50)
        if content:
            return [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
        return []

    def _get_main_files(self, repo_path: str, language: str) -> List[Dict[str, str]]:
        """获取主要源文件内容"""
        main_files = []
        patterns = {
            'Python': ['main.py', 'app.py', '__main__.py', 'run.py', 'server.py'],
            'JavaScript': ['index.js', 'main.js', 'app.js', 'server.js', 'src/index.js'],
            'TypeScript': ['index.ts', 'main.ts', 'app.ts', 'src/index.ts'],
            'Go': ['main.go', 'cmd/main.go'],
            'Java': ['Main.java', 'Application.java', 'src/main/java/Main.java']
        }

        files_to_check = patterns.get(language, ['main.py', 'index.js'])
        
        for file_name in files_to_check:
            content = self._read_file_content(repo_path, file_name, 50)
            if content:
                main_files.append({
                    "name": file_name,
                    "content": content
                })

        return main_files

    def _get_directory_tree(self, repo_path: str, max_depth: int = 2) -> str:
        """获取目录树"""
        lines = []
        
        def walk_dir(path: str, prefix: str = "", depth: int = 0):
            if depth > max_depth:
                return
            try:
                items = sorted(os.listdir(path))
                dirs = [i for i in items if os.path.isdir(os.path.join(path, i)) and not i.startswith('.')]
                files = [i for i in items if os.path.isfile(os.path.join(path, i)) and not i.startswith('.')]
                
                for d in dirs[:10]:
                    lines.append(f"{prefix}├── {d}/")
                    walk_dir(os.path.join(path, d), prefix + "│   ", depth + 1)
                
                for f in files[:10]:
                    lines.append(f"{prefix}├── {f}")
            except Exception:
                pass

        walk_dir(repo_path)
        return '\n'.join(lines[:50])

    def _call_llm(self, prompt: str, max_tokens: int = 2000) -> str:
        """调用LLM生成内容"""
        if not self.llm:
            return None
        
        try:
            from langchain_core.messages import HumanMessage
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content
        except Exception as e:
            print(f"LLM call failed: {e}")
            return None

    def generate_with_llm(self, context: Dict[str, Any], repo_path: str, analysis_results: Dict[str, Any]) -> str:
        """使用LLM生成文档 - 子类实现"""
        raise NotImplementedError("Subclasses must implement generate_with_llm")

    def generate_fallback(self, context: Dict[str, Any], repo_path: str, analysis_results: Dict[str, Any]) -> str:
        """降级生成 - 当LLM不可用时使用模板"""
        raise NotImplementedError("Subclasses must implement generate_fallback")
