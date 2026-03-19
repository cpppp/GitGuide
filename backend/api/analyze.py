"""
分析 API
"""
import uuid
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Optional

from backend.models.schemas import (
    AnalyzeRequest, AnalyzeResponse, TaskStatus, HistoryItem, FavoriteItem
)
from backend.websocket.manager import WebSocketManager, task_store
from core.validators import validate_github_url

router = APIRouter()

# 模块级别的 WebSocket 管理器（由 main.py 注入）
ws_manager: WebSocketManager = None

# 依赖：获取 WebSocket 管理器
# 注意：这里使用简单的依赖注入方式


@router.post("/analyze", response_model=AnalyzeResponse)
async def start_analyze(request: AnalyzeRequest):
    """
    启动仓库分析
    """
    # 验证 URL
    validation = validate_github_url(request.repo_url)
    if not validation["valid"]:
        raise ValueError(validation["message"])

    # 生成任务 ID
    job_id = str(uuid.uuid4())

    # 创建任务
    task_store.create_task(job_id, request.repo_url, request.mode.value)

    # 异步执行分析（不阻塞）
    asyncio.create_task(run_analysis_async(job_id, request.repo_url, request.mode.value))

    return AnalyzeResponse(job_id=job_id, status="pending")


@router.get("/analyze/{job_id}/status", response_model=TaskStatus)
async def get_status(job_id: str):
    """获取任务状态"""
    task = task_store.get_task(job_id)
    if not task:
        return TaskStatus(
            job_id=job_id,
            status="not_found",
            error="任务不存在"
        )

    return TaskStatus(
        job_id=task["job_id"],
        status=task["status"],
        progress=task["progress"],
        progress_message=task["progress_message"],
        result=task.get("result"),
        error=task.get("error"),
        cancelled=task.get("cancelled", False)
    )


@router.post("/analyze/{job_id}/cancel")
async def cancel_analysis(job_id: str):
    """取消分析"""
    task = task_store.get_task(job_id)
    if not task:
        return {"success": False, "error": "任务不存在"}

    # 设置取消标志
    task_store.set_cancel_flag(job_id)
    task_store.set_cancelled(job_id)

    return {"success": True, "message": "取消成功"}


@router.websocket("/ws/analyze/{job_id}")
async def websocket_analyze(websocket: WebSocket, job_id: str):
    """WebSocket 实时进度推送"""
    await ws_manager.connect(websocket, job_id)

    try:
        # 发送初始状态
        task = task_store.get_task(job_id)
        if task:
            await websocket.send_json({
                "type": "status",
                "status": task["status"],
                "progress": task["progress"],
                "message": task["progress_message"]
            })

        # 保持连接，等待进度更新
        while True:
            data = await websocket.receive_text()
            # 可以处理客户端发送的消息（如心跳）
            if data == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, job_id)
    except Exception as e:
        ws_manager.disconnect(websocket, job_id)


@router.get("/history")
async def get_history():
    """获取历史记录"""
    from core.history import get_history
    history = get_history()
    return [HistoryItem(**item) for item in history]


@router.post("/history/clear")
async def clear_history():
    """清除历史记录"""
    from core.history import clear_history
    clear_history()
    return {"success": True}


@router.get("/favorites")
async def get_favorites():
    """获取收藏列表"""
    from core.favorites import get_favorites
    favorites = get_favorites()
    return [FavoriteItem(**item) for item in favorites]


@router.post("/favorites")
async def add_favorite(repo_url: str):
    """添加收藏"""
    from core.favorites import add_favorite as add_fav
    from tools.github_tools import get_repo_info

    repo_info = get_repo_info(repo_url)
    if isinstance(repo_info, dict) and "error" not in repo_info:
        add_fav(repo_url, repo_info)
        return {"success": True}
    return {"success": False, "error": "无法获取仓库信息"}


@router.delete("/favorites")
async def remove_favorite(repo_url: str):
    """移除收藏"""
    from core.favorites import remove_favorite
    remove_favorite(repo_url)
    return {"success": True}


