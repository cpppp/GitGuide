"""Knowledge Builder - 知识库构建器

构建仓库知识库，支持文档和源码的向量存储
"""
import os
import json
import hashlib
from typing import Dict, List, Optional, Any
from pathlib import Path

try:
    from langchain_community.vectorstores import Chroma
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.schema import Document
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

try:
    from langchain_huggingface import HuggingFaceEmbeddings
    HF_AVAILABLE = True
except ImportError:
    try:
        from langchain.embeddings import HuggingFaceEmbeddings
        HF_AVAILABLE = True
    except ImportError:
        HF_AVAILABLE = False

from .source_code_indexer import SourceCodeIndexer


EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DEVICE = "cpu"
EMBEDDING_BATCH_SIZE = 32


class KnowledgeBuilder:
    def __init__(self, repo_url: str, persist_directory: str = None):
        self.repo_url = repo_url
        self.repo_id = self._generate_repo_id(repo_url)

        if persist_directory is None:
            persist_directory = os.path.join(os.getcwd(), "data", "knowledge_base", self.repo_id)

        self.persist_directory = persist_directory
        self.source_indexer: Optional[SourceCodeIndexer] = None
        self.vectorstore = None
        self.embeddings = None
        self._initialized = False

    def _generate_repo_id(self, repo_url: str) -> str:
        return hashlib.md5(repo_url.encode()).hexdigest()

    def _get_embeddings(self):
        if not CHROMA_AVAILABLE:
            return None

        if self.embeddings is None:
            if HF_AVAILABLE:
                self.embeddings = HuggingFaceEmbeddings(
                    model_name=EMBEDDING_MODEL,
                    model_kwargs={"device": EMBEDDING_DEVICE},
                    encode_kwargs={"batch_size": EMBEDDING_BATCH_SIZE, "normalize_embeddings": True}
                )
        return self.embeddings

    def initialize(self, repo_path: str, analysis_result: Dict[str, Any] = None):
        if self._initialized:
            return

        self.source_indexer = SourceCodeIndexer(repo_path)
        self.source_indexer.index_directory()

        if CHROMA_AVAILABLE and self._get_embeddings():
            self._build_vectorstore(analysis_result)

        self._initialized = True

    def _build_vectorstore(self, analysis_result: Dict[str, Any] = None):
        documents = []

        if self.source_indexer:
            for relative_path, source_file in self.source_indexer.files.items():
                chunks = self._split_code_chunks(source_file)
                for i, chunk in enumerate(chunks):
                    metadata = {
                        "source": "code",
                        "file_path": relative_path,
                        "language": source_file.language,
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                    }
                    documents.append(Document(page_content=chunk, metadata=metadata))

        if analysis_result:
            doc_content = self._extract_docs_from_analysis(analysis_result)
            if doc_content:
                doc_chunks = self._split_text_chunks(doc_content)
                for i, chunk in enumerate(doc_chunks):
                    metadata = {
                        "source": "document",
                        "chunk_index": i,
                    }
                    documents.append(Document(page_content=chunk, metadata=metadata))

        if documents and self._get_embeddings():
            os.makedirs(self.persist_directory, exist_ok=True)

            self.vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self._get_embeddings(),
                persist_directory=self.persist_directory,
                collection_name=f"repo_{self.repo_id}"
            )
            self.vectorstore.persist()

    def _split_code_chunks(self, source_file, max_chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        content = source_file.content
        lines = content.split("\n")

        chunks = []
        current_chunk = []
        current_size = 0

        header = f"# File: {source_file.relative_path}\n# Language: {source_file.language}\n\n"
        header_size = len(header.split("\n"))

        for i, line in enumerate(lines):
            line_with_num = f"{i+1}: {line}"
            line_size = len(line_with_num)

            if current_size + line_size > max_chunk_size and current_chunk:
                chunks.append("\n".join(current_chunk))
                overlap_lines = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                current_chunk = overlap_lines + [line_with_num]
                current_size = sum(len(l) for l in current_chunk)
            else:
                current_chunk.append(line_with_num)
                current_size += line_size

        if current_chunk:
            chunks.append("\n".join(current_chunk))

        if not chunks and content:
            chunks = [header + content[:max_chunk_size]]

        return [header + chunk if not chunk.startswith(header.split("\n")[0]) else chunk for chunk in chunks]

    def _split_text_chunks(self, text: str, max_chunk_size: int = 2000, overlap: int = 200) -> List[str]:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=max_chunk_size,
            chunk_overlap=overlap,
            separators=["\n\n", "\n", ". ", " "]
        )
        return text_splitter.split_text(text)

    def _extract_docs_from_analysis(self, analysis_result: Dict[str, Any]) -> str:
        parts = []

        if isinstance(analysis_result, dict):
            if "readme" in analysis_result:
                parts.append(f"# README\n{analysis_result['readme']}")

            for doc_type in ["quick_start", "overview", "architecture", "install_guide",
                            "usage_tutorial", "dev_guide", "troubleshooting"]:
                if doc_type in analysis_result and analysis_result[doc_type]:
                    parts.append(f"# {doc_type.replace('_', ' ').title()}\n{analysis_result[doc_type]}")

            if "structure" in analysis_result:
                parts.append(f"# Project Structure\n{json.dumps(analysis_result['structure'], indent=2)}")

        return "\n\n".join(parts)

    def get_vectorstore(self):
        if not self._initialized:
            return None
        return self.vectorstore

    def get_source_indexer(self) -> Optional[SourceCodeIndexer]:
        if not self._initialized:
            return None
        return self.source_indexer

    def is_ready(self) -> bool:
        return self._initialized

    def get_stats(self) -> Dict:
        stats = {
            "repo_id": self.repo_id,
            "repo_url": self.repo_url,
            "initialized": self._initialized,
            "vectorstore_ready": self.vectorstore is not None,
        }

        if self.source_indexer:
            stats["source_files"] = len(self.source_indexer.files)
            stats["source_summary"] = self.source_indexer.get_summary()

        return stats

    @classmethod
    def load_existing(cls, repo_url: str, persist_directory: str = None) -> Optional["KnowledgeBuilder"]:
        kb = cls(repo_url, persist_directory)

        if persist_directory is None:
            persist_directory = kb.persist_directory

        if os.path.exists(persist_directory) and CHROMA_AVAILABLE:
            embeddings = kb._get_embeddings()
            if embeddings:
                kb.vectorstore = Chroma(
                    persist_directory=persist_directory,
                    embedding_function=embeddings,
                    collection_name=f"repo_{kb.repo_id}"
                )
                kb._initialized = True
                return kb

        return None

    def clear(self):
        if self.vectorstore:
            self.vectorstore.delete_collection()

        if os.path.exists(self.persist_directory):
            import shutil
            shutil.rmtree(self.persist_directory, ignore_errors=True)

        self._initialized = False
