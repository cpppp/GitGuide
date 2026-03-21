from collections import defaultdict
from pathlib import Path
import os
import re
import json

class CodeGraphService:
    @staticmethod
    def analyze_structure(repo_path: str) -> dict:
        result = {
            "tree": CodeGraphService._build_tree(repo_path),
            "stats": CodeGraphService._get_file_stats(repo_path),
            "dependencies": CodeGraphService._analyze_dependencies(repo_path),
            "mermaid_architecture": CodeGraphService.generate_mermaid_diagram(repo_path)
        }
        return result

    @staticmethod
    def generate_mermaid_diagram(repo_path: str) -> str:
        """生成 Mermaid 格式的架构图"""
        tree = CodeGraphService._build_tree(repo_path, max_depth=2)
        dependencies = CodeGraphService._analyze_dependencies(repo_path)

        mermaid_lines = ["flowchart TD"]

        # 根节点
        root_name = Path(repo_path).name
        mermaid_lines.append(f"    Root[\"{root_name}\"]")

        # 添加子模块
        if tree.get("children"):
            for child in tree["children"][:5]:  # 最多5个一级模块
                child_name = child.get("name", "")
                if child.get("type") == "folder":
                    # 转换为有效的 Mermaid 节点 ID
                    node_id = child_name.replace("-", "_").replace(".", "_")
                    mermaid_lines.append(f"    {node_id}[\"{child_name}\"]")
                    mermaid_lines.append(f"    Root --> {node_id}")

                    # 添加二级子模块
                    if child.get("children"):
                        for sub_child in child["children"][:3]:
                            sub_name = sub_child.get("name", "")
                            if sub_child.get("type") == "folder":
                                sub_id = sub_name.replace("-", "_").replace(".", "_")
                                mermaid_lines.append(f"    {sub_id}[\"{sub_name}\"]")
                                mermaid_lines.append(f"    {node_id} --> {sub_id}")

        # 添加依赖关系（显示主要依赖）
        if dependencies.get("imports"):
            for imp in dependencies["imports"][:5]:
                imp_id = imp.replace("-", "_").replace(".", "_")
                mermaid_lines.append(f"    External[\"{imp}\"]")
                mermaid_lines.append(f"    {imp_id} --> External")

        return "\n".join(mermaid_lines)
    
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
                    children.append(build_node(item, depth + 1))
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

    @staticmethod
    def extract_examples(repo_path: str) -> list:
        """提取示例代码"""
        examples = []
        example_patterns = ['example', 'demo', 'test', 'sample', 'example_', '_example']

        for root, dirs, files in os.walk(repo_path):
            # 跳过不必要的目录
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', 'venv', '__pycache__', 'dist', 'build']]

            for file in files:
                file_lower = file.lower()
                # 检查是否是示例文件
                if any(pattern in file_lower for pattern in example_patterns):
                    if file.endswith(('.py', '.js', '.ts', '.go', '.java', '.rb', '.rs')):
                        file_path = os.path.join(root, file)
                        example = CodeGraphService._extract_code_snippet(file_path, file)
                        if example:
                            examples.append(example)

                # 检查是否包含示例代码的目录
                rel_path = os.path.relpath(root, repo_path)
                if any(pattern in rel_path.lower() for pattern in example_patterns):
                    if file.endswith(('.py', '.js', '.ts', '.go', '.java', '.rb', '.rs')):
                        file_path = os.path.join(root, file)
                        example = CodeGraphService._extract_code_snippet(file_path, file)
                        if example:
                            examples.append(example)

        return examples[:10]  # 最多返回10个示例

    @staticmethod
    def _extract_code_snippet(file_path: str, filename: str) -> dict:
        """从文件中提取代码片段"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # 获取相对路径
            lines = content.split('\n')

            # 提取函数/类定义作为示例
            snippets = []

            # Python
            if filename.endswith('.py'):
                # 查找函数定义
                func_matches = re.findall(r'^(?:def |class )(\w+).*?:', content, re.MULTILINE)
                for match in func_matches[:3]:
                    snippets.append({
                        "type": "function",
                        "name": match,
                        "language": "python",
                        "description": f"Python {('class' if 'class ' in content else 'function')}: {match}"
                    })

            # JavaScript/TypeScript
            elif filename.endswith(('.js', '.ts')):
                func_matches = re.findall(r'^(?:function |const |let |var )(\w+)\s*[\=\(]', content, re.MULTILINE)
                for match in func_matches[:3]:
                    snippets.append({
                        "type": "function",
                        "name": match,
                        "language": "javascript",
                        "description": f"JS function/variable: {match}"
                    })

            # Go
            elif filename.endswith('.go'):
                func_matches = re.findall(r'^func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)\(', content, re.MULTILINE)
                for match in func_matches[:3]:
                    snippets.append({
                        "type": "function",
                        "name": match,
                        "language": "go",
                        "description": f"Go function: {match}"
                    })

            # 取前50行作为代码预览
            preview = '\n'.join(lines[:50])

            return {
                "filename": filename,
                "path": file_path,
                "snippets": snippets,
                "preview": preview,
                "total_lines": len(lines)
            }
        except:
            return None
