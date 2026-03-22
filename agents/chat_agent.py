"""Chat Agent - 问答专家（V3.2 增强版）

支持源码级别分析的 RAG 问答系统
"""
import os
import json
import tempfile
from typing import Dict, List, Optional, Any
from pathlib import Path

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from core.config import get_llm
from tools.github_tools import github_tools
from tools.git_tools import git_tools

from agents.chat.knowledge_builder import KnowledgeBuilder
from agents.chat.rag_retriever import RAGRetriever
from agents.chat.conversation_manager import ConversationManager


_git_repo_cache: Dict[str, str] = {}


def _get_repo_path(repo_url: str) -> Optional[str]:
    if repo_url in _git_repo_cache:
        return _git_repo_cache[repo_url]

    temp_dir = tempfile.mkdtemp()
    try:
        import git
        git.Repo.clone_from(repo_url, temp_dir, depth=1)
        _git_repo_cache[repo_url] = temp_dir
        return temp_dir
    except Exception:
        return None


def _cleanup_repo_path(repo_url: str):
    if repo_url in _git_repo_cache:
        path = _git_repo_cache.pop(repo_url)
        try:
            import shutil
            shutil.rmtree(path, ignore_errors=True)
        except Exception:
            pass


class ChatSession:
    def __init__(self, repo_url: str, repo_path: str = None, analysis_result: Dict[str, Any] = None):
        self.repo_url = repo_url
        self.repo_path = repo_path
        self.analysis_result = analysis_result
        self.knowledge_builder: Optional[KnowledgeBuilder] = None
        self.conversation_manager: Optional[ConversationManager] = None
        self._initialized = False

    def initialize(self):
        if self._initialized:
            return

        if not self.repo_path:
            self.repo_path = _get_repo_path(self.repo_url)

        if not self.repo_path:
            return

        self.knowledge_builder = KnowledgeBuilder(self.repo_url)
        self.knowledge_builder.initialize(self.repo_path, self.analysis_result)

        self.conversation_manager = ConversationManager(self.knowledge_builder)

        self._initialized = True

    def is_ready(self) -> bool:
        return self._initialized and self.knowledge_builder is not None

    def chat(self, query: str, chat_history: List[Dict] = None) -> Dict[str, Any]:
        if not self.is_ready():
            return {
                "success": False,
                "error": "Chat session not initialized",
                "response": "",
                "referenced_files": []
            }

        try:
            llm = get_llm()
            if not llm:
                return {
                    "success": False,
                    "error": "LLM not configured",
                    "response": "",
                    "referenced_files": []
                }

            if chat_history:
                for msg in chat_history:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    if role == "user":
                        self.conversation_manager.chat_history.add_user_message(content)
                    elif role == "assistant":
                        self.conversation_manager.chat_history.add_ai_message(content)

            context, analyzed_file = self.conversation_manager.get_context_for_query(query)

            repo_info = self._get_repo_basic_info()

            system_prompt = self.conversation_manager.build_system_prompt()

            messages = [SystemMessage(content=system_prompt)]

            for msg in self.conversation_manager.chat_history.messages[-10:]:
                messages.append(msg)

            rag_context = self._build_rag_context(query, analyzed_file)

            user_message = f"""仓库信息：
{repo_info}

代码上下文：
{rag_context}

用户问题：{query}

请根据上述代码上下文和仓库信息回答用户的问题。如果涉及到具体文件，请引用文件名和行号。"""

            messages.append(HumanMessage(content=user_message))

            response = llm.invoke(messages)
            output = response.content if hasattr(response, 'content') else str(response)

            retrieval_results = self.conversation_manager.rag_retriever.hybrid_retrieve(query, file_path=analyzed_file, k=3)
            referenced_files = self.conversation_manager.rag_retriever.get_referenced_files(retrieval_results)

            if analyzed_file and analyzed_file not in referenced_files:
                referenced_files.insert(0, analyzed_file)

            self.conversation_manager.add_turn(query, output, referenced_files)

            return {
                "success": True,
                "response": output,
                "referenced_files": referenced_files,
                "analyzed_file": analyzed_file,
                "repo_url": self.repo_url
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": "",
                "referenced_files": []
            }

    def _get_repo_basic_info(self) -> str:
        info = f"仓库URL: {self.repo_url}\n"

        if self.analysis_result:
            if isinstance(self.analysis_result, dict):
                info += f"项目名称: {self.analysis_result.get('name', 'N/A')}\n"
                info += f"项目描述: {self.analysis_result.get('description', 'N/A')}\n"
                info += f"主要语言: {self.analysis_result.get('language', 'N/A')}\n"

                if 'readme' in self.analysis_result:
                    info += f"\nREADME:\n{self.analysis_result['readme'][:1000]}..."
        else:
            try:
                repo_info = github_tools.get_repo_info(self.repo_url)
                if isinstance(repo_info, dict):
                    info += f"项目名称: {repo_info.get('name', 'N/A')}\n"
                    info += f"项目描述: {repo_info.get('description', 'N/A')}\n"
                    info += f"主要语言: {repo_info.get('language', 'N/A')}\n"
            except Exception:
                pass

        if self.knowledge_builder and self.knowledge_builder.source_indexer:
            summary = self.knowledge_builder.source_indexer.get_summary()
            info += f"\n源码统计: {summary.get('total_files', 0)} 个文件\n"
            lang_stats = summary.get('language_stats', {})
            if lang_stats:
                langs = [f"{lang}({stats['file_count']}个)" for lang, stats in list(lang_stats.items())[:5]]
                info += f"语言分布: {', '.join(langs)}\n"

        return info

    def _build_rag_context(self, query: str, file_path: str = None) -> str:
        if not self.conversation_manager:
            return "无可用上下文"

        context = self.conversation_manager.rag_retriever.build_context(query, file_path=file_path, max_context_length=5000)

        if not context:
            context = "代码上下文未找到，请基于仓库基本信息回答。"

        return context

    def clear(self):
        if self.conversation_manager:
            self.conversation_manager.clear_history()
        _cleanup_repo_path(self.repo_url)


