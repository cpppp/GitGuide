<template>
  <div class="docs">
    <div class="header">
      <el-button text @click="$router.push('/')">← {{ language === 'zh' ? '返回首页' : 'Back' }}</el-button>
      <h1 class="title">{{ repoInfo?.name || (language === 'zh' ? '文档' : 'Docs') }}</h1>
    </div>

    <div v-if="!store.result" class="empty-state">
      <el-empty :description="language === 'zh' ? '暂无分析结果，请先分析仓库' : 'No analysis result, please analyze a repo first'">
        <el-button type="primary" @click="$router.push('/')">{{ language === 'zh' ? '去分析' : 'Go to Analyze' }}</el-button>
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
            <a :href="repoInfo?.html_url" target="_blank">{{ language === 'zh' ? '在 GitHub 查看 →' : 'View on GitHub →' }}</a>
          </div>
          <el-button
            :type="isFavorited ? 'warning' : 'default'"
            @click="handleToggleFavorite"
          >
            {{ isFavorited ? (language === 'zh' ? '⭐ 已收藏' : '⭐ Favorited') : (language === 'zh' ? '☆ 收藏' : '☆ Favorite') }}
          </el-button>
        </div>
      </el-card>

      <!-- 文档标签页 - V3.1 支持7种文档 -->
      <el-tabs v-model="activeTab" class="doc-tabs">
        <el-tab-pane :label="language === 'zh' ? '快速入门' : 'Quick Start'" name="quick_start">
          <div class="markdown-content" v-html="renderMarkdown(store.result?.quick_start || store.result?.learning_doc || '')"></div>
        </el-tab-pane>
        <el-tab-pane :label="language === 'zh' ? '项目概览' : 'Overview'" name="overview">
          <div class="markdown-content" v-html="renderMarkdown(store.result?.overview || '')"></div>
        </el-tab-pane>
        <el-tab-pane :label="language === 'zh' ? '架构设计' : 'Architecture'" name="architecture">
          <div class="markdown-content" v-html="renderMarkdown(store.result?.architecture || '')"></div>
        </el-tab-pane>
        <el-tab-pane :label="language === 'zh' ? '安装部署' : 'Install Guide'" name="install_guide">
          <div class="markdown-content" v-html="renderMarkdown(store.result?.install_guide || store.result?.setup_guide || '')"></div>
        </el-tab-pane>
        <el-tab-pane :label="language === 'zh' ? '使用教程' : 'Tutorial'" name="usage_tutorial">
          <div class="markdown-content" v-html="renderMarkdown(store.result?.usage_tutorial || '')"></div>
        </el-tab-pane>
        <el-tab-pane :label="language === 'zh' ? '开发指南' : 'Dev Guide'" name="dev_guide">
          <div class="markdown-content" v-html="renderMarkdown(store.result?.dev_guide || '')"></div>
        </el-tab-pane>
        <el-tab-pane :label="language === 'zh' ? '故障排查' : 'Troubleshoot'" name="troubleshooting">
          <div class="markdown-content" v-html="renderMarkdown(store.result?.troubleshooting || '')"></div>
        </el-tab-pane>
        <el-tab-pane :label="language === 'zh' ? '代码图谱' : 'Code Atlas'" name="atlas">
          <CodeAtlas :result="store.result" :loading="false" />
        </el-tab-pane>
        <el-tab-pane :label="language === 'zh' ? '示例代码' : 'Examples'" name="examples">
          <ExampleCode :result="store.result" :loading="false" />
        </el-tab-pane>
      </el-tabs>

      <!-- 操作按钮 -->
      <div class="actions">
        <el-button type="primary" @click="$router.push('/chat')">{{ language === 'zh' ? '💬 AI 问答' : '💬 AI Chat' }}</el-button>

        <!-- 导出下拉菜单 -->
        <el-dropdown @command="handleExport">
          <el-button>
            📥 {{ language === 'zh' ? '导出' : 'Export' }}
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="markdown">📄 Markdown</el-dropdown-item>
              <el-dropdown-item command="html">🌐 HTML</el-dropdown-item>
              <el-dropdown-item command="pdf">📑 PDF</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAnalysisStore } from '@/stores/analysis'
import { useSettingsStore } from '@/stores/settings'
import { storeToRefs } from 'pinia'
import { marked } from 'marked'
import hljs from 'highlight.js'
import { getFavorites, addFavorite, removeFavorite } from '@/api/analyze'
import { ElMessage } from 'element-plus'
import CodeAtlas from '@/components/CodeAtlas.vue'
import ExampleCode from '@/components/ExampleCode.vue'
import { exportToMarkdown, exportToHTML, exportToPDF, downloadFile } from '@/utils/export'

const router = useRouter()
const store = useAnalysisStore()
const settingsStore = useSettingsStore()
const { language } = storeToRefs(settingsStore)

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
      ElMessage.success(language.value === 'zh' ? '已取消收藏' : 'Unfavorited')
    } else {
      await addFavorite(url)
      ElMessage.success(language.value === 'zh' ? '收藏成功' : 'Favorited')
    }
    loadFavorites()
  } catch (e) {
    ElMessage.error(language.value === 'zh' ? '操作失败' : 'Operation failed')
  }
}

function handleExport(command) {
  const result = store.result
  const repoName = repoInfo.value?.name || 'docs'

  switch (command) {
    case 'markdown':
      const mdContent = exportToMarkdown(result)
      downloadFile(mdContent, `${repoName}.md`, 'text/markdown')
      ElMessage.success(language.value === 'zh' ? '已导出 Markdown' : 'Markdown exported')
      break

    case 'html':
      const htmlContent = exportToHTML(result)
      downloadFile(htmlContent, `${repoName}.html`, 'text/html')
      ElMessage.success(language.value === 'zh' ? '已导出 HTML' : 'HTML exported')
      break

    case 'pdf':
      exportToPDF(result)
      break
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
  color: var(--text-color-secondary, #666);
  margin-bottom: 15px;
}

.repo-meta {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
}

.repo-meta a {
  color: var(--primary-color);
}

.doc-tabs {
  margin-bottom: 20px;
}

.markdown-content {
  padding: 20px;
  background: var(--bg-color-secondary, #fff);
  border-radius: 4px;
  line-height: 1.6;
}

.markdown-content :deep(h1) {
  font-size: 1.8em;
  margin: 0 0 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border-color, #eee);
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
  background: var(--bg-color, #f5f5f5);
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 0.9em;
}

.markdown-content :deep(pre) {
  background: var(--bg-color, #f5f5f5);
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