# GitGuide 项目实施计划

> **文档版本**：v2.0\
> **最后更新**：2026-03-18\
> **更新说明**：基于 MVP 成功实现，重新规划后续迭代实施计划

***

## 概述

本文档基于产品设计文档 v2.0 和迭代计划，详细规划 GitGuide 项目的后续实施步骤。MVP 阶段已完成，后续将按照 6 个迭代阶段逐步推进。

**项目状态**：MVP 已完成 ✅

**核心目标**：将 GitGuide 从 MVP 升级为功能完善、用户体验优秀的 GitHub 仓库分析工具。

***

## MVP 阶段回顾（已完成）

### 已实现功能

| 功能     | 状态 | 说明                    |
| :----- | :- | :-------------------- |
| URL 输入 | ✅  | 支持公开 GitHub 仓库 URL 输入 |
| 一键生成   | ✅  | 点击按钮自动分析仓库            |
| 学习文档   | ✅  | 项目概述、技术栈、目录结构、依赖项     |
| 启动指南   | ✅  | 环境要求、安装命令、运行步骤        |
| AI 问答  | ✅  | 基于 LangChain 的智能问答    |

***

## 迭代一：用户体验优化（v1.1）

**优先级**：高\
**预计工作量**：3 天\
**目标**：提升用户等待体验，完善错误处理

### 步骤 1.1：进度反馈与状态管理

**任务**：

1. 在首页添加进度条组件
2. 实现分阶段状态提示：
   - 阶段 1：正在获取仓库信息... (20%)
   - 阶段 2：正在分析目录结构... (40%)
   - 阶段 3：正在生成学习文档... (60%)
   - 阶段 4：正在生成启动指南... (80%)
   - 阶段 5：完成！ (100%)
3. 添加预计剩余时间显示
4. 实现取消分析任务功能

**实现方案**：

```python
# pages/1_🏠_Home.py
import streamlit as st
import time

def analyze_with_progress(repo_url):
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # 阶段 1
    status_text.text("🔍 正在获取仓库信息...")
    progress_bar.progress(20)
    repo_info = get_repo_info(repo_url)
    
    # 阶段 2
    status_text.text("📁 正在分析目录结构...")
    progress_bar.progress(40)
    structure = analyze_structure(repo_url)
    
    # 阶段 3
    status_text.text("📝 正在生成学习文档...")
    progress_bar.progress(60)
    learning_doc = generate_learning_doc(repo_info, structure)
    
    # 阶段 4
    status_text.text("🚀 正在生成启动指南...")
    progress_bar.progress(80)
    setup_guide = generate_setup_guide(repo_info, structure)
    
    # 完成
    status_text.text("✅ 分析完成！")
    progress_bar.progress(100)
    
    return {"learning_doc": learning_doc, "setup_guide": setup_guide}
```

**验证方法**：

- 输入测试仓库 URL，确认进度条正常显示
- 确认各阶段状态提示清晰
- 确认取消按钮可中断分析

***

### 步骤 1.2：错误处理与友好提示

**任务**：

1. 实现 URL 格式实时验证
2. 添加仓库不存在/私有仓库提示
3. 实现 API 限流提示和重试建议
4. 添加网络错误自动重试机制
5. 实现错误日志记录

**实现方案**：

```python
# core/validators.py
import re

def validate_github_url(url):
    """验证 GitHub URL 格式"""
    if not url:
        return False, "请输入 GitHub 仓库 URL"
    
    patterns = [
        r'^https?://github\.com/[^/]+/[^/]+/?$',
        r'^https?://github\.com/[^/]+/[^/]+/tree/[^/]+/?$'
    ]
    
    for pattern in patterns:
        if re.match(pattern, url):
            return True, "✅ URL 格式正确"
    
    return False, "❌ 请输入有效的 GitHub 仓库 URL（如：https://github.com/user/repo）"

def handle_api_error(error):
    """处理 API 错误并返回友好提示"""
    error_messages = {
        "rate_limit": "GitHub API 请求次数已达上限，请稍后再试或配置 GITHUB_TOKEN",
        "not_found": "仓库不存在或为私有仓库，请检查 URL 是否正确",
        "network": "网络连接失败，请检查网络后重试",
        "timeout": "请求超时，仓库可能过大，请尝试较小的仓库"
    }
    
    error_type = classify_error(error)
    return error_messages.get(error_type, f"发生错误: {str(error)}")
```

**验证方法**：

- 输入无效 URL，确认显示错误提示
- 输入私有仓库 URL，确认提示正确
- 模拟网络错误，确认重试机制生效

***

### 步骤 1.3：历史记录功能

