import streamlit as st

st.set_page_config(
    page_title="GitGuide - Home",
    page_icon="🚀"
)

st.title("🚀 GitGuide")
st.markdown("### 快速上手任意 GitHub 仓库")
st.markdown("输入 GitHub 仓库 URL，我们会为您生成详细的学习文档和启动指南")

# URL 输入框
repo_url = st.text_input(
    "GitHub 仓库 URL",
    placeholder="https://github.com/user/repo",
    help="请输入完整的 GitHub 仓库链接"
)

# 生成按钮
if st.button("生成文档", type="primary"):
    if repo_url:
        # 验证 URL 格式
        from core.utils import is_valid_github_url
        if not is_valid_github_url(repo_url):
            st.error("请输入有效的 GitHub 仓库 URL")
        else:
            st.info("正在分析仓库... 这可能需要几分钟时间")

            try:
                # 导入 Orchestrator
                from agents.orchestrator import run

                # 运行分析
                with st.spinner("正在分析仓库，请稍候..."):
                    result = run(repo_url)

                if result.get("success"):
                    # 保存结果到 session state
                    st.session_state["analysis_result"] = result
                    st.session_state["repo_url"] = repo_url
                    st.success("分析完成！正在跳转到文档页面...")
                    st.switch_page("pages/2_📚_Documentation.py")
                else:
                    st.error(f"分析失败: {result.get('error', '未知错误')}")
            except Exception as e:
                st.error(f"发生错误: {str(e)}")
    else:
        st.error("请输入有效的 GitHub 仓库 URL")

# 示例仓库
st.markdown("---")
st.markdown("### 示例仓库")

example_repos = [
    ("python/cpython", "Python 官方解释器"),
    ("facebook/react", "React 前端框架"),
    ("gin-gonic/gin", "Go Web 框架")
]

for repo, desc in example_repos:
    full_url = f"https://github.com/{repo}"
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**{repo}** - {desc}")
    with col2:
        if st.button(f"试用", key=repo):
            st.session_state["repo_url"] = full_url
            # 立即分析示例仓库
            try:
                from agents.orchestrator import run
                with st.spinner("正在分析仓库，请稍候..."):
                    result = run(full_url)
                if result.get("success"):
                    st.session_state["analysis_result"] = result
                    st.switch_page("pages/2_📚_Documentation.py")
                else:
                    st.error(f"分析失败: {result.get('error', '未知错误')}")
            except Exception as e:
                st.error(f"发生错误: {str(e)}")