# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.0] - 2026-03-20

### Added
- **数据库集成** - SQLite + SQLAlchemy ORM 支持
- **AI 问答记录持久化** - 问答记录自动保存到数据库，支持清除历史记录
- **仓库文档持久化** - 分析结果自动保存，支持离线查看
- **已分析仓库列表** - 首页展示已分析仓库卡片，点击可快速查看历史文档
- **数据导出导入** - 支持导出和导入用户数据（JSON 格式）
- **收藏功能数据库迁移** - 收藏功能从 JSON 文件迁移到数据库

### Changed
- 重构收藏 API 使用数据库存储
- 优化数据库会话管理

### Fixed
- 修复收藏功能操作失败问题
- 修复文档页面 Markdown 渲染问题
- 修复已分析仓库文档不显示问题

## [2.1.0] - 2026-03-20

### Added
- **文档导出功能** - 支持导出为 Markdown、PDF、HTML 格式
- **深色模式** - 深色/浅色主题切换，主题设置持久化
- **多语言支持** - 界面语言切换（中英文），所有页面支持多语言

### Changed
- 优化启动指南，只包含核心启动内容
- 改进错误处理和用户提示

## [2.0.0] - 2026-03-19

### Added
- **前后端分离架构** - Vue 3 + FastAPI 架构重构
- **WebSocket 实时进度** - 实时推送分析进度
- **可靠的取消功能** - 支持中断当前分析任务
- **现代化响应式界面** - 基于 Element Plus 的 UI 组件

### Changed
- 从 Streamlit 迁移到 Vue 3 前端
- 重构后端为 FastAPI REST API

### Removed
- Streamlit 前端界面

## [1.1.0] - 2026-03-19

### Added
- **进度反馈** - 实时进度条显示分析阶段
- **错误处理** - URL 格式验证、仓库不存在提示、API 限流提示
- **历史记录** - 本地存储分析历史
- **收藏仓库** - 收藏功能持久化
- **异步任务队列** - Redis + RQ 后台任务队列架构

### Fixed
- 修复文档页仓库链接显示问题

## [1.0.0] - 2026-03-18

### Added
- **URL 输入** - 支持公开 GitHub 仓库 URL 输入
- **一键生成** - 点击按钮自动分析仓库
- **学习文档** - 项目概述、技术栈、目录结构、依赖项
- **启动指南** - 环境要求、安装命令、运行步骤
- **AI 问答** - 基于 LangChain 的智能问答
- **多项目类型支持** - 兼容 Python、Node.js、Java、Go 等多种技术栈

---

## 未来计划

### [3.0.0] - 计划中

#### Multi-Agent 架构升级（完整流水线）
- SOP 标准化流程定义
- Supervisor Agent（Planner、Scheduler、Reviewer、Optimizer）
- Analyzer Team（TypeAnalyzer、StructureAnalyzer、DependencyAnalyzer、CodePatternAnalyzer）
- **Generator Team 核心实现**（QuickStart、Overview、Architecture、InstallGuide）
- 并行执行引擎
- 端到端可工作（输入 URL → 输出 4 种文档）
- 分析效率提升 60%+

### [3.1.0] - 计划中

#### 文档质量提升（质量团队+扩展）
- **Quality Team 实现**（DocReviewer、DocOptimizer、QualityScorer）
- Generator Team 扩展（Tutorial、DevGuide、Troubleshoot）
- 7 种文档类型全覆盖
- 5 种辅助素材（架构图、目录树、代码图谱、示例代码、学习路径）
- 质量控制机制（多轮优化）
- 文档质量评分系统（>85分）

---

*Last updated: 2026-03-20*
