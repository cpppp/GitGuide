"""Analyzer Agent - 仓库分析专家"""
from langchain.agents import create_agent
from langchain_core.tools import tool
from core.config import get_llm
from tools.github_tools import get_repo_info as github_get_repo_info
from tools.git_tools import analyze_structure as git_analyze_structure
from tools.file_tools import detect_project_type as file_detect_project_type


# 定义 Agent 工具列表 (LangChain 1.0+ 风格)
@tool
def get_repo_info_analyzer(repo_url: str) -> str:
    """获取 GitHub 仓库的基本信息"""
    return github_get_repo_info.invoke({"repo_url": repo_url})


@tool
def analyze_structure_analyzer(repo_url: str) -> str:
    """分析仓库的目录结构"""
    return git_analyze_structure.invoke({"repo_url": repo_url})


@tool
def detect_project_type_analyzer(repo_url: str) -> str:
    """检测项目类型"""
    return file_detect_project_type.invoke({"repo_url": repo_url})


analyzer_tools = [get_repo_info_analyzer, analyze_structure_analyzer, detect_project_type_analyzer]

# Analyzer Agent 的系统提示
ANALYZER_SYSTEM_PROMPT = """你是一个仓库分析专家，专门帮助用户理解 GitHub 仓库的结构和内容。

你的职责：
1. 识别项目类型（Node.js, Python, Java, Go, Docker 等）
2. 分析目录结构，了解项目的组织方式
3. 解析依赖关系，找出主要依赖
4. 提取关键信息，包括：
   - 项目描述和用途
   - 主要编程语言
   - 入口文件或主要模块
   - 配置文件

请使用提供的工具来获取仓库信息，然后以结构化的方式返回分析结果。

输出格式要求：
返回结构化的分析结果，包含以下字段：
- project_type: 项目类型
- description: 项目描述
- language: 主要编程语言
- directory_structure: 目录结构（简要）
- key_files: 关键文件列表
- dependencies: 主要依赖（如果可以识别）
- entry_points: 入口点或主要模块
"""


def create_analyzer_agent():
    """创建 Analyzer Agent"""
    llm = get_llm()

    # 使用 create_agent (LangChain 1.2+ API)
    agent = create_agent(
        model=llm,
        tools=analyzer_tools,
        system_prompt=ANALYZER_SYSTEM_PROMPT
    )

    return agent


# 全局 Agent 实例
analyzer_agent = create_analyzer_agent()


def run_analyzer(repo_url: str) -> dict:
    """运行 Analyzer Agent 分析仓库"""
    try:
        result = analyzer_agent.invoke({
            "messages": [{"role": "user", "content": f"分析这个 GitHub 仓库: {repo_url}\n\n请提供完整的项目分析，包括项目类型、目录结构、主要文件和依赖信息。"}]
        })

        # 从 result 中提取 messages
        messages = result.get("messages", [])
        if messages:
            # 获取最后一条消息的内容
            last_message = messages[-1]
            output = last_message.content if hasattr(last_message, 'content') else str(last_message)
        else:
            output = ""

        return {
            "success": True,
            "analysis": output,
            "repo_url": repo_url
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "repo_url": repo_url
        }