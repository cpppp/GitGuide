"""
异步任务模块 - 使用 Redis + RQ 实现后台任务处理
"""
import os
import sys
import json
import time
from typing import Dict, Any

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from redis import Redis
from rq import Queue, get_current_job
from rq.job import Job


def create_queue() -> Queue:
    """创建 Redis 队列连接"""
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    return Queue("gitguide", connection=Redis.from_url(redis_url))


def analyze_repo_async(repo_url: str) -> str:
    """
    异步分析仓库的入口函数

    参数:
        repo_url: GitHub 仓库 URL

    返回:
        任务 ID (job.id)
    """
    queue = create_queue()
    job = queue.enqueue(
        "backend.worker.run_analysis",
        repo_url,
        job_timeout=300,  # 5分钟超时
        result_ttl=3600,  # 结果保留1小时
        on_failure=on_task_failure,
        on_success=on_task_success
    )
    return job.id


def get_task_status(job_id: str) -> Dict[str, Any]:
    """
    获取任务状态

    参数:
        job_id: 任务 ID

    返回:
        状态字典 {status, progress, result, error}
    """
    queue = create_queue()
    job = Job.fetch(job_id, connection=queue.connection)

    result = {
        "status": job.get_status(),
        "progress": job.meta.get("progress", 0),
        "progress_message": job.meta.get("progress_message", ""),
        "result": None,
        "error": None
    }

    if job.is_finished:
        try:
            result["result"] = job.result
        except:
            result["result"] = None
    elif job.is_failed:
        result["error"] = job.exc_info

    return result


def cancel_task(job_id: str) -> bool:
    """取消任务"""
    queue = create_queue()
    job = Job.fetch(job_id, connection=queue.connection)
    if job.is_queued:
        job.cancel()
        return True
    return False


def on_task_failure(job, exc_type, exc_value, traceback):
    """任务失败回调"""
    job.meta["error"] = str(exc_value)
    job.save_meta()


def on_task_success(job, result, connection, result_ttl):
    """任务成功回调"""
    # 任务完成后自动清理
    pass