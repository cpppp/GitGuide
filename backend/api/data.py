"""
数据导出导入 API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.config import get_db
from backend.database.crud import RepositoryCRUD, ChatMessageCRUD
import json

router = APIRouter()

@router.get("/data/export")
async def export_data(db: Session = Depends(get_db)):
    """
    导出所有数据（JSON格式）
    """
    repos = RepositoryCRUD.get_all(db)
    
    export_data = {
        "repositories": [],
        "chat_messages": []
    }
    
    for repo in repos:
        repo_data = {
            "url": repo.url,
            "name": repo.name,
            "description": repo.description,
            "language": repo.language,
            "stars": repo.stars,
            "learning_doc": repo.learning_doc,
            "setup_guide": repo.setup_guide,
            "created_at": repo.created_at.isoformat() if repo.created_at else None,
            "updated_at": repo.updated_at.isoformat() if repo.updated_at else None
        }
        export_data["repositories"].append(repo_data)
        
        messages = ChatMessageCRUD.get_by_repo(db, repo.id)
        for msg in messages:
            export_data["chat_messages"].append({
                "repo_url": repo.url,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat() if msg.created_at else None
            })
    
    return export_data

@router.post("/data/import")
async def import_data(data: dict, db: Session = Depends(get_db)):
    """
    导入数据（JSON格式）
    """
    imported_count = 0
    
    for repo_data in data.get("repositories", []):
        existing = RepositoryCRUD.get_by_url(db, repo_data["url"])
        if not existing:
            RepositoryCRUD.create(db, repo_data)
            imported_count += 1
    
    return {"success": True, "imported_count": imported_count}
