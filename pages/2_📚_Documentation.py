import streamlit as st

st.set_page_config(
    page_title="GitGuide - Documentation",
    page_icon="📚"
)

st.title("📚 学习文档")

# 从 session state 获取分析结果
analysis_result = st.session_state.get("analysis_result")

if analysis_result:
    # 显示仓库信息
    repo_info = analysis_result.get("repo_info", {})
    repo_url = st.session_state.get("repo_url", "")

    # 收藏功能
    from core.favorites import is_favorite, add_favorite, remove_favorite

    if repo_url:
        is_fav = is_favorite(repo_url)

        # 解析 repo_url 获取名称
        repo_name = repo_info.get("full_name") or repo_info.get("name") or repo_url.replace("https://github.com/", "")
        repo_html_url = repo_info.get("html_url") or repo_url

        # 标题行
        col_title, col_fav = st.columns([5, 1])
        with col_title:
            st.markdown(f"**仓库**: [{repo_name}]({repo_html_url})")
        with col_fav:
            if is_fav:
                if st.button("⭐ 已收藏", key="unfavorite_btn"):
                    remove_favorite(repo_url)
                    st.rerun()
            else:
                if st.button("☆ 收藏", key="favorite_btn"):
                    add_favorite(repo_url, repo_info)
                    st.rerun()

        if repo_info.get("description"):
            st.markdown(f"**描述**: {repo_info.get('description')}")
        if repo_info.get("language"):
            st.markdown(f"**语言**: {repo_info.get('language')}")
        if repo_info.get("stargazers_count"):
            st.markdown(f"**Stars**: {repo_info.get('stargazers_count')}")

    st.markdown("---")

    # 标签页
    tab1, tab2 = st.tabs(["学习文档", "启动指南"])

    with tab1:
        learning_doc = analysis_result.get("learning_doc", "")
        if learning_doc:
            st.markdown(learning_doc)
        else:
            st.markdown("**暂无学习文档**")

    with tab2:
        setup_guide = analysis_result.get("setup_guide", "")
        if setup_guide:
            st.markdown(setup_guide)
        else:
            st.markdown("**暂无启动指南**")

    # 返回首页按钮
    st.markdown("---")
    if st.button("返回首页"):
        st.switch_page("pages/1_🏠_Home.py")
else:
    st.markdown("**请先在首页输入 GitHub 仓库 URL 并生成文档**")
    if st.button("返回首页"):
        st.switch_page("pages/1_🏠_Home.py")