<template>
  <div class="home">
    <!-- 英雄区 -->
    <div class="hero">
      <div class="hero-decoration">
        <div class="deco-line deco-line-1"></div>
        <div class="deco-line deco-line-2"></div>
        <div class="deco-dot deco-dot-1"></div>
        <div class="deco-dot deco-dot-2"></div>
      </div>
      <div class="hero-content">
        <div class="hero-icon">
          <svg viewBox="0 0 80 80" class="hero-svg">
            <defs>
              <linearGradient id="heroGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#3d5a6c" />
                <stop offset="100%" style="stop-color:#2c3e4a" />
              </linearGradient>
              <linearGradient id="accentGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" style="stop-color:#c4a35a" />
                <stop offset="100%" style="stop-color:#b8956e" />
              </linearGradient>
            </defs>
            <!-- 外圈 -->
            <circle cx="40" cy="40" r="38" fill="none" stroke="url(#heroGrad)" stroke-width="1" opacity="0.2"/>
            <circle cx="40" cy="40" r="32" fill="none" stroke="url(#heroGrad)" stroke-width="1" opacity="0.3"/>
            <!-- 书本轮廓 -->
            <path d="M20 25 L20 60 Q20 62 22 62 L38 62 Q40 62 40 60 L40 25 Q40 23 38 23 L22 23 Q20 23 20 25Z" fill="url(#heroGrad)" opacity="0.15"/>
            <path d="M40 25 L40 60 Q40 62 42 62 L58 62 Q60 62 60 60 L60 25 Q60 23 58 23 L42 23 Q40 23 40 25Z" fill="url(#heroGrad)" opacity="0.08"/>
            <!-- 装饰线条 -->
            <line x1="24" y1="32" x2="36" y2="32" stroke="url(#accentGrad)" stroke-width="2" stroke-linecap="round"/>
            <line x1="24" y1="40" x2="34" y2="40" stroke="url(#heroGrad)" stroke-width="1.5" stroke-linecap="round" opacity="0.5"/>
            <line x1="24" y1="47" x2="32" y2="47" stroke="url(#heroGrad)" stroke-width="1.5" stroke-linecap="round" opacity="0.3"/>
            <!-- 右侧装饰 -->
            <line x1="44" y1="35" x2="56" y2="35" stroke="url(#accentGrad)" stroke-width="2" stroke-linecap="round"/>
            <line x1="44" y1="43" x2="52" y2="43" stroke="url(#heroGrad)" stroke-width="1.5" stroke-linecap="round" opacity="0.5"/>
            <line x1="44" y1="51" x2="50" y2="51" stroke="url(#heroGrad)" stroke-width="1.5" stroke-linecap="round" opacity="0.3"/>
          </svg>
        </div>
        <h1 class="hero-title">
          <span class="title-main">{{ t('app.title', language) }}</span>
          <span class="title-sub">{{ t('app.subtitle', language) }}</span>
        </h1>
        <p class="hero-desc">
          {{ language === 'zh'
            ? '输入任意 GitHub 仓库，获得结构化学习文档、快速启动指南和 AI 问答支持'
            : 'Enter any GitHub repository to get structured learning docs, quick start guides, and AI-powered Q&A support'
          }}
        </p>
      </div>
    </div>

    <!-- 输入区域 -->
    <el-card class="input-card">
      <div class="input-wrapper">
        <div class="input-icon">
          <svg viewBox="0 0 24 24" width="20" height="20">
            <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
          </svg>
        </div>
        <el-input
          v-model="repoUrl"
          :placeholder="t('home.inputPlaceholder', language)"
          size="large"
          class="repo-input"
          :disabled="store.isAnalyzing"
          @keyup.enter="handleAnalyze"
        />
        <el-button
          type="primary"
          size="large"
          class="analyze-btn"
          :loading="store.isAnalyzing"
          @click="handleAnalyze"
        >
          <span v-if="!store.isAnalyzing" class="btn-icon">⚡</span>
          {{ store.isAnalyzing ? t('home.analyzing', language) : t('home.analyzeBtn', language) }}
        </el-button>
      </div>
    </el-card>

    <!-- 进度面板 -->
    <transition name="progress-slide">
      <div v-if="store.isAnalyzing" class="progress-bar-container">
        <div class="progress-inner">
          <div class="progress-info">
            <span class="progress-label">{{ language === 'zh' ? '正在分析' : 'Analyzing' }}</span>
            <span class="progress-percent">{{ store.progress }}%</span>
          </div>
          <el-progress
            :percentage="store.progress"
            :status="store.isFailed ? 'exception' : undefined"
            :stroke-width="6"
            :show-text="false"
            class="compact-progress"
          />
          <div class="stage-mini">
            <span
              v-for="(stage, index) in stages"
              :key="stage.key"
              class="stage-mini-item"
              :class="{
                'stage-completed': getStageIndex(store.stageKey) > index,
                'stage-current': getStageIndex(store.stageKey) === index
              }"
            >
              <span class="stage-mini-dot"></span>
              {{ language === 'zh' ? stage.name : stage.nameEn }}
            </span>
          </div>
        </div>
        <el-button size="small" type="danger" text @click="handleCancel" class="cancel-btn">
          ×
        </el-button>
      </div>
    </transition>

    <!-- 错误提示 -->
    <transition name="fade">
      <el-alert v-if="store.error" :title="store.error" type="error" show-icon closable @close="store.error = ''" class="error-alert" />
    </transition>

    <!-- 内容区域 -->
    <div class="content-section">
      <!-- 示例仓库 -->
      <el-card class="example-card">
        <template #header>
          <div class="card-header">
            <span class="card-icon">✦</span>
            <span>{{ t('home.examples', language) }}</span>
          </div>
        </template>
        <div class="example-list">
          <div v-for="[repo, desc] in exampleRepos" :key="repo" class="example-item">
            <div class="example-info">
              <span class="example-name">{{ repo }}</span>
              <span class="example-desc">{{ language === 'zh' ? desc[0] : desc[1] }}</span>
            </div>
            <el-button size="small" :disabled="store.isAnalyzing" @click="handleExample(repo)">
              {{ language === 'zh' ? '试用' : 'Try' }}
            </el-button>
          </div>
        </div>
      </el-card>

      <!-- 数据标签页 -->
      <el-card class="data-tabs-card">
        <template #header>
          <div class="data-tabs-header">
            <span
              v-for="tab in dataTabs"
              :key="tab.key"
              class="data-tab-item"
              :class="{ 'is-active': activeDataTab === tab.key }"
              @click="activeDataTab = tab.key"
            >
              <span class="tab-icon">{{ tab.icon }}</span>
              <span class="tab-text">{{ language === 'zh' ? tab.name : tab.nameEn }}</span>
              <span class="tab-count">{{ tab.count }}</span>
            </span>
          </div>
        </template>

        <!-- 已分析仓库 -->
        <div v-show="activeDataTab === 'saved'" class="data-content">
          <div v-if="savedRepos.length === 0" class="empty-state-small">
            <span class="empty-icon">📭</span>
            <span>{{ language === 'zh' ? '暂无已分析的仓库' : 'No saved repositories' }}</span>
          </div>
          <div v-else class="data-list">
            <div v-for="(item, index) in savedRepos.slice(0, 5)" :key="index" class="data-item">
              <div class="data-item-info">
                <span class="data-item-name">{{ item.name || item.url }}</span>
                <span class="data-item-date">{{ formatDate(item.updated_at) }}</span>
              </div>
              <div class="data-item-actions">
                <el-button size="small" :disabled="store.isAnalyzing" @click="viewSavedRepo(item)">
                  {{ language === 'zh' ? '查看' : 'View' }}
                </el-button>
                <el-button size="small" type="danger" text @click="handleDeleteSavedRepo(item.url)">×</el-button>
              </div>
            </div>
            <el-button v-if="savedRepos.length > 5" text @click="$router.push('/repositories')" class="view-more-btn">
              {{ language === 'zh' ? '查看全部 →' : 'View All →' }}
            </el-button>
          </div>
        </div>

        <!-- 收藏仓库 -->
        <div v-show="activeDataTab === 'favorites'" class="data-content">
          <div v-if="favorites.length === 0" class="empty-state-small">
            <span class="empty-icon">☆</span>
            <span>{{ t('home.noFavorites', language) }}</span>
          </div>
          <div v-else class="data-list">
            <div v-for="(item, index) in favorites.slice(0, 5)" :key="index" class="data-item">
              <div class="data-item-info">
                <span class="data-item-name">{{ item.name }}</span>
                <el-tag v-if="item.language" size="small">{{ item.language }}</el-tag>
              </div>
              <div class="data-item-actions">
                <el-button size="small" :disabled="store.isAnalyzing" @click="handleFavorite(item.url)">
                  {{ t('home.viewDocs', language) }}
                </el-button>
                <el-button size="small" type="danger" text @click="handleUnfavorite(item.url)">×</el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- 历史记录 -->
        <div v-show="activeDataTab === 'history'" class="data-content">
          <div v-if="history.length === 0" class="empty-state-small">
            <span class="empty-icon">📋</span>
            <span>{{ t('home.noHistory', language) }}</span>
          </div>
          <div v-else class="data-list">
            <div v-for="(item, index) in history.slice(0, 5)" :key="index" class="data-item">
              <div class="data-item-info">
                <span class="data-item-name">{{ item.name }}</span>
                <span class="data-item-date">{{ item.timestamp?.slice(0, 10) }}</span>
              </div>
              <el-button size="small" :disabled="store.isAnalyzing" @click="handleHistory(item.url)">
                {{ t('home.reAnalyze', language) }}
              </el-button>
            </div>
            <el-button v-if="history.length > 0" text @click="handleClearHistory" class="clear-history-btn">
              {{ t('home.clearHistory', language) }}
            </el-button>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAnalysisStore } from '@/stores/analysis'