_chat_sessions: Dict[str, ChatSession] = {}


def get_chat_session(repo_url: str, repo_path: str = None, analysis_result: Dict[str, Any] = None) -> ChatSession:
    cache_key = repo_url

    if cache_key not in _chat_sessions:
        _chat_sessions[cache_key] = ChatSession(repo_url, repo_path, analysis_result)
        _chat_sessions[cache_key].initialize()

    return _chat_sessions[cache_key]


def clear_chat_session(repo_url: str):
    if repo_url in _chat_sessions:
        _chat_sessions[repo_url].clear()
        del _chat_sessions[repo_url]


def run_chat(query: str, repo_url: str, chat_history: List[Dict] = None, file_path: str = None) -> Dict[str, Any]:
    """运行 Chat Agent 回答用户问题（支持源码级别分析）"""
    try:
        query_with_file = query
        if file_path:
            query_with_file = f"{query} (分析文件: {file_path})"

        session = get_chat_session(repo_url)

        if not session.is_ready():
            return _run_basic_chat(query, repo_url, chat_history)

        result = session.chat(query_with_file, chat_history)

        return result

    except Exception as e:
        return _run_basic_chat(query, repo_url, chat_history)


def _run_basic_chat(query: str, repo_url: str, chat_history: List[Dict] = None) -> Dict[str, Any]:
    """基础聊天（无RAG降级方案）"""
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

        messages = [SystemMessage(content=system_prompt)]

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
            "repo_url": repo_url,
            "referenced_files": []
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "repo_url": repo_url
        }


def build_knowledge_base(repo_url: str, repo_path: str = None, analysis_result: Dict[str, Any] = None) -> Dict[str, Any]:
    """为仓库构建知识库"""
    try:
        session = get_chat_session(repo_url, repo_path, analysis_result)

        if not session.is_ready():
            return {
                "success": False,
                "error": "Failed to initialize chat session"
            }

        stats = session.knowledge_builder.get_stats()

        return {
            "success": True,
            "stats": stats,
            "repo_url": repo_url
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
