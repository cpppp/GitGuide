"""RAG Retriever - 检索增强生成

支持文件级别的精确检索和混合检索
"""
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

try:
    from langchain_core.retrievers import BaseRetriever
    from langchain_core.callbacks import CallbackManagerForRetrieverRun
    CHAIN_AVAILABLE = True
except ImportError:
    CHAIN_AVAILABLE = False

from .source_code_indexer import SourceCodeIndexer, SourceFile
from .knowledge_builder import KnowledgeBuilder


@dataclass
class RetrievalResult:
    content: str
    source: str
    file_path: Optional[str] = None
    score: float = 0.0
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    metadata: Dict[str, Any] = None


class CodeSnippetExtractor:
    @staticmethod
    def extract_function(code: str, function_name: str) -> Optional[str]:
        lines = code.split("\n")
        start_idx = -1
        end_idx = -1

        for i, line in enumerate(lines):
            if f"def {function_name}" in line or f"function {function_name}" in line:
                start_idx = i
                break

        if start_idx == -1:
            return None

        brace_count = 0
        in_function = False
        for i in range(start_idx, len(lines)):
            line = lines[i]
            for char in line:
                if char == "{":
                    brace_count += 1
                    in_function = True
                elif char == "}":
                    brace_count -= 1

            if in_function and brace_count == 0:
                end_idx = i
                break

        if end_idx == -1:
            end_idx = start_idx + 20

        return "\n".join(lines[start_idx:end_idx+1])

    @staticmethod
    def extract_lines(content: str, start_line: int, end_line: int = None) -> str:
        lines = content.split("\n")
        if end_line is None:
            end_line = start_line + 20
        return "\n".join(f"{i+1}: {lines[i]}" for i in range(max(0, start_line-1), min(len(lines), end_line)))

    @staticmethod
    def extract_class(code: str, class_name: str) -> Optional[str]:
        lines = code.split("\n")
        start_idx = -1
        end_idx = -1

        for i, line in enumerate(lines):
            if f"class {class_name}" in line:
                start_idx = i
                break

        if start_idx == -1:
            return None

        brace_count = 0
        in_class = False
        indent = 0
        class_indent = 0

        for i in range(start_idx, len(lines)):
            line = lines[i]
            if start_idx == i:
                class_indent = len(line) - len(line.lstrip())
                in_class = True

            for char in line:
                if char == "{":
                    brace_count += 1
                    in_class = True

            stripped = line.strip()
            if in_class and stripped and not stripped.startswith("#"):
                current_indent = len(line) - len(line.lstrip())
                if current_indent <= class_indent and i > start_idx:
                    end_idx = i - 1
                    break

                if "}" in line:
                    brace_count -= 1
                    if brace_count <= 0:
                        end_idx = i
                        break
        else:
            end_idx = min(start_idx + 50, len(lines) - 1)

        return "\n".join(lines[start_idx:end_idx+1])