import { useSettingsStore } from '@/stores/settings'
import { storeToRefs } from 'pinia'
import { getHistory, clearHistory, getFavorites, removeFavorite } from '@/api/analyze'
import { ElMessage, ElMessageBox } from 'element-plus'
import { t } from '@/i18n'

const router = useRouter()
const store = useAnalysisStore()
const settingsStore = useSettingsStore()
const { language } = storeToRefs(settingsStore)

const repoUrl = ref('')
const history = ref([])
const favorites = ref([])
const savedRepos = ref([])
const activeDataTab = ref('saved')

const dataTabs = computed(() => [
  { key: 'saved', name: '已分析', nameEn: 'Saved', icon: '📚', count: savedRepos.value.length },
  { key: 'favorites', name: '收藏', nameEn: 'Favorites', icon: '⭐', count: favorites.value.length },
  { key: 'history', name: '历史', nameEn: 'History', icon: '📜', count: history.value.length }
])

// 监听分析完成事件
function handleAnalysisCompleted(event) {
  const result = event.detail
  if (result) {
    ElMessageBox.alert(
      language.value === 'zh'
        ? '文档生成完成！点击"查看文档"按钮查看生成的学习文档和启动指南。'
        : 'Documentation generated! Click "View Docs" to see the learning docs and setup guide.',
      language.value === 'zh' ? '✅ 分析完成' : '✅ Analysis Complete',
      {
        confirmButtonText: language.value === 'zh' ? '查看文档' : 'View Docs',
        cancelButtonText: language.value === 'zh' ? '留在本页' : 'Stay Here',
        type: 'success'
      }
    ).then(() => {
      router.push('/docs')
    }).catch(() => {
      // 用户点击留在本页
    })
  }
}

