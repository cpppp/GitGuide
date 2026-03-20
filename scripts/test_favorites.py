"""测试收藏功能"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database.config import SessionLocal
from backend.database.crud import FavoriteCRUD

def test_favorites():
    db = SessionLocal()
    try:
        print("=== 测试收藏功能 ===")
        
        print("\n1. 添加收藏...")
        repo_info = {
            'name': 'vue',
            'full_name': 'vuejs/vue',
            'description': 'Vue.js framework',
            'language': 'TypeScript',
            'stargazers_count': 45000
        }
        result = FavoriteCRUD.add_by_url(db, 'https://github.com/vuejs/vue', repo_info)
        print(f"   添加结果: {result}")
        
        print("\n2. 获取收藏列表...")
        favs = FavoriteCRUD.get_all_with_repo(db)
        print(f"   收藏数量: {len(favs)}")
        for fav in favs:
            print(f"   - {fav['url']}: {fav['name']} ({fav['stars']} stars)")
        
        print("\n3. 检查是否已收藏...")
        is_fav = FavoriteCRUD.is_favorite_by_url(db, 'https://github.com/vuejs/vue')
        print(f"   is_favorite: {is_fav}")
        
        print("\n4. 删除收藏...")
        deleted = FavoriteCRUD.remove_by_url(db, 'https://github.com/vuejs/vue')
        print(f"   删除数量: {deleted}")
        
        print("\n5. 再次获取收藏列表...")
        favs = FavoriteCRUD.get_all_with_repo(db)
        print(f"   收藏数量: {len(favs)}")
        
        print("\n=== 测试完成 ===")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_favorites()
