<template>
  <div class="home">
    <div class="header">
      <h1 class="title">{{ t('app.title', language) }}</h1>
      <p class="subtitle">{{ t('app.subtitle', language) }}</p>
    </div>

    <el-card class="input-card">
      <el-input
        v-model="repoUrl"
        :placeholder="t('home.inputPlaceholder', language)"
        size="large"
        :disabled="store.isAnalyzing"
        @keyup.enter="handleAnalyze"
      >
        <template #prepend>{{ language === 'zh' ? '仓库 URL' : 'Repo URL' }}</template>
      </el-input>

      <el-radio-group v-model="analysisMode" class="mode-select" :disabled="store.isAnalyzing">
        <el-radio value="fast">{{ t('home.fastMode', language) }}</el-radio>
        <el-radio value="detailed">{{ t('home.detailedMode', language) }}</el-radio>
      </el-radio-group>

      <el-button
        type="primary"
        size="large"
        class="analyze-btn"
        :loading="store.isAnalyzing"
        @click="handleAnalyze"
      >
        {{ store.isAnalyzing ? t('home.analyzing', language) : t('home.analyzeBtn', language) }}
      </el-button>
    </el-card>

    <!-- 进度面板 -->
    <el-card v-if="store.isAnalyzing" class="progress-card">
      <el-progress
        :percentage="store.progress"
        :status="store.isFailed ? 'exception' : undefined"
        :stroke-width="20"
      />
      <p class="progress-message">{{ store.progressMessage }}</p>

      <div class="stage-list">
        <div
          v-for="(stage, index) in stages"
          :key="stage.key"
          class="stage-item"
          :class="{
            'stage-completed': getStageIndex(store.stageKey) > index,
            'stage-current': getStageIndex(store.stageKey) === index
          }"
        >
          <span class="stage-icon">{{ getStageIndex(store.stageKey) > index ? '✅' : getStageIndex(store.stageKey) === index ? '🔄' : '⏳' }}</span>
          {{ language === 'zh' ? stage.name : stage.nameEn }}
        </div>
      </div>

      <el-button type="danger" @click="handleCancel">{{ language === 'zh' ? '取消分析' : 'Cancel' }}</el-button>
    </el-card>

    <!-- 错误提示 -->
    <el-alert v-if="store.error" :title="store.error" type="error" show-icon closable @close="store.error = ''" />

    <!-- 示例仓库 -->
    <el-card class="example-card">
      <template #header>
        <span>{{ t('home.examples', language) }}</span>
      </template>
      <div v-for="[repo, desc] in exampleRepos" :key="repo" class="example-item">
        <span><strong>{{ repo }}</strong> - {{ language === 'zh' ? desc[0] : desc[1] }}</span>
        <el-button size="small" :disabled="store.isAnalyzing" @click="handleExample(repo)">{{ language === 'zh' ? '试用' : 'Try' }}</el-button>
      </div>
    </el-card>

    <!-- 已分析仓库 -->
    <el-card class="saved-repos-card">
      <template #header>
        <div class="card-header">
          <span>{{ language === 'zh' ? '📚 已分析仓库' : '📚 Saved Repositories' }}</span>
          <el-button text @click="$router.push('/repositories')">{{ language === 'zh' ? '查看全部' : 'View All' }}</el-button>
        </div>
      </template>
      <div v-if="savedRepos.length === 0" class="empty-text">{{ language === 'zh' ? '暂无已分析的仓库' : 'No saved repositories' }}</div>
      <div v-else>
        <div v-for="(item, index) in savedRepos.slice(0, 5)" :key="index" class="saved-repo-item">
          <span><strong>{{ item.name || item.url }}</strong> ({{ formatDate(item.updated_at) }})</span>
          <el-button size="small" :disabled="store.isAnalyzing" @click="viewSavedRepo(item)">{{ language === 'zh' ? '查看' : 'View' }}</el-button>
        </div>
      </div>
    </el-card>

    <!-- 历史记录 -->
    <el-card class="history-card">
      <template #header>
        <div class="card-header">
          <span>{{ t('home.history', language) }}</span>
          <el-button v-if="history.length > 0" text @click="handleClearHistory">{{ t('home.clearHistory', language) }}</el-button>
        </div>
      </template>
      <div v-if="history.length === 0" class="empty-text">{{ t('home.noHistory', language) }}</div>
      <div v-else>
        <div v-for="(item, index) in history.slice(0, 5)" :key="index" class="history-item">
          <span><strong>{{ item.name }}</strong> ({{ item.timestamp?.slice(0, 10) }})</span>
          <el-button size="small" :disabled="store.isAnalyzing" @click="handleHistory(item.url)">{{ t('home.reAnalyze', language) }}</el-button>
        </div>
      </div>
    </el-card>

    <!-- 收藏仓库 -->
    <el-card class="favorites-card">
      <template #header>
        <span>{{ t('home.favorites', language) }}</span>
      </template>
      <div v-if="favorites.length === 0" class="empty-text">{{ t('home.noFavorites', language) }}</div>
      <div v-else>
        <div v-for="(item, index) in favorites" :key="index" class="favorite-item">
          <span><strong>{{ item.name }}</strong> {{ item.language ? `_${item.language}_` : '' }}</span>
          <div>
            <el-button size="small" :disabled="store.isAnalyzing" @click="handleFavorite(item.url)">{{ t('home.viewDocs', language) }}</el-button>
            <el-button size="small" type="danger" text @click="handleUnfavorite(item.url)">{{ t('home.remove', language) }}</el-button>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
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
const analysisMode = ref('fast')
const history = ref([])
const favorites = ref([])
const savedRepos = ref([])

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
  { key: 'validating', name: '正在验证仓库...', nameEn: 'Validating repository...' },
  { key: 'getting_repo_info', name: '正在获取仓库信息...', nameEn: 'Fetching repo info...' },
  { key: 'analyzing_structure', name: '正在分析目录结构...', nameEn: 'Analyzing structure...' },
  { key: 'generating_learning_doc', name: '正在生成学习文档...', nameEn: 'Generating learning docs...' },
  { key: 'generating_setup_guide', name: '正在生成启动指南...', nameEn: 'Generating setup guide...' },
  { key: 'finalizing', name: '正在整理结果...', nameEn: 'Finalizing...' },
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

  await store.start(url, analysisMode.value)

  if (store.isCompleted) {
    router.push('/docs')
  }
}

