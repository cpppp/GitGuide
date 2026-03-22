"""
问答 API（V3.2 增强版）
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.models.schemas import ChatRequest, ChatResponse
from backend.database.config import get_db
from backend.database.crud import RepositoryCRUD, ChatMessageCRUD

router = APIRouter()


def import_chat_functions():
    from agents.chat_agent import run_chat, get_chat_session, clear_chat_session, build_knowledge_base
    return run_chat, get_chat_session, clear_chat_session, build_knowledge_base


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    问答接口（支持源码级别分析）
    """
    try:
        run_chat, _, _, _ = import_chat_functions()

        repo = RepositoryCRUD.get_by_url(db, request.repo_url)
        if not repo:
            repo = RepositoryCRUD.create(db, {"url": request.repo_url})

        ChatMessageCRUD.create(db, repo.id, "user", request.query)

        history = None
        if request.history:
            history = [{"role": msg.role, "content": msg.content} for msg in request.history]

        result = run_chat(
            request.query,
            request.repo_url,
            history,
            file_path=request.file_path
        )

        if result.get("success"):
            response_text = result.get("response", "")

            ChatMessageCRUD.create(db, repo.id, "assistant", response_text)

            return ChatResponse(
                success=True,
                response=response_text,
                repo_url=request.repo_url,
                referenced_files=result.get("referenced_files", []),
                analyzed_file=result.get("analyzed_file")
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


@router.post("/chat/build-knowledge-base")
async def build_knowledge_base(repo_url: str, db: Session = Depends(get_db)):
    """
    为仓库构建知识库（预索引源码）
    """
    try:
        _, _, _, build_kb = import_chat_functions()

        repo = RepositoryCRUD.get_by_url(db, repo_url)
        if not repo:
            return {"success": False, "error": "Repository not found"}

        analysis_result = None
        if repo.analysis_result:
            try:
                import json
                analysis_result = json.loads(repo.analysis_result)
            except:
                pass

        result = build_kb(repo_url, analysis_result=analysis_result)

        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/chat/file-content")
async def get_file_content(repo_url: str, file_path: str, db: Session = Depends(get_db)):
    """
    获取仓库中指定文件的内容（用于前端展示）
    """
    try:
        _, get_chat_session, _, _ = import_chat_functions()

        session = get_chat_session(repo_url)

        if not session.is_ready():
            return {"success": False, "error": "Knowledge base not ready"}

        source_indexer = session.knowledge_builder.source_indexer
        if not source_indexer:
            return {"success": False, "error": "Source indexer not available"}

        source_file = source_indexer.get_file_by_path(file_path)
        if not source_file:
            return {"success": False, "error": f"File not found: {file_path}"}

        return {
            "success": True,
            "file_path": source_file.relative_path,
            "language": source_file.language,
            "content": source_file.content,
            "line_count": source_file.line_count,
            "symbols": [
                {"name": s.name, "type": s.type, "line_number": s.line_number}
                for s in source_file.symbols
            ]
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
