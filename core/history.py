"""
历史记录管理模块
"""
import json
import os
from datetime import datetime
from pathlib import Path

# 数据目录
DATA_DIR = Path(__file__).parent.parent / "data"
HISTORY_FILE = DATA_DIR / "history.json"

# 最大历史记录数
MAX_HISTORY_COUNT = 20


def ensure_data_dir():
    """确保数据目录存在"""
    DATA_DIR.mkdir(exist_ok=True)


def load_history() -> list:
    """加载历史记录"""
    ensure_data_dir()

    if not HISTORY_FILE.exists():
        return []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_history(history: list):
    """保存历史记录"""
    ensure_data_dir()

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def add_history(repo_url: str, repo_info: dict = None):
    """
    添加历史记录

    Args:
        repo_url: 仓库 URL
        repo_info: 仓库信息字典
    """
    history = load_history()

    # 检查是否已存在相同 URL
    for item in history:
        if item.get("url") == repo_url:
            # 更新时间戳并移到最前面
            history.remove(item)
            break

    # 创建新记录
    new_record = {
        "url": repo_url,
        "name": repo_info.get("name", repo_info.get("full_name", "Unknown")) if repo_info else Path(repo_url).stem,
        "description": repo_info.get("description", "") if repo_info else "",
        "language": repo_info.get("language", "") if repo_info else "",
        "timestamp": datetime.now().isoformat()
    }

    # 添加到列表开头
    history.insert(0, new_record)

    # 限制数量
    if len(history) > MAX_HISTORY_COUNT:
        history = history[:MAX_HISTORY_COUNT]

    save_history(history)


def get_history() -> list:
    """获取历史记录列表"""
    return load_history()


def clear_history():
    """清除所有历史记录"""
    save_history([])


def remove_history_item(url: str):
    """删除指定历史记录"""
    history = load_history()
    history = [item for item in history if item.get("url") != url]
    save_history(history)


def is_in_history(url: str) -> bool:
    """检查 URL 是否在历史记录中"""
    history = load_history()
    return any(item.get("url") == url for item in history)