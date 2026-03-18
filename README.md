# GitGuide

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Streamlit-1.40+-red.svg" alt="Streamlit">
  <img src="https://img.shields.io/badge/LangChain-1.0+-green.svg" alt="LangChain">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</p>

<p align="center">
  <b>🚀 智能化 GitHub 仓库学习工具</b>
</p>

<p align="center">
  输入 GitHub 仓库 URL，自动生成结构化学习文档、详细启动指南，并提供 AI 智能问答，让你快速掌握任何项目
</p>

***

## 🎯 核心功能

- **智能仓库分析** - 自动识别项目结构、技术栈和核心模块
- **一键文档生成** - 快速生成包含项目概述、架构设计、安装指南的完整文档
- **交互式 AI 问答** - 针对项目细节提供智能解答，支持代码解释和功能查询
- **多项目类型支持** - 兼容 Python、Node.js、Java、Go 等多种技术栈
- **直观用户界面** - 基于 Streamlit 的现代化 Web 界面，操作简单便捷

## 🛠️ 技术栈

| 组件       | 技术                  | 版本            | 用途                        |
| :------- | :------------------ | :------------ | :------------------------ |
| 前端       | Streamlit           | 1.40+         | 提供现代化 Web 界面           |
| Agent 框架 | LangChain           | 1.0+          | 构建智能 Agent 系统           |
| Agent 框架 | LangGraph           | 0.2+          | 管理 Agent 间的工作流和状态       |
| LLM      | OpenAI API / 智谱 GLM | GPT-4 / glm-4 | 提供自然语言处理能力              |
| 仓库分析     | PyGithub            | 2.1+          | 调用 GitHub API 获取仓库信息     |
| 仓库分析     | GitPython           | 3.1+          | 本地仓库克隆和分析               |

## 📁 项目结构

```
GitGuide/
├── app.py                      # Streamlit 主入口文件
├── pages/                      # Streamlit 多页面应用
│   ├── 1_🏠_Home.py            # 首页 - 仓库 URL 输入
│   ├── 2_📚_Documentation.py   # 文档页 - 展示生成的学习文档
│   └── 3_💬_Chat.py            # 聊天页 - AI 智能问答
├── agents/                     # LangChain Agent 实现
│   ├── orchestrator.py         # 协调器 - 管理多 Agent 工作流
│   ├── analyzer.py             # 分析器 - 仓库结构和技术栈分析
│   ├── doc_generator.py        # 文档生成器 - 生成学习文档和指南
│   └── chat.py                 # 聊天 Agent - 回答项目相关问题
├── tools/                      # 工具函数库
│   ├── github_tools.py         # GitHub API 交互工具
│   ├── git_tools.py            # Git 仓库操作工具
│   └── file_tools.py           # 文件读取和分析工具
├── core/                       # 核心模块
│   ├── config.py               # 配置管理
│   └── utils.py                # 通用工具函数
├── memory-bank/                # 项目文档
│   ├── architecture.md         # 架构设计文档
│   ├── product-design-document.md # 产品设计文档
│   ├── tech-stack.md           # 技术栈说明
│   ├── implementation-plan.md  # 实施计划
│   └── process.md              # 项目进度跟踪
├── requirements.txt            # Python 依赖包
├── .env.example                # 环境变量示例
└── README.md                   # 项目说明文档
```

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/your-username/GitGuide.git
cd GitGuide
```

### 2. 创建虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# Windows 激活环境
venv\Scripts\activate

# macOS/Linux 激活环境
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的 API Key
```

`.env` 文件配置示例：

```env
# OpenAI API（或兼容的 API）
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.openai.com/v1  # 或其他兼容端点
OPENAI_MODEL=gpt-4

# GitHub API（可选，提高速率限制）
GITHUB_TOKEN=your_github_token

# 应用配置
APP_ENV=development
DEBUG=true
```

### 5. 运行应用

```bash
streamlit run app.py
```

应用将在 <http://localhost:8501> 启动。

## 📖 使用指南

1. **访问应用** - 打开浏览器访问 <http://localhost:8501>
2. **输入仓库 URL** - 在首页输入 GitHub 仓库 URL（例如：`https://github.com/cpppp/GitGuide.git`）
3. **生成文档** - 点击"生成文档"按钮，系统将自动分析仓库并生成文档
4. **查看学习文档** - 在文档页面浏览生成的项目概述、技术栈分析和启动指南
5. **AI 智能问答** - 切换到 Chat 页面，针对项目提出问题，获取智能解答

