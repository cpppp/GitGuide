"""
问答 API
"""
from fastapi import APIRouter

from backend.models.schemas import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    问答接口
    """
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    try:
        from agents.chat import run_chat

        # 转换历史记录格式
        history = None
        if request.history:
            history = [{"role": msg.role, "content": msg.content} for msg in request.history]

        result = run_chat(request.query, request.repo_url, history)

        if result.get("success"):
            return ChatResponse(
                success=True,
                response=result.get("response", ""),
                repo_url=result.get("repo_url", request.repo_url)
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