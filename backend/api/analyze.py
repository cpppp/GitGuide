"""
分析 API
"""
import uuid
import asyncio
import json
import os
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Optional

from backend.models.schemas import (
    AnalyzeRequest, AnalyzeResponse, TaskStatus, HistoryItem, FavoriteItem
)
from backend.websocket.manager import WebSocketManager, task_store
from backend.database.config import SessionLocal, get_db
from backend.database.crud import FavoriteCRUD
from core.validators import validate_github_url

router = APIRouter()

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
async def get_favorites(db = Depends(get_db)):
    """获取收藏列表"""
    favorites = FavoriteCRUD.get_all_with_repo(db)
    return [FavoriteItem(
        url=fav["url"],
        name=fav["name"] or "",
        description=fav["description"] or "",
        language=fav["language"] or "",
        stargazers_count=fav["stars"] or 0,
        added_at=fav["created_at"] or ""
    ) for fav in favorites]


@router.post("/favorites")
async def add_favorite(repo_url: str, db = Depends(get_db)):
    """添加收藏"""
    from tools.github_tools import get_repo_info
    
    repo_info = get_repo_info(repo_url)
    if isinstance(repo_info, dict) and "error" not in repo_info:
        FavoriteCRUD.add_by_url(db, repo_url, repo_info)
        return {"success": True}
    return {"success": False, "error": "无法获取仓库信息"}


@router.delete("/favorites")
async def remove_favorite(repo_url: str, db = Depends(get_db)):
    """移除收藏"""
    FavoriteCRUD.remove_by_url(db, repo_url)
    return {"success": True}


