"""CodePatternAnalyzer - 代码模式识别

负责识别代码模式、分析架构风格
"""

from typing import Dict, List, Any
import os
import re


class CodePatternAnalyzer:
    """代码模式分析器 - 识别代码模式和架构风格"""

    def __init__(self):
        self.name = "CodePatternAnalyzer"
        self.version = "1.0"

    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析代码模式

        参数:
            context: 包含 repo_url、repo_path、language 等信息

        返回:
            Dict: 包含代码模式、架构风格等信息
        """
        repo_url = context.get("repo_url", "")
        repo_path = context.get("repo_path")
        language = context.get("language")

        if not repo_path or not os.path.exists(repo_path):
            return {
                "success": False,
                "error": "仓库路径不存在",
                "repo_url": repo_url
            }

        try:
            # 1. 分析架构风格
            architecture_style = self._analyze_architecture_style(repo_path, language)

            # 2. 识别设计模式
            design_patterns = self._identify_design_patterns(repo_path, language)

            # 3. 分析代码组织
            code_organization = self._analyze_code_organization(repo_path, language)

            # 4. 检测测试覆盖
            test_coverage = self._detect_test_coverage(repo_path, language)

            return {
                "success": True,
                "repo_url": repo_url,
                "architecture_style": architecture_style,
                "design_patterns": design_patterns,
                "code_organization": code_organization,
                "test_coverage": test_coverage
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "repo_url": repo_url
            }

    def _analyze_architecture_style(self, repo_path: str, language: str) -> Dict[str, Any]:
        """分析架构风格"""
        styles = []

        # 检查目录结构
        dirs = set()
        for item in os.listdir(repo_path):
            if os.path.isdir(os.path.join(repo_path, item)):
                dirs.add(item.lower())

        # MVC 风格
        if any(d in dirs for d in ["models", "views", "controllers"]):
            styles.append({
                "pattern": "MVC",
                "description": "Model-View-Controller 架构",
                "confidence": "high"
            })

        # 分层架构
        if "layers" in dirs or any(d in dirs for d in ["services", "repositories", "dtos"]):
            styles.append({
                "pattern": "Layered Architecture",
                "description": "分层架构（Service-Repository-DTO）",
                "confidence": "medium"
            })

        # 微服务架构
        if "docker" in dirs or "kubernetes" in dirs or "docker-compose" in dirs:
            styles.append({
                "pattern": "Microservices",
                "description": "微服务架构",
                "confidence": "high"
            })

        # 插件架构
        if "plugins" in dirs or "extensions" in dirs or "addons" in dirs:
            styles.append({
                "pattern": "Plugin Architecture",
                "description": "插件架构",
                "confidence": "medium"
            })

        # 模块化架构
        if "modules" in dirs or "components" in dirs:
            styles.append({
                "pattern": "Modular",
                "description": "模块化架构",
                "confidence": "medium"
            })

        # 如果没有检测到特定架构，使用通用的
        if not styles:
            styles.append({
                "pattern": "Monolith",
                "description": "单体架构",
                "confidence": "low"
            })

        return {
            "detected_patterns": styles,
            "primary_style": styles[0]["pattern"] if styles else "Unknown"
        }

    def _identify_design_patterns(self, repo_path: str, language: str) -> List[str]:
        """识别设计模式"""
        patterns = []

        # 检查特定文件和目录
        dirs = set()
        for item in os.listdir(repo_path):
            if os.path.isdir(os.path.join(repo_path, item)):
                dirs.add(item.lower())

        # 单例模式
        if "singleton" in dirs:
            patterns.append("Singleton Pattern")

        # 工厂模式
        if "factory" in dirs:
            patterns.append("Factory Pattern")

        # 观察者模式
        if "observer" in dirs or "events" in dirs:
            patterns.append("Observer/Event Pattern")

        # 策略模式
        if "strategy" in dirs:
            patterns.append("Strategy Pattern")

        # 依赖注入
        if "injection" in dirs or "di" in dirs:
            patterns.append("Dependency Injection")

        # 仓储模式
        if "repositories" in dirs or "dao" in dirs:
            patterns.append("Repository/DAO Pattern")

        # 装饰器模式
        if "decorators" in dirs:
            patterns.append("Decorator Pattern")

        # 建造者模式
        if "builders" in dirs:
            patterns.append("Builder Pattern")

        return patterns

    def _analyze_code_organization(self, repo_path: str, language: str) -> Dict[str, Any]:
        """分析代码组织"""
        org = {
            "structure_type": "unknown",
            "has_config_dir": False,
            "has_tests_dir": False,
            "has_docs_dir": False,
            "has_examples_dir": False
        }

        # 检查常见目录目录
        dirs = [d.lower() for d in os.listdir(repo_path) if os.path.isdir(os.path.join(repo_path, d))]

        org["has_config_dir"] = "config" in dirs or "conf" in dirs
        org["has_tests_dir"] = "test" in dirs or "tests" in dirs
        org["has_docs_dir"] = "docs" in dirs or "documentation" in dirs
        org["has_examples_dir"] = "examples" in dirs or "samples" in dirs

        # 判断结构类型
        if "src" in dirs:
            org["structure_type"] = "src-based"
        elif "lib" in dirs or "app" in dirs:
            org["structure_type"] = "lib-based"
        elif "bin" in dirs and "pkg" in dirs:
            org["structure_type"] = "go-style"
        else:
            org["structure_type"] = "flat"

        return org

    def _detect_test_coverage(self, repo_path: str, language: str) -> Dict[str, Any]:
        """检测测试覆盖"""
        coverage = {
            "has_tests": False,
            "test_framework": None,
            "estimated_coverage": "unknown"
        }

        # 查找测试目录
        test_dirs = []
        for item in os.listdir(repo_path):
            if os.path.isdir(os.path.join(repo_path, item)):
                if item.lower() in ["test", "tests", "__tests__"]:
                    test_dirs.append(item)

        if not test_dirs:
            return coverage

        coverage["has_tests"] = True

        # 检测测试框架
        for test_dir in test_dirs:
            test_path = os.path.join(repo_path, test_dir)

            # Python 测试框架
            if language == "Python":
                for file in os.listdir(test_path):
                    if file.endswith(".py"):
                        file_path = os.path.join(test_path, file)
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                content = f.read()
                                if "unittest" in content or "pytest" in content:
                                    coverage["test_framework"] = file
                                    break
                        except:
                            pass

            # JavaScript/TypeScript 测试框架
            elif language in ["JavaScript", "TypeScript"]:
                if os.path.exists(os.path.join(test_path, "jest.config.js")):
                    coverage["test_framework"] = "Jest"
                elif os.path.exists(os.path.join(test_path, "vitest.config.js")):
                    coverage["test_framework"] = "Vitest"
                elif os.path.exists(os.path.join(test_path, "mocha.config.js")):
                    coverage["test_framework"] = "Mocha"

        return coverage


# 全局实例
code_pattern_analyzer = CodePatternAnalyzer()