onMounted(() => {
  window.addEventListener('analysis-completed', handleAnalysisCompleted)
})

onUnmounted(() => {
  window.removeEventListener('analysis-completed', handleAnalysisCompleted)
})

// 示例仓库: [repo, [中文描述, 英文描述]]
const exampleRepos = [
  ['python/cpython', ['Python 官方解释器', 'Python Interpreter']],
  ['facebook/react', ['React 前端框架', 'React Frontend Framework']],
  ['gin-gonic/gin', ['Go Web 框架', 'Go Web Framework']]
]

const stages = [
  { key: 'starting', name: '正在启动...', nameEn: 'Starting...' },
  { key: 'cloning', name: '正在克隆仓库...', nameEn: 'Cloning repository...' },
  { key: 'getting_info', name: '正在获取仓库信息...', nameEn: 'Fetching repo info...' },
  { key: 'generating', name: '正在生成文档...', nameEn: 'Generating documentation...' },
  { key: 'completed', name: '完成！', nameEn: 'Complete!' }
]

function getStageIndex(key) {
  return stages.findIndex(s => s.key === key)
}

async function handleAnalyze() {
  if (!repoUrl.value) {
    ElMessage.error(language.value === 'zh' ? '请输入 GitHub 仓库 URL' : 'Please enter a GitHub repo URL')
    return
  }

  // 验证 URL 格式
  if (!repoUrl.value.includes('github.com')) {
    ElMessage.error(language.value === 'zh' ? '请输入有效的 GitHub 仓库 URL' : 'Please enter a valid GitHub repo URL')
    return
  }

  // 确保 URL 格式正确
  let url = repoUrl.value.trim()
  if (!url.startsWith('http')) {
    url = 'https://' + url
  }

  await store.start(url)

  if (store.isCompleted) {
    router.push('/docs')
  }
}

