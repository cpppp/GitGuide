import re
from urllib.parse import urlparse

# 从 URL 中提取仓库信息
def parse_github_url(url):
    """解析 GitHub URL，返回 owner 和 repo 名称"""
    parsed = urlparse(url)
    path = parsed.path.strip('/')
    parts = path.split('/')
    
    if len(parts) >= 2:
        return {
            "owner": parts[0],
            "repo": parts[1],
            "full_name": f"{parts[0]}/{parts[1]}"
        }
    return None

# 检查是否是有效的 GitHub URL
def is_valid_github_url(url):
    """验证是否是有效的 GitHub 仓库 URL"""
    if not url:
        return False
    
    patterns = [
        r'^https?://github\.com/[^/]+/[^/]+/?$',
        r'^https?://github\.com/[^/]+/[^/]+/[^/]+/?$'
    ]
    
    for pattern in patterns:
        if re.match(pattern, url):
            return True
    return False

# 限制文本长度
def truncate_text(text, max_length=5000):
    """截断文本到指定长度"""
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text

# 格式化目录结构
def format_directory_structure(structure, max_depth=3, current_depth=0):
    """格式化目录结构为可读的树形结构"""
    result = []
    indent = "  " * current_depth
    
    for item in structure:
        if isinstance(item, dict):
            for name, children in item.items():
                result.append(f"{indent}- {name}/")
                if current_depth < max_depth - 1:
                    result.extend(format_directory_structure(
                        children, max_depth, current_depth + 1
                    ))
        else:
            result.append(f"{indent}- {item}")
    
    return result