**任务**：

1. 创建历史记录存储模块
2. 实现历史记录列表展示
3. 添加快速重新分析功能
4. 实现清除历史记录选项

**实现方案**：

```python
# core/history.py
import json
import os
from datetime import datetime

HISTORY_FILE = "data/history.json"

def save_to_history(repo_url, result):
    """保存分析结果到历史记录"""
    history = load_history()
    history.insert(0, {
        "url": repo_url,
        "name": result.get("project_name", "Unknown"),
        "timestamp": datetime.now().isoformat(),
        "language": result.get("language", "Unknown")
    })
    # 只保留最近 20 条
    history = history[:20]
    
    os.makedirs("data", exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def load_history():
    """加载历史记录"""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def clear_history():
    """清除历史记录"""
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)
```

**验证方法**：

- 分析多个仓库，确认历史记录正确保存
- 点击历史记录项，确认可快速重新分析
- 清除历史记录，确认数据被删除

***

### 步骤 1.4：收藏仓库功能

**任务**：

1. 创建收藏存储模块
2. 在文档页面添加收藏按钮
3. 创建收藏列表页面
4. 实现收藏数据持久化

**实现方案**：

```python
# core/favorites.py
import json
import os

FAVORITES_FILE = "data/favorites.json"

def add_favorite(repo_url, repo_info):
    """添加收藏"""
    favorites = load_favorites()
    if not any(f["url"] == repo_url for f in favorites):
        favorites.append({
            "url": repo_url,
            "name": repo_info.get("name", "Unknown"),
            "language": repo_info.get("language", "Unknown"),
            "added_at": datetime.now().isoformat()
        })
        save_favorites(favorites)
        return True
    return False

def remove_favorite(repo_url):
    """取消收藏"""
    favorites = load_favorites()
    favorites = [f for f in favorites if f["url"] != repo_url]
    save_favorites(favorites)

def is_favorited(repo_url):
    """检查是否已收藏"""
    favorites = load_favorites()
    return any(f["url"] == repo_url for f in favorites)
```

**验证方法**：

- 点击收藏按钮，确认收藏成功
- 刷新页面，确认收藏状态保持
- 在收藏列表查看已收藏仓库

***

## 迭代二：功能增强（v1.2）

**优先级**：高\
**预计工作量**：5 天\
**目标**：增加导出功能、可视化、主题切换

### 步骤 2.1：导出功能

**任务**：

1. 实现 Markdown 导出
2. 实现 PDF 导出
3. 实现 HTML 导出
4. 添加导出按钮到文档页面

**实现方案**：

```python
# core/export.py
from datetime import datetime

def export_to_markdown(result):
    """导出为 Markdown"""
    content = f"""# {result.get('project_name', '项目分析报告')}

> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> 仓库地址：{result.get('repo_url', '')}

---

## 📋 项目概述

{result.get('overview', '暂无概述')}

---

## 🔧 技术栈

{result.get('tech_stack', '暂无技术栈信息')}

---

## 📁 目录结构

```

{result.get('directory\_structure', '暂无目录结构')}

```

---

## 🚀 启动指南

{result.get('setup_guide', '暂无启动指南')}

---

*本文档由 GitGuide 自动生成*
"""
    return content

def export_to_html(result):
    """导出为 HTML"""
    md_content = export_to_markdown(result)
    # 使用 markdown 库转换
    import markdown
    html_content = markdown.markdown(md_content)
    
    html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{result.get('project_name', '项目分析报告')}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        pre {{ background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; }}
        code {{ background: #f5f5f5; padding: 2px 6px; border-radius: 3px; }}
    </style>
</head>
<body>
    {html_content}
</body>
</html>"""
    return html_template
```

**验证方法**：

- 点击导出 Markdown，确认文件下载正确
- 点击导出 PDF，确认格式正确
- 点击导出 HTML，确认可在浏览器打开

***

### 步骤 2.2：代码图谱可视化

**任务**：

1. 实现目录树可视化
2. 实现模块依赖关系图
3. 添加文件大小分布图
4. 创建新的图谱标签页

**实现方案**：

```python
# core/visualization.py
import plotly.express as px
import plotly.graph_objects as go

def create_directory_tree(structure):
    """创建目录树可视化"""
    # 使用 plotly 创建树形图
    labels = []
    parents = []
    
    def traverse(node, parent=""):
        for name, children in node.items():
            labels.append(name)
            parents.append(parent)
            if children:
                traverse(children, name)
    
    traverse(structure)
    
    fig = go.Figure(go.Treemap(
        labels=labels,
        parents=parents,
        root_color="lightgrey"
    ))
    return fig

def create_dependency_graph(dependencies):
    """创建依赖关系图"""
    import networkx as nx
    
    G = nx.DiGraph()
    for dep in dependencies:
        G.add_edge(dep['from'], dep['to'])
    
    # 使用 plotly 绘制
    pos = nx.spring_layout(G)
    
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=edge_x, y=edge_y, mode='lines', line=dict(width=0.5, color='#888')))
    
    return fig
```