# 异步分析任务
async def run_analysis_async(job_id: str, repo_url: str, mode: str):
    """异步执行分析任务"""
    # 使用模块级别的 ws_manager（由 main.py 注入）
    global ws_manager
    if ws_manager is None:
        ws_manager = WebSocketManager()

    # 任务超时设置（秒）- 防止任务永久卡住
    TASK_TIMEOUT = 600  # 10分钟

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
            # 定义进度回调函数（线程安全版本）
            def fast_progress_callback(stage_key, progress_value, message):
                task_store.update_progress(job_id, stage_key, progress_value, message)
                print(f"[PROGRESS] {stage_key}: {progress_value}% - {message}")
                # 注意：WebSocket 发送只在主线程进行，这里只更新 TaskStore

            # 使用 run_fast 带进度回调
            loop = asyncio.get_event_loop()
            try:
                result = await asyncio.wait_for(
                    loop.run_in_executor(None, run_fast, repo_url, fast_progress_callback),
                    timeout=TASK_TIMEOUT
                )
            except asyncio.TimeoutError:
                result = {"success": False, "error": f"任务超时（{TASK_TIMEOUT}秒），请重试或使用更小的仓库"}

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

            # 定义进度回调函数（线程安全版本）
            def progress_callback(stage_key, progress_value, message):
                task_store.update_progress(job_id, stage_key, progress_value, message)
                print(f"[PROGRESS] {stage_key}: {progress_value}% - {message}")
                # 注意：WebSocket 发送只在主线程进行，这里只更新 TaskStore

            # 调用详细分析
            loop = asyncio.get_event_loop()
            try:
                result = await asyncio.wait_for(
                    loop.run_in_executor(None, run_with_progress, repo_url, progress_callback),
                    timeout=TASK_TIMEOUT
                )
            except asyncio.TimeoutError:
                result = {"success": False, "error": f"任务超时（{TASK_TIMEOUT}秒），请重试或使用更小的仓库"}

        # 检查取消
        if task_store.is_cancelled(job_id):
            await ws_manager.send_cancelled(job_id)
            return

        if result.get("success"):
            # 阶段 3: 整理结果
            task_store.update_progress(job_id, "finalizing", 95, "正在整理结果...")
            await ws_manager.send_progress(job_id, "finalizing", 95, "正在整理结果...")

            # 构建结果对象（统一发送给 TaskStore、WebSocket 和前端）
            result_data = {
                "repo_url": result["repo_url"],
                # V3.0 文档（兼容旧字段）
                "quick_start": result.get("quick_start", result.get("learning_doc", "")),
                "overview": result.get("overview", ""),
                "architecture": result.get("architecture", ""),
                "install_guide": result.get("install_guide", result.get("setup_guide", "")),
                # V3.1 新文档
                "usage_tutorial": result.get("usage_tutorial", ""),
                "dev_guide": result.get("dev_guide", ""),
                "troubleshooting": result.get("troubleshooting", ""),
                # V3.1 代码图谱数据
                "code_graph": result.get("code_graph", {}),
                "examples": result.get("examples", []),
                # 旧字段（兼容）
                "learning_doc": result.get("learning_doc", ""),
                "setup_guide": result.get("setup_guide", ""),
                "repo_info": result.get("repo_info", {})
            }

            # 保存结果到 TaskStore（统一的数据结构）
            task_store.set_result(job_id, result_data)

            # 保存到数据库 - 支持7种文档
            from backend.database.config import SessionLocal
            from backend.database.crud import RepositoryCRUD
            db = SessionLocal()
            try:
                repo_info = result.get("repo_info", {})
                existing_repo = RepositoryCRUD.get_by_url(db, repo_url)

                repo_data = {
                    "url": repo_url,
                    "name": repo_info.get("name") or repo_info.get("full_name", ""),
                    "description": repo_info.get("description", ""),
                    "language": repo_info.get("language", ""),
                    "stars": repo_info.get("stargazers_count", 0) or repo_info.get("stars", 0),
                    # V3.0 文档
                    "quick_start": result.get("quick_start", ""),
                    "overview_doc": result.get("overview", ""),
                    "architecture_doc": result.get("architecture", ""),
                    "install_guide": result.get("install_guide", ""),
                    # V3.1 新文档
                    "usage_tutorial": result.get("usage_tutorial", ""),
                    "dev_guide": result.get("dev_guide", ""),
                    "troubleshooting": result.get("troubleshooting", ""),
                    # V3.1 代码图谱数据
                    "code_graph": json.dumps(result.get("code_graph", {}), ensure_ascii=False),
                    "examples": json.dumps(result.get("examples", []), ensure_ascii=False),
                    # 旧字段（兼容）
                    "learning_doc": result.get("learning_doc", ""),
                    "setup_guide": result.get("setup_guide", ""),
                    "analysis_result": str(result.get("repo_info", {}))
                }

                if existing_repo:
                    RepositoryCRUD.update(db, repo_url, repo_data)
                else:
                    RepositoryCRUD.create(db, repo_data)
            finally:
                db.close()

            # 发送完成
            await ws_manager.send_progress(job_id, "completed", 100, "分析完成！")
            await ws_manager.send_result(job_id, result_data)

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

@router.get("/analyze/{job_id}/code-graph")
async def get_code_graph(job_id: str):
    """
    获取代码图谱 - V3.1 从存储的结果中获取
    """
    task = task_store.get_task(job_id)
    if not task or task.get("status") != "completed":
        return {"error": "Job not found or not completed"}
    
    result = task.get("result", {})
    
    # V3.1: 优先使用存储的代码图谱数据
    code_graph = result.get("code_graph", {})
    examples = result.get("examples", [])
    
    if code_graph:
        code_graph["examples"] = examples
        return code_graph
    
    # 降级：如果存储数据不存在，尝试从仓库路径获取
    repo_path = result.get("repo_path")
    if repo_path and os.path.exists(repo_path):
        from backend.services.code_graph import CodeGraphService
        graph = CodeGraphService.analyze_structure(repo_path)
        graph["examples"] = CodeGraphService.extract_examples(repo_path)
        return graph
    
    return {"error": "Code graph data not available", "tree": {}, "stats": {}, "dependencies": {}}