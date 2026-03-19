"""
URL 验证和错误处理模块
"""
import re
from urllib.parse import urlparse
import requests


def validate_github_url(url: str) -> dict:
    """
    验证 GitHub URL 并返回详细结果

    Returns:
        dict: {"valid": bool, "message": str, "parsed": dict or None}
    """
    if not url or not url.strip():
        return {
            "valid": False,
            "message": "请输入 GitHub 仓库 URL",
            "parsed": None
        }

    url = url.strip()

    # 基本格式验证
    patterns = [
        r'^https?://github\.com/[^/]+/[^/]+/?$',
        r'^https?://github\.com/[^/]+/[^/]+/tree/[^/]+/[^/]+/?$',
        r'^https?://github\.com/[^/]+/[^/]+/blob/[^/]+/[^/]+/?$'
    ]

    is_valid_format = False
    for pattern in patterns:
        if re.match(pattern, url):
            is_valid_format = True
            break

    if not is_valid_format:
        return {
            "valid": False,
            "message": "请输入有效的 GitHub 仓库 URL（例如：https://github.com/user/repo）",
            "parsed": None
        }

    # 解析 URL 获取 owner 和 repo
    parsed = urlparse(url)
    path = parsed.path.strip('/')
    parts = path.split('/')

    # 如果 URL 包含 tree 或 blob，去掉这些部分
    if len(parts) > 2 and parts[2] in ['tree', 'blob']:
        parts = parts[:2]

    if len(parts) < 2:
        return {
            "valid": False,
            "message": "URL 格式不正确，请确保包含 owner 和仓库名",
            "parsed": None
        }

    owner = parts[0]
    repo = parts[1].replace('.git', '')

    return {
        "valid": True,
        "message": "URL 验证通过",
        "parsed": {
            "owner": owner,
            "repo": repo,
            "full_name": f"{owner}/{repo}",
            "url": f"https://github.com/{owner}/{repo}"
        }
    }


def check_repo_exists(repo_url: str, github_token: str = None) -> dict:
    """
    检查仓库是否存在（公开或私有）

    Args:
        repo_url: GitHub 仓库 URL
        github_token: GitHub API Token（可选）

    Returns:
        dict: {"exists": bool, "is_private": bool, "message": str}
    """
    from core.utils import parse_github_url

    parsed_info = parse_github_url(repo_url)
    if not parsed_info:
        return {
            "exists": False,
            "is_private": False,
            "message": "无法解析仓库信息"
        }

    owner = parsed_info["owner"]
    repo = parsed_info["repo"]

    headers = {"Accept": "application/vnd.github.v3+json"}
    if github_token:
        headers["Authorization"] = f"token {github_token}"

    api_url = f"https://api.github.com/repos/{owner}/{repo}"

    try:
        response = requests.get(api_url, headers=headers, timeout=10)

        if response.status_code == 200:
            return {
                "exists": True,
                "is_private": False,
                "message": "仓库存在"
            }
        elif response.status_code == 404:
            return {
                "exists": False,
                "is_private": False,
                "message": "仓库不存在或为私有仓库"
            }
        elif response.status_code == 403:
            # 可能是 API 限流
            return {
                "exists": True,
                "is_private": True,
                "message": "无法确认仓库状态，可能是 API 限流"
            }
        else:
            return {
                "exists": False,
                "is_private": False,
                "message": f"检查仓库失败: HTTP {response.status_code}"
            }

    except requests.exceptions.Timeout:
        return {
            "exists": False,
            "is_private": False,
            "message": "请求超时，请稍后重试"
        }
    except requests.exceptions.RequestException as e:
        return {
            "exists": False,
            "is_private": False,
            "message": f"网络错误: {str(e)}"
        }


def handle_api_error(error: Exception) -> dict:
    """
    处理 API 错误并返回友好的错误消息

    Args:
        error: 异常对象

    Returns:
        dict: {"type": str, "message": str, "suggestion": str}
    """
    error_str = str(error).lower()

    # API 限流
    if "rate limit" in error_str or "too many requests" in error_str:
        return {
            "type": "rate_limit",
            "message": "GitHub API 请求次数已达上限",
            "suggestion": "请稍后重试，或配置 GitHub Token 以提高 API 限制"
        }

    # 网络错误
    if "connection" in error_str or "timeout" in error_str:
        return {
            "type": "network",
            "message": "网络连接失败",
            "suggestion": "请检查网络后重试"
        }

    # 仓库不存在
    if "not found" in error_str or "404" in error_str:
        return {
            "type": "not_found",
            "message": "仓库不存在或为私有仓库",
            "suggestion": "请确认仓库 URL 是否正确，或检查是否为私有仓库"
        }

    # 认证错误
    if "unauthorized" in error_str or "401" in error_str:
        return {
            "type": "auth",
            "message": "认证失败",
            "suggestion": "请检查 GitHub Token 是否正确"
        }

    # 默认错误
    return {
        "type": "unknown",
        "message": f"发生错误: {str(error)}",
        "suggestion": "请稍后重试"
    }