"""
Pydantic 数据模型
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class AnalysisMode(str, Enum):
    """分析模式"""
    FAST = "fast"
    DETAILED = "detailed"


class AnalyzeRequest(BaseModel):
    """分析请求"""
    repo_url: str = Field(..., description="GitHub 仓库 URL")
    mode: AnalysisMode = Field(default=AnalysisMode.FAST, description="分析模式")


class AnalyzeResponse(BaseModel):
    """分析响应"""
    job_id: str = Field(..., description="任务 ID")
    status: str = Field(default="pending", description="任务状态")


class TaskStatus(BaseModel):
    """任务状态"""
    job_id: str
    status: str  # pending, running, completed, failed, cancelled
    progress: int = Field(default=0, ge=0, le=100)
    progress_message: str = ""
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    cancelled: bool = False


class ProgressUpdate(BaseModel):
    """进度更新"""
    job_id: str
    stage_key: str
    progress: int
    message: str


class ChatMessage(BaseModel):
    """聊天消息"""
    role: str = Field(..., description="角色: user/assistant")
    content: str = Field(..., description="消息内容")


class ChatRequest(BaseModel):
    """问答请求"""
    repo_url: str = Field(..., description="GitHub 仓库 URL")
    query: str = Field(..., description="用户问题")
    history: Optional[List[ChatMessage]] = Field(default_factory=list, description="聊天历史")


class ChatResponse(BaseModel):
    """问答响应"""
    success: bool
    response: str
    repo_url: str


class HistoryItem(BaseModel):
    """历史记录项"""
    url: str
    name: str
    timestamp: str
    language: Optional[str] = None


class FavoriteItem(BaseModel):
    """收藏项"""
    url: str
    name: str
    language: Optional[str] = None
    added_at: Optional[str] = None