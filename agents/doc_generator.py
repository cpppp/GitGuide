"""DocGen Agent - 文档生成专家"""
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from core.config import get_llm
from tools.github_tools import get_repo_info as github_get_repo_info


# DocGen Agent 的工具
@tool
def get_repo_info_docgen(repo_url: str) -> str:
    """获取 GitHub 仓库的基本信息"""
    return github_get_repo_info.invoke({"repo_url": repo_url})


docgen_tools = [get_repo_info_docgen]

# DocGen Agent 的系统提示（简化版）
DOCGEN_SYSTEM_PROMPT = """你是一个文档生成专家，专门帮助用户生成学习文档和启动指南。

请根据提供的仓库信息，生成简洁的学习文档和启动指南。

重要提示：
1. 启动指南只需要包含：环境要求、安装步骤、运行命令
2. 学习文档包含：项目概述、技术栈、目录结构、核心模块

请直接生成内容，不要询问问题。格式如下：

## 学习文档
### 项目概述
[项目描述]

### 技术栈
- 主要语言：[语言]
- 其他技术：[技术]

### 目录结构
[简要目录结构]

### 核心模块
[主要模块]

## 启动指南
### 环境要求
- [要求]

### 安装步骤
1. [步骤]

### 运行项目
```bash
[命令]
```
"""


def create_docgen_agent():
    """创建 DocGen Agent"""
    llm = get_llm()

    # 使用 create_agent (LangChain 1.2+ API)
    agent = create_agent(
        model=llm,
        tools=docgen_tools,
        system_prompt=DOCGEN_SYSTEM_PROMPT
    )

    return agent


# 全局 Agent 实例
docgen_agent = create_docgen_agent()


def run_docgen_fast(repo_url: str, repo_info: dict = None) -> dict:
    """
    快速版本的文档生成 - 直接使用 LLM，不通过 Agent
    这种方式更快，适合简单场景
    """
    llm = get_llm()

    # 获取仓库信息
    if repo_info is None:
        repo_info_str = github_get_repo_info.invoke({"repo_url": repo_url})
        import ast
        try:
            repo_info = ast.literal_eval(repo_info_str) if isinstance(repo_info_str, str) else repo_info_str
        except:
            repo_info = {}

    readme = repo_info.get("readme", "")[:2000] if repo_info else ""  # 限制 README 长度

    prompt = f"""请根据以下仓库信息生成学习文档和启动指南：

仓库名称: {repo_url.split('/')[-1]}
描述: {repo_info.get('description', '无')}
语言: {repo_info.get('language', '未知')}
Stars: {repo_info.get('stargazers_count', 0)}

README:
{readme}

请按以下格式生成：

## 学习文档
### 项目概述
[简短描述项目]

### 技术栈
- 主要语言: {repo_info.get('language', '未知')}

### 目录结构
[简要说明]

### 核心模块
[主要模块]

## 启动指南
### 环境要求
- [环境要求]

### 安装步骤
1. [安装步骤]

### 运行项目
```bash
[运行命令]
```
"""

    try:
        # 直接调用 LLM
        response = llm.invoke([HumanMessage(content=prompt)])
        output = response.content if hasattr(response, 'content') else str(response)

        # 解析输出
        learning_doc = output
        setup_guide = output

        if "## 启动指南" in output:
            parts = output.split("## 启动指南")
            if len(parts) >= 2:
                learning_doc = parts[0].strip()
                if parts[1]:
                    setup_guide = "## 启动指南\n" + parts[1].strip()

        return {
            "success": True,
            "learning_doc": learning_doc,
            "setup_guide": setup_guide,
            "repo_info": repo_info,
            "repo_url": repo_url
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "repo_url": repo_url
        }


def run_docgen(repo_url: str, analysis_result: str = None) -> dict:
    """运行 DocGen Agent 生成文档"""
    try:
        # 首先获取仓库基本信息
        repo_info = github_get_repo_info.invoke({"repo_url": repo_url})

        # 解析 repo_info
        if isinstance(repo_info, str):
            # 从字符串中提取信息
            import ast
            try:
                repo_info_dict = ast.literal_eval(repo_info)
            except:
                repo_info_dict = {"name": "Unknown", "description": "", "language": "Unknown", "stargazers_count": 0, "readme": ""}
        else:
            repo_info_dict = repo_info if isinstance(repo_info, dict) else {"name": "Unknown", "description": "", "language": "Unknown", "stargazers_count": 0, "readme": ""}

        # 准备输入信息
        input_text = f"""
仓库 URL: {repo_url}

仓库信息：
- 名称: {repo_info_dict.get('name', 'N/A')}
- 描述: {repo_info_dict.get('description', 'N/A')}
- 语言: {repo_info_dict.get('language', 'N/A')}
- Star 数: {repo_info_dict.get('stargazers_count', 0)}

README 内容:
{repo_info_dict.get('readme', '无 README')}

仓库分析结果:
{analysis_result or '请自行分析仓库结构'}
"""

        # 调用 Agent 生成文档
        result = docgen_agent.invoke({
            "messages": [{"role": "user", "content": input_text}]
        })

        # 从 result 中提取 output
        messages = result.get("messages", [])
        if messages:
            last_message = messages[-1]
            output = last_message.content if hasattr(last_message, 'content') else str(last_message)
        else:
            output = ""

        # 尝试解析输出，提取学习文档和启动指南
        learning_doc = output
        setup_guide = output

        # 简单的解析逻辑
        if "## 学习文档" in output:
            parts = output.split("## 启动指南")
            if len(parts) >= 2:
                learning_doc = parts[0].replace("## 学习文档", "").strip()
                setup_guide = parts[1].strip()

        return {
            "success": True,
            "learning_doc": learning_doc,
            "setup_guide": setup_guide,
            "repo_info": repo_info_dict,
            "repo_url": repo_url
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "repo_url": repo_url
        }