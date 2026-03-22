from sqlalchemy.orm import Session
from backend.models.database import Repository, ChatMessage, Favorite, AnalysisHistory
from typing import Optional, List

class RepositoryCRUD:
    @staticmethod
    def get_by_url(db: Session, url: str) -> Optional[Repository]:
        return db.query(Repository).filter(Repository.url == url).first()
    
    @staticmethod
    def get_by_id(db: Session, repo_id: int) -> Optional[Repository]:
        return db.query(Repository).filter(Repository.id == repo_id).first()
    
    @staticmethod
    def create(db: Session, repo_data: dict) -> Repository:
        db_repo = Repository(**repo_data)
        db.add(db_repo)
        db.commit()
        db.refresh(db_repo)
        return db_repo
    
    @staticmethod
    def update(db: Session, url: str, update_data: dict) -> Optional[Repository]:
        db_repo = RepositoryCRUD.get_by_url(db, url)
        if db_repo:
            for key, value in update_data.items():
                setattr(db_repo, key, value)
            db.commit()
            db.refresh(db_repo)
        return db_repo
    
    @staticmethod
    def get_all(db: Session) -> List[Repository]:
        return db.query(Repository).order_by(Repository.updated_at.desc()).all()
    
    @staticmethod
    def delete(db: Session, url: str) -> bool:
        db_repo = RepositoryCRUD.get_by_url(db, url)
        if db_repo:
            db.delete(db_repo)
            db.commit()
            return True
        return False

    @staticmethod
    def delete_all(db: Session) -> int:
        deleted = db.query(Repository).delete()
        db.commit()
        return deleted

class ChatMessageCRUD:
    @staticmethod
    def create(db: Session, repo_id: int, role: str, content: str) -> ChatMessage:
        db_message = ChatMessage(repo_id=repo_id, role=role, content=content)
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        return db_message
    
    @staticmethod
    def get_by_repo(db: Session, repo_id: int) -> List[ChatMessage]:
        return db.query(ChatMessage).filter(
            ChatMessage.repo_id == repo_id
        ).order_by(ChatMessage.created_at).all()
    
    @staticmethod
    def delete_by_repo(db: Session, repo_id: int) -> int:
        deleted = db.query(ChatMessage).filter(
            ChatMessage.repo_id == repo_id
        ).delete()
        db.commit()
        return deleted
    
    @staticmethod
    def delete_by_id(db: Session, message_id: int) -> bool:
        db_message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
        if db_message:
            db.delete(db_message)
            db.commit()
            return True
        return False

class FavoriteCRUD:
    @staticmethod
    def add(db: Session, repo_id: int) -> Favorite:
        existing = db.query(Favorite).filter(Favorite.repo_id == repo_id).first()
        if existing:
            return existing
        db_fav = Favorite(repo_id=repo_id)
        db.add(db_fav)
        db.commit()
        db.refresh(db_fav)
        return db_fav
    
    @staticmethod
    def add_by_url(db: Session, url: str, repo_info: dict = None) -> Optional[Favorite]:
        repo = RepositoryCRUD.get_by_url(db, url)
        if not repo:
            repo_data = {
                "url": url,
                "name": repo_info.get("name", repo_info.get("full_name", "")) if repo_info else "",
                "description": repo_info.get("description", "") if repo_info else "",
                "language": repo_info.get("language", "") if repo_info else "",
                "stars": repo_info.get("stargazers_count", 0) if repo_info else 0,
            }
            repo = RepositoryCRUD.create(db, repo_data)
        return FavoriteCRUD.add(db, repo.id)
    
    @staticmethod
    def remove(db: Session, repo_id: int) -> int:
        deleted = db.query(Favorite).filter(Favorite.repo_id == repo_id).delete()
        db.commit()
        return deleted
    
    @staticmethod
    def remove_by_url(db: Session, url: str) -> int:
        repo = RepositoryCRUD.get_by_url(db, url)
        if repo:
            return FavoriteCRUD.remove(db, repo.id)
        return 0
    
    @staticmethod
    def get_all(db: Session) -> List[Favorite]:
        return db.query(Favorite).order_by(Favorite.created_at.desc()).all()
    
    @staticmethod
    def get_all_with_repo(db: Session) -> List[dict]:
        favorites = db.query(Favorite).join(Repository).order_by(Favorite.created_at.desc()).all()
        return [
            {
                "id": fav.id,
                "repo_id": fav.repo_id,
                "url": fav.repository.url,
                "name": fav.repository.name,
                "description": fav.repository.description,
                "language": fav.repository.language,
                "stars": fav.repository.stars,
                "created_at": fav.created_at.isoformat() if fav.created_at else None
            }
            for fav in favorites
        ]
    
    @staticmethod
    def is_favorite(db: Session, repo_id: int) -> bool:
        return db.query(Favorite).filter(Favorite.repo_id == repo_id).first() is not None
    
    @staticmethod
    def is_favorite_by_url(db: Session, url: str) -> bool:
        repo = RepositoryCRUD.get_by_url(db, url)
        if repo:
            return FavoriteCRUD.is_favorite(db, repo.id)
        return False

class AnalysisHistoryCRUD:
    @staticmethod
    def create(db: Session, repo_id: int) -> AnalysisHistory:
        db_history = AnalysisHistory(repo_id=repo_id)
        db.add(db_history)
        db.commit()
        db.refresh(db_history)
        return db_history
    
    @staticmethod
    def get_by_repo(db: Session, repo_id: int) -> List[AnalysisHistory]:
        return db.query(AnalysisHistory).filter(
            AnalysisHistory.repo_id == repo_id
        ).order_by(AnalysisHistory.analyzed_at.desc()).all()
