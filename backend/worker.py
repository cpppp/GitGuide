"""
RQ Worker - 后台任务执行器

使用方式:
    python -m rq worker gitguide

或启动 worker 服务:
    rq worker gitguide --with-scheduler
"""
import os
import sys

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def update_progress(job, progress: int, message: str):
    """更新任务进度"""
    job.meta["progress"] = progress
    job.meta["progress_message"] = message
    job.save_meta()


def run_analysis(repo_url: str):
    """
    执行仓库分析任务

    此函数会在 RQ worker 进程中执行，不阻塞主应用
    """
    from rq import get_current_job
    from agents.orchestrator import run_with_progress

    job = get_current_job()

    # 初始化进度
    update_progress(job, 10, "正在验证仓库...")

    # 定义进度回调
    def progress_callback(stage_key: str, progress_value: int, message: str):
        update_progress(job, progress_value, message)

    try:
        # 执行分析
        result = run_with_progress(repo_url, progress_callback=progress_callback)

        # 更新进度到完成
        update_progress(job, 100, "分析完成")

        return result

    except Exception as e:
        # 记录错误
        job.meta["error"] = str(e)
        job.save_meta()
        raise


def test_connection():
    """测试 Redis 连接"""
    from redis import Redis
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    r = Redis.from_url(redis_url)
    r.ping()
    return True


if __name__ == "__main__":
    # 测试连接
    if test_connection():
        print("Redis 连接成功!")
    else:
        print("Redis 连接失败!")