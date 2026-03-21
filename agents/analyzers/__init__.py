"""Analyzers - 项目分析器团队

V3.0 支持4种分析器
"""

from .type_analyzer import TypeAnalyzer
from .structure_analyzer import StructureAnalyzer
from .dependency_analyzer import DependencyAnalyzer
from .code_pattern_analyzer import CodePatternAnalyzer

# 创建全局实例
type_analyzer = TypeAnalyzer()
structure_analyzer = StructureAnalyzer()
dependency_analyzer = DependencyAnalyzer()
code_pattern_analyzer = CodePatternAnalyzer()

__all__ = [
    "type_analyzer",
    "structure_analyzer",
    "dependency_analyzer",
    "code_pattern_analyzer",
    "TypeAnalyzer",
    "StructureAnalyzer",
    "DependencyAnalyzer",
    "CodePatternAnalyzer"
]
