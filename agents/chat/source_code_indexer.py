"""Source Code Indexer - 源码索引构建器

扫描仓库源码，构建文件级别的索引，支持按路径精确检索
"""
import os
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


LANGUAGE_EXTENSIONS = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".java": "java",
    ".go": "go",
    ".rs": "rust",
    ".cpp": "cpp",
    ".c": "c",
    ".h": "c",
    ".hpp": "cpp",
    ".cs": "csharp",
    ".rb": "ruby",
    ".php": "php",
    ".swift": "swift",
    ".kt": "kotlin",
    ".scala": "scala",
}

IGNORE_DIRS = {
    ".git", "__pycache__", "node_modules", "venv", ".venv",
    "dist", "build", ".venv", "env", ".env",
    ".idea", ".vscode", ".vscode",
    "coverage", ".nyc_output", ".pytest_cache",
    "bower_components", "vendor", "target",
}

IGNORE_PATTERNS = {
    "*.pyc", "*.pyo", "*.so", "*.dll", "*.dylib",
    "*.exe", "*.bin", "*.o", "*.a",
    ".DS_Store", "Thumbs.db",
    "package-lock.json", "yarn.lock", "poetry.lock",
    "*.min.js", "*.min.css",
}

MAX_FILE_SIZE = 100 * 1024


@dataclass
class CodeSymbol:
    name: str
    type: str
    line_number: int
    end_line: int
    signature: str


@dataclass
class SourceFile:
    file_path: str
    relative_path: str
    content: str
    language: str
    symbols: List[CodeSymbol]
    imports: List[str]
    exports: List[str]
    line_count: int


