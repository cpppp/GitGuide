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
    获取所有已分析的仓库 - 支持7种文档 + 代码图谱
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
                # V3.0 文档
                "quick_start": r.quick_start,
                "overview": r.overview_doc,
                "architecture": r.architecture_doc,
                "install_guide": r.install_guide,
                # V3.1 新文档
                "usage_tutorial": r.usage_tutorial,
                "dev_guide": r.dev_guide,
                "troubleshooting": r.troubleshooting,
                # V3.1 代码图谱数据
                "code_graph": json.loads(r.code_graph) if r.code_graph else None,
                "examples": json.loads(r.examples) if r.examples else [],
                # 旧字段（兼容）
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
    获取指定仓库的详细信息 - 支持7种文档 + 代码图谱
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
        # V3.0 文档
        "quick_start": repo.quick_start,
        "overview": repo.overview_doc,
        "architecture": repo.architecture_doc,
        "install_guide": repo.install_guide,
        # V3.1 新文档
        "usage_tutorial": repo.usage_tutorial,
        "dev_guide": repo.dev_guide,
        "troubleshooting": repo.troubleshooting,
        # V3.1 代码图谱数据
        "code_graph": json.loads(repo.code_graph) if repo.code_graph else None,
        "examples": json.loads(repo.examples) if repo.examples else [],
        # 旧字段（兼容）
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
