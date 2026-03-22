"""Conversation Manager - 多轮对话管理器

支持源码级别分析的多轮对话上下文管理
"""
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.outputs import ChatGeneration, ChatResult

from .knowledge_builder import KnowledgeBuilder
from .rag_retriever import RAGRetriever


@dataclass
class ConversationTurn:
    user_message: str
    ai_response: str
    timestamp: datetime
    referenced_files: List[str] = field(default_factory=list)
    analyzed_file: Optional[str] = None


@dataclass
class AnalyzedFileContext:
    file_path: str
    first_analyzed: datetime
    last_used: datetime
    summary: str
    key_insights: List[str]


class InMemoryChatHistory(BaseChatMessageHistory):
    def __init__(self):
        self.messages: List[Any] = []

    def add_user_message(self, message: str) -> None:
        self.messages.append(HumanMessage(content=message))

    def add_ai_message(self, message: str) -> None:
        self.messages.append(AIMessage(content=message))

    def add_message(self, message: Any) -> None:
        self.messages.append(message)

    def clear(self) -> None:
        self.messages = []

    @property
    def messages(self) -> List[Any]:
        return self._messages

    @messages.setter
    def messages(self, value: List[Any]):
        self._messages = value


class ConversationManager:
    FILE_PATH_PATTERNS = [
        r'(?: analyze | show me | explain | look at | what is | find )([^"\s]+\.(?:py|js|ts|jsx|tsx|java|go|rs|cpp|c|h|hpp|cs|rb|php|swift|kt|scala))',
        r'["\']([^\"\']+\.(?:py|js|ts|jsx|tsx|java|go|rs|cpp|c|h|hpp|cs|rb|php|swift|kt|scala))["\']',
        r'(?:file|source|code)[^\w]*(?:named|called)?[^\w]*([^\s]+\.(?:py|js|ts|jsx|tsx|java|go|rs|cpp|c|h|hpp|cs|rb|php|swift|kt|scala))',
        r'/([a-zA-Z0-9_/-]+\.(?:py|js|ts|jsx|tsx|java|go|rs|cpp|c|h|hpp|cs|rb|php|swift|kt|scala))',
    ]

    COMMON_ENTRY_POINTS = [
        "main.py", "app.py", "index.py", "server.py", "app.js", "index.js", "main.js",
        "main.ts", "index.ts", "main.java", "Main.java", "main.go", "lib.rs", "main.rs",
    ]

    def __init__(self, knowledge_builder: KnowledgeBuilder, max_history: int = 20):
        self.kb = knowledge_builder
        self.rag_retriever = RAGRetriever(knowledge_builder)
        self.chat_history = InMemoryChatHistory()
        self.conversation_turns: List[ConversationTurn] = []
        self.analyzed_files: Dict[str, AnalyzedFileContext] = {}
        self.max_history = max_history
        self.current_file_path: Optional[str] = None

    def extract_file_path(self, query: str) -> Optional[str]:
        query_lower = query.lower()

        for pattern in self.FILE_PATH_PATTERNS:
            matches = re.findall(pattern, query_lower)
            if matches:
                file_path = matches[0].strip()
                return self._normalize_file_path(file_path)

        for entry_point in self.COMMON_ENTRY_POINTS:
            if entry_point in query_lower:
                return entry_point

        return None

    def _normalize_file_path(self, file_path: str) -> str:
        file_path = file_path.strip()
        if not file_path:
            return file_path

        if file_path.startswith("/"):
            file_path = file_path[1:]

        if not any(file_path.endswith(ext) for ext in [".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rs", ".cpp", ".c", ".h", ".hpp", ".cs", ".rb", ".php", ".swift", ".kt", ".scala"]):
            common_names = [f"{name}.py" for name in ["main", "app", "index", "server", "main"]]

            source_files = self.kb.source_indexer.get_all_files() if self.kb.source_indexer else []

            for common in common_names:
                for sf in source_files:
                    if sf.endswith(common) or sf.endswith(f"/{common}"):
                        return sf

        return file_path

    def _find_best_matching_file(self, file_path: str) -> Optional[str]:
        if not self.kb.source_indexer:
            return None

        all_files = self.kb.source_indexer.get_all_files()

        exact_matches = [f for f in all_files if f == file_path or f.endswith(f"/{file_path}")]
        if exact_matches:
            return exact_matches[0]

        filename = file_path.split("/")[-1]
        name_matches = [f for f in all_files if f.endswith(f"/{filename}") or f == filename]
        if name_matches:
            return name_matches[0]

        partial_matches = [f for f in all_files if filename in f]
        if partial_matches:
            return partial_matches[0]

        return None

    def update_analyzed_file(self, file_path: str, summary: str = "", insights: List[str] = None):
        now = datetime.now()

        if file_path in self.analyzed_files:
            self.analyzed_files[file_path].last_used = now
            if summary:
                self.analyzed_files[file_path].summary = summary
            if insights:
                self.analyzed_files[file_path].key_insights.extend(insights)
        else:
            self.analyzed_files[file_path] = AnalyzedFileContext(
                file_path=file_path,
                first_analyzed=now,
                last_used=now,
                summary=summary,
                key_insights=insights or []
            )

        self.current_file_path = file_path

    def get_context_for_query(self, query: str) -> Tuple[str, Optional[str]]:
        file_path = self.extract_file_path(query)

        if file_path:
            matched_path = self._find_best_matching_file(file_path)
            if matched_path:
                self.current_file_path = matched_path
                file_path = matched_path

            self.update_analyzed_file(file_path)

        if not file_path and self.current_file_path:
            recent_mentions = [f for f in self.analyzed_files.keys()]
            if recent_mentions and "这个文件" in query or "该文件" in query or "它" in query:
                file_path = self.current_file_path

        context = self.rag_retriever.build_context(query, file_path=file_path)

        return context, file_path

    def add_turn(self, user_message: str, ai_response: str, referenced_files: List[str] = None):
        turn = ConversationTurn(
            user_message=user_message,
            ai_response=ai_response,
            timestamp=datetime.now(),
            referenced_files=referenced_files or [],
            analyzed_file=self.current_file_path
        )
        self.conversation_turns.append(turn)

        self.chat_history.add_user_message(user_message)
        self.chat_history.add_ai_message(ai_response)

        if len(self.conversation_turns) > self.max_history:
            self.conversation_turns = self.conversation_turns[-self.max_history:]
            self.chat_history.messages = self.chat_history.messages[-(self.max_history * 2):]

    def get_recent_files(self, limit: int = 5) -> List[str]:
        recent = sorted(
            self.analyzed_files.items(),
            key=lambda x: x[1].last_used,
            reverse=True
        )
        return [f[0] for f in recent[:limit]]

    def build_system_prompt(self) -> str:
        recent_files = self.get_recent_files(3)
        recent_files_str = ", ".join(recent_files) if recent_files else "无"

        return f"""你是一个专业的 GitHub 仓库代码分析助手。

你的能力：
1. 理解项目整体结构和架构
2. 分析和解释代码文件的内容和功能
3. 追踪代码中的函数调用和依赖关系
4. 回答关于代码实现细节的问题

当前仓库信息：
- 已分析的文件: {recent_files_str}
- 当前专注的文件: {self.current_file_path or '无'}

回答要求：
1. 基于提供的代码上下文进行回答
2. 引用具体的文件路径和行号
3. 代码解释要清晰、易懂
4. 如果不确定某事，诚实地说明

当用户询问特定文件时，确保从知识库中检索该文件的完整内容进行分析。"""

    def get_conversation_context(self) -> str:
        if not self.conversation_turns:
            return ""

        context_parts = []
        for i, turn in enumerate(self.conversation_turns[-3:], 1):
            context_parts.append(f"轮次 {i}:")
            context_parts.append(f"用户: {turn.user_message}")
            context_parts.append(f"AI: {turn.ai_response[:200]}..." if len(turn.ai_response) > 200 else f"AI: {turn.ai_response}")
            if turn.analyzed_file:
                context_parts.append(f"分析的文件: {turn.analyzed_file}")

        return "\n".join(context_parts)

    def get_messages_for_llm(self) -> List[Any]:
        messages = [SystemMessage(content=self.build_system_prompt())]

        for msg in self.chat_history.messages[-self.max_history*2:]:
            messages.append(msg)

        return messages

    def clear_history(self):
        self.chat_history.clear()
        self.conversation_turns = []
        self.analyzed_files = {}
        self.current_file_path = None

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_turns": len(self.conversation_turns),
            "analyzed_files_count": len(self.analyzed_files),
            "current_file": self.current_file_path,
            "recent_files": self.get_recent_files(5),
        }
