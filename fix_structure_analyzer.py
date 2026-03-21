"""StructureAnalyzer - 目录结构分析

负责分析目录结构、识别核心模块、提取入口点
"""

from typing import Dict, List, Any
import os


class StructureAnalyzer:
    """结构分析器 - 分析项目目录结构和核心模块"""

    def __init__(self):
        self.name = "StructureAnalyzer"
        self.version = "1.0"

    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析目录结构

        参数:
            context: 包含 repo_url、repo_path 等信息

        返回:
            Dict: 包含目录结构、核心模块、入口点等信息
        """
        repo_url = context.get("repo_url", "")
        repo_path = context.get("repo_path")
        language = context.get("language")

        if not repo_path or not os.path.exists(repo_path):
            return {
                "success": False,
                "error": "仓库路径不存在",
                "repo_url": repo_url
            }

        try:
            # 1. 构建目录树
            tree = self._build_tree(repo_path)

            # 2. 识别核心模块
            core_modules = self._identify_core_modules(repo_path, language)

            # 3. 提取入口点
            entry_points = self._find_entry_points(repo_path, language)

            # 4. 统计文件信息
            stats = self._get_file_stats(repo_path)

            return {
                "success": True,
                "repo_url": repo_url,
                "tree": tree,
                "core_modules": core_modules,
                "entry_points": entry_points,
                "stats": stats
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "repo_url": repo_url
            }

    def _build_tree(self, repo_path: str, max_depth: int = 3) -> List[Dict[str, Any]]:
        """
        构建目录树

        参数:
            repo_path: 仓库路径
            max_depth: 最大深度

        返回:
            List: 目录树结构
        """
        def _build_tree_recursive(path: str, depth: int = 0) -> List[Dict[str, Any]]:
            if depth > max_depth:
                return []

            items = []
            skip_dirs = {'.git', '__pycache__', 'node_modules', 'venv', 'env',
                        '.venv', '.env', 'dist', 'build', '.next', '.nuxt',
                        'target', 'bin', 'obj', 'out'}

            try:
                entries = sorted(os.listdir(path))
            except:
                return []

            for entry in entries:
                entry_path = os.path.join(path, entry)

                # 跳过隐藏文件和目录
                if entry.startswith('.'):
                    continue

                # 跳过特定目录
                if os.path.isdir(entry_path) and entry in skip_dirs:
                    continue

                if os.path.isfile(entry_path):
                    # 文件
                    ext = os.path.splitext(entry)[1]
                    items.append({
                        "name": entry,
                        "type": "file",
                        "extension": ext
                    })
                elif os.path.isdir(entry_path):
                    # 目录
                    children = _build_tree_recursive(entry_path, depth + 1)
                    items.append({
                        "name": entry,
                        "type": "directory",
                        "children": children
                    })

            return items

        return _build_tree_recursive(repo_path)

    def _identify_core_modules(self, repo_path: str, language: str) -> List[Dict[str, Any]]:
        """识别核心模块"""
        modules = []
        skip_dirs = {'.git', '__pycache__', 'node_modules', 'venv', 'env',
                    '.venv', '.env', 'dist', 'build', '.next', '.nuxt',
                    'target', 'bin', 'obj', 'out', 'test', 'tests'}

        # Python 核心模块识别
        if language == "Python":
            python_core_patterns = {
                "models": ["models/", "model.py"],
                "views": ["views/", "view.py", "controllers/"],
                "utils": ["utils/", "util.py", "helpers/"],
                "config": ["config/", "settings.py", "conf.py"],
                "api": ["api/", "apis/"],
                "services": ["services/", "service.py"]
            }

            for module_name, patterns in python_core_patterns.items():
                for pattern in patterns:
                    if os.path.exists(os.path.join(repo_path, pattern)):
                        modules.append({
                            "name": module_name,
                            "type": "directory" if pattern.endswith("/") else "file",
                            "path": pattern
                        })
                        break

        # JavaScript/TypeScript 核心模块识别
        elif language in ["JavaScript", "TypeScript"]:
            js_core_patterns = {
                "components": ["components/", "src/components/"],
                "pages": ["pages/", "src/pages/"],
                "utils": ["utils/", "src/utils/", "lib/"],
                "hooks": ["hooks/", "src/hooks/"],
                "services": ["services/", "src/services/"],
                "api": ["api/", "src/api/"],
                "store": ["store/", "src/store/", "redux/"]
            }

            for module_name, patterns in js_core_patterns.items():
                for pattern in patterns:
                    if os.path.exists(os.path.join(repo_path, pattern)):
                        modules.append({
                            "name": module_name,
                            "type": "directory",
                            "path": pattern
                        })
                        break

        # 检查 src 目录
        if os.path.exists(os.path.join(repo_path, "src")):
            modules.append({
                "name": "source",
                "type": "directory",
                "path": "src/"
            })

        return modules

    def _find_entry_points(self, repo_path: str, language: str) -> List[Dict[str, Any]]:
        """找入口点"""
        entry_points = []

        # Python 入口点
        if language == "Python":
            python_entries = [
                "main.py", "__main__.py", "app.py", "manage.py",
                "wsgi.py", "run.py"
            ]
            for entry in python_entries:
                if os.path.exists(os.path.join(repo_path, entry)):
                    entry_points.append({
                        "name": entry,
                        "type": "file",
                        "description": self._get_entry_description(entry)
                    })

        # JavaScript/TypeScript 入口点
        elif language in ["JavaScript", "TypeScript"]:
            js_entries = ["index.js", "index.ts", "main.js", "main.ts", "app.js", "app.ts"]
            for entry in js_entries:
                # 检查根目录和 src 目录
                paths = ["", "src/", "lib/"]
                for prefix in paths:
                    full_path = os.path.join(repo_path, prefix + entry)
                    if os.path.exists(full_path):
                        entry_points.append({
                            "name": prefix + entry,
                            "type": "file",
                            "description": self._get_entry_description(entry)
                        })
                        break

            # 检查 package.json 中的入口
            if os.path.exists(os.path.join(repo_path, "package.json")):
                try:
                    import json
                    with open(os.path.join(repo_path, "package.json")) as f:
                        pkg = json.load(f)
                    main = pkg.get("main", pkg.get("module"))
                    if main:
                        entry_points.append({
                            "name": main,
                            "type": "file",
                            "description": "package.json 中定义的入口文件"
                        })
                except:
                    pass

        # Java 入口点
        elif language == "Java":
            # 查找包含 main 方法的文件
            for root, dirs, files in = os.walk(repo_path):
                # 限制搜索深度
                if len(root.replace(repo_path, "").split(os.sep)) > 5:
                    continue

                for file in files:
                    if file.endswith(".java"):
                        try:
                            with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                                content = f.read()
                                if "public static void main" in content:
                                    entry_points.append({
                                        "name": file,
                                        "path": os.path.relpath(os.path.join(root, file), repo_path),
                                        "type": "file",
                                        "description": "Java main 方法"
                                    })
                        except:
                            pass

        return entry_points

    def _get_entry_description(self, entry_name: str) -> str:
        """获取入口点描述"""
        descriptions = {
            "main.py": "Python 主程序入口",
            "__main__.py": "Python 包入口",
            "app.py": "Flask/FastAPI 应用入口",
            "manage.py": "Django 管理脚本",
            "wsgi.py": "WSGI 应用入口",
            "run.py": "运行脚本",
            "index.js": "JavaScript 入口",
            "index.ts": "TypeScript 入口",
            "main.js": "JavaScript 主入口",
            "main.ts": "TypeScript 主入口"
        }
        return descriptions.get(entry_name, "入口文件")

    def _get_file_stats(self, repo_path: str) -> Dict[str, Any]:
        """获取文件统计信息"""
        stats = {
            "total_files": 0,
            "total_directories": 0,
            "by_extension": {},
            "total_lines": 0
        }

        skip_dirs = {'.git', '__pycache__', 'node_modules', 'venv', 'env',
                    '.venv', '.env', 'dist', 'build', '.next', '.nuxt',
                    'target', 'bin', 'obj', 'out'}

        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in skip_dirs]

            stats["total_directories"] += len(dirs)

            for file in files:
                stats["total_files"] += 1

                # 统计扩展名
                ext = os.path.splitext(file)[1] or "(无扩展名)"
                stats["by_extension"][ext] = stats["by_extension"].get(ext, 0) + 1

                # 统计代码行数（仅文本文件）
                text_extensions = ['.py', '.js', '.ts', '.java', '.go', '.rs', '.c', '.cpp', '.h', '.php', '.rb', '.swift']
                if ext in text_extensions:
                    try:
                        with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                            stats["total_lines"] += len(f.readlines())
                    except:
                        pass

        return stats


# 全局实例
structure_analyzer = StructureAnalyzer()