function handleCancel() {
  store.cancel()
}

async function handleExample(repo) {
  repoUrl.value = `https://github.com/${repo}`
  await store.start(repoUrl.value, 'fast')
  if (store.isCompleted) {
    router.push('/docs')
  }
}

async function handleHistory(url) {
  repoUrl.value = url
  await store.start(url, 'fast')
  if (store.isCompleted) {
    router.push('/docs')
  }
}

async function handleFavorite(url) {
  repoUrl.value = url
  await store.start(url, 'fast')
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
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.title {
  font-size: 2.5em;
  margin-bottom: 10px;
}

.subtitle {
  color: var(--text-color-secondary, #666);
  font-size: 1.2em;
}

.input-card {
  margin-bottom: 20px;
}

.input-card .el-input {
  margin-bottom: 15px;
}

.mode-select {
  display: block;
  margin-bottom: 15px;
}

.analyze-btn {
  width: 100%;
}

.progress-card {
  margin-bottom: 20px;
}

.progress-message {
  margin: 15px 0;
  text-align: center;
  color: var(--primary-color, #409eff);
}

.stage-list {
  margin-bottom: 15px;
}

.stage-item {
  padding: 5px 0;
  color: #999;
}

.stage-completed {
  color: #67c23a;
}

.stage-current {
  color: var(--primary-color, #409eff);
}

.stage-icon {
  margin-right: 8px;
}

.example-card,
.history-card,
.favorites-card,
.saved-repos-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.example-item,
.history-item,
.favorite-item,
.saved-repo-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid var(--border-color, #eee);
}

.example-item:last-child,
.history-item:last-child,
.favorite-item:last-child,
.saved-repo-item:last-child {
  border-bottom: none;
}

.empty-text {
  color: var(--text-color-secondary, #999);
  text-align: center;
  padding: 20px;
}
</style>