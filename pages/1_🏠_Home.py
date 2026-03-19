import streamlit as st
import time

st.set_page_config(
    page_title="GitGuide - Home",
    page_icon="🚀"
)

# 进度阶段定义 - 更细粒度的阶段
PROGRESS_STAGES = [
    {"name": "正在验证仓库...", "progress": 10, "key": "validating"},
    {"name": "正在获取仓库信息...", "progress": 25, "key": "getting_repo_info"},
    {"name": "正在分析目录结构...", "progress": 45, "key": "analyzing_structure"},
    {"name": "正在生成学习文档...", "progress": 65, "key": "generating_learning_doc"},
    {"name": "正在生成启动指南...", "progress": 85, "key": "generating_setup_guide"},
    {"name": "正在整理结果...", "progress": 95, "key": "finalizing"},
    {"name": "完成！", "progress": 100, "key": "completed"}
]

# 阶段映射 - 用于显示哪个阶段正在进行
STAGE_INDEX_MAP = {stage["key"]: i for i, stage in enumerate(PROGRESS_STAGES)}


def update_progress(stage_key, progress_value, message):
    """更新进度状态"""
    st.session_state["current_stage"] = stage_key
    st.session_state["current_stage_index"] = STAGE_INDEX_MAP.get(stage_key, 0)
    st.session_state["progress_value"] = progress_value
    st.session_state["progress_message"] = message
    # 记录当前阶段开始时间用于计算剩余时间
    if "stage_start_times" not in st.session_state:
        st.session_state["stage_start_times"] = {}
    st.session_state["stage_start_times"][stage_key] = time.time()


