"""DocGen Agent - 文档生成专家"""
from langchain.agents import create_agent
from langchain_core.tools import tool
from core.config import get_llm
from tools.github_tools import get_repo_info as github_get_repo_info


# DocGen Agent 的工具
@tool
def get_repo_info_docgen(repo_url: str) -> str:
    """获取 GitHub 仓库的基本信息"""
    return github_get_repo_info.invoke({"repo_url": repo_url})


docgen_tools = [get_repo_info_docgen]

# DocGen Agent 的系统提示
DOCGEN_SYSTEM_PROMPT = """你是一个文档生成专家，专门帮助用户生成学习文档和启动指南。

你的职责：
1. 根据仓库分析结果生成学习文档
2. 生成详细的启动指南，包括环境准备、安装步骤、运行命令
3. 提取项目的关键信息并组织成易读的格式

输入信息包括：
- 仓库基本信息（名称、描述、语言、star 数）
- README 内容（如果有）
- 目录结构分析
- 项目类型和依赖

输出格式要求：
请生成以下内容：

## 学习文档 (learning_doc)
### 项目概述
[项目名称] 是一个 [项目描述]

### 技术栈
- 主要语言：[语言]
- 依赖管理：[包管理器]
- 其他技术：[其他相关技术]

### 目录结构
[简要说明目录结构]

### 核心模块
[列出主要模块及其作用]

## 启动指南 (setup_guide)
### 环境要求
- [环境要求 1]
- [环境要求 2]

### 安装步骤
1. [步骤 1]
2. [步骤 2]
3. [步骤 3]

### 运行命令
```bash
[运行命令]
```

### 常见问题
[列出可能的常见问题及解决方案]

请确保内容准确、实用，适合初学者阅读。
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