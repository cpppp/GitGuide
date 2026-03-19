"""
健康检查 API
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "service": "GitGuide API"}


@router.get("/")
async def root():
    """根路径"""
    return {"message": "Welcome to GitGuide API", "version": "1.0.0"}