"""
FastAPI 后端入口
"""
import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from backend.api import analyze, chat, health, repositories, data
from backend.websocket.manager import WebSocketManager
from backend.database.config import init_db


# 全局 WebSocket 管理器
ws_manager = WebSocketManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    init_db()
    ws_manager.cleanup()
    yield
    # 关闭时
    ws_manager.cleanup()


# 创建 FastAPI 应用
app = FastAPI(
    title="GitGuide API",
    description="GitGuide 后端 API",
    version="1.0.0",
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 注册路由
app.include_router(health.router, prefix="/api", tags=["健康检查"])
app.include_router(analyze.router, prefix="/api", tags=["分析"])
app.include_router(chat.router, prefix="/api", tags=["问答"])
app.include_router(repositories.router, prefix="/api", tags=["仓库"])
app.include_router(data.router, prefix="/api", tags=["数据"])


# 依赖注入 - 提供全局 WebSocket 管理器
def get_ws_manager() -> WebSocketManager:
    return ws_manager


# 将 ws_manager 注入到 analyze 模块
from backend.api import analyze as analyze_module
analyze_module.ws_manager = ws_manager


app.dependency_overrides[WebSocketManager] = get_ws_manager


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)