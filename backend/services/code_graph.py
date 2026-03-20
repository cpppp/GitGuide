from collections import defaultdict
from pathlib import Path
import os
import re

class CodeGraphService:
    @staticmethod
    def analyze_structure(repo_path: str) -> dict:
        result = {
            "tree": CodeGraphService._build_tree(repo_path),
            "stats": CodeGraphService._get_file_stats(repo_path),
            "dependencies": CodeGraphService._analyze_dependencies(repo_path)
        }
        return result
    
    @staticmethod
    def _build_tree(repo_path: str, max_depth: int = 3) -> dict:
        def build_node(path: Path, depth: int) -> dict:
            if depth > max_depth:
                return {"name": path.name, "type": "folder", "collapsed": True}
            
            if path.is_file():
                return {"name": path.name, "type": "file"}
            
            children = []
            try:
                for item in sorted(path.iterdir()):
                    if item.name.startswith('.'):
                        continue
                    children children.append(build_node(item, depth + 1))
            except PermissionError:
                pass
            
            return {"name": path.name, "type": "folder", "children": children}
        
        return build_node(Path(repo_path), 0)
    
    @staticmethod
    def _get_file_stats(repo_path: str) -> dict:
        stats = defaultdict(lambda: {"count": 0, "lines": 0})
        
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                ext = Path(file).suffix or "other"
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = len(f.readlines())
                    stats[ext]["count"] += 1
                    stats[ext]["lines"] += lines
                except:
                    pass
        
        return dict(stats)
    
    @staticmethod
    def _analyze_dependencies(repo_path: str) -> dict:
        dependencies = {"imports": [], "modules": []}
        
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    CodeGraphService._extract_python_imports(file_path, dependencies)
                elif file.endswith('.js') or file.endswith('.ts'):
                    file_path = os.path.join(root, file)
                    CodeGraphService._extract_js_imports(file_path, dependencies)
        
        return dependencies
    
    @staticmethod
    def _extract_python_imports(file_path: str, dependencies: dict):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                imports = re.findall(r'^import\s+(\w+)|^from\s+(\w+)', content, re.MULTILINE)
                for imp in imports:
                    module = imp[0] or imp[1]
                    if module and module not in dependencies["imports"]:
                        dependencies["imports"].append(module)
        except:
            pass
    
    @staticmethod
    def _extract_js_imports(file_path: str, dependencies: dict):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                imports = re.findall(r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]|require\([\'"]([^\'"]+)[\'"]', content)
                for imp in imports:
                    module = imp[0] or imp[1]
                    if module and module not in dependencies["imports"]:
                        dependencies["imports"].append(module)
        except:
            pass
