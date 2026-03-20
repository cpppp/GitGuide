"""
迁移脚本：将收藏数据从 JSON 文件迁移到数据库
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database.config import SessionLocal, engine
from backend.models.database import Base
from backend.database.crud import RepositoryCRUD, FavoriteCRUD

FAVORITES_FILE = Path(__file__).parent.parent / "data" / "favorites.json"


def migrate_favorites():
    """迁移收藏数据"""
    if not FAVORITES_FILE.exists():
        print("未找到收藏数据文件，跳过迁移")
        return
    
    with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
        favorites = json.load(f)
    
    if not favorites:
        print("收藏数据为空，跳过迁移")
        return
    
    db = SessionLocal()
    try:
        migrated_count = 0
        for item in favorites:
            url = item.get("url")
            if not url:
                continue
            
            repo_info = {
                "name": item.get("name", ""),
                "description": item.get("description", ""),
                "language": item.get("language", ""),
                "stargazers_count": item.get("stargazers_count", 0),
            }
            
            result = FavoriteCRUD.add_by_url(db, url, repo_info)
            if result:
                migrated_count += 1
                print(f"已迁移: {url}")
        
        print(f"\n迁移完成！共迁移 {migrated_count} 条收藏记录")
        
        backup_file = FAVORITES_FILE.with_suffix(".json.bak")
        FAVORITES_FILE.rename(backup_file)
        print(f"原文件已备份至: {backup_file}")
        
    except Exception as e:
        print(f"迁移失败: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("开始迁移收藏数据...")
    print("=" * 50)
    migrate_favorites()