function handleCancel() {
  store.cancel()
}

async function handleExample(repo) {
  repoUrl.value = `https://github.com/${repo}`
  await store.start(repoUrl.value)
  if (store.isCompleted) {
    router.push('/docs')
  }
}

async function handleHistory(url) {
  repoUrl.value = url
  await store.start(url)
  if (store.isCompleted) {
    router.push('/docs')
  }
}

async function handleFavorite(url) {
  repoUrl.value = url
  await store.start(url)
  if (store.isCompleted) {
    router.push('/docs')
  }
}

async function handleUnfavorite(url) {
  await removeFavorite(url)
  loadFavorites()
}

async function handleClearHistory() {
  await clearHistory()
  loadHistory()
}

async function handleDeleteSavedRepo(url) {
  try {
    await ElMessageBox.confirm(
      language.value === 'zh'
        ? '确定要删除这个已分析的仓库吗？'
        : 'Are you sure you want to delete this analyzed repository?',
      language.value === 'zh' ? '确认删除' : 'Confirm Delete',
      {
        confirmButtonText: language.value === 'zh' ? '删除' : 'Delete',
        cancelButtonText: language.value === 'zh' ? '取消' : 'Cancel',
        type: 'warning'
      }
    )
    const response = await fetch(`/api/repositories/${encodeURIComponent(url)}`, {
      method: 'DELETE'
    })
    const data = await response.json()
    if (data.success) {
      savedRepos.value = savedRepos.value.filter(r => r.url !== url)
      ElMessage.success(language.value === 'zh' ? '已删除' : 'Deleted')
    } else {
      ElMessage.error(language.value === 'zh' ? '删除失败' : 'Failed to delete')
    }
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(language.value === 'zh' ? '删除失败' : 'Failed to delete')
    }
  }
}

async function loadHistory() {
  try {
    const response = await getHistory()
    history.value = response.data
  } catch (e) {
    console.error('Failed to load history:', e)
  }
}

async function loadFavorites() {
  try {
    const response = await getFavorites()
    favorites.value = response.data
  } catch (e) {
    console.error('Failed to load favorites:', e)
  }
}

async function loadSavedRepos() {
  try {
    const response = await fetch('/api/repositories')
    const data = await response.json()
    savedRepos.value = data.repositories || []
  } catch (e) {
    console.error('Failed to load saved repos:', e)
  }
}

function formatDate(dateString) {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString()
}

