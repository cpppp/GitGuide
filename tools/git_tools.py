"""Git 工具 - 使用 LangChain @tool 装饰器"""
import os
import tempfile
import git
from langchain_core.tools import tool
from core.utils import parse_github_url, format_directory_structure


class GitTools:
    def __init__(self):
        self.temp_dirs = []

    def __del__(self):
        # 清理临时目录
        for temp_dir in self.temp_dirs:
            try:
                import shutil
                shutil.rmtree(temp_dir)
            except:
                pass

    def clone_repo(self, repo_url):
        """克隆仓库到临时目录"""
        temp_dir = tempfile.mkdtemp()
        self.temp_dirs.append(temp_dir)

        try:
            git.Repo.clone_from(repo_url, temp_dir, depth=1)
            return temp_dir
        except Exception as e:
            return {"error": f"Failed to clone repo: {str(e)}"}

    def analyze_structure(self, repo_url):
        """分析仓库目录结构"""
        # 克隆仓库
        repo_path = self.clone_repo(repo_url)
        if isinstance(repo_path, dict) and "error" in repo_path:
            return repo_path

        # 忽略的目录和文件
        ignore_patterns = [
            ".git", "__pycache__", "node_modules", "venv", ".venv",
            "dist", "build", "*.pyc", ".DS_Store", "Thumbs.db"
        ]

        def should_ignore(path):
            for pattern in ignore_patterns:
                if pattern in path:
                    return True
            return False

        # 递归分析目录结构
        def get_structure(root, max_depth=3, current_depth=0):
            if current_depth >= max_depth:
                return []

            structure = []
            try:
                items = os.listdir(root)
                for item in sorted(items):
                    item_path = os.path.join(root, item)

                    if should_ignore(item_path):
                        continue

                    if os.path.isdir(item_path):
                        sub_structure = get_structure(item_path, max_depth, current_depth + 1)
                        structure.append({item: sub_structure})
                    else:
                        structure.append(item)
            except Exception as e:
                pass

            return structure

        # 获取目录结构
        structure = get_structure(repo_path)

        # 转换为可读格式
        formatted_structure = format_directory_structure(structure)

        return {
            "structure": structure,
            "formatted": "\n".join(formatted_structure)
        }


# 全局实例
git_tools = GitTools()


# 使用 @tool 装饰器导出工具函数
@tool
def clone_repo(repo_url: str) -> str:
    """
    克隆 GitHub 仓库到临时目录并返回本地路径。

    参数:
        repo_url: GitHub 仓库的完整 URL

    返回:
        临时目录路径
    """
    result = git_tools.clone_repo(repo_url)
    return str(result)


@tool
def analyze_structure(repo_url: str) -> str:
    """
    分析 GitHub 仓库的目录结构。

    参数:
        repo_url: GitHub 仓库的完整 URL

    返回:
        包含目录结构的字符串
    """
    result = git_tools.analyze_structure(repo_url)
    return str(result)