def calculate_remaining_time(current_progress):
    """根据已用时间计算预计剩余时间"""
    if "analysis_start_time" not in st.session_state:
        return None

    # 随着进度增加，估算会越来越准确
    if current_progress < 20:
        return None  # 刚开始无法估算

    start_time = st.session_state["analysis_start_time"]
    elapsed = time.time() - start_time

    if current_progress <= 0:
        return None

    # 估算总时间
    total_estimated = elapsed / (current_progress / 100)
    remaining = total_estimated - elapsed

    if remaining <= 0 or remaining > 600:  # 超过10分钟则不显示
        return None

    # 格式化剩余时间
    if remaining < 60:
        return f"约 {int(remaining)} 秒"
    else:
        minutes = int(remaining // 60)
        seconds = int(remaining % 60)
        return f"约 {minutes} 分 {seconds} 秒"


def run_analysis_with_progress(repo_url):
    """带进度显示的分析流程"""
    # 初始化进度状态
    st.session_state["analysis_started"] = True
    st.session_state["analysis_cancelled"] = False
    st.session_state["progress_value"] = 0
    st.session_state["progress_message"] = "正在准备分析..."
    st.session_state["analysis_start_time"] = time.time()
    st.session_state["stage_start_times"] = {}
    st.session_state["repo_url_pending"] = repo_url

    # 根据模式设置进度消息
    mode = st.session_state.get("analysis_mode", "fast")
    if mode == "fast":
        st.session_state["progress_message"] = "正在快速分析..."
    else:
        st.session_state["progress_message"] = "正在详细分析..."

    # 立即刷新页面显示初始状态
    st.rerun()


# ============ 在脚本开头处理待分析任务 ============
# 检测是否有待处理的分析任务
if st.session_state.get("analysis_started") and st.session_state.get("repo_url_pending"):
    pending_url = st.session_state.get("repo_url_pending")

    # 检查是否取消
    if st.session_state.get("analysis_cancelled"):
        # 清理状态
        if "analysis_started" in st.session_state:
            del st.session_state["analysis_started"]
        if "repo_url_pending" in st.session_state:
            del st.session_state["repo_url_pending"]
        st.warning("分析已取消")
    else:
        # 根据模式显示不同的提示信息
        mode = st.session_state.get("analysis_mode", "fast")
        if mode == "fast":
            st.info("⚡ 正在快速分析仓库...（约需 30 秒）")
        else:
            st.info("⏳ 正在详细分析仓库，请耐心等待...（约需 1-2 分钟）")

        try:
            import time as time_module
            from agents.orchestrator import run_with_progress, run_fast

            # 记录开始时间用于显示
            start_time = time_module.time()

            # 根据模式选择分析函数
            if mode == "fast":
                # 快速模式：直接生成文档（带进度回调）
                result = run_fast(
                    pending_url,
                    progress_callback=update_progress
                )
            else:
                # 详细模式：带进度回调的分析
                result = run_with_progress(
                    pending_url,
                    progress_callback=update_progress
                )

            elapsed = time_module.time() - start_time

            if result.get("success"):
                # 保存结果到 session state
                st.session_state["analysis_result"] = result
                st.session_state["repo_url"] = pending_url

                # 添加到历史记录
                from core.history import add_history
                add_history(pending_url, result.get("repo_info", {}))

                # 清理待分析状态
                if "analysis_started" in st.session_state:
                    del st.session_state["analysis_started"]
                if "repo_url_pending" in st.session_state:
                    del st.session_state["repo_url_pending"]
                if "progress_value" in st.session_state:
                    del st.session_state["progress_value"]

                st.success(f"✅ 分析完成！耗时 {int(elapsed)} 秒，正在跳转到文档页面...")
                st.switch_page("pages/2_📚_Documentation.py")
            elif result.get("cancelled"):
                if "analysis_started" in st.session_state:
                    del st.session_state["analysis_started"]
                if "repo_url_pending" in st.session_state:
                    del st.session_state["repo_url_pending"]
                st.warning("分析已取消")
            else:
                st.session_state["analysis_error"] = result.get("error", "未知错误")
                # 清理状态
                if "analysis_started" in st.session_state:
                    del st.session_state["analysis_started"]
                if "repo_url_pending" in st.session_state:
                    del st.session_state["repo_url_pending"]

        except Exception as e:
            st.session_state["analysis_error"] = str(e)
            # 清理状态
            if "analysis_started" in st.session_state:
                del st.session_state["analysis_started"]
            if "repo_url_pending" in st.session_state:
                del st.session_state["repo_url_pending"]


st.title("🚀 GitGuide")
st.markdown("### 快速上手任意 GitHub 仓库")
st.markdown("输入 GitHub 仓库 URL，我们会为您生成详细的学习文档和启动指南")

# 显示错误信息
if st.session_state.get("analysis_error"):
    st.error(f"分析失败: {st.session_state.get('analysis_error')}")
    # 清除错误
    st.session_state.pop("analysis_error", None)

# 判断是否正在分析
is_analyzing = bool(st.session_state.get("analysis_started") and st.session_state.get("repo_url_pending"))

# URL 输入框 - 分析时禁用
repo_url = st.text_input(
    "GitHub 仓库 URL",
    placeholder="https://github.com/user/repo",
    help="请输入完整的 GitHub 仓库链接",
    key="repo_url_input",
    disabled=is_analyzing
)

# 分析模式选择
if "analysis_mode" not in st.session_state:
    st.session_state["analysis_mode"] = "fast"

with st.expander("⚙️ 分析选项", expanded=False):
    analysis_mode = st.radio(
        "选择分析模式",
        ["fast", "detailed"],
        format_func=lambda x: "快速模式（约30秒）" if x == "fast" else "详细模式（约2分钟）",
        index=0 if st.session_state.get("analysis_mode") == "fast" else 1,
        disabled=is_analyzing
    )
    st.session_state["analysis_mode"] = analysis_mode
    if analysis_mode == "fast":
        st.caption("快速模式：直接生成文档，跳过详细分析。适合快速预览。")
    else:
        st.caption("详细模式：先分析仓库结构，再生成文档。内容更丰富但耗时更长。")

# 生成按钮 - 分析时禁用
if st.button("生成文档", type="primary", disabled=is_analyzing):
    if repo_url:
        # 验证 URL 格式
        from core.validators import validate_github_url
        validation_result = validate_github_url(repo_url)

        if not validation_result["valid"]:
            st.error(validation_result["message"])
        else:
            # 根据模式选择不同的分析函数
            if st.session_state.get("analysis_mode") == "fast":
                # 快速模式：直接使用 run_fast
                run_analysis_with_progress(repo_url)
            else:
                # 详细模式：使用带进度的分析
                run_analysis_with_progress(repo_url)
    else:
        st.error("请输入 GitHub 仓库 URL")

# 显示进度条和取消按钮（位于输入区域下方）
if is_analyzing:
    st.markdown("---")

    # 进度条
    progress_value = st.session_state.get("progress_value", 0)
    progress_message = st.session_state.get("progress_message", "分析中...")

    # 计算预计剩余时间
    remaining_time = calculate_remaining_time(progress_value)
    if remaining_time:
        progress_text = f"{progress_message} | 预计剩余: {remaining_time}"
    else:
        progress_text = progress_message

    st.progress(progress_value / 100, text=progress_text)

    # 进度阶段
    current_stage_index = st.session_state.get("current_stage_index", 0)
    st.markdown("**进度阶段：**")
    for i, stage in enumerate(PROGRESS_STAGES):
        if i < current_stage_index:
            st.markdown(f"✅ {stage['name']}")
        elif i == current_stage_index:
            st.markdown(f"🔄 {stage['name']}")
        else:
            st.markdown(f"⏳ {stage['name']}")

    # 取消按钮
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("取消分析", type="secondary", key="cancel_analysis"):
            st.session_state["analysis_cancelled"] = True
            st.rerun()

# 示例仓库 - 分析时显示但不可交互
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
        if not is_analyzing:
            if st.button(f"试用", key=f"example_{repo}"):
                st.session_state["repo_url"] = full_url
                # 立即分析示例仓库
                try:
                    from agents.orchestrator import run
                    result = run(full_url)
                    if result.get("success"):
                        st.session_state["analysis_result"] = result
                        # 添加到历史记录
                        from core.history import add_history
                        add_history(full_url, result.get("repo_info", {}))
                        st.switch_page("pages/2_📚_Documentation.py")
                    else:
                        st.error(f"分析失败: {result.get('error', '未知错误')}")
                except Exception as e:
                    st.error(f"发生错误: {str(e)}")
        else:
            st.markdown("<span style='color: gray;'>试用</span>", unsafe_allow_html=True)

# 历史记录 - 分析时显示但部分禁用
st.markdown("---")
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("### 📜 历史记录")
with col2:
    from core.history import get_history, clear_history
    history = get_history()
    if history and not is_analyzing:
        if st.button("清除历史", key="clear_history"):
            clear_history()
            st.rerun()

if history:
    for i, item in enumerate(history[:5]):
        col_left, col_right = st.columns([4, 1])
        with col_left:
            timestamp = item.get("timestamp", "")[:10]
            st.markdown(f"**{item.get('name', item.get('url', 'Unknown'))}** ({timestamp})")
        with col_right:
            if not is_analyzing:
                if st.button("重新分析", key=f"history_{i}"):
                    st.session_state["repo_url"] = item["url"]
                    try:
                        from agents.orchestrator import run
                        result = run(item["url"])
                        if result.get("success"):
                            st.session_state["analysis_result"] = result
                            # 更新历史记录时间戳
                            from core.history import add_history
                            add_history(item["url"], result.get("repo_info", {}))
                            st.switch_page("pages/2_📚_Documentation.py")
                        else:
                            st.error(f"分析失败: {result.get('error', '未知错误')}")
                    except Exception as e:
                        st.error(f"发生错误: {str(e)}")
            else:
                st.markdown("<span style='color: gray;'>重新分析</span>", unsafe_allow_html=True)
else:
    st.markdown("*暂无历史记录*")

# 收藏仓库 - 分析时显示但部分禁用
st.markdown("---")
st.markdown("### ⭐ 收藏仓库")

from core.favorites import get_favorites, remove_favorite
favorites = get_favorites()

if favorites:
    for i, item in enumerate(favorites):
        col_left, col_mid, col_right = st.columns([3, 1, 1])
        with col_left:
            st.markdown(f"**{item.get('name', item.get('url', 'Unknown'))}**")
        with col_mid:
            if item.get("language"):
                st.markdown(f"_{item.get('language')}_")
        with col_right:
            if not is_analyzing:
                if st.button("移除", key=f"unfav_{i}"):
                    remove_favorite(item["url"])
                    st.rerun()
            else:
                st.markdown("<span style='color: gray;'>移除</span>", unsafe_allow_html=True)

        col_btn, _ = st.columns([1, 4])
        with col_btn:
            if not is_analyzing:
                if st.button("查看文档", key=f"fav_view_{i}"):
                    st.session_state["repo_url"] = item["url"]
                    try:
                        from agents.orchestrator import run
                        result = run(item["url"])
                        if result.get("success"):
                            st.session_state["analysis_result"] = result
                            st.switch_page("pages/2_📚_Documentation.py")
                        else:
                            st.error(f"分析失败: {result.get('error', '未知错误')}")
                    except Exception as e:
                        st.error(f"发生错误: {str(e)}")
            else:
                st.markdown("<span style='color: gray;'>查看文档</span>", unsafe_allow_html=True)
else:
    st.markdown("*暂无收藏仓库，在文档页面可以收藏仓库*")