function viewSavedRepo(item) {
  const urlParts = item.url.replace('https://github.com/', '').split('/')
  const fullName = urlParts.join('/')

  store.setRepoUrl(item.url)
  store.setResult({
    repo_url: item.url,
    repo_info: {
      full_name: fullName,
      name: item.name || fullName.split('/')[1],
      description: item.description || '',
      language: item.language || '',
      stargazers_count: item.stars || 0,
      html_url: item.url
    },
    // V3.0 文档
    quick_start: item.quick_start,
    overview: item.overview,
    architecture: item.architecture,
    install_guide: item.install_guide,
    // V3.1 新文档
    usage_tutorial: item.usage_tutorial,
    dev_guide: item.dev_guide,
    troubleshooting: item.troubleshooting,
    // V3.1 代码图谱数据
    code_graph: item.code_graph,
    examples: item.examples,
    // 旧字段（兼容）
    learning_doc: item.learning_doc,
    setup_guide: item.setup_guide
  })
  router.push('/docs')
}

onMounted(() => {
  loadHistory()
  loadFavorites()
  loadSavedRepos()
})
</script>

<style scoped>
.home {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}

/* 英雄区 */
.hero {
  text-align: center;
  padding: 40px 20px 50px;
  position: relative;
  margin-bottom: 20px;
}

.hero-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  overflow: hidden;
}

.deco-line {
  position: absolute;
  background: linear-gradient(90deg, transparent, var(--accent-color), transparent);
  opacity: 0.15;
  height: 1px;
}

.deco-line-1 {
  width: 200px;
  top: 30%;
  left: -50px;
  transform: rotate(-15deg);
}

.deco-line-2 {
  width: 150px;
  top: 60%;
  right: -30px;
  transform: rotate(20deg);
}

.deco-dot {
  position: absolute;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--accent-color);
  opacity: 0.2;
}

.deco-dot-1 {
  top: 20%;
  right: 15%;
}

.deco-dot-2 {
  bottom: 25%;
  left: 10%;
}

.hero-content {
  position: relative;
  z-index: 1;
}

.hero-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 24px;
  animation: float-icon 6s ease-in-out infinite;
}

@keyframes float-icon {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

.hero-svg {
  width: 100%;
  height: 100%;
}

.hero-title {
  margin: 0 0 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.title-main {
  font-family: 'Noto Serif SC', 'Crimson Pro', Georgia, serif;
  font-size: 2.8em;
  font-weight: 700;
  color: var(--text-color);
  letter-spacing: 0.02em;
  background: linear-gradient(135deg, var(--text-color) 0%, var(--primary-color) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.title-sub {
  font-size: 1.1em;
  color: var(--text-color-secondary);
  font-weight: 400;
}

.hero-desc {
  color: var(--text-color-muted);
  font-size: 15px;
  max-width: 560px;
  margin: 0 auto;
  line-height: 1.8;
}

/* 输入卡片 */
.input-card {
  margin-bottom: 24px;
  padding: 24px !important;
}

.input-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.input-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-warm);
  border-radius: var(--radius-md);
  color: var(--primary-color);
  flex-shrink: 0;
}

.repo-input {
  flex: 1;
}

.repo-input :deep(.el-input__wrapper) {
  padding: 8px 16px !important;
}

.analyze-btn {
  flex-shrink: 0;
  min-width: 140px;
  height: 48px !important;
  font-size: 15px !important;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-icon {
  font-size: 16px;
}

.input-options {
  display: flex;
  justify-content: center;
}

.mode-select :deep(.el-radio-button__inner) {
  padding: 10px 20px;
  font-size: 14px;
}

.mode-select :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
  border-color: var(--primary-color);
  box-shadow: none;
}

.mode-icon {
  margin-right: 6px;
}

/* 进度条容器 - 紧凑设计 */
.progress-bar-container {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 14px 20px;
  background: var(--bg-paper);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  margin-bottom: 20px;
  box-shadow: var(--shadow-sm);
}

.progress-inner {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.progress-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-color-secondary);
}

.progress-percent {
  font-size: 13px;
  font-weight: 600;
  color: var(--primary-color);
}

.compact-progress {
  width: 100%;
}

.compact-progress :deep(.el-progress-bar__outer) {
  height: 6px !important;
  border-radius: 3px !important;
}

.compact-progress :deep(.el-progress-bar__inner) {
  border-radius: 3px !important;
}

.stage-mini {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.stage-mini-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: var(--text-color-muted);
  transition: all var(--transition-fast);
}

.stage-mini-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--border-color);
  transition: all var(--transition-fast);
}