class RAGRetriever:
    def __init__(self, knowledge_builder: KnowledgeBuilder):
        self.kb = knowledge_builder
        self.source_indexer = knowledge_builder.source_indexer
        self.vectorstore = knowledge_builder.vectorstore
        self.code_extractor = CodeSnippetExtractor()

    def retrieve_by_file_path(self, file_path: str, max_content_length: int = 8000) -> Optional[RetrievalResult]:
        if not self.source_indexer:
            return None

        source_file = self.source_indexer.get_file_by_path(file_path)
        if not source_file:
            candidates = self.source_indexer.search_files_by_pattern(re.escape(file_path))
            if candidates:
                source_file = candidates[0]

        if not source_file:
            return None

        content = source_file.content
        if len(content) > max_content_length:
            content = content[:max_content_length] + f"\n... (truncated, total {source_file.line_count} lines)"

        return RetrievalResult(
            content=f"# {source_file.relative_path}\n# Language: {source_file.language}\n# Lines: {source_file.line_count}\n\n{content}",
            source="code",
            file_path=source_file.relative_path,
            score=1.0,
            metadata={
                "language": source_file.language,
                "line_count": source_file.line_count,
                "symbols": [{"name": s.name, "type": s.type, "line": s.line_number} for s in source_file.symbols[:10]],
                "imports": source_file.imports[:10],
            }
        )

    def retrieve_code_symbol(self, symbol_name: str, file_path: str = None) -> Optional[RetrievalResult]:
        if not self.source_indexer:
            return None

        if file_path:
            source_file = self.source_indexer.get_file_by_path(file_path)
            if source_file:
                for symbol in source_file.symbols:
                    if symbol.name == symbol_name:
                        code = CodeSnippetExtractor.extract_function(source_file.content, symbol_name)
                        if not code:
                            code = CodeSnippetExtractor.extract_class(source_file.content, symbol_name)
                        if not code:
                            code = CodeSnippetExtractor.extract_lines(
                                source_file.content, symbol.line_number, symbol.end_line
                            )
                        return RetrievalResult(
                            content=code or f"Symbol {symbol_name} at line {symbol.line_number}",
                            source="code",
                            file_path=source_file.relative_path,
                            score=0.9,
                            line_start=symbol.line_number,
                            line_end=symbol.end_line,
                            metadata={"symbol": symbol_name, "type": symbol.type}
                        )

        for relative_path, source_file in self.source_indexer.files.items():
            for symbol in source_file.symbols:
                if symbol.name == symbol_name:
                    code = CodeSnippetExtractor.extract_function(source_file.content, symbol_name)
                    if not code:
                        code = CodeSnippetExtractor.extract_class(source_file.content, symbol_name)
                    return RetrievalResult(
                        content=code or f"Symbol {symbol_name} at line {symbol.line_number}",
                        source="code",
                        file_path=relative_path,
                        score=0.9,
                        line_start=symbol.line_number,
                        line_end=symbol.end_line,
                        metadata={"symbol": symbol_name, "type": symbol.type}
                    )

        return None

    def retrieve_with_mmr(self, query: str, k: int = 5, fetch_k: int = 20, lambda_mult: float = 0.7) -> List[RetrievalResult]:
        if not self.vectorstore:
            return []

        try:
            results = self.vectorstore.max_marginal_relevance_search(
                query, k=k, fetch_k=fetch_k, lambda_mult=lambda_mult
            )

            retrieval_results = []
            for doc in results:
                retrieval_results.append(RetrievalResult(
                    content=doc.page_content,
                    source=doc.metadata.get("source", "unknown"),
                    file_path=doc.metadata.get("file_path"),
                    score=0.0,
                    metadata=doc.metadata
                ))
            return retrieval_results
        except Exception:
            return self.similarity_search(query, k)

    def similarity_search(self, query: str, k: int = 5) -> List[RetrievalResult]:
        if not self.vectorstore:
            return []

        try:
            docs = self.vectorstore.similarity_search(query, k=k)
            retrieval_results = []
            for doc in docs:
                retrieval_results.append(RetrievalResult(
                    content=doc.page_content,
                    source=doc.metadata.get("source", "unknown"),
                    file_path=doc.metadata.get("file_path"),
                    score=0.0,
                    metadata=doc.metadata
                ))
            return retrieval_results
        except Exception:
            return []

    def hybrid_retrieve(self, query: str, file_path: str = None, k: int = 5) -> List[RetrievalResult]:
        results = []

        if file_path:
            file_result = self.retrieve_by_file_path(file_path)
            if file_result:
                results.append(file_result)

            symbol_result = self.retrieve_code_symbol(file_path)
            if symbol_result:
                results.append(symbol_result)

        keyword_results = self._keyword_search(query)
        results.extend(keyword_results)

        vector_results = self.retrieve_with_mmr(query, k=k)
        results.extend(vector_results)

        seen = set()
        unique_results = []
        for r in results:
            key = (r.file_path, r.content[:100])
            if key not in seen:
                seen.add(key)
                unique_results.append(r)

        return unique_results[:k*2]

    def _keyword_search(self, query: str) -> List[RetrievalResult]:
        if not self.source_indexer:
            return []

        results = []
        query_lower = query.lower()

        keywords = re.findall(r'\w+', query_lower)
        keywords = [k for k in keywords if len(k) > 3]

        for relative_path, source_file in self.source_indexer.files.items():
            score = 0
            matched_lines = []

            path_parts = relative_path.lower().split("/")
            for kw in keywords:
                if kw in path_parts:
                    score += 2

            for symbol in source_file.symbols:
                if any(kw in symbol.name.lower() for kw in keywords):
                    score += 1
                    matched_lines.append(f"{symbol.type}: {symbol.name} (line {symbol.line_number})")

            if score > 0:
                preview = source_file.content[:500]
                if matched_lines:
                    preview += "\n\nMatched symbols:\n" + "\n".join(matched_lines[:5])

                results.append(RetrievalResult(
                    content=preview,
                    source="code",
                    file_path=relative_path,
                    score=score,
                    metadata={"matched_symbols": matched_lines[:5]}
                ))

        results.sort(key=lambda x: x.score, reverse=True)
        return results[:5]

    def build_context(self, query: str, file_path: str = None, max_context_length: int = 6000) -> str:
        results = self.hybrid_retrieve(query, file_path=file_path, k=3)

        if not results and file_path:
            direct_result = self.retrieve_by_file_path(file_path)
            if direct_result:
                results = [direct_result]

        context_parts = []
        total_length = 0

        for result in results:
            if total_length + len(result.content) > max_context_length:
                remaining = max_context_length - total_length
                if remaining > 200:
                    context_parts.append(result.content[:remaining] + "\n... (truncated)")
                break

            header = ""
            if result.file_path:
                header = f"\n{'='*60}\n"
                header += f"File: {result.file_path}\n"
                if result.line_start:
                    header += f"Lines: {result.line_start}-{result.line_end or result.line_start}\n"
                header += f"Source: {result.source}\n"
                header += "="*60 + "\n"

            context_parts.append(header + result.content)
            total_length += len(header) + len(result.content)

        return "\n\n".join(context_parts) if context_parts else ""

    def get_referenced_files(self, results: List[RetrievalResult]) -> List[str]:
        files = []
        for result in results:
            if result.file_path and result.file_path not in files:
                files.append(result.file_path)
        return files
