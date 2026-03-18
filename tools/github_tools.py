"""GitHub API 工具 - 使用 LangChain @tool 装饰器"""
import requests
import base64
import urllib3
from langchain_core.tools import tool
from core.config import Config
from core.utils import parse_github_url, truncate_text

# 禁用 SSL 证书警告（Windows 环境下常见问题）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class GitHubTools:
    def __init__(self):
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if Config.GITHUB_TOKEN:
            self.headers["Authorization"] = f"token {Config.GITHUB_TOKEN}"

        # 创建 session，禁用 SSL 证书验证
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        # 禁用 SSL 证书验证（解决 Windows 下证书问题）
        self.session.verify = False

    def get_repo_info(self, repo_url):
        """获取 GitHub 仓库基本信息"""
        repo_info = parse_github_url(repo_url)
        if not repo_info:
            return {"error": "Invalid GitHub URL"}

        owner = repo_info["owner"]
        repo = repo_info["repo"]

        # 获取仓库元数据
        url = f"https://api.github.com/repos/{owner}/{repo}"
        response = self.session.get(url)

        if response.status_code != 200:
            return {"error": f"Failed to get repo info: {response.status_code}"}

        data = response.json()

        # 获取 README
        readme_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
        readme_response = self.session.get(readme_url)
        readme_content = ""

        if readme_response.status_code == 200:
            readme_data = readme_response.json()
            if "content" in readme_data:
                try:
                    readme_content = base64.b64decode(readme_data["content"]).decode('utf-8')
                except:
                    pass

        return {
            "name": data.get("name"),
            "description": data.get("description"),
            "language": data.get("language"),
            "stargazers_count": data.get("stargazers_count"),
            "full_name": data.get("full_name"),
            "html_url": data.get("html_url"),
            "readme": truncate_text(readme_content, 10000)
        }

    def get_file_content(self, repo_url, file_path):
        """获取指定文件的内容"""
        repo_info = parse_github_url(repo_url)
        if not repo_info:
            return {"error": "Invalid GitHub URL"}

        owner = repo_info["owner"]
        repo = repo_info["repo"]

        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
        response = self.session.get(url)

        if response.status_code != 200:
            return {"error": f"Failed to get file: {response.status_code}"}

        data = response.json()
        if "content" in data:
            try:
                content = base64.b64decode(data["content"]).decode('utf-8')
                return truncate_text(content, 5000)
            except:
                return {"error": "Failed to decode content"}

        return {"error": "No content found"}


# 全局实例
github_tools = GitHubTools()


# 使用 @tool 装饰器导出工具函数
@tool
def get_repo_info(repo_url: str) -> str:
    """
    获取 GitHub 仓库的基本信息。

    参数:
        repo_url: GitHub 仓库的完整 URL，例如 https://github.com/user/repo

    返回:
        包含仓库名称、描述、语言、star数量和README的字典
    """
    result = github_tools.get_repo_info(repo_url)
    return str(result)


@tool
def get_file_content(repo_url: str, file_path: str) -> str:
    """
    获取 GitHub 仓库中指定文件的内容。

    参数:
        repo_url: GitHub 仓库的完整 URL
        file_path: 文件路径，例如 README.md、src/main.py

    返回:
        文件内容字符串
    """
    result = github_tools.get_file_content(repo_url, file_path)
    return str(result)