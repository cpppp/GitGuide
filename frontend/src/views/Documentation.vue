<template>
  <div class="docs">
    <div class="header">
      <el-button text @click="$router.push('/')">← 返回首页</el-button>
      <h1 class="title">{{ repoInfo?.name || '文档' }}</h1>
    </div>

    <div v-if="!store.result" class="empty-state">
      <el-empty description="暂无分析结果，请先分析仓库">
        <el-button type="primary" @click="$router.push('/')">去分析</el-button>
      </el-empty>
    </div>

    <div v-else class="content">
      <!-- 仓库信息 -->
      <el-card class="info-card">
        <div class="repo-info">
          <h2>{{ repoInfo?.full_name }}</h2>
          <p>{{ repoInfo?.description }}</p>
          <div class="repo-meta">
            <el-tag v-if="repoInfo?.language">{{ repoInfo.language }}</el-tag>
            <span>⭐ {{ repoInfo?.stargazers_count || 0 }}</span>
            <a :href="repoInfo?.html_url" target="_blank">在 GitHub 查看 →</a>
          </div>
          <el-button
            :type="isFavorited ? 'warning' : 'default'"
            @click="handleToggleFavorite"
          >
            {{ isFavorited ? '⭐ 已收藏' : '☆ 收藏' }}
          </el-button>
        </div>
      </el-card>

      <!-- 文档标签页 -->
      <el-tabs v-model="activeTab" class="doc-tabs">
        <el-tab-pane label="学习文档" name="learning">
          <div class="markdown-content" v-html="renderMarkdown(store.result?.learning_doc || '')"></div>
        </el-tab-pane>
        <el-tab-pane label="启动指南" name="setup">
          <div class="markdown-content" v-html="renderMarkdown(store.result?.setup_guide || '')"></div>
        </el-tab-pane>
      </el-tabs>

      <!-- 操作按钮 -->
      <div class="actions">
        <el-button type="primary" @click="$router.push('/chat')">💬 AI 问答</el-button>
        <el-button @click="handleExport">📥 导出 Markdown</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAnalysisStore } from '@/stores/analysis'
import { marked } from 'marked'
import hljs from 'highlight.js'
import { getFavorites, addFavorite, removeFavorite } from '@/api/analyze'
import { ElMessage } from 'element-plus'

const router = useRouter()
const store = useAnalysisStore()

const activeTab = ref('learning')
const favorites = ref([])

const repoInfo = computed(() => store.result?.repo_info)
const isFavorited = computed(() => {
  if (!repoInfo.value?.full_name) return false
  return favorites.value.some(f => f.url?.includes(repoInfo.value.full_name))
})

// 配置 marked
marked.setOptions({
  highlight: function(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value
    }
    return code
  }
})

function renderMarkdown(content) {
  if (!content) return ''
  return marked(content)
}

async function handleToggleFavorite() {
  const url = repoInfo.value?.html_url
  if (!url) return

  try {
    if (isFavorited.value) {
      await removeFavorite(url)
      ElMessage.success('已取消收藏')
    } else {
      await addFavorite(url)
      ElMessage.success('收藏成功')
    }
    loadFavorites()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

function handleExport() {
  const content = `# ${repoInfo.value?.full_name}\n\n${store.result?.learning_doc || ''}\n\n---\n\n# 启动指南\n\n${store.result?.setup_guide || ''}`
  const blob = new Blob([content], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${repoInfo.value?.name || 'docs'}.md`
  a.click()
  URL.revokeObjectURL(url)
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
  loadFavorites()
})
</script>

<style scoped>
.docs {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
}

.title {
  margin: 0;
}

.empty-state {
  padding: 100px 0;
}

.info-card {
  margin-bottom: 20px;
}

.repo-info h2 {
  margin: 0 0 10px;
}

.repo-info p {
  color: #666;
  margin-bottom: 15px;
}

.repo-meta {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
}

.doc-tabs {
  margin-bottom: 20px;
}

.markdown-content {
  padding: 20px;
  background: #fff;
  border-radius: 4px;
  line-height: 1.6;
}

.markdown-content :deep(h1) {
  font-size: 1.8em;
  margin: 0 0 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.markdown-content :deep(h2) {
  font-size: 1.5em;
  margin: 30px 0 15px;
}

.markdown-content :deep(h3) {
  font-size: 1.3em;
  margin: 20px 0 10px;
}

.markdown-content :deep(code) {
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 0.9em;
}

.markdown-content :deep(pre) {
  background: #f5f5f5;
  padding: 15px;
  border-radius: 6px;
  overflow-x: auto;
}

.markdown-content :deep(pre code) {
  background: none;
  padding: 0;
}

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  padding-left: 20px;
}

.markdown-content :deep(li) {
  margin: 5px 0;
}

.actions {
  display: flex;
  gap: 10px;
}
</style>