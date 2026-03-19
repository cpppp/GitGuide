<template>
  <div class="home">
    <div class="header">
      <h1 class="title">🚀 GitGuide</h1>
      <p class="subtitle">快速上手任意 GitHub 仓库</p>
    </div>

    <el-card class="input-card">
      <el-input
        v-model="repoUrl"
        placeholder="https://github.com/user/repo"
        size="large"
        :disabled="store.isAnalyzing"
        @keyup.enter="handleAnalyze"
      >
        <template #prepend>仓库 URL</template>
      </el-input>

      <el-radio-group v-model="analysisMode" class="mode-select" :disabled="store.isAnalyzing">
        <el-radio value="fast">快速模式（约30秒）</el-radio>
        <el-radio value="detailed">详细模式（约2分钟）</el-radio>
      </el-radio-group>

      <el-button
        type="primary"
        size="large"
        class="analyze-btn"
        :loading="store.isAnalyzing"
        @click="handleAnalyze"
      >
        {{ store.isAnalyzing ? '分析中...' : '生成文档' }}
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
          {{ stage.name }}
        </div>
      </div>

      <el-button type="danger" @click="handleCancel">取消分析</el-button>
    </el-card>

    <!-- 错误提示 -->
    <el-alert v-if="store.error" :title="store.error" type="error" show-icon closable @close="store.error = ''" />

    <!-- 示例仓库 -->
    <el-card class="example-card">
      <template #header>
        <span>示例仓库</span>
      </template>
      <div v-for="[repo, desc] in exampleRepos" :key="repo" class="example-item">
        <span><strong>{{ repo }}</strong> - {{ desc }}</span>
        <el-button size="small" :disabled="store.isAnalyzing" @click="handleExample(repo)">试用</el-button>
      </div>
    </el-card>

    <!-- 历史记录 -->
    <el-card class="history-card">
      <template #header>
        <div class="card-header">
          <span>📜 历史记录</span>
          <el-button v-if="history.length > 0" text @click="handleClearHistory">清除历史</el-button>
        </div>
      </template>
      <div v-if="history.length === 0" class="empty-text">暂无历史记录</div>
      <div v-else>
        <div v-for="(item, index) in history.slice(0, 5)" :key="index" class="history-item">
          <span><strong>{{ item.name }}</strong> ({{ item.timestamp?.slice(0, 10) }})</span>
          <el-button size="small" :disabled="store.isAnalyzing" @click="handleHistory(item.url)">重新分析</el-button>
        </div>
      </div>
    </el-card>

    <!-- 收藏仓库 -->
    <el-card class="favorites-card">
      <template #header>
        <span>⭐ 收藏仓库</span>
      </template>
      <div v-if="favorites.length === 0" class="empty-text">暂无收藏仓库</div>
      <div v-else>
        <div v-for="(item, index) in favorites" :key="index" class="favorite-item">
          <span><strong>{{ item.name }}</strong> {{ item.language ? `_${item.language}_` : '' }}</span>
          <div>
            <el-button size="small" :disabled="store.isAnalyzing" @click="handleFavorite(item.url)">查看文档</el-button>
            <el-button size="small" type="danger" text @click="handleUnfavorite(item.url)">移除</el-button>
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
import { getHistory, clearHistory, getFavorites, removeFavorite } from '@/api/analyze'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const store = useAnalysisStore()

const repoUrl = ref('')
const analysisMode = ref('fast')
const history = ref([])
const favorites = ref([])

// 监听分析完成事件
function handleAnalysisCompleted(event) {
  const result = event.detail
  if (result) {
    ElMessageBox.alert(
      '文档生成完成！点击"查看文档"按钮查看生成的学习文档和启动指南。',
      '✅ 分析完成',
      {
        confirmButtonText: '查看文档',
        cancelButtonText: '留在本页',
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

const exampleRepos = [
  ['python/cpython', 'Python 官方解释器'],
  ['facebook/react', 'React 前端框架'],
  ['gin-gonic/gin', 'Go Web 框架']
]

const stages = [
  { key: 'validating', name: '正在验证仓库...' },
  { key: 'getting_repo_info', name: '正在获取仓库信息...' },
  { key: 'analyzing_structure', name: '正在分析目录结构...' },
  { key: 'generating_learning_doc', name: '正在生成学习文档...' },
  { key: 'generating_setup_guide', name: '正在生成启动指南...' },
  { key: 'finalizing', name: '正在整理结果...' },
  { key: 'completed', name: '完成！' }
]

function getStageIndex(key) {
  return stages.findIndex(s => s.key === key)
}

async function handleAnalyze() {
  if (!repoUrl.value) {
    ElMessage.error('请输入 GitHub 仓库 URL')
    return
  }

  // 验证 URL 格式
  if (!repoUrl.value.includes('github.com')) {
    ElMessage.error('请输入有效的 GitHub 仓库 URL')
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

onMounted(() => {
  loadHistory()
  loadFavorites()
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
  color: #666;
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
  color: #409eff;
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
  color: #409eff;
}

.stage-icon {
  margin-right: 8px;
}

.example-card,
.history-card,
.favorites-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.example-item,
.history-item,
.favorite-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.example-item:last-child,
.history-item:last-child,
.favorite-item:last-child {
  border-bottom: none;
}

.empty-text {
  color: #999;
  text-align: center;
  padding: 20px;
}
</style>