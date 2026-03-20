"""
问答 API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.models.schemas import ChatRequest, ChatResponse
from backend.database.config import get_db
from backend.database.crud import RepositoryCRUD, ChatMessageCRUD

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    问答接口
    """
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    try:
        from agents.chat import run_chat
        
        # 获取或创建仓库记录
        repo = RepositoryCRUD.get_by_url(db, request.repo_url)
        if not repo:
            repo = RepositoryCRUD.create(db, {"url": request.repo_url})
        
        # 保存用户消息
        ChatMessageCRUD.create(db, repo.id, "user", request.query)
        
        # 转换历史记录格式
        history = None
        if request.history:
            history = [{"role": msg.role, "content": msg.content} for msg in request.history]
        
        result = run_chat(request.query, request.repo_url, history)
        
        if result.get("success"):
            response_text = result.get("response", "")
            
            # 保存 AI 回复
            ChatMessageCRUD.create(db, repo.id, "assistant", response_text)
            
            return ChatResponse(
                success=True,
                response=response_text,
                repo_url=request.repo_url
            )
        else:
            return ChatResponse(
                success=False,
                response=result.get("error", "问答服务出错"),
                repo_url=request.repo_url
            )
    except Exception as e:
        return ChatResponse(
            success=False,
            response=f"服务错误: {str(e)}",
            repo_url=request.repo_url
        )

@router.get("/chat/history")
async def get_chat_history(repo_url: str, db: Session = Depends(get_db)):
    """
    获取问答历史记录
    """
    repo = RepositoryCRUD.get_by_url(db, repo_url)
    if not repo:
        return {"messages": []}
    
    messages = ChatMessageCRUD.get_by_repo(db, repo.id)
    return {
        "messages": [{"role": m.role, "content": m.content} for m in messages]
    }

@router.delete("/chat/history")
async def clear_chat_history(repo_url: str, db: Session = Depends(get_db)):
    """
    清除问答历史记录
    """
    repo = RepositoryCRUD.get_by_url(db, repo_url)
    if repo:
        ChatMessageCRUD.delete_by_repo(db, repo.id)
    
    return {"success": True}