**验证方法**：

- 分析仓库后，确认图谱标签页显示
- 确认目录树可视化正确
- 确认依赖关系图可交互

***

### 步骤 2.3：深色模式

**任务**：

1. 实现深色/浅色主题切换
2. 添加主题切换按钮
3. 保存用户主题偏好

**实现方案**：

```python
# core/theme.py
import streamlit as st

def apply_theme():
    """应用主题"""
    theme = st.session_state.get("theme", "light")
    
    if theme == "dark":
        st.markdown("""
        <style>
        .stApp {
            background-color: #1E1E1E;
            color: #FFFFFF;
        }
        .stTextInput > div > div > input {
            background-color: #2D2D2D;
            color: #FFFFFF;
        }
        .stButton > button {
            background-color: #3D3D3D;
            color: #FFFFFF;
        }
        </style>
        """, unsafe_allow_html=True)

def toggle_theme():
    """切换主题"""
    current = st.session_state.get("theme", "light")
    st.session_state["theme"] = "dark" if current == "light" else "light"
```

**验证方法**：

- 点击主题切换按钮，确认界面颜色变化
- 刷新页面，确认主题设置保持

***

### 步骤 2.4：多语言支持

**任务**：

1. 创建语言配置文件
2. 实现界面语言切换
3. 实现文档语言选择
4. 实现 AI 回答语言适配

**实现方案**：

```python
# core/i18n.py

LANGUAGES = {
    "zh": {
        "app_title": "🚀 GitGuide",
        "app_subtitle": "快速上手任意 GitHub 仓库",
        "input_label": "GitHub 仓库 URL",
        "input_placeholder": "https://github.com/user/repo",
        "generate_btn": "生成文档",
        "learning_doc_tab": "学习文档",
        "setup_guide_tab": "启动指南",
        "chat_placeholder": "问关于这个项目的问题...",
        "history_title": "历史记录",
        "favorites_title": "收藏仓库"
    },
    "en": {
        "app_title": "🚀 GitGuide",
        "app_subtitle": "Quick Start for Any GitHub Repository",
        "input_label": "GitHub Repository URL",
        "input_placeholder": "https://github.com/user/repo",
        "generate_btn": "Generate Docs",
        "learning_doc_tab": "Learning Docs",
        "setup_guide_tab": "Setup Guide",
        "chat_placeholder": "Ask questions about this project...",
        "history_title": "History",
        "favorites_title": "Favorites"
    }
}

def get_text(key, lang="zh"):
    """获取多语言文本"""
    return LANGUAGES.get(lang, LANGUAGES["zh"]).get(key, key)
```

**验证方法**：

- 切换语言，确认界面文本变化
- 确认文档生成语言正确
- 确认 AI 回答语言适配

***

## 迭代三：分析能力提升（v2.0）

**优先级**：中\
**预计工作量**：9 天\
**目标**：提供更深入的代码分析能力

### 步骤 3.1：深度代码分析

**任务**：

1. 实现函数/类关系分析
2. 实现代码质量评分
3. 实现潜在问题检测
4. 实现最佳实践建议

**实现方案**：

```python
# tools/code_analyzer.py
import ast
from typing import Dict, List

class CodeAnalyzer:
    def analyze_python_file(self, code: str) -> Dict:
        """分析 Python 代码"""
        tree = ast.parse(code)
        
        functions = []
        classes = []
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    "name": node.name,
                    "args": [arg.arg for arg in node.args.args],
                    "docstring": ast.get_docstring(node),
                    "complexity": self._calculate_complexity(node)
                })
            elif isinstance(node, ast.ClassDef):
                classes.append({
                    "name": node.name,
                    "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                    "docstring": ast.get_docstring(node)
                })
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(self._get_import_name(node))
        
        return {
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "lines_of_code": len(code.splitlines()),
            "quality_score": self._calculate_quality_score(functions, classes)
        }
    
    def _calculate_complexity(self, node) -> int:
        """计算圈复杂度"""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
        return complexity
```

**验证方法**：

- 分析 Python 项目，确认函数/类列表正确
- 确认代码质量评分合理
- 确认问题检测准确

***

