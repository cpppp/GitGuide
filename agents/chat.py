"""Chat Agent - 问答专家"""
""" 旧架构, 待整体更新后删去 """
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
from core.config import get_llm
from tools.github_tools import get_repo_info as github_get_repo_info, get_file_content as github_get_file_content


# Chat Agent 的工具
@tool
def get_repo_info_chat(repo_url: str) -> str:
    """获取 GitHub 仓库的基本信息"""
    return github_get_repo_info.invoke({"repo_url": repo_url})


@tool
def get_file_content_chat(repo_url: str, file_path: str) -> str:
    """获取项目文件的内容"""
    return github_get_file_content.invoke({"repo_url": repo_url, "file_path": file_path})


chat_tools = [get_repo_info_chat, get_file_content_chat]

# Chat Agent 的系统提示
CHAT_SYSTEM_PROMPT = """你是一个 GitHub 仓库问答助手，专门帮助用户解答关于项目的问题。

你的职责：
1. 回答用户关于项目结构的问题
2. 解释代码的功能和用途
3. 提供运行和开发建议
4. 解答项目相关的问题

你可以使用的工具：
- get_repo_info: 获取仓库基本信息
- get_file_content: 获取项目文件内容

上下文信息：
- 项目的 README 内容
- 项目的分析结果
- 项目的基本信息（名称、描述、语言等）

请根据提供的上下文信息回答用户的问题。如果需要查看特定文件的内容，请使用工具来获取。

回答要求：
- 简洁明了，易于理解
- 如果不确定某事，请如实说明
- 提供具体的建议和示例
"""


def create_chat_agent():
    """创建 Chat Agent"""
    llm = get_llm()

    # 使用 create_agent (LangChain 1.2+ API)
    agent = create_agent(
        model=llm,
        tools=chat_tools,
        system_prompt=CHAT_SYSTEM_PROMPT
    )

    return agent


# 全局 Agent 实例
chat_agent = create_chat_agent()


def run_chat(query: str, repo_url: str, chat_history: list = None) -> dict:
    """运行 Chat Agent 回答用户问题"""
    try:
        # 获取仓库上下文
        repo_info = github_get_repo_info.invoke({"repo_url": repo_url})

        # 解析 repo_info
        if isinstance(repo_info, str):
            import ast
            try:
                repo_info_dict = ast.literal_eval(repo_info)
            except:
                repo_info_dict = {"name": "Unknown", "description": "", "language": "Unknown", "readme": ""}
        else:
            repo_info_dict = repo_info if isinstance(repo_info, dict) else {"name": "Unknown", "description": "", "language": "Unknown", "readme": ""}

        context = f"""
项目名称: {repo_info_dict.get('name', 'N/A')}
项目描述: {repo_info_dict.get('description', 'N/A')}
主要语言: {repo_info_dict.get('language', 'N/A')}

README 内容:
{repo_info_dict.get('readme', '无 README')}
"""

        # 构建用户消息
        input_text = f"""项目上下文：
{context}

用户问题：{query}

请根据上述项目上下文回答用户的问题。如果需要查看具体文件，请说明需要查看什么文件。"""

        # 准备输入
        input_dict = {"messages": [{"role": "user", "content": input_text}]}

        # 如果有历史消息，添加到 messages
        if chat_history:
            messages = []
            for msg in chat_history:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "user":
                    messages.append({"role": "user", "content": content})
                elif role == "assistant":
                    messages.append({"role": "assistant", "content": content})
            input_dict["messages"] = messages + [{"role": "user", "content": input_text}]

        # 调用 Agent
        result = chat_agent.invoke(input_dict)

        # 从 result 中提取 output
        messages = result.get("messages", [])
        if messages:
            last_message = messages[-1]
            output = last_message.content if hasattr(last_message, 'content') else str(last_message)
        else:
            output = ""

        return {
            "success": True,
            "response": output,
            "repo_url": repo_url
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "repo_url": repo_url
        }