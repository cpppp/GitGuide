"""TypeAnalyzer - 项目类型识别

负责识别项目类型（Python/Node/Java/Go等）、框架检测、构建系统识别
"""

from typing import Dict, Any, Optional
import os


class TypeAnalyzer:
    """类型分析器 - 识别项目类型和框架"""

    def __init__(self):
        self.name = "TypeAnalyzer"
        self.version = "1.0"

    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析项目类型

        参数:
            context: 包含 repo_url、repo_path 等信息

        返回:
            Dict: 包含项目类型、语言、框架、构建系统等信息
        """
        repo_url = context.get("repo_url", "")
        repo_path = context.get("repo_path")

        # 如果没有本地路径，尝试临时克隆
        if not repo_path or not os.path.exists(repo_path):
            return {
                "success": False,
                "error": "仓库路径不存在",
                "repo_url": repo_url
            }

        try:
            # 1. 检测语言
            language = self._detect_language(repo_path)

            # 2. 检测项目类型
            project_type = self._detect_project_type(repo_path, language)

            # 3. 检测框架
            frameworks = self._detect_frameworks(repo_path, language)

            # 4. 检测构建系统
            build_system = self._detect_build_system(repo_path, language)

            # 5. 检测包管理器
            package_manager = self._detect_package_manager(repo_path, language)

            return {
                "success": True,
                "repo_url": repo_url,
                "language": language,
                "project_type": project_type,
                "frameworks": frameworks,
                "build_system": build_system,
                "package_manager": package_manager
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "repo_url": repo_url
            }

    def _detect_language(self, repo_path: str) -> str:
        """检测主要编程语言"""
        # 统计文件扩展名
        extensions = {}
        skip_dirs = {'.git', '__pycache__', 'node_modules', 'venv', 'env',
                    'dist', 'build', '.next', '.nuxt', 'target'}

        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in skip_dirs]

            for file in files:
                _, ext = os.path.splitext(file)
                if ext:
                    extensions[ext] = extensions.get(ext, 0) + 1

        # 语言映射
        language_mapping = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.go': 'Go',
            '.rs': 'Rust',
            '.cpp': 'C++',
            '.cc': 'C++',
            '.cxx': 'C++',
            '.c': 'C',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
        }

        # 计算语言分数
        language_scores = {}
        for ext, count in extensions.items():
            lang = language_mapping.get(ext)
            if lang:
                language_scores[lang] = language_scores.get(lang, 0) + count

        # 返回得分最高的语言
        if language_scores:
            return max(language_scores.items(), key=lambda x: x[1])[0]

        return "Unknown"

    def _detect_project_type(self, repo_path: str, language: str) -> str:
        """检测项目类型"""
        # 检查特定文件
        files_to_check = []

        # Python 项目类型
        if language == "Python":
            if os.path.exists(os.path.join(repo_path, "Dockerfile")):
                return "Python (Docker)"
            if os.path.exists(os.path.join(repo_path, "manage.py")):
                return "Python (Django)"
            if os.path.exists(os.path.join(repo_path, "app.py")):
                return "Python (Flask)"
            if os.path.exists(os.path.join(repo_path, "main.py")):
                return "Python (CLI/Script)"
            if os.path.exists(os.path.join(repo_path, "__main__.py")):
                return "Python (Package)"

        # JavaScript/TypeScript 项目类型
        elif language in ["JavaScript", "TypeScript"]:
            if os.path.exists(os.path.join(repo_path, "package.json")):
                # 读取 package.json 检查 dependencies
                try:
                    import json
                    with open(os.path.join(repo_path, "package.json")) as f:
                        pkg = json.load(f)

                    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}

                    if "react" in deps or "@types/react" in deps:
                        return "React"
                    if "vue" in deps or "@vue/" in deps:
                        return "Vue"
                    if "next" in deps:
                        return "Next.js"
                    if "nuxt" in deps:
                        return "Nuxt.js"
                    if "angular" in deps or "@angular/" in deps:
                        return "Angular"
                    if "express" in deps:
                        return "Express.js"
                    if "electron" in deps:
                        return "Electron"
                    if "svelte" in deps:
                        return "Svelte"

                    return f"{language} (Node.js)"
                except:
                    return f"{language} (Node.js)"

        # Java 项目类型
        elif language == "Java":
            if os.path.exists(os.path.join(repo_path, "pom.xml")):
                return "Java (Maven)"
            if os.path.exists(os.path.join(repo_path, "build.gradle")):
                return "Java (Gradle)"
            return "Java"

        # Go 项目类型
        elif language == "Go":
            return "Go (Module)"

        # Rust 项目类型
        elif language == "Rust":
            return "Rust"

        return language

    def _detect_frameworks(self, repo_path: str, language: str) -> list:
        """检测使用的框架"""
        frameworks = []

        # Python 框架
        if language == "Python":
            framework_files = {
                "Django": ["manage.py", "django"],
                "Flask": ["app.py", "flask"],
                "FastAPI": ["fastapi"],
                "Tornado": ["tornado"],
                "SQLAlchemy": ["sqlalchemy"],
                "PyTorch": ["torch", "pytorch"],
                "TensorFlow": ["tensorflow"],
                "Scikit-learn": ["sklearn", "scikit-learn"]
            }

            for framework, keywords in framework_files.items():
                if self._check_file_contents(repo_path, keywords):
                    frameworks.append(framework)

        # JavaScript/TypeScript 框架
        elif language in ["JavaScript", "TypeScript"]:
            try:
                import json
                with open(os.path.join(repo_path, "package.json")) as f:
                    pkg = json.load(f)

                deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}

                js_frameworks = [
                    "react", "vue", "next", "nuxt", "angular",
                    "express", "koa", "nestjs", "electron", "svelte"
                ]

                for fw in js_frameworks:
                    if fw in deps:
                        frameworks.append(fw.capitalize())
            except:
                pass

        return frameworks

    def _detect_build_system(self, repo_path: str, language: str) -> str:
        """检测构建系统"""
        build_files = {
            "Python": {
                "setup.py": "setuptools",
                "pyproject.toml": "poetry/pip"
            },
            "JavaScript": {
                "webpack.config.js": "Webpack",
                "vite.config.js": "Vite",
                "vite.config.ts": "Vite",
                "rollup.config.js": "Rollup",
                "tsconfig.json": "TypeScript"
            },
            "Java": {
                "pom.xml": "Maven",
                "build.gradle": "Gradle"
            },
            "Rust": {
                "Cargo.toml": "Cargo"
            }
        }

        language_build_files = build_files.get(language, {})

        for file, system in language_build_files.items():
            if os.path.exists(os.path.join(repo_path, file)):
                return system

        return "None"

    def _detect_package_manager(self, repo_path: str, language: str) -> str:
        """检测包管理器"""
        if language == "Python":
            if os.path.exists(os.path.join(repo_path, "poetry.lock")):
                return "poetry"
            if os.path.exists(os.path.join(repo_path, "Pipfile")):
                return "pipenv"
            return "pip"

        elif language in ["JavaScript", "TypeScript"]:
            if os.path.exists(os.path.join(repo_path, "yarn.lock")):
                return "yarn"
            if os.path.exists(os.path.join(repo_path, "pnpm-lock.yaml")):
                return "pnpm"
            return "npm"

        elif language == "Java":
            if os.path.exists(os.path.join(repo_path, "pom.xml")):
                return "maven"
            if os.path.exists(os.path.join(repo_path, "build.gradle")):
                return "gradle"

        elif language == "Go":
            return "go mod"

        elif language == "Rust":
            return "cargo"

        return "None"

    def _check_file_contents(self, repo_path: str, keywords: list) -> bool:
        """检查文件内容是否包含关键词"""
        # 简化实现：检查文件名和常见配置文件
        skip_dirs = {'.git', '__pycache__', 'node_modules', 'venv', 'env',
                    'dist', 'build', '.next', '.nuxt', 'target'}

        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in skip_dirs]

            for file in files:
                # 检查文件名
                for keyword in keywords:
                    if keyword.lower() in file.lower():
                        return True

            # 只检查根目录级别，避免递归太深 fancys
            if root != repo_path and len(root.replace(repo_path, "").split(os.sep)) > 3:
                break

        return False


# 全局实例
type_analyzer = TypeAnalyzer()
