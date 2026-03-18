"""文件工具 - 使用 LangChain @tool 装饰器"""
import os
from langchain_core.tools import tool
from tools.github_tools import get_file_content as github_get_file_content
from tools.git_tools import clone_repo as git_clone_repo


class FileTools:
    def read_file_from_repo(self, repo_url, file_path):
        """从仓库中读取文件内容"""
        # 首先尝试通过 GitHub API 获取
        content = github_get_file_content.invoke({"repo_url": repo_url, "file_path": file_path})
        if not content or "error" not in content.lower():
            return content

        # 如果 API 失败，尝试克隆仓库后读取
        repo_path = git_clone_repo.invoke({"repo_url": repo_url})
        if not repo_path or "error" in str(repo_path).lower():
            return {"error": "Failed to clone repo"}

        # 解析路径
        repo_path_str = str(repo_path).strip()
        if repo_path_str.startswith("'"):
            repo_path_str = repo_path_str.strip("'")
        if repo_path_str.startswith('"'):
            repo_path_str = repo_path_str.strip('"')

        full_path = os.path.join(repo_path_str, file_path)
        if os.path.exists(full_path):
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return content[:5000]  # 限制大小
            except Exception as e:
                return {"error": f"Failed to read file: {str(e)}"}

        return {"error": "File not found"}

    def detect_project_type(self, repo_url):
        """检测项目类型"""
        # 检查关键文件
        project_files = {
            "package.json": "Node.js",
            "requirements.txt": "Python",
            "setup.py": "Python",
            "pyproject.toml": "Python",
            "pom.xml": "Java (Maven)",
            "build.gradle": "Java (Gradle)",
            "go.mod": "Go",
            "Cargo.toml": "Rust",
            "Dockerfile": "Docker"
        }

        for file_path, project_type in project_files.items():
            try:
                content = github_get_file_content.invoke({"repo_url": repo_url, "file_path": file_path})
                if content and "error" not in str(content).lower():
                    return project_type
            except:
                continue

        return "Unknown"


# 全局实例
file_tools = FileTools()


# 使用 @tool 装饰器导出工具函数
@tool
def read_file_from_repo(repo_url: str, file_path: str) -> str:
    """
    从 GitHub 仓库中读取指定文件的内容。

    参数:
        repo_url: GitHub 仓库的完整 URL
        file_path: 文件路径，例如 src/main.py、config.json

    返回:
        文件内容字符串
    """
    result = file_tools.read_file_from_repo(repo_url, file_path)
    return str(result)


@tool
def detect_project_type(repo_url: str) -> str:
    """
    检测 GitHub 仓库的项目类型。

    参数:
        repo_url: GitHub 仓库的完整 URL

    返回:
        项目类型字符串，例如 "Node.js"、"Python"、"Java (Maven)" 等
    """
    result = file_tools.detect_project_type(repo_url)
    return str(result)