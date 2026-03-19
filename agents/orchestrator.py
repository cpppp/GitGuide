"""Orchestrator Agent - 工作流协调器"""
from typing import Dict, Any, Callable, Optional
from agents.analyzer import run_analyzer
from agents.doc_generator import run_docgen, run_docgen_fast


def run(repo_url: str) -> Dict[str, Any]:
    """
    运行 Orchestrator 协调整个工作流程

    工作流程：
    1. 调用 Analyzer Agent 分析仓库
    2. 调用 DocGen Agent 生成文档
    3. 返回完整结果
    """
    result = {
        "repo_url": repo_url,
        "analysis": None,
        "learning_doc": None,
        "setup_guide": None,
        "repo_info": None,
        "success": True,
        "error": None
    }

    try:
        # 步骤 1: 分析仓库
        analysis_result = run_analyzer(repo_url)

        if not analysis_result.get("success"):
            result["success"] = False
            result["error"] = f"仓库分析失败: {analysis_result.get('error')}"
            return result

        result["analysis"] = analysis_result.get("analysis", "")

        # 步骤 2: 生成文档
        doc_result = run_docgen(repo_url, result["analysis"])

        if not doc_result.get("success"):
            result["success"] = False
            result["error"] = f"文档生成失败: {doc_result.get('error')}"
            return result

        result["learning_doc"] = doc_result.get("learning_doc", "")
        result["setup_guide"] = doc_result.get("setup_guide", "")
        result["repo_info"] = doc_result.get("repo_info", {})

        return result

    except Exception as e:
        result["success"] = False
        result["error"] = f"工作流执行失败: {str(e)}"
        return result


def run_with_progress(repo_url: str, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
    """
    带进度回调的 Orchestrator 协调整个工作流程

    工作流程：
    1. 调用 Analyzer Agent 分析仓库 (进度 25% -> 45%)
    2. 调用 DocGen Agent 生成文档 (进度 65% -> 85%)
    3. 返回完整结果

    参数:
        repo_url: GitHub 仓库 URL
        progress_callback: 进度回调函数，签名为 callback(stage_key, progress_value, message)
    """
    result = {
        "repo_url": repo_url,
        "analysis": None,
        "learning_doc": None,
        "setup_guide": None,
        "repo_info": None,
        "success": True,
        "error": None
    }

    def progress(stage_key, progress_value, message):
        if progress_callback:
            progress_callback(stage_key, progress_value, message)

    try:
        # 步骤 1: 分析仓库 (进度 25% -> 45%)
        progress("getting_repo_info", 25, "正在获取仓库信息...")

        analysis_result = run_analyzer(repo_url)

        if not analysis_result.get("success"):
            result["success"] = False
            result["error"] = f"仓库分析失败: {analysis_result.get('error')}"
            return result

        result["analysis"] = analysis_result.get("analysis", "")

        # 更新进度：分析目录结构
        progress("analyzing_structure", 45, "正在分析目录结构...")

        # 步骤 2: 生成文档 (进度 65% -> 85%)
        progress("generating_learning_doc", 65, "正在生成学习文档...")

        doc_result = run_docgen(repo_url, result["analysis"])

        if not doc_result.get("success"):
            result["success"] = False
            result["error"] = f"文档生成失败: {doc_result.get('error')}"
            return result

        result["learning_doc"] = doc_result.get("learning_doc", "")
        result["setup_guide"] = doc_result.get("setup_guide", "")
        result["repo_info"] = doc_result.get("repo_info", {})

        # 更新进度：生成启动指南
        progress("generating_setup_guide", 85, "正在生成启动指南...")

        # 更新进度：整理结果
        progress("finalizing", 95, "正在整理结果...")

        # 完成
        progress("completed", 100, "分析完成！")

        return result

    except Exception as e:
        result["success"] = False
        result["error"] = f"工作流执行失败: {str(e)}"
        return result


def run_simple(repo_url: str) -> Dict[str, Any]:
    """
    简化版本的 Orchestrator
    直接调用 DocGen 生成文档，跳过详细分析
    """
    from tools.github_tools import get_repo_info

    result = {
        "repo_url": repo_url,
        "learning_doc": "",
        "setup_guide": "",
        "repo_info": None,
        "success": True,
        "error": None
    }

    try:
        # 获取仓库信息
        repo_info = get_repo_info(repo_url)

        if isinstance(repo_info, dict) and "error" in repo_info:
            result["success"] = False
            result["error"] = repo_info["error"]
            return result

        result["repo_info"] = repo_info

        # 生成文档（使用快速模式）
        doc_result = run_docgen_fast(repo_url, repo_info)

        if not doc_result.get("success"):
            result["success"] = False
            result["error"] = doc_result.get("error")
            return result

        result["learning_doc"] = doc_result.get("learning_doc", "")
        result["setup_guide"] = doc_result.get("setup_guide", "")

        return result

    except Exception as e:
        result["success"] = False
        result["error"] = str(e)
        return result


def run_fast(repo_url: str) -> Dict[str, Any]:
    """
    快速版本的 Orchestrator
    跳过 Analyzer，直接使用快速文档生成
    适用于需要快速获取结果的场景
    """
    result = {
        "repo_url": repo_url,
        "analysis": None,
        "learning_doc": None,
        "setup_guide": None,
        "repo_info": None,
        "success": True,
        "error": None
    }

    try:
        # 直接使用快速文档生成
        doc_result = run_docgen_fast(repo_url)

        if not doc_result.get("success"):
            result["success"] = False
            result["error"] = f"文档生成失败: {doc_result.get('error')}"
            return result

        result["learning_doc"] = doc_result.get("learning_doc", "")
        result["setup_guide"] = doc_result.get("setup_guide", "")
        result["repo_info"] = doc_result.get("repo_info", {})

        return result

    except Exception as e:
        result["success"] = False
        result["error"] = f"工作流执行失败: {str(e)}"
        return result