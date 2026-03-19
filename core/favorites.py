"""
收藏仓库管理模块
"""
import json
import os
from datetime import datetime
from pathlib import Path

# 数据目录
DATA_DIR = Path(__file__).parent.parent / "data"
FAVORITES_FILE = DATA_DIR / "favorites.json"


def ensure_data_dir():
    """确保数据目录存在"""
    DATA_DIR.mkdir(exist_ok=True)


def load_favorites() -> list:
    """加载收藏列表"""
    ensure_data_dir()

    if not FAVORITES_FILE.exists():
        return []

    try:
        with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_favorites(favorites: list):
    """保存收藏列表"""
    ensure_data_dir()

    with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
        json.dump(favorites, f, ensure_ascii=False, indent=2)


def add_favorite(repo_url: str, repo_info: dict = None):
    """
    添加收藏

    Args:
        repo_url: 仓库 URL
        repo_info: 仓库信息字典
    """
    favorites = load_favorites()

    # 检查是否已存在
    if is_favorite(repo_url):
        return False

    # 创建收藏记录
    new_favorite = {
        "url": repo_url,
        "name": repo_info.get("name", repo_info.get("full_name", "Unknown")) if repo_info else Path(repo_url).stem,
        "description": repo_info.get("description", "") if repo_info else "",
        "language": repo_info.get("language", "") if repo_info else "",
        "stargazers_count": repo_info.get("stargazers_count", 0) if repo_info else 0,
        "added_at": datetime.now().isoformat()
    }

    favorites.append(new_favorite)
    save_favorites(favorites)
    return True


def remove_favorite(repo_url: str):
    """
    取消收藏

    Args:
        repo_url: 仓库 URL
    """
    favorites = load_favorites()
    favorites = [item for item in favorites if item.get("url") != repo_url]
    save_favorites(favorites)


def get_favorites() -> list:
    """获取收藏列表"""
    return load_favorites()


def is_favorite(repo_url: str) -> bool:
    """
    检查仓库是否已收藏

    Args:
        repo_url: 仓库 URL

    Returns:
        bool: 是否已收藏
    """
    favorites = load_favorites()
    return any(item.get("url") == repo_url for item in favorites)


def clear_favorites():
    """清除所有收藏"""
    save_favorites([])