.stage-mini-item.stage-completed {
  color: var(--success-color);
}

.stage-mini-item.stage-completed .stage-mini-dot {
  background: var(--success-color);
}

.stage-mini-item.stage-current {
  color: var(--primary-color);
}

.stage-mini-item.stage-current .stage-mini-dot {
  background: var(--primary-color);
  animation: pulse-dot 1.5s ease-in-out infinite;
}

.cancel-btn {
  font-size: 18px;
  padding: 4px 8px;
  color: var(--text-color-muted);
}

.cancel-btn:hover {
  color: var(--danger-color);
}

@keyframes pulse-dot {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.3); opacity: 0.7; }
}

/* 错误提示 */
.error-alert {
  margin-bottom: 24px;
}

/* 内容区域 */
.content-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 示例卡片 */
.example-card {
  padding: 0 !important;
}

.example-card :deep(.el-card__header) {
  padding: 18px 24px !important;
}

.example-list {
  padding: 8px 24px 20px;
}

.example-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  background: var(--bg-warm);
  border-radius: var(--radius-md);
  margin-bottom: 10px;
  transition: all var(--transition-normal);
}

.example-item:last-child {
  margin-bottom: 0;
}

.example-item:hover {
  transform: translateX(4px);
  box-shadow: var(--shadow-sm);
}

.example-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.example-name {
  font-weight: 600;
  color: var(--text-color);
  font-family: 'Crimson Pro', monospace;
  font-size: 15px;
}

.example-desc {
  font-size: 13px;
  color: var(--text-color-muted);
}

/* 数据标签页卡片 */
.data-tabs-card {
  padding: 0 !important;
}

.data-tabs-header {
  display: flex;
  gap: 8px;
  padding: 0 4px;
}

.data-tab-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-normal);
  color: var(--text-color-secondary);
  font-size: 14px;
  border: 1px solid transparent;
}

.data-tab-item:hover {
  background: var(--bg-warm);
  color: var(--text-color);
}

.data-tab-item.is-active {
  background: var(--bg-warm);
  color: var(--primary-color);
  border-color: var(--border-light);
}

.data-tab-item .tab-icon {
  font-size: 15px;
}

.data-tab-item .tab-count {
  font-size: 12px;
  padding: 2px 8px;
  background: var(--border-light);
  border-radius: 10px;
  color: var(--text-color-muted);
}

.data-tab-item.is-active .tab-count {
  background: var(--primary-color);
  color: #fff;
}

.data-content {
  padding: 8px 16px 16px;
}

.data-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.data-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--bg-warm);
  border-radius: var(--radius-md);
  transition: all var(--transition-normal);
}

.data-item:hover {
  transform: translateX(4px);
  box-shadow: var(--shadow-sm);
}

.data-item-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.data-item-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-color);
}

.data-item-date {
  font-size: 12px;
  color: var(--text-color-muted);
}

.data-item-actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

.view-more-btn,
.clear-history-btn {
  margin-top: 8px;
  color: var(--primary-color);
  font-size: 13px;
}

.empty-state-small {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 24px;
  color: var(--text-color-muted);
  font-size: 14px;
}

.empty-icon {
  font-size: 24px;
  opacity: 0.4;
}

/* 过渡动画 */
.progress-slide-enter-active,
.progress-slide-leave-active {
  transition: all 0.4s ease;
}

.progress-slide-enter-from,
.progress-slide-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>