### 步骤 3.2：API 文档生成

**任务**：

1. 识别 REST API 端点
2. 提取函数签名和文档字符串
3. 生成 API 使用示例
4. 支持 OpenAPI/Swagger 格式

**实现方案**：

```python
# tools/api_extractor.py
import re
from typing import List, Dict

class APIExtractor:
    def extract_fastapi_routes(self, code: str) -> List[Dict]:
        """从 FastAPI 代码提取路由"""
        routes = []
        
        # 匹配 @app.get, @app.post 等
        pattern = r'@(?:app|router)\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']\)'
        
        for match in re.finditer(pattern, code):
            method = match.group(1).upper()
            path = match.group(2)
            
            # 提取函数定义
            func_start = match.end()
            func_match = re.search(r'def\s+(\w+)\s*\(([^)]*)\)', code[func_start:])
            
            if func_match:
                routes.append({
                    "method": method,
                    "path": path,
                    "function": func_match.group(1),
                    "params": func_match.group(2)
                })
        
        return routes
    
    def generate_openapi_spec(self, routes: List[Dict]) -> Dict:
        """生成 OpenAPI 规范"""
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "API Documentation", "version": "1.0.0"},
            "paths": {}
        }
        
        for route in routes:
            path = route["path"]
            if path not in spec["paths"]:
                spec["paths"][path] = {}
            
            spec["paths"][path][route["method"].lower()] = {
                "summary": f"{route['method']} {path}",
                "operationId": route["function"]
            }
        
        return spec
```

**验证方法**：

- 分析 FastAPI 项目，确认路由提取正确
- 确认 OpenAPI 规范生成正确

***

### 步骤 3.3：测试覆盖率分析

**任务**：

1. 检测测试文件
2. 分析测试覆盖率（如果有配置）
3. 提供测试建议
4. 识别未测试的关键模块

**验证方法**：

- 分析有测试的项目，确认测试文件识别
- 确认测试建议合理

***

### 步骤 3.4：性能建议

**任务**：

1. 识别性能瓶颈
2. 依赖版本检查
3. 安全漏洞扫描
4. 优化建议生成

**验证方法**：

- 分析项目，确认性能问题识别
- 确认依赖版本检查正确

***

## 迭代四：协作与分享（v2.1）

**优先级**：中\
**预计工作量**：2 天

### 步骤 4.1：分享分析结果

**任务**：

1. 生成分享链接
2. 生成二维码
3. 添加社交媒体分享按钮

**验证方法**：

- 确认分享链接可访问
- 确认二维码可扫描

***

### 步骤 4.2：用户反馈系统

**任务**：

1. 文档质量评分
2. AI 回答满意度反馈
3. 问题报告功能

**验证方法**：

- 确认评分功能正常
- 确认反馈数据保存

***

## 迭代五：技术改进（v2.2）

**优先级**：中\
**预计工作量**：4.5 天

### 步骤 5.1：缓存机制优化

**任务**：

1. Redis 缓存集成
2. 分析结果持久化
3. 智能缓存失效

**验证方法**：

- 确认缓存命中时响应更快
- 确认缓存失效逻辑正确

***

### 步骤 5.2：异步处理

**任务**：

1. 后台任务队列
2. WebSocket 实时推送
3. 超时处理

**验证方法**：

- 确认大仓库分析不阻塞
- 确认进度实时更新

***

### 步骤 5.3：支持更多 LLM

**任务**：

1. 支持 Claude API
2. 支持本地模型（Ollama）
3. 支持更多国产模型

**验证方法**：

- 确认模型切换正常
- 确认各模型回答质量

***

## 实施检查清单

### 迭代一检查项

- [ ] 进度条正常显示
- [ ] 状态提示清晰
- [ ] 错误处理友好
- [ ] 历史记录功能正常
- [ ] 收藏功能正常

### 迭代二检查项

- [ ] Markdown 导出正常
- [ ] PDF 导出正常
- [ ] 代码图谱可视化
- [ ] 深色模式切换
- [ ] 多语言支持

### 迭代三检查项

- [ ] 代码分析功能
- [ ] API 文档生成
- [ ] 测试覆盖率分析
- [ ] 性能建议

### 迭代四检查项

- [ ] 分享功能
- [ ] 反馈系统

### 迭代五检查项

- [ ] 缓存优化
- [ ] 异步处理
- [ ] 多 LLM 支持

### 迭代六检查项

- [ ] 私有仓库支持
- [ ] 自定义模板
- [ ] 批量分析

***

*本实施计划将根据实际开发进度和用户反馈持续更新*

*Last updated: 2026-03-18 18:30 PM*
