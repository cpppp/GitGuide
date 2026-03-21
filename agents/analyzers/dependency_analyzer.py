"""DependencyAnalyzer - 依赖关系分析

负责分析依赖关系、检查版本兼容性
"""

from typing import Dict, List, Any
import os
import json


class DependencyAnalyzer:
    """依赖分析器 - 分析项目依赖关系"""

    def __init__(self):
        self.name = "DependencyAnalyzer"
        self.version = "1.0"

    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析依赖关系

        参数:
            context: 包含 repo_url、repo_path、language 等信息

        返回:
            Dict: 包含依赖列表、版本信息、兼容性检查等
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
            # 1. 解析依赖
            dependencies = self._parse_dependencies(repo_path, language)

            # 2. 分析版本
            version_info = self._analyze_versions(dependencies)

            # 3. 检查兼容性
            compatibility_issues = self._check_compatibility(dependencies, language)

            # 4. 识别关键依赖
            key_dependencies = self._identify_key_dependencies(dependencies, language)

            return {
                "success": True,
                "repo_url": repo_url,
                "dependencies": dependencies,
                "version_info": version_info,
                "compatibility_issues": compatibility_issues,
                "key_dependencies": key_dependencies,
                "total_count": len(dependencies)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "repo_url": repo_url
            }

    def _parse_dependencies(self, repo_path: str, language: str) -> Dict[str, Any]:
        """解析依赖"""
        dependencies = {}

        # Python 依赖
        if language == "Python":
            # requirements.txt
            req_file = os.path.join(repo_path, "requirements.txt")
            if os.path.exists(req_file):
                dependencies.update(self._parse_requirements_txt(req_file))

            # pyproject.toml
            pyproject_file = os.path.join(repo_path, "pyproject.toml")
            if os.path.exists(pyproject_file):
                dependencies.update(self._parse_pyproject_toml(pyproject_file))

            # setup.py
            setup_file = os.path.join(repo_path, "setup.py")
            if os.path.exists(setup_file):
                dependencies.update(self._parse_setup_py(setup_file))

        # JavaScript/TypeScript 依赖
        elif language in ["JavaScript", "TypeScript"]:
            package_file = os.path.join(repo_path, "package.json")
            if os.path.exists(package_file):
                deps = self._parse_package_json(package_file)
                dependencies.update(deps)

        # Java 依赖
        elif language == "Java":
            pom_file = os.path.join(repo_path, "pom.xml")
            if os.path.exists(pom_file):
                dependencies.update(self._parse_pom_xml(pom_file))

            gradle_file = os.path.join(repo_path, "build.gradle")
            if os.path.exists(gradle_file):
                dependencies.update(self._parse_build_gradle(gradle_file))

        # Go 依赖
        elif language == "Go":
            go_mod_file = os.path.join(repo_path, "go.mod")
            if os.path.exists(go_mod_file):
                dependencies.update(self._parse_go_mod(go_mod_file))

        return dependencies

    def _parse_requirements_txt(self, file_path: str) -> Dict[str, Any]:
        """解析 requirements.txt"""
        dependencies = {}
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    # 跳过注释和空行
                    if not line or line.startswith("#"):
                        continue

                    # 解析包名和版本
                    if "==" in line:
                        name, version = line.split("==", 1)
                        dependencies[name] = {
                            "version": version.strip(),
                            "source": "requirements.txt"
                        }
                    elif ">=" in line:
                        name, version = line.split(">=", 1)
                        dependencies[name] = {
                            "version": version.strip(),
                            "constraint": ">=",
                            "source": "requirements.txt"
                        }
                    else:
                        dependencies[line] = {
                            "version": "latest",
                            "source": "requirements.txt"
                        }
        except:
            pass
        return dependencies

    def _parse_pyproject_toml(self, file_path: str) -> Dict[str, Any]:
        """解析 pyproject.toml"""
        dependencies = {}
        try:
            import toml
            with open(file_path, "r", encoding="utf-8") as f:
                data = toml.load(f)

            # 尝试从 dependencies 或 [project.dependencies] 获取
            deps = data.get("project", {}).get("dependencies", [])
            if not deps:
                deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})

            for dep in deps:
                if isinstance(dep, str):
                    # 解析 "package>=version" 格式
                    for a_op in [">=", "==", "~=", "<=", ">"]:
                        if a_op in dep:
                            name, version = dep.split(a_op, 1)
                            dependencies[name] = {
                                "version": version.strip(),
                                "constraint": a_op,
                                "source": "pyproject.toml"
                            }
                            break
                    else:
                        dependencies[dep] = {
                            "version": "latest",
                            "source": "pyproject.toml"
                        }
                elif isinstance(dep, dict):
                    for name, spec in dep.items():
                        if isinstance(spec, dict):
                            dependencies[name] = {
                                "version": spec.get("version", "latest"),
                                "source": "pyproject.toml"
                            }
        except:
            pass
        return dependencies

    def _parse_setup_py(self, file_path: str) -> Dict[str, Any]:
        """解析 setup.py（简化实现）"""
        dependencies = {}
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 查找 install_requires
            import re
            match = re.search(r"install_requires\s*=\s*\[(.*?)\]", content, re.DOTALL)
            if match:
                deps_str = match.group(1)
                # 简单提取包名
                packages = re.findall(r"[\"\']([^\"\']+)[\"\']", deps_str)
                for pkg in packages:
                    # 清理版本约束
                    name = pkg.split(">=")[0].split("==")[0].split("<")[0].strip()
                    dependencies[name] = {
                        "version": "unknown",
                        "source": "setup.py"
                    }
        except:
            pass
        return dependencies

    def _parse_package_json(self, file_path: str) -> Dict[str, Any]:
        """解析 package.json"""
        dependencies = {}
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 合并 dependencies 和 devDependencies
            all_deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}

            for name, version in all_deps.items():
                dependencies[name] = {
                    "version": version,
                    "source": "package.json"
                }
        except:
            pass
        return dependencies

    def _parse_pom_xml(self, file_path: str) -> Dict[str, Any]:
        """解析 pom.xml（简化实现）"""
        dependencies = {}
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(file_path)
            root = tree.getroot()

            # 查找 dependencies
            ns = {"m": "http://maven.apache.org/POM/4.0.0"}
            deps = root.findall(".//m:dependency", ns)

            for dep in deps:
                group_id = dep.find("m:groupId", ns)
                artifact_id = dep.find("m:artifactId", ns)
                version = dep.find("m:version", ns)

                if group_id is not None and artifact_id is not None:
                    name = f"{group_id.text}:{artifact_id.text}"
                    dependencies[name] = {
                        "version": version.text if version is not None else "unknown",
                        "source": "pom.xml"
                    }
        except:
            pass
        return dependencies

    def _parse_build_gradle(self, file_path: str) -> Dict[str, Any]:
        """解析 build.gradle（简化实现）"""
        dependencies = {}
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 简单匹配 implementation "group:module:version"
            import re
            matches = re.findall(r"implementation\s+[\"\']([^\"\']+)[\"\']", content)

            for dep in matches:
                parts = dep.split(":")
                if len(parts) >= 3:
                    name = f"{parts[0]}:{parts[1]}"
                    dependencies[name] = {
                        "version": parts[2],
                        "source": "build.gradle"
                    }
        except:
            pass
        return dependencies

    def _parse_go_mod(self, file_path: str) -> Dict[str, Any]:
        """解析 go.mod"""
        dependencies = {}
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 匹配 require 指令
            import re
            matches = re.findall(r"require\s+([^\s]+)\s+v([^\s]+)", content)

            for path, version in matches:
                dependencies[path] = {
                    "version": version,
                    "source": "go.mod"
                }
        except:
            pass
        return dependencies

    def _analyze_versions(self, dependencies: Dict[str, Any]) -> Dict[str, Any]:
        """分析版本信息"""
        # 统计版本类型
        version_types = {
            "exact": 0,        # 精确版本
            "range": 0,         # 版本范围
            "latest": 0,        # 最新版本
            "unknown": 0         # 未知版本
        }

        for name, info in dependencies.items():
            version = info.get("version", "")

            if version in ["latest", "unknown"]:
                version_types[version] += 1
            elif info.get("constraint"):
                version_types["range"] += 1
            elif version:
                version_types["exact"] += 1
            else:
                version_types["unknown"] += 1

        return {
            "total": len(dependencies),
            "types": version_types
        }

    def _check_compatibility(self, dependencies: Dict[str, Any], language: str) -> List[Dict[str, Any]]:
        """检查版本兼容性"""
        issues = []

        # Python 常见兼容性问题
        if language == "Python":
            # 检查 Django 版本
            if "django" in dependencies:
                version = dependencies["django"].get("version", "")
                if version and version.startswith("2."):
                    issues.append({
                        "package": "django",
                        "issue": "Django 2.x 已停止支持",
                        "suggestion": "升级到 Django 3.x 或 4.x"
                    })

            # 检查 Flask 版本
            if "flask" in dependencies:
                version = dependencies["flask"].get("version", "")
                if version and version.startswith("0."):
                    issues.append({
                        "package": "flask",
                        "issue": "Flask 0.x 版本过旧",
                        "suggestion": "升级到 Flask 1.x 或 2.x"
                    })

        # JavaScript/TypeScript 常见兼容性问题
        elif language in ["JavaScript", "TypeScript"]:
            # 检查 React 版本
            if "react" in dependencies:
                version = dependencies["react"].get("version", "")
                if version and version.startswith("16"):
                    issues.append({
                        "package": "react",
                        "issue": "React 16 版本较旧",
                        "suggestion": "考虑升级到 React 17 或 18"
                    })

        return issues

    def _identify_key_dependencies(self, dependencies: Dict[str, Any], language: str) -> List[str]:
        """识别关键依赖"""
        key_deps = []

        # Python 关键依赖
        python_key = {
            "django": "Web 框架",
            "flask": "Web 框架",
            "fastapi": "Web 框架",
            "numpy": "数值计算",
            "pandas": "数据分析",
            "tensorflow": "机器学习",
            "torch": "机器学习",
            "scikit-learn": "机器学习",
            "sqlalchemy": "ORM",
            "requests": "HTTP 客户端"
        }

        # JavaScript/TypeScript 关键依赖
        js_key = {
            "react": "UI 框架",
            "vue": "UI 框架",
            "angular": "UI 框架",
            "next": "全栈框架",
            "nuxt": "全栈框架",
            "express": "Web 框架",
            "axios": "HTTP 客户端",
            "lodash": "工具库"
        }

        if language == "Python":
            key_map = python_key
        elif language in ["JavaScript", "TypeScript"]:
            key_map = js_key
        else:
            return []

        for name, desc in key_map.items():
            if name in dependencies:
                key_deps.append(f"{name} ({desc})")

        return key_deps


# 全局实例
dependency_analyzer = DependencyAnalyzer()
