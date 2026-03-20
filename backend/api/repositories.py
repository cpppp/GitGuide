"""
仓库 API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.config import get_db
from backend.database.crud import RepositoryCRUD
import json

router = APIRouter()

@router.get("/repositories")
async def get_repositories(db: Session = Depends(get_db)):
    """
    获取所有已分析的仓库
    """
    repos = RepositoryCRUD.get_all(db)
    return {
        "repositories": [
            {
                "id": r.id,
                "url": r.url,
                "name": r.name,
                "description": r.description,
                "language": r.language,
                "stars": r.stars,
                "learning_doc": r.learning_doc,
                "setup_guide": r.setup_guide,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "updated_at": r.updated_at.isoformat() if r.updated_at else None
            }
            for r in repos
        ]
    }

@router.get("/repositories/{repo_url:path}")
async def get_repository(repo_url: str, db: Session = Depends(get_db)):
    """
    获取指定仓库的详细信息
    """
    repo = RepositoryCRUD.get_by_url(db, repo_url)
    if not repo:
        return {"error": "Repository not found"}
    
    return {
        "id": repo.id,
        "url": repo.url,
        "name": repo.name,
        "description": repo.description,
        "language": repo.language,
        "stars": repo.stars,
        "learning_doc": repo.learning_doc,
        "setup_guide": repo.setup_guide,
        "analysis_result": json.loads(repo.analysis_result) if repo.analysis_result else None,
        "created_at": repo.created_at.isoformat() if repo.created_at else None,
        "updated_at": repo.updated_at.isoformat() if repo.updated_at else None
    }

@router.delete("/repositories/{repo_url:path}")
async def delete_repository(repo_url: str, db: Session = Depends(get_db)):
    """
    删除指定仓库
    """
    success = RepositoryCRUD.delete(db, repo_url)
    return {"success": success}