class SourceCodeIndexer:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.files: Dict[str, SourceFile] = {}
        self._symbol_patterns = self._build_symbol_patterns()

    def _build_symbol_patterns(self) -> Dict[str, List[Tuple[str, str]]]:
        return {
            "python": [
                (r"^class\s+(\w+)", "class"),
                (r"^def\s+(\w+)\s*\(", "function"),
                (r"^async\s+def\s+(\w+)\s*\(", "function"),
                (r"^(\w+)\s*=\s*(?:class|type)\s*", "class"),
            ],
            "javascript": [
                (r"(?:export|export\s+default)\s+(?:class|const|function|async\s+function)\s+(\w+)", "export"),
                (r"(?:class|function|const|let|var)\s+(\w+)\s*[=({]", "declaration"),
            ],
            "typescript": [
                (r"(?:export|export\s+default)\s+(?:class|interface|type|const|function|async\s+function)\s+(\w+)", "export"),
                (r"(?:class|interface|type)\s+(\w+)", "declaration"),
            ],
            "java": [
                (r"(?:public|private|protected)?\s*(?:static)?\s*(?:class|interface|enum)\s+(\w+)", "class"),
                (r"(?:public|private|protected)?\s*(?:static)?\s*(?:final)?\s*(?:void|int|String|List|Map|Boolean)\s+(\w+)\s*\(", "method"),
            ],
            "go": [
                (r"^func\s+(\w+)\s*\(", "function"),
                (r"^type\s+(\w+)\s+struct", "struct"),
                (r"^type\s+(\w+)\s+interface", "interface"),
            ],
            "rust": [
                (r"^(?:pub\s+)?(?:fn|async\s+fn)\s+(\w+)\s*", "function"),
                (r"^(?:pub\s+)?struct\s+(\w+)", "struct"),
                (r"^(?:pub\s+)?enum\s+(\w+)", "enum"),
            ],
            "cpp": [
                (r"^(?:public|private|protected)?\s*(?:class|struct|enum)\s+(\w+)", "class"),
                (r"^(?:inline\s+)?(?:const\s+)?(?:void|int|float|double|string|auto)\s+(\w+)\s*\(", "function"),
            ],
        }

    def _should_ignore_dir(self, dirname: str) -> bool:
        return dirname in IGNORE_DIRS or dirname.startswith(".")

    def _should_ignore_file(self, filename: str) -> bool:
        for pattern in IGNORE_PATTERNS:
            if "*" in pattern:
                if filename.endswith(pattern.replace("*", "")):
                    return True
        return False

    def _get_language(self, file_path: str) -> Optional[str]:
        _, ext = os.path.splitext(file_path)
        return LANGUAGE_EXTENSIONS.get(ext.lower())

    def _extract_imports(self, content: str, language: str) -> List[str]:
        imports = []
        if language == "python":
            import_patterns = [
                r"^import\s+(\w+)",
                r"^from\s+(\w+)\s+import",
            ]
            for pattern in import_patterns:
                matches = re.findall(pattern, content, re.MULTILINE)
                imports.extend(matches)
        elif language in ("javascript", "typescript"):
            import_patterns = [
                r"import\s+.*\s+from\s+['\"]([^'\"]+)['\"]",
                r"require\s*\(['\"]([^'\"]+)['\"]\)",
            ]
            for pattern in import_patterns:
                matches = re.findall(pattern, content)
                imports.extend(matches)
        elif language == "java":
            import_patterns = [r"^package\s+([\w.]+);"]
            for pattern in import_patterns:
                matches = re.findall(pattern, content, re.MULTILINE)
                imports.extend(matches)
        elif language == "go":
            import_patterns = [r"\"([^\"]+)\""]
            for pattern in import_patterns:
                matches = re.findall(pattern, content)
                imports.extend(matches)
        return list(set(imports))

    def _extract_exports(self, content: str, language: str) -> List[str]:
        exports = []
        if language == "python":
            exports = re.findall(r"^__all__\s*=\s*\[(.*?)\]", content, re.MULTILINE | re.DOTALL)
            if exports:
                exports = [e.strip().replace("'", "").replace('"', "") for e in exports[0].split(",")]
        elif language in ("javascript", "typescript"):
            export_patterns = [
                r"export\s+(?:default\s+)?(?:class|function|const|interface|type)\s+(\w+)",
                r"module\.exports\s*=\s*(\w+)",
            ]
            for pattern in export_patterns:
                matches = re.findall(pattern, content)
                exports.extend(matches)
        return list(set(exports))

    def _extract_symbols(self, content: str, language: str) -> List[CodeSymbol]:
        symbols = []
        patterns = self._symbol_patterns.get(language, [])

        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            for pattern, symbol_type in patterns:
                match = re.search(pattern, line)
                if match:
                    name = match.group(1) if match.groups() else "unknown"
                    end_line = i
                    if symbol_type in ("class", "function", "struct"):
                        brace_count = 0
                        started = False
                        for j in range(i - 1, min(len(lines), i + 100)):
                            for ch in lines[j]:
                                if ch == "{":
                                    brace_count += 1
                                    started = True
                                elif ch == "}":
                                    brace_count -= 1
                            if started and brace_count == 0:
                                end_line = j + 1
                                break
                    symbols.append(CodeSymbol(
                        name=name,
                        type=symbol_type,
                        line_number=i,
                        end_line=end_line,
                        signature=line.strip()
                    ))
                    break
        return symbols

    def index_file(self, file_path: str, relative_path: str) -> Optional[SourceFile]:
        try:
            if not os.path.exists(file_path):
                return None

            file_size = os.path.getsize(file_path)
            if file_size > MAX_FILE_SIZE:
                return None

            language = self._get_language(file_path)
            if not language:
                return None

            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            imports = self._extract_imports(content, language)
            exports = self._extract_exports(content, language)
            symbols = self._extract_symbols(content, language)

            return SourceFile(
                file_path=file_path,
                relative_path=relative_path,
                content=content,
                language=language,
                symbols=symbols,
                imports=imports,
                exports=exports,
                line_count=len(content.split("\n"))
            )
        except Exception as e:
            return None

    def index_directory(self, max_depth: int = 5) -> Dict[str, SourceFile]:
        self.files = {}

        def walk_directory(current_path: str, relative_path: str, depth: int):
            if depth > max_depth:
                return

            try:
                for item in os.listdir(current_path):
                    if self._should_ignore_dir(item):
                        continue

                    item_path = os.path.join(current_path, item)
                    item_relative = os.path.join(relative_path, item) if relative_path else item

                    if os.path.isdir(item_path):
                        walk_directory(item_path, item_relative, depth + 1)
                    elif os.path.isfile(item_path):
                        if self._should_ignore_file(item):
                            continue

                        source_file = self.index_file(item_path, item_relative)
                        if source_file:
                            self.files[item_relative] = source_file
            except PermissionError:
                pass
            except Exception:
                pass

        walk_directory(self.repo_path, "", 0)
        return self.files

    def get_file_by_path(self, file_path: str) -> Optional[SourceFile]:
        for relative_path, source_file in self.files.items():
            if relative_path.endswith(file_path) or relative_path == file_path:
                return source_file
            if file_path in relative_path.split("/")[-1]:
                if relative_path.endswith(file_path):
                    return source_file
        return None

    def search_files_by_pattern(self, pattern: str) -> List[SourceFile]:
        results = []
        regex = re.compile(pattern, re.IGNORECASE)
        for source_file in self.files.values():
            if regex.search(source_file.relative_path):
                results.append(source_file)
        return results

    def get_code_context(self, file_path: str, start_line: int = 1, context_lines: int = 5) -> str:
        source_file = self.get_file_by_path(file_path)
        if not source_file:
            return ""

        lines = source_file.content.split("\n")
        start = max(0, start_line - 1)
        end = min(len(lines), start_line + context_lines)

        return "\n".join(f"{i+1}: {line}" for i, line in enumerate(lines[start:end]))

    def get_all_files(self) -> List[str]:
        return list(self.files.keys())

    def get_summary(self) -> Dict:
        language_stats = {}
        for source_file in self.files.values():
            lang = source_file.language
            if lang not in language_stats:
                language_stats[lang] = {"file_count": 0, "total_lines": 0}
            language_stats[lang]["file_count"] += 1
            language_stats[lang]["total_lines"] += source_file.line_count

        return {
            "total_files": len(self.files),
            "language_stats": language_stats,
            "files": list(self.files.keys())[:20]
        }
