"""
WebSocket 管理器
"""
import asyncio
import json
from typing import Dict, Set, Callable, Optional
from fastapi import WebSocket


class WebSocketManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.progress_callbacks: Dict[str, Callable] = {}

    async def connect(self, websocket: WebSocket, job_id: str):
        """连接 WebSocket"""
        await websocket.accept()
        if job_id not in self.active_connections:
            self.active_connections[job_id] = set()
        self.active_connections[job_id].add(websocket)

    def disconnect(self, websocket: WebSocket, job_id: str):
        """断开 WebSocket"""
        if job_id in self.active_connections:
            self.active_connections[job_id].discard(websocket)
            if not self.active_connections[job_id]:
                del self.active_connections[job_id]

    async def send_progress(self, job_id: str, stage_key: str, progress: int, message: str):
        """发送进度更新"""
        if job_id not in self.active_connections:
            return

        data = {
            "type": "progress",
            "stage_key": stage_key,
            "progress": progress,
            "message": message
        }

        # 复制连接集合，避免迭代时修改
        connections = list(self.active_connections.get(job_id, set()))
        for connection in connections:
            try:
                await connection.send_json(data)
            except Exception:
                # 连接断开，移除
                self.disconnect(connection, job_id)

    async def send_result(self, job_id: str, result: dict):
        """发送结果"""
        if job_id not in self.active_connections:
            return

        data = {
            "type": "result",
            "result": result
        }

        connections = list(self.active_connections.get(job_id, set()))
        for connection in connections:
            try:
                await connection.send_json(data)
            except Exception:
                self.disconnect(connection, job_id)

    async def send_error(self, job_id: str, error: str):
        """发送错误"""
        if job_id not in self.active_connections:
            return

        data = {
            "type": "error",
            "error": error
        }

        connections = list(self.active_connections.get(job_id, set()))
        for connection in connections:
            try:
                await connection.send_json(data)
            except Exception:
                self.disconnect(connection, job_id)

    async def send_cancelled(self, job_id: str):
        """发送取消确认"""
        if job_id not in self.active_connections:
            return

        data = {
            "type": "cancelled"
        }

        connections = list(self.active_connections.get(job_id, set()))
        for connection in connections:
            try:
                await connection.send_json(data)
            except Exception:
                self.disconnect(connection, job_id)

    def cleanup(self):
        """清理所有连接"""
        self.active_connections.clear()
        self.progress_callbacks.clear()


# 任务状态存储（内存）
class TaskStore:
    """任务状态存储"""

    def __init__(self):
        self.tasks: Dict[str, dict] = {}

    def create_task(self, job_id: str, repo_url: str):
        """创建任务"""
        self.tasks[job_id] = {
            "job_id": job_id,
            "repo_url": repo_url,
            "status": "pending",
            "progress": 0,
            "progress_message": "",
            "stage_key": "",
            "result": None,
            "error": None,
            "cancelled": False
        }

    def update_progress(self, job_id: str, stage_key: str, progress: int, message: str):
        """更新进度"""
        if job_id in self.tasks:
            self.tasks[job_id]["progress"] = progress
            self.tasks[job_id]["progress_message"] = message
            self.tasks[job_id]["stage_key"] = stage_key
            self.tasks[job_id]["status"] = "running"

    def set_result(self, job_id: str, result: dict):
        """设置结果"""
        if job_id in self.tasks:
            self.tasks[job_id]["result"] = result
            self.tasks[job_id]["status"] = "completed"
            self.tasks[job_id]["progress"] = 100

    def set_error(self, job_id: str, error: str):
        """设置错误"""
        if job_id in self.tasks:
            self.tasks[job_id]["error"] = error
            self.tasks[job_id]["status"] = "failed"

    def set_cancelled(self, job_id: str):
        """设置取消"""
        if job_id in self.tasks:
            self.tasks[job_id]["cancelled"] = True
            self.tasks[job_id]["status"] = "cancelled"

    def get_task(self, job_id: str) -> Optional[dict]:
        """获取任务"""
        return self.tasks.get(job_id)

    def set_cancel_flag(self, job_id: str):
        """设置取消标志"""
        if job_id in self.tasks:
            self.tasks[job_id]["cancel_requested"] = True

    def is_cancelled(self, job_id: str) -> bool:
        """检查是否取消"""
        task = self.tasks.get(job_id)
        if task:
            return task.get("cancel_requested", False)
        return False


# 全局任务存储
task_store = TaskStore()