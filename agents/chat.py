"""Chat Agent - 问答专家"""
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from core.config import get_llm
from tools.github_tools import github_tools


def run_chat(query: str, repo_url: str, chat_history: list = None) -> dict:
    """运行 Chat Agent 回答用户问题"""
    try:
        llm = get_llm()
        if not llm:
            return {
                "success": False,
                "error": "LLM not initialized. Please check API configuration.",
                "repo_url": repo_url
            }

        repo_info = github_tools.get_repo_info(repo_url)
        if isinstance(repo_info, dict) and "error" in repo_info:
            repo_info_dict = {"name": "Unknown", "description": "", "language": "Unknown", "readme": ""}
        elif isinstance(repo_info, str):
            import ast
            try:
                repo_info_dict = ast.literal_eval(repo_info)
            except:
                repo_info_dict = {"name": "Unknown", "description": "", "language": "Unknown", "readme": ""}
        else:
            repo_info_dict = repo_info if isinstance(repo_info, dict) else {"name": "Unknown", "description": "", "language": "Unknown", "readme": ""}

        context = f"""项目名称: {repo_info_dict.get('name', 'N/A')}
项目描述: {repo_info_dict.get('description', 'N/A')}
主要语言: {repo_info_dict.get('language', 'N/A')}

README 内容:
{repo_info_dict.get('readme', '无 README')}"""

        system_prompt = """你是一个 GitHub 仓库问答助手，专门帮助用户解答关于项目的问题。

你的职责：
1. 回答用户关于项目结构的问题
2. 解释代码的功能和用途
3. 提供运行和开发建议
4. 解答项目相关的问题

回答要求：
- 简洁明了，易于理解
- 如果不确定某事，请如实说明
- 提供具体的建议和示例"""

        messages = [HumanMessage(content=system_prompt)]

        if chat_history:
            for msg in chat_history:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "user":
                    messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    messages.append(AIMessage(content=content))

        user_message = f"""项目上下文：
{context}

用户问题：{query}

请根据上述项目上下文回答用户的问题。"""

        messages.append(HumanMessage(content=user_message))

        response = llm.invoke(messages)
        output = response.content if hasattr(response, 'content') else str(response)

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
