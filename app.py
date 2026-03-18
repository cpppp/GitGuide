import streamlit as st

# 设置页面配置
st.set_page_config(
    page_title="GitGuide",
    page_icon="🚀",
    layout="wide"
)

# 主页面内容
st.title("🚀 GitGuide")
st.markdown("### 快速上手任意 GitHub 仓库")
st.markdown("输入 GitHub 仓库 URL，获取学习文档和启动指南")

# 导航到其他页面的链接
st.markdown("---")
st.markdown("### 功能")
st.markdown("- **URL 输入**：粘贴 GitHub 仓库链接")
st.markdown("- **一键生成**：自动分析仓库并生成文档")
st.markdown("- **学习文档**：项目概述、技术栈、目录结构")
st.markdown("- **启动指南**：环境准备、安装命令、运行步骤")
st.markdown("- **AI 问答**：针对项目的交互式问答")

# 跳转提示
st.markdown("---")
st.markdown("### 开始使用")
st.markdown("请从左侧导航栏选择 '🏠 Home' 页面开始")