# 异步分析任务
async def run_analysis_async(job_id: str, repo_url: str, mode: str):
    """异步执行分析任务"""
    # 使用模块级别的 ws_manager（由 main.py 注入）
    global ws_manager
    if ws_manager is None:
        ws_manager = WebSocketManager()

    try:
        # 设置取消检查器
        from agents.orchestrator import set_cancelled_checker
        set_cancelled_checker(lambda: task_store.is_cancelled(job_id))

        # 定义进度回调（使用 asyncio 确保在事件循环中执行）
        async def progress_callback(stage_key: str, progress: int, message: str):
            task_store.update_progress(job_id, stage_key, progress, message)
            await ws_manager.send_progress(job_id, stage_key, progress, message)

        # 阶段 1: 验证仓库
        task_store.update_progress(job_id, "validating", 10, "正在验证仓库...")
        await ws_manager.send_progress(job_id, "validating", 10, "正在验证仓库...")

        if task_store.is_cancelled(job_id):
            await ws_manager.send_cancelled(job_id)
            return

        await asyncio.sleep(0.5)

        # 阶段 2: 获取仓库信息
        task_store.update_progress(job_id, "getting_repo_info", 25, "正在获取仓库信息...")
        await ws_manager.send_progress(job_id, "getting_repo_info", 25, "正在获取仓库信息...")

        if task_store.is_cancelled(job_id):
            await ws_manager.send_cancelled(job_id)
            return

        # 调用 agents
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

        from agents.orchestrator import run_fast, run_with_progress

        if mode == "fast":
            # 发送开始分析的消息
            task_store.update_progress(job_id, "generating_learning_doc", 50, "正在生成学习文档...")
            await ws_manager.send_progress(job_id, "generating_learning_doc", 50, "正在生成学习文档...")

            # 使用同步包装器来调用 run_fast，因为 run_fast 内部已有 time.sleep
            # 需要在后台线程中运行以免阻塞事件循环
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, run_fast, repo_url)

            # 发送后续进度
            task_store.update_progress(job_id, "generating_setup_guide", 85, "正在生成启动指南...")
            await ws_manager.send_progress(job_id, "generating_setup_guide", 85, "正在生成启动指南...")

            task_store.update_progress(job_id, "finalizing", 95, "正在整理结果...")
            await ws_manager.send_progress(job_id, "finalizing", 95, "正在整理结果...")
        else:
            # 详细模式
            task_store.update_progress(job_id, "analyzing_structure", 40, "正在分析目录结构...")
            await ws_manager.send_progress(job_id, "analyzing_structure", 40, "正在分析目录结构...")

            if task_store.is_cancelled(job_id):
                await ws_manager.send_cancelled(job_id)
                return

            await asyncio.sleep(0.5)

            task_store.update_progress(job_id, "generating_learning_doc", 50, "正在生成学习文档...")
            await ws_manager.send_progress(job_id, "generating_learning_doc", 50, "正在生成学习文档...")

            if task_store.is_cancelled(job_id):
                await ws_manager.send_cancelled(job_id)
                return

            # 定义进度回调函数（更新任务状态，依赖前端轮询获取进度）
            def progress_callback(stage_key, progress_value, message):
                task_store.update_progress(job_id, stage_key, progress_value, message)

            # 调用详细分析
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, run_with_progress, repo_url, progress_callback)

        # 检查取消
        if task_store.is_cancelled(job_id):
            await ws_manager.send_cancelled(job_id)
            return

        if result.get("success"):
            # 阶段 3: 整理结果
            task_store.update_progress(job_id, "finalizing", 95, "正在整理结果...")
            await ws_manager.send_progress(job_id, "finalizing", 95, "正在整理结果...")

            # 保存结果
            task_store.set_result(job_id, {
                "repo_url": result["repo_url"],
                "learning_doc": result.get("learning_doc", ""),
                "setup_guide": result.get("setup_guide", ""),
                "repo_info": result.get("repo_info", {})
            })

            # 发送完成
            await ws_manager.send_progress(job_id, "completed", 100, "分析完成！")
            await ws_manager.send_result(job_id, result)

            # 添加到历史记录
            from core.history import add_history
            add_history(repo_url, result.get("repo_info", {}))
        else:
            error = result.get("error", "未知错误")
            task_store.set_error(job_id, error)
            await ws_manager.send_error(job_id, error)

    except Exception as e:
        error_msg = str(e)
        task_store.set_error(job_id, error_msg)
        await ws_manager.send_error(job_id, error_msg)