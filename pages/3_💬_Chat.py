import streamlit as st

st.set_page_config(
    page_title="GitGuide - Chat",
    page_icon="💬"
)

st.title("💬 AI 问答")

# 检查是否有分析结果
analysis_result = st.session_state.get("analysis_result")
repo_url = st.session_state.get("repo_url")

if not analysis_result or not repo_url:
    st.warning("请先在首页输入 GitHub 仓库 URL 并生成文档")
    if st.button("返回首页"):
        st.switch_page("pages/1_🏠_Home.py")
    st.stop()

# 显示当前仓库信息
repo_info = analysis_result.get("repo_info", {})
if repo_info:
    st.markdown(f"**当前项目**: {repo_info.get('name', 'Unknown')}")

st.markdown("---")

# 初始化聊天历史
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示聊天历史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 聊天输入
if prompt := st.chat_input("问关于这个项目的问题..."):
    # 添加用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # 生成 AI 回答
    with st.chat_message("assistant"):
        try:
            from agents.chat_agent import run_chat

            # 获取聊天历史（只保留最近10条，避免上下文过长）
            chat_history = st.session_state.messages[-10:] if len(st.session_state.messages) > 10 else st.session_state.messages

            with st.spinner("AI 正在思考..."):
                result = run_chat(prompt, repo_url, chat_history)

            if result.get("success"):
                response = result.get("response", "抱歉，我无法回答这个问题。")
            else:
                response = f"抱歉，发生错误: {result.get('error', '未知错误')}"

            st.markdown(response)
        except Exception as e:
            response = f"抱歉，发生错误: {str(e)}"
            st.markdown(response)

    # 添加 AI 回答
    st.session_state.messages.append({"role": "assistant", "content": response})

# 侧边栏 - 聊天管理
with st.sidebar:
    st.markdown("### 聊天管理")

    if st.button("清空聊天历史"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("### 快捷问题")

    quick_questions = [
        "这个项目是用来做什么的？",
        "如何在本地运行这个项目？",
        "这个项目的主要依赖有哪些？"
    ]

    for q in quick_questions:
        if st.button(q, key=f"quick_{q}"):
            # 模拟用户输入这个问题
            st.session_state.messages.append({"role": "user", "content": q})

            with st.chat_message("user"):
                st.markdown(q)

            # 生成 AI 回答
            with st.chat_message("assistant"):
                try:
                    from agents.chat_agent import run_chat

                    chat_history = st.session_state.messages[:-1][-10:]

                    with st.spinner("AI 正在思考..."):
                        result = run_chat(q, repo_url, chat_history)

                    if result.get("success"):
                        response = result.get("response", "抱歉，我无法回答这个问题。")
                    else:
                        response = f"抱歉，发生错误: {result.get('error', '未知错误')}"

                    st.markdown(response)
                except Exception as e:
                    response = f"抱歉，发生错误: {str(e)}"
                    st.markdown(response)

            st.session_state.messages.append({"role": "assistant", "content": response})