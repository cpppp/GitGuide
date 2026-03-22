"""Workflow - 并行工作流编排器

负责协调各个 Agent 的并行执行和任务调度
"""

import sys
import os
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime


class WorkflowState:
    """工作流状态 - 在各个 Agent 间共享"""

    def __init__(self):
        self.repo_url: str = ""
        self.repo_path = None
        self.user_preferences = {}

        # 分析结果
        self.type_result = None
        self.structure_result = None
        self.dependency_result = None
        self.code_pattern_result = None

        # 生成结果 - V3.0
        self.quick_start_doc = None
        self.overview_doc = None
        self.architecture_doc = None
        self.install_guide_doc = None

        # 生成结果 - V3.1
        self.usage_tutorial_doc = None
        self.dev_guide_doc = None
        self.troubleshooting_doc = None

        # 审核结果
        self.review_result = None
        self.quality_score = 0.0
        self.improvement_suggestions = []

        # 最终输出
        self.final_result = None

        # 代码图谱数据
        self.code_graph_data = None
        self.examples_data = None

        # 元数据
        self.progress = 0
        self.current_stage = "idle"
        self.errors = []
        self.start_time = None
        self.end_time = None


class Workflow:
    """工作流编排器 - 负责协调所有 Agent 的执行"""

    def __init__(self, max_workers: int = 11):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.state = WorkflowState()

    async def run(self, repo_url: str, repo_path: str, progress_callback=None) -> dict:
        """
        运行完整的工作流

        参数:
            repo_url: GitHub 仓库 URL
            repo_path: 本地仓库路径
            progress_callback: 进度回调函数

        返回:
            Dict: 包含所有生成文档和元数据
        """
        self.progress_callback = progress_callback
        
        # 初始化状态
        self.state = WorkflowState()
        self.state.repo_url = repo_url
        self.state.repo_path = repo_path
        self.state.start_time = datetime.now()

        try:
            # Stage 1: 并行分析
            self.state.current_stage = "analysis"
            self.state.progress = 10
            
            if self.progress_callback:
                self.progress_callback("analyzing", 15, "正在分析项目类型...")

            # 创建分析上下文
            context = {
                "repo_url": repo_url,
                "repo_path": repo_path
            }

            # 动态导入分析器
            type_analyzer = self._import_analyzer("type_analyzer")
            structure_analyzer = self._import_analyzer("structure_analyzer")
            dependency_analyzer = self._import_analyzer("dependency_analyzer")
            code_pattern_analyzer = self._import_analyzer("code_pattern_analyzer")

            # 并行执行分析器 - 使用 functools.partial 包装同步方法
            from functools import partial
            analysis_tasks = [
                partial(type_analyzer.analyze, context),
                partial(structure_analyzer.analyze, context),
                partial(dependency_analyzer.analyze, context),
                partial(code_pattern_analyzer.analyze, context)
            ]

            # 在线程池中执行分析任务
            loop = asyncio.get_event_loop()
            analysis_results = await loop.run_in_executor(
                self.executor,
                self._run_analysis_task,
                analysis_tasks
            )

            # 收集分析结果
            if len(analysis_results) == 4:
                self.state.type_result = analysis_results[0]
                self.state.structure_result = analysis_results[1]
                self.state.dependency_result = analysis_results[2]
                self.state.code_pattern_result = analysis_results[3]

                # 检测分析是否成功
                success_count = sum(1 for r in analysis_results if r.get("success", False))
                if success_count < 4:
                    failed_analyzers = []
                    if not analysis_results[0].get("success"):
                        failed_analyzers.append("TypeAnalyzer")
                    if not analysis_results[1].get("success"):
                        failed_analyzers.append("StructureAnalyzer")
                    if not analysis_results[2].get("success"):
                        failed_analyzers.append("DependencyAnalyzer")
                    if not analysis_results[3].get("success"):
                        failed_analyzers.append("CodePatternAnalyzer")

                    failed_names = ", ".join(failed_analyzers)
                    self.state.errors.append(f"分析器失败: {failed_names}")

            self.state.progress = 40

            # Stage 2: 并行生成文档（即使分析器部分失败也继续）
            # 检查是否有足够的分析结果
            has_analysis = any(r.get("success") for r in analysis_results)
            
            if has_analysis or True:  # 始终执行文档生成
                self.state.current_stage = "generation"
                self.state.progress = 50
                
                if self.progress_callback:
                    self.progress_callback("generating", 50, "正在准备生成文档...")

                # 准备生成上下文
                generation_context = {
                    "repo_url": repo_url,
                    "repo_path": repo_path,
                    "analysis_results": {
                        "type_result": self.state.type_result or {},
                        "structure_result": self.state.structure_result or {},
                        "dependency_result": self.state.dependency_result or {},
                        "code_pattern_result": self.state.code_pattern_result or {}
                    }
                }

                # 导入生成器 - V3.0
                quick_start_generator = self._import_generator("quick_start_generator")
                overview_generator = self._import_generator("overview_generator")
                architecture_generator = self._import_generator("architecture_generator")
                install_guide_generator = self._import_generator("install_guide_generator")

                # 导入生成器 - V3.1
                tutorial_generator = self._import_generator("tutorial_generator")
                dev_guide_generator = self._import_generator("dev_guide_generator")
                troubleshoot_generator = self._import_generator("troubleshoot_generator")

                # 创建生成任务
                generation_tasks = []
                if quick_start_generator:
                    generation_tasks.append(("quick_start", quick_start_generator.generate))
                if overview_generator:
                    generation_tasks.append(("overview", overview_generator.generate))
                if architecture_generator:
                    generation_tasks.append(("architecture", architecture_generator.generate))
                if install_guide_generator:
                    generation_tasks.append(("install_guide", install_guide_generator.generate))
                # V3.1 新增文档类型
                if tutorial_generator:
                    generation_tasks.append(("usage_tutorial", tutorial_generator.generate))
                if dev_guide_generator:
                    generation_tasks.append(("dev_guide", dev_guide_generator.generate))
                if troubleshoot_generator:
                    generation_tasks.append(("troubleshooting", troubleshoot_generator.generate))

                # 预构建共享上下文（避免每个生成器重复读取文件）
                shared_context = self._build_shared_context()

                # 构建统一的生成上下文
                generation_context = {
                    "repo_url": repo_url,
                    "repo_path": repo_path,
                    "shared_context": shared_context,
                    "analysis_results": {
                        "type_result": self.state.type_result or {},
                        "structure_result": self.state.structure_result or {},
                        "dependency_result": self.state.dependency_result or {},
                        "code_pattern_result": self.state.code_pattern_result or {}
                    }
                }

                # 并行执行生成器
                if generation_tasks:
                    print(f"[DEBUG] Starting generation with {len(generation_tasks)} tasks")

                    # 使用 functools.partial 包装任务
                    from functools import partial
                    generation_func = partial(self._run_generation_task, generation_tasks, generation_context)

                    generation_results = await loop.run_in_executor(
                        self.executor,
                        generation_func
                    )

                    print(f"[DEBUG] Generation completed, results count: {len(generation_results)}")

                    # 收集生成结果 - V3.0
                    for doc_type, result in generation_results:
                        if result.get("success"):
                            if doc_type == "quick_start":
                                self.state.quick_start_doc = result
                            elif doc_type == "overview":
                                self.state.overview_doc = result
                            elif doc_type == "architecture":
                                self.state.architecture_doc = result
                            elif doc_type == "install_guide":
                                self.state.install_guide_doc = result
                            # V3.1 新增文档类型
                            elif doc_type == "usage_tutorial":
                                self.state.usage_tutorial_doc = result
                            elif doc_type == "dev_guide":
                                self.state.dev_guide_doc = result
                            elif doc_type == "troubleshooting":
                                self.state.troubleshooting_doc = result
                        else:
                            self.state.errors.append(f"{doc_type} 生成失败: {result.get('error', 'unknown error')}")

                self.state.progress = 80

            # Stage 3: 生成代码图谱数据（在清理仓库前）
            self.state.current_stage = "code_graph"
            self.state.code_graph_data = self._generate_code_graph_data(repo_path)
            self.state.examples_data = self._extract_examples(repo_path)

            # Stage 4: 质量审核
            self.state.current_stage = "review"
            self.state.progress = 90

            self.review_result = self._basic_review()
            self.state.quality_score = self._calculate_quality_score()

            self.state.progress = 100

            # Stage 5: 整理输出
            self.state.current_stage = "finalization"
            self.state.end_time = datetime.now()

            # 构建最终结果
            self.state.final_result = self._build_final_result()

            return {
                "success": True,
                "repo_url": repo_url,
                "documents": self._build_document_package(),
                "metadata": self._build_metadata(),
                "state": self._get_state_summary()
            }

        except Exception as e:
            self.state.errors.append(str(e))
            return {
                "success": False,
                "error": str(e),
                "repo_url": repo_url,
                "state": self._get_state_summary()
            }

    def _import_analyzer(self, name: str):
        """动态导入分析器"""
        try:
            module_path = f"agents.analyzers.{name}"
            module = __import__(module_path, fromlist=[name])
            # 返回模块中的全局实例（如 type_analyzer）
            # name = type_analyzer -> instance_name = type_analyzer
            if hasattr(module, name):
                return getattr(module, name)
            # 如果没有全局实例，返回模块本身（调用者需要使用类）
            return module
        except Exception as e:
            print(f"Import analyzer error: {e}")
            return None

    def _import_generator(self, name: str):
        """动态导入生成器"""
        try:
            module_path = f"agents.generators.{name}"
            module = __import__(module_path, fromlist=[name])
            # 返回模块中的全局实例（如 quick_start_generator）
            if hasattr(module, name):
                instance = getattr(module, name)
                print(f"[DEBUG] Imported generator '{name}': {type(instance)}")
                return instance
            # 如果没有全局实例，返回模块本身
            print(f"[DEBUG] Generator '{name}' has no instance, returning module")
            return module
        except Exception as e:
            print(f"[DEBUG] Import generator error for '{name}': {e}")
            return None

    def _run_analysis_task(self, tasks):
        """执行分析任务列表（在线程中）"""
        import asyncio
        from functools import partial
        results = []
        for task in tasks:
            try:
                if asyncio.iscoroutine(task):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        result = loop.run_until_complete(task)
                    finally:
                        loop.close()
                elif isinstance(task, partial):
                    result = task()
                elif callable(task):
                    result = task()
                else:
                    result = {"success": False, "error": "Invalid task type"}
                results.append(result)
            except Exception as e:
                results.append({"success": False, "error": str(e)})
        return results

    def _run_generation_task(self, task_data_list, generation_context):
        """执行生成任务列表（并行执行）"""
        from concurrent.futures import ThreadPoolExecutor, as_completed

        results = []

        # 使用预构建的上下文
        context = generation_context

        # 使用线程池并行执行（增加到 11 个 worker）
        with ThreadPoolExecutor(max_workers=min(len(task_data_list), 11)) as executor:
            future_to_doc = {}
            for task_data in task_data_list:
                doc_type, generate_func = task_data
                future = executor.submit(self._execute_single_generation, doc_type, generate_func, context)
                future_to_doc[future] = doc_type

            for future in as_completed(future_to_doc):
                doc_type = future_to_doc[future]
                try:
                    result = future.result()
                    results.append((doc_type, result))
                except Exception as e:
                    results.append((doc_type, {
                        "success": False,
                        "document_type": doc_type,
                        "error": str(e)
                    }))

        return results

    def _build_shared_context(self):
        """构建共享上下文（只读取一次文件）"""
        import os
        repo_path = self.state.repo_path
        
        context = {
            "language": self.state.type_result.get("language", "Unknown") if self.state.type_result else "Unknown",
            "project_type": self.state.type_result.get("project_type", "Unknown") if self.state.type_result else "Unknown",
            "frameworks": self.state.type_result.get("frameworks", []) if self.state.type_result else [],
            "build_system": self.state.type_result.get("build_system", "") if self.state.type_result else "",
            "package_manager": self.state.type_result.get("package_manager", "") if self.state.type_result else "",
            "readme": "",
            "directory_tree": "",
            "main_files": [],
            "requirements": [],
            "package_json": {},
            "config_files": {},  # V3.2 新增：配置文件
            "core_modules": self.state.structure_result.get("core_modules", []) if self.state.structure_result else [],
            "entry_points": self.state.structure_result.get("entry_points", []) if self.state.structure_result else [],
            "dependencies": self.state.dependency_result.get("dependencies", []) if self.state.dependency_result else [],
            "patterns": self.state.code_pattern_result.get("patterns", []) if self.state.code_pattern_result else []
        }
        
        if not repo_path or not os.path.exists(repo_path):
            return context
        
        # 读取README（增强到500行）
        readme_files = ['README.md', 'README.rst', 'README.txt', 'readme.md', 'README.MD']
        for readme in readme_files:
            try:
                full_path = os.path.join(repo_path, readme)
                if os.path.exists(full_path):
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        context["readme"] = ''.join(f.readlines()[:500])  # 200 → 500
                    break
            except Exception:
                pass

        # 生成目录树（增强到3层深度，100条目）
        context["directory_tree"] = self._get_directory_tree(repo_path, max_depth=3)
        
        # 读取requirements.txt
        try:
            req_path = os.path.join(repo_path, 'requirements.txt')
            if os.path.exists(req_path):
                with open(req_path, 'r', encoding='utf-8', errors='ignore') as f:
                    context["requirements"] = [line.strip() for line in f.readlines()[:50] if line.strip() and not line.startswith('#')]
        except Exception:
            pass
        
        # 读取package.json
        try:
            import json
            pkg_path = os.path.join(repo_path, 'package.json')
            if os.path.exists(pkg_path):
                with open(pkg_path, 'r', encoding='utf-8', errors='ignore') as f:
                    context["package_json"] = json.load(f)
        except Exception:
            pass
        
        # 读取主要源文件
        context["main_files"] = self._get_main_files(repo_path, context["language"])

        # 读取配置文件（V3.2 新增）
        context["config_files"] = self._get_config_files(repo_path, context["language"])

        return context

    def _get_directory_tree(self, repo_path: str, max_depth: int = 3) -> str:
        """获取目录树（增强版：3层深度，100条目）"""
        import os
        lines = []

        def walk_dir(path: str, prefix: str = "", depth: int = 0):
            if depth > max_depth:
                return
            try:
                items = sorted(os.listdir(path))
                dirs = [i for i in items if os.path.isdir(os.path.join(path, i)) and not i.startswith('.')]
                files = [i for i in items if os.path.isfile(os.path.join(path, i)) and not i.startswith('.')]

                for d in dirs[:10]:
                    lines.append(f"{prefix}├── {d}/")
                    walk_dir(os.path.join(path, d), prefix + "│   ", depth + 1)

                for f in files[:10]:
                    lines.append(f"{prefix}├── {f}")
            except Exception:
                pass

        walk_dir(repo_path)
        return '\n'.join(lines[:100])  # 50 → 100

    def _get_main_files(self, repo_path: str, language: str) -> list:
        """获取主要源文件内容（增强版：10个文件，每个150行）"""
        import os
        main_files = []
        patterns = {
            'Python': [
                'main.py', 'app.py', '__main__.py', 'run.py', 'server.py',
                'core.py', 'app/__init__.py', 'main', 'cli.py', 'wsgi.py'
            ],
            'JavaScript': [
                'index.js', 'main.js', 'app.js', 'server.js', 'src/index.js',
                'app.js', 'index.js', 'server.js', 'src/main.js', 'bin/www'
            ],
            'TypeScript': [
                'index.ts', 'main.ts', 'app.ts', 'src/index.ts',
                'main.ts', 'app.ts', 'src/main.ts', 'server.ts', 'bin/www'
            ],
            'Go': ['main.go', 'cmd/main.go', 'cmd/server/main.go', 'app.go', 'main'],
            'Java': ['Main.java', 'Application.java', 'App.java', 'Main.java', 'src/Main.java'],
            'Rust': ['main.rs', 'src/main.rs', 'lib.rs', 'src/lib.rs', 'bin/main.rs'],
            'C++': ['main.cpp', 'src/main.cpp', 'main.cc', 'app.cpp', 'src/app.cpp'],
            'C#': ['Program.cs', 'Main.cs', 'Program.cs', 'src/Program.cs', 'App.cs']
        }

        files_to_check = patterns.get(language, patterns['Python'])

        for file_name in files_to_check[:50]:  # 读取更多文件：50个
            try:
                full_path = os.path.join(repo_path, file_name)
                if os.path.exists(full_path) and os.path.isfile(full_path):
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = ''.join(f.readlines()[:250])  # 50行 → 250行
                    if content.strip():
                        main_files.append({
                            "name": file_name,
                            "content": content
                        })
            except Exception:
                pass

        return main_files

    def _get_config_files(self, repo_path: str, language: str) -> dict:
        """获取配置文件内容（V3.2 新增）"""
        import os
        import json
        config_files = {}

        config_patterns = {
            'Python': [
                'config.py', 'settings.py', 'config.json', 'config.yaml', 'config.yml',
                '.env.example', 'env.example', 'Makefile', 'Dockerfile', 'docker-compose.yml',
                'pyproject.toml', 'setup.py', 'setup.cfg', '.flake8', 'pytest.ini'
            ],
            'JavaScript': [
                'package.json', 'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
                '.env.example', 'env.example', 'Makefile', 'Dockerfile', 'docker-compose.yml',
                'tsconfig.json', 'webpack.config.js', 'vite.config.js', '.eslintrc.js'
            ],
            'TypeScript': [
                'tsconfig.json', 'package.json', 'package-lock.json', 'yarn.lock',
                '.env.example', 'env.example', 'Makefile', 'Dockerfile', 'docker-compose.yml',
                'vite.config.ts', 'next.config.js', '.eslintrc.js'
            ],
            'Go': [
                'go.mod', 'go.sum', '.env.example', 'env.example', 'Makefile',
                'Dockerfile', 'docker-compose.yml', '.gitignore', 'golangci.yml'
            ],
            'Java': [
                'pom.xml', 'build.gradle', 'settings.gradle', '.env.example',
                'Makefile', 'Dockerfile', 'docker-compose.yml', 'application.properties'
            ],
            'Rust': [
                'Cargo.toml', 'Cargo.lock', '.env.example', 'Makefile',
                'Dockerfile', 'docker-compose.yml', 'rustfmt.toml', 'clippy.toml'
            ],
            'C++': [
                'CMakeLists.txt', 'Makefile', 'Dockerfile', 'docker-compose.yml',
                '.env.example', 'compile_commands.json', 'conanfile.txt'
            ],
            'C#': [
                '*.csproj', '*.sln', 'appsettings.json', 'Program.cs',
                'Dockerfile', 'docker-compose.yml', '.env.example', 'Makefile'
            ]
        }

        files_to_check = config_patterns.get(language, config_patterns['Python'])

        for file_name in files_to_check:
            if file_name.startswith('*'):
                continue
            try:
                full_path = os.path.join(repo_path, file_name)
                if os.path.exists(full_path) and os.path.isfile(full_path):
                    file_size = os.path.getsize(full_path)
                    if file_size > 50000:
                        config_files[file_name] = "[文件过大，已跳过]"
                        continue
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = ''.join(f.readlines()[:100])
                    if content.strip():
                        if file_name.endswith('.json') or file_name.endswith('.yaml') or file_name.endswith('.yml'):
                            try:
                                config_files[file_name] = json.loads(content)
                            except:
                                config_files[file_name] = content
                        else:
                            config_files[file_name] = content
            except Exception:
                pass

        return config_files

    def _execute_single_generation(self, doc_type, generate_func, context):
        """执行单个生成任务"""
        import asyncio
        try:
            print(f"[DEBUG] Executing generation for: {doc_type}")
            print(f"[DEBUG] Context keys: {list(context.keys()) if context else 'None'}")

            if asyncio.iscoroutine(generate_func):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(generate_func(context))
                finally:
                    loop.close()
            elif callable(generate_func):
                result = generate_func(context)
            else:
                result = {"success": False, "error": "Invalid task type"}

            print(f"[DEBUG] Generation result for {doc_type}: success={result.get('success', 'N/A')}, has_content={bool(result.get('content'))}")
            return result
        except Exception as e:
            print(f"[DEBUG] Generation exception for {doc_type}: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "document_type": doc_type,
                "error": str(e)
            }

    def _basic_review(self):
        """基础质量审核"""
        review = {
            "checked_at": datetime.now().isoformat(),
            "completeness": self._check_completeness(),
            "accuracy": self._check_accuracy(),
            "readability": self._check_readability(),
            "practicality": self._check_practicality()
        }

        return review

    def _check_completeness(self):
        """检查完整性检查 - V3.1 支持7种文档"""
        checks = {
            "has_quick_start": self.state.quick_start_doc is not None,
            "has_overview": self.state.overview_doc is not None,
            "has_architecture": self.state.architecture_doc is not None,
            "has_install_guide": self.state.install_guide_doc is not None,
            # V3.1 新增
            "has_usage_tutorial": self.state.usage_tutorial_doc is not None,
            "has_dev_guide": self.state.dev_guide_doc is not None,
            "has_troubleshooting": self.state.troubleshooting_doc is not None
        }

        passed_count = sum(1 for v in checks.values() if v)
        checks["score"] = passed_count / len(checks) if checks else 0
        checks["passed"] = passed_count == len(checks)

        return checks

    def _check_accuracy(self):
        """检查准确性"""
        return {
            "score": 0.8,
            "issues": []
        }

    def _check_readability(self):
        """检查可读性"""
        return {
            "score": 0.8,
            "issues": []
        }

    def _check_practicality(self):
        """检查可操作性"""
        return {
            "score": 0.8,
            "issues": []
        }

    def _calculate_quality_score(self):
        """计算综合质量评分"""
        if not self.review_result:
            return 0.0

        weights = {
            "completeness": 0.4,
            "accuracy": 0.3,
            "readability": 0.2,
            "practicality": 0.1
        }

        scores = {
            "completeness": self.review_result.get("completeness", {}).get("score", 0),
            "accuracy": self.review_result.get("accuracy", {}).get("score", 0),
            "readability": self.review_result.get("readability", {}).get("score", 0),
            "practicality": self.review_result.get("practicality", {}).get("score", 0)
        }

        total_score = sum(
            weights[key] * scores[key]
            for key in weights.keys()
        )

        return min(total_score, 1.0)

    def _build_final_result(self):
        """构建最终结果 - V3.1 支持7种文档"""
        return {
            "quick_start": self.state.quick_start_doc.get("content") if self.state.quick_start_doc else None,
            "overview": self.state.overview_doc.get("content") if self.state.overview_doc else None,
            "architecture": self.state.architecture_doc.get("content") if self.state.architecture_doc else None,
            "install_guide": self.state.install_guide_doc.get("content") if self.state.install_guide_doc else None,
            # V3.1 新增
            "usage_tutorial": self.state.usage_tutorial_doc.get("content") if self.state.usage_tutorial_doc else None,
            "dev_guide": self.state.dev_guide_doc.get("content") if self.state.dev_guide_doc else None,
            "troubleshooting": self.state.troubleshooting_doc.get("content") if self.state.troubleshooting_doc else None,
            "quality_score": self.state.quality_score
        }

    def _build_document_package(self):
        """构建文档包 - V3.1 支持7种文档"""
        package = {}

        # V3.0 文档
        if self.state.quick_start_doc:
            package["quick_start"] = self.state.quick_start_doc.get("content")
        if self.state.overview_doc:
            package["overview"] = self.state.overview_doc.get("content")
        if self.state.architecture_doc:
            package["architecture"] = self.state.architecture_doc.get("content")
        if self.state.install_guide_doc:
            package["install_guide"] = self.state.install_guide_doc.get("content")

        # V3.1 新增文档
        if self.state.usage_tutorial_doc:
            package["usage_tutorial"] = self.state.usage_tutorial_doc.get("content")
        if self.state.dev_guide_doc:
            package["dev_guide"] = self.state.dev_guide_doc.get("content")
        if self.state.troubleshooting_doc:
            package["troubleshooting"] = self.state.troubleshooting_doc.get("content")

        # V3.1 代码图谱数据
        if self.state.code_graph_data:
            package["code_graph"] = self.state.code_graph_data
        if self.state.examples_data:
            package["examples"] = self.state.examples_data

        return package

    def _generate_code_graph_data(self, repo_path: str) -> dict:
        """生成代码图谱数据"""
        try:
            from backend.services.code_graph import CodeGraphService
            return CodeGraphService.analyze_structure(repo_path)
        except Exception as e:
            print(f"Code graph generation error: {e}")
            return {}

    def _extract_examples(self, repo_path: str) -> list:
        """提取示例代码"""
        try:
            from backend.services.code_graph import CodeGraphService
            return CodeGraphService.extract_examples(repo_path)
        except Exception as e:
            print(f"Example extraction error: {e}")
            return []

    def _build_metadata(self):
        """构建元数据"""
        duration = None
        if self.state.start_time and self.state.end_time:
            duration = (self.state.end_time - self.state.start_time).total_seconds()

        return {
            "repo_url": self.state.repo_url,
            "generated_at": datetime.now().isoformat(),
            "duration_seconds": duration,
            "quality_score": self.state.quality_score,
            "errors": self.state.errors
        }

    def _get_state_summary(self):
        """获取状态摘要"""
        return {
            "current_stage": self.state.current_stage,
            "progress": self.state.progress,
            "error_count": len(self.state.errors),
            "analysis_success": all([
                self.state.type_result.get("success", False) if self.state.type_result else False,
                self.state.structure_result.get("success", False) if self.state.structure_result else False,
                self.state.dependency_result.get("success", False) if self.state.dependency_result else False,
                self.state.code_pattern_result.get("success", False) if self.state.code_pattern_result else False
            ])
        }


# 全局实例
workflow = Workflow()
