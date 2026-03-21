"""
Orchestrator - 任务编排器

负责协调仓库分析任务，支持快速模式和详细模式
"""

import asyncio
import uuid
import time
import tempfile
import shutil
from typing import Dict, Optional, Callable, Any
from pathlib import Path
from datetime import datetime

from tools.github_tools import github_tools
from core.config import Config

# 取消检查器
_cancelled_checker = None


def set_cancelled_checker(checker: Callable[[], bool]):
    """设置取消检查器"""
    global _cancelled_checker
    _cancelled_checker = checker


def is_cancelled() -> bool:
    """检查是否已取消"""
    if _cancelled_checker:
        return _cancelled_checker()
    return False


def run_fast(repo_url: str, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
    """
    快速模式：直接生成文档

    参数:
        repo_url: GitHub 仓库 URL
        progress_callback: 进度回调函数

    返回:
        Dict: 包含生成的文档
    """
    # 报告进度
    if progress_callback:
        progress_callback("starting", 5, "开始分析...")

    # 检查取消
    if is_cancelled():
        return {"success": False, "error": "任务已取消"}

    try:
        # 阶段 1: 克隆仓库
        if progress_callback:
            progress_callback("cloning", 15, "正在克隆仓库...")

        repo_path = _clone_repo(repo_url)
        if not repo_path:
            return {"success": False, "error": "无法克隆仓库"}

        if is_cancelled():
            return {"success": False, "error": "任务已取消"}

        # 阶段 2: 获取仓库信息
        if progress_callback:
            progress_callback("getting_info", 25, "正在获取仓库信息...")

        repo_info = _get_repo_info(repo_url)

        if is_cancelled():
            return {"success": False, "error": "任务已取消"}

        # 阶段 3: 生成文档
        if progress_callback:
            progress_callback("generating", 35, "正在生成文档...")

        result = _generate_documents(repo_url, repo_path, progress_callback)

        if is_cancelled():
            return {"success": False, "error": "任务已取消"}

        # 阶段 4: 完成
        if progress_callback:
            progress_callback("completed", 100, "分析完成")

        # 清理临时目录
        _cleanup_repo(repo_path)

        return {
            "success": True,
            "repo_url": repo_url,
            "repo_info": repo_info,
            **result
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


def run_with_progress(repo_url: str, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
    """
    详细模式：带进度回调的完整分析

    参数:
        repo_url: GitHub 仓库 URL
        progress_callback: 进度回调函数

    返回:
        Dict: 包含生成的文档和元数据
    """
    # 报告进度
    if progress_callback:
        progress_callback("starting", 5, "开始分析...")

    # 检查取消
    if is_cancelled():
        return {"success": False, "error": "任务已取消"}

    try:
        # 阶段 1: 克隆仓库
        if progress_callback:
            progress_callback("cloning", 10, "正在克隆仓库...")

        repo_path = _clone_repo(repo_url)
        if not repo_path:
            return {"success": False, "error": "无法克隆仓库"}

        if is_cancelled():
            return {"success": False, "error": "任务已取消"}

        # 阶段 2: 获取仓库信息
        if progress_callback:
            progress_callback("getting_info", 25, "正在获取仓库信息...")

        repo_info = _get_repo_info(repo_url)

        if is_cancelled():
            return {"success": False, "error": "任务已取消"}

        # 阶段 3: 生成文档
        if progress_callback:
            progress_callback("generating", 50, "正在生成文档...")

        result = _generate_documents(repo_url, repo_path, progress_callback)

        if is_cancelled():
            return {"success": False, "error": "任务已取消"}

        # 阶段 4: 完成
        if progress_callback:
            progress_callback("completed", 100, "分析完成")

        # 清理临时目录
        _cleanup_repo(repo_path)

        return {
            "success": True,
            "repo_url": repo_url,
            "repo_info": repo_info,
            **result
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


def _clone_repo(repo_url: str) -> Optional[str]:
    """克隆仓库到临时目录"""
    try:
        from tools.git_tools import git_tools
        result = git_tools.clone_repo(repo_url)
        if isinstance(result, dict) and "error" in result:
            print(f"Clone error: {result['error']}")
            return None
        return result
    except Exception as e:
        print(f"Clone error: {e}")
        return None


def _get_repo_info(repo_url: str) -> Dict[str, Any]:
    """获取仓库信息"""
    try:
        from tools.github_tools import github_tools
        info = github_tools.get_repo_info(repo_url)
        if isinstance(info, dict):
            return info
        elif isinstance(info, str):
            import ast
            try:
                return ast.literal_eval(info)
            except:
                return {}
        return {}
    except Exception:
        return {}


def _generate_documents(repo_url: str, repo_path: str, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
    """使用 Workflow 生成所有文档"""
    try:
        from agents.workflow import Workflow

        workflow = Workflow()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            if progress_callback:
                progress_callback("generating", 55, "正在分析项目结构...")

            result = loop.run_until_complete(workflow.run(repo_url, repo_path, progress_callback))
        except Exception as e:
            print(f"Workflow execution exception: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            loop.close()

        if result.get("success"):
            if progress_callback:
                progress_callback("generating", 95, "文档生成完成，正在整理...")
            return result.get("documents", {})
        else:
            error_msg = result.get("error", "未知错误")
            state_summary = result.get("state", {})
            errors = state_summary.get("errors", [])
            print(f"Workflow returned failure: {error_msg}")
            if errors:
                print(f"Workflow errors: {errors}")
            return _generate_fallback_documents()

    except Exception as e:
        print(f"Document generation error: {e}")
        import traceback
        traceback.print_exc()
        return _generate_fallback_documents()


def _generate_fallback_documents() -> Dict[str, Any]:
    """生成基于模板的降级文档"""
    return {
        "quick_start": "# 快速入门\n\n无法生成文档，请检查仓库是否可访问。",
        "overview": "# 项目概览\n\n无法生成文档，请检查仓库是否可访问。",
        "architecture": "# 架构设计\n\n无法生成文档，请检查仓库是否可访问。",
        "install_guide": "# 安装部署\n\n无法生成文档，请检查仓库是否可访问。",
        "usage_tutorial": "# 使用教程\n\n无法生成文档，请检查仓库是否可访问。",
        "dev_guide": "# 开发指南\n\n无法生成文档，请检查仓库是否可访问。",
        "troubleshooting": "# 故障排查\n\n无法生成文档，请检查仓库是否可访问。"
    }


def _cleanup_repo(repo_path: str):
    """清理临时仓库目录"""
    try:
        import shutil
        if repo_path and os.path.exists(repo_path):
            shutil.rmtree(repo_path)
    except Exception:
        pass