## 📂 支持的项目类型

- **Node.js** - 基于 package.json 识别
- **Python** - 基于 requirements.txt 或 setup.py 识别
- **Java** - 基于 pom.xml 或 build.gradle 识别
- **Go** - 基于 go.mod 识别
- **Docker** - 基于 Dockerfile 识别

## 🏗️ 多 Agent 架构

GitGuide 采用先进的 LangChain + LangGraph 多 Agent 架构，实现高效的仓库分析和文档生成：

```
用户输入 GitHub URL
        │
        ▼
┌─────────────────────┐
│  Orchestrator       │  协调器
│  (任务分发与管理)      │
└──────────┬──────────┘
           │
     ┌─────┼─────┐
     ▼     ▼     ▼
┌────────┐ ┌────────┐ ┌────────┐
│Analyzer│ │DocGen  │ │ Chat   │
│(仓库分析) │ │(文档生成) │ │(智能问答) │
└────────┘ └────────┘ └────────┘
```

### Agent 职责说明

- **Orchestrator** - 负责协调各 Agent 工作流程，管理任务分发和状态跟踪
- **Analyzer Agent** - 分析仓库结构、识别技术栈、提取核心模块和依赖关系
- **DocGen Agent** - 根据分析结果生成结构化学习文档和详细启动指南
- **Chat Agent** - 基于生成的文档和仓库知识，回答用户关于项目的问题

## ⚙️ 环境变量配置

| 变量名               | 必填 | 说明                          | 默认值                     |
| :---------------- | :- | :-------------------------- | :---------------------- |
| `OPENAI_API_KEY`  | 是  | OpenAI API 密钥或兼容 API 密钥       | -                       |
| `OPENAI_BASE_URL` | 否  | API 端点 URL（默认 OpenAI）         | `https://api.openai.com/v1` |
| `OPENAI_MODEL`    | 否  | 模型名称（默认 gpt-4）              | `gpt-4`                 |
| `GITHUB_TOKEN`    | 否  | GitHub Token（提高 API 限额）        | -                       |

## ❓ 常见问题

### Q: API 调用失败怎么办？

A: 请检查 `.env` 文件中的 `OPENAI_API_KEY` 是否正确配置，确保 API Key 有效且未过期。

### Q: GitHub API 限流怎么办？

A: 配置 `GITHUB_TOKEN` 可将 API 调用限额从 60 次/小时提升到 5000 次/小时，显著提高分析速度。

### Q: 支持私有仓库吗？

A: 当前版本仅支持公开仓库，私有仓库支持将在 v1.2 版本中推出。

### Q: 分析大型仓库需要多长时间？

A: 分析时间取决于仓库大小和网络速度，一般在 1-3 分钟内完成。大型仓库可能需要更长时间。

## 📅 开发路线

### v1.1（开发中）
- [ ] 实时进度反馈与状态管理
- [ ] 错误处理与异常恢复机制
- [ ] 分析历史记录功能
- [ ] 仓库收藏与管理功能

### v1.2（计划中）
- [ ] 文档导出功能（Markdown、PDF、HTML）
- [ ] 代码结构图谱可视化
- [ ] 深色模式支持
- [ ] 多语言界面支持
- [ ] 私有仓库分析支持

### v2.0（规划中）
- [ ] 深度代码分析与复杂度评估
- [ ] 自动 API 文档生成
- [ ] 测试覆盖率分析
- [ ] 性能优化建议
- [ ] 代码质量评估

## 🤝 贡献指南

我们欢迎社区贡献，共同改进 GitGuide！

### 贡献流程
1. **Fork** 本仓库到你的 GitHub 账户
2. **创建特性分支** - `git checkout -b feature/YourFeatureName`
3. **提交更改** - `git commit -m 'Add: 功能描述'`
4. **推送到分支** - `git push origin feature/YourFeatureName`
5. **提交 Pull Request** - 描述你的更改和实现细节

### 开发规范
- 遵循 PEP 8 代码风格
- 添加适当的测试用例
- 更新相关文档
- 确保代码通过所有测试

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

***

<p align="center">
  Made with ❤️ by GitGuide Team
</p>