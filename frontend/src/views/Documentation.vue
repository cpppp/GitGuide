<template>
  <div class="docs">
    <!-- 空状态 -->
    <div v-if="!store.result" class="empty-state">
      <div class="empty-illustration">
        <svg viewBox="0 0 120 120" class="empty-svg">
          <defs>
            <linearGradient id="emptyGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" style="stop-color:#c4a35a" />
              <stop offset="100%" style="stop-color:#3d5a6c" />
            </linearGradient>
          </defs>
          <rect x="20" y="25" width="80" height="70" rx="4" fill="none" stroke="url(#emptyGrad)" stroke-width="1.5" opacity="0.3"/>
          <rect x="25" y="30" width="70" height="55" rx="2" fill="none" stroke="url(#emptyGrad)" stroke-width="1" opacity="0.5"/>
          <line x1="35" y1="45" x2="80" y2="45" stroke="url(#emptyGrad)" stroke-width="1.5" stroke-linecap="round" opacity="0.4"/>
          <line x1="35" y1="55" x2="70" y2="55" stroke="url(#emptyGrad)" stroke-width="1" stroke-linecap="round" opacity="0.3"/>
          <line x1="35" y1="65" x2="60" y2="65" stroke="url(#emptyGrad)" stroke-width="1" stroke-linecap="round" opacity="0.2"/>
          <circle cx="60" cy="75" r="15" fill="none" stroke="url(#emptyGrad)" stroke-width="1" opacity="0.2"/>
          <path d="M55 75 L60 80 L68 70" stroke="url(#emptyGrad)" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <el-empty :description="language === 'zh' ? '暂无分析结果，请先分析仓库' : 'No analysis result, please analyze a repo first'">
        <el-button type="primary" @click="$router.push('/')">{{ language === 'zh' ? '去分析' : 'Go to Analyze' }}</el-button>
      </el-empty>
    </div>

    <div v-else class="content">
      <!-- 顶部导航 -->
      <div class="page-header">
        <el-button text class="back-btn" @click="$router.push('/')">
          <span class="back-icon">←</span>
          {{ language === 'zh' ? '返回首页' : 'Back' }}
        </el-button>
      </div>

      <!-- 仓库信息卡片 -->
      <el-card class="info-card">
        <div class="repo-header">
          <div class="repo-icon">
            <svg viewBox="0 0 40 40" width="40" height="40">
              <rect x="5" y="8" width="30" height="24" rx="3" fill="var(--primary-color)" opacity="0.15"/>
              <rect x="8" y="11" width="24" height="18" rx="2" fill="none" stroke="var(--primary-color)" stroke-width="1.5"/>
              <path d="M14 17 L18 20 L14 23" stroke="var(--accent-color)" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
              <line x1="20" y1="20" x2="26" y2="20" stroke="var(--primary-color)" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </div>
          <div class="repo-info">
            <h2 class="repo-name">{{ repoInfo?.full_name }}</h2>
            <p class="repo-desc">{{ repoInfo?.description || (language === 'zh' ? '暂无描述' : 'No description') }}</p>
            <div class="repo-meta">
              <el-tag v-if="repoInfo?.language" class="lang-tag">{{ repoInfo.language }}</el-tag>
              <span class="meta-item"><span class="meta-icon">⭐</span> {{ repoInfo?.stargazers_count || 0 }}</span>
              <a :href="repoInfo?.html_url" target="_blank" class="github-link">
                {{ language === 'zh' ? '在 GitHub 查看' : 'View on GitHub' }}
                <span class="link-icon">→</span>
              </a>
            </div>
          </div>
          <el-button
            :type="isFavorited ? 'warning' : 'default'"
            class="favorite-btn"
            @click="handleToggleFavorite"
          >
            <span class="favorite-icon">{{ isFavorited ? '★' : '☆' }}</span>
            {{ isFavorited ? (language === 'zh' ? '已收藏' : 'Favorited') : (language === 'zh' ? '收藏' : 'Favorite') }}
          </el-button>
        </div>
      </el-card>

      <!-- 文档内容区域 - 左侧导航 + 右侧内容 -->
      <div class="docs-layout">
        <!-- 左侧导航栏 -->
        <aside class="docs-sidebar">
          <div class="sidebar-header">
            <span class="sidebar-title">{{ language === 'zh' ? '文档目录' : 'Contents' }}</span>
          </div>
          <nav class="sidebar-nav">
            <div
              v-for="item in docMenuItems"
              :key="item.name"
              class="nav-section"
            >
              <div
                class="nav-item"
                :class="{ 'is-active': activeTab === item.name }"
                @click="activeTab = item.name"
              >
                <span class="nav-icon">{{ item.icon }}</span>
                <span class="nav-text">{{ language === 'zh' ? item.label : item.labelEn }}</span>
              </div>
            </div>
          </nav>
          <div class="sidebar-footer">
            <el-button type="primary" class="chat-btn" @click="$router.push('/chat')">
              <span class="btn-icon">💬</span>
              {{ language === 'zh' ? 'AI 问答' : 'AI Chat' }}
            </el-button>
          </div>
        </aside>

        <!-- 右侧文档内容 -->
         <main class="docs-main">
           <el-card class="doc-content-card">
             <div class="doc-header">
               <h1 class="doc-title">
                 <span class="doc-title-icon">{{ currentDocIcon }}</span>
                 {{ currentDocTitle }}
               </h1>
             </div>
             <div v-if="!isSpecialTab" class="markdown-content" v-html="renderMarkdown(currentDocContent)"></div>
             <div v-else-if="activeTab === 'atlas'" class="component-content">
               <CodeAtlas :result="store.result" :loading="false" />
             </div>
             <div v-else-if="activeTab === 'examples'" class="component-content">
               <ExampleCode :result="store.result" :loading="false" />
             </div>
           </el-card>

          <!-- 导出操作栏 -->
          <div class="export-bar">
            <span class="export-label">{{ language === 'zh' ? '导出文档' : 'Export' }}:</span>
            <el-button size="small" @click="handleExport('markdown')">
              <span class="export-icon">📄</span> Markdown
            </el-button>
            <el-button size="small" @click="handleExport('html')">
              <span class="export-icon">🌐</span> HTML
            </el-button>
            <el-button size="small" @click="handleExport('pdf')">
              <span class="export-icon">📑</span> PDF
            </el-button>
          </div>
        </main>
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

const activeTab = ref('quick_start')

const docMenuItems = [
  { name: 'quick_start', label: '快速入门', labelEn: 'Quick Start', icon: '⚡' },
  { name: 'overview', label: '项目概览', labelEn: 'Overview', icon: '📋' },
  { name: 'architecture', label: '架构设计', labelEn: 'Architecture', icon: '🏛' },
  { name: 'install_guide', label: '安装部署', labelEn: 'Install Guide', icon: '⚙' },
  { name: 'usage_tutorial', label: '使用教程', labelEn: 'Tutorial', icon: '📖' },
  { name: 'dev_guide', label: '开发指南', labelEn: 'Dev Guide', icon: '🔧' },
  { name: 'troubleshooting', label: '故障排查', labelEn: 'Troubleshoot', icon: '🔍' },
  { name: 'atlas', label: '代码图谱', labelEn: 'Code Atlas', icon: '🗺' },
  { name: 'examples', label: '示例代码', labelEn: 'Examples', icon: '💡' }
]

const currentDocIcon = computed(() => {
  const item = docMenuItems.find(m => m.name === activeTab.value)
  return item?.icon || '📄'
})

const currentDocTitle = computed(() => {
  const item = docMenuItems.find(m => m.name === activeTab.value)
  return language.value === 'zh' ? item?.label : item?.labelEn
})

const currentDocContent = computed(() => {
  const result = store.result
  if (!result) return ''

  switch (activeTab.value) {
    case 'quick_start':
      return result.quick_start || result.learning_doc || ''
    case 'overview':
      return result.overview || ''
    case 'architecture':
      return result.architecture || ''
    case 'install_guide':
      return result.install_guide || result.setup_guide || ''
    case 'usage_tutorial':
      return result.usage_tutorial || ''
    case 'dev_guide':
      return result.dev_guide || ''
    case 'troubleshooting':
      return result.troubleshooting || ''
    case 'atlas':
    case 'examples':
      return '' // 这些使用组件渲染
    default:
      return ''
  }
})

const isSpecialTab = computed(() => {
  return activeTab.value === 'atlas' || activeTab.value === 'examples'
})
const favorites = ref([])

function handleTabChange(activeName) {
  return true
}

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
  padding: 20px;
}

/* 页面头部 */
.page-header {
  margin-bottom: 20px;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--text-color-secondary) !important;
  font-size: 14px;
  transition: all var(--transition-normal);
}

.back-btn:hover {
  color: var(--primary-color) !important;
  transform: translateX(-4px);
}

.back-icon {
  font-size: 16px;
}

/* 空状态 */
.empty-state {
  padding: 80px 0;
  text-align: center;
}

.empty-illustration {
  width: 120px;
  height: 120px;
  margin: 0 auto 24px;
  opacity: 0.6;
}

.empty-svg {
  width: 100%;
  height: 100%;
}

/* 仓库信息卡片 */
.info-card {
  margin-bottom: 24px;
  padding: 24px !important;
}

.repo-header {
  display: flex;
  align-items: flex-start;
  gap: 20px;
}

.repo-icon {
  flex-shrink: 0;
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-warm);
  border-radius: var(--radius-md);
}

.repo-info {
  flex: 1;
  min-width: 0;
}

.repo-name {
  font-family: 'Noto Serif SC', 'Crimson Pro', Georgia, serif;
  font-size: 1.5em;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 8px;
}

.repo-desc {
  color: var(--text-color-secondary);
  font-size: 14px;
  margin: 0 0 14px;
  line-height: 1.6;
}

.repo-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.lang-tag {
  background: var(--bg-warm) !important;
  border-color: var(--border-color) !important;
  color: var(--primary-color) !important;
  font-weight: 500;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  color: var(--text-color-secondary);
}

.meta-icon {
  font-size: 14px;
}

.github-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: var(--primary-color);
  font-size: 14px;
  text-decoration: none;
  transition: all var(--transition-normal);
}

.github-link:hover {
  color: var(--primary-dark);
}

.github-link:hover .link-icon {
  transform: translateX(3px);
}

.link-icon {
  transition: transform var(--transition-normal);
}

.favorite-btn {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 6px;
}

.favorite-icon {
  font-size: 16px;
}

/* 文档布局 - 左侧导航 + 右侧内容 */
.docs-layout {
  display: flex;
  gap: 24px;
  align-items: flex-start;
}

/* 左侧导航栏 */
.docs-sidebar {
  width: 240px;
  flex-shrink: 0;
  background: var(--bg-paper);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  overflow: hidden;
  position: sticky;
  top: 20px;
}

.sidebar-header {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-light);
  background: var(--bg-warm);
}

.sidebar-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-color);
}

.sidebar-nav {
  padding: 12px 8px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-normal);
  color: var(--text-color-secondary);
  font-size: 14px;
  margin-bottom: 4px;
}

.nav-item:last-child {
  margin-bottom: 0;
}

.nav-item:hover {
  background: var(--bg-warm);
  color: var(--text-color);
}

.nav-item.is-active {
  background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
  color: #fff;
}

.nav-item.is-active .nav-icon {
  opacity: 1;
}

.nav-icon {
  font-size: 16px;
  opacity: 0.8;
}

.nav-text {
  font-weight: 500;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid var(--border-light);
  background: var(--bg-warm);
}

.chat-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

/* 右侧文档内容 */
.docs-main {
  flex: 1;
  min-width: 0;
}

.doc-content-card {
  padding: 0 !important;
  overflow: hidden;
}

.doc-header {
  padding: 20px 28px;
  border-bottom: 1px solid var(--border-light);
  background: var(--bg-warm);
}

.doc-title {
  font-family: 'Noto Serif SC', 'Crimson Pro', Georgia, serif;
  font-size: 1.4em;
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.doc-title-icon {
  font-size: 24px;
}

.component-content {
  padding: 20px;
}

/* Markdown 内容区 */
.markdown-content {
  padding: 28px 32px;
  background: var(--bg-paper);
  line-height: 1.8;
  min-height: 300px;
}

.markdown-content :deep(h1) {
  font-family: 'Noto Serif SC', 'Crimson Pro', Georgia, serif;
  font-size: 1.6em;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 20px;
  padding-bottom: 12px;
  border-bottom: 2px solid var(--border-light);
}

.markdown-content :deep(h2) {
  font-family: 'Noto Serif SC', Georgia, serif;
  font-size: 1.3em;
  font-weight: 600;
  color: var(--text-color);
  margin: 28px 0 14px;
  padding-left: 12px;
  border-left: 3px solid var(--accent-color);
}

.markdown-content :deep(h3) {
  font-size: 1.1em;
  font-weight: 600;
  color: var(--text-color);
  margin: 20px 0 10px;
}

.markdown-content :deep(h4) {
  font-size: 1em;
  font-weight: 600;
  color: var(--text-color-secondary);
  margin: 18px 0 8px;
}

.markdown-content :deep(p) {
  margin: 12px 0;
  color: var(--text-color);
}

.markdown-content :deep(code) {
  background: var(--bg-warm);
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 0.9em;
  font-family: 'Crimson Pro', 'Fira Code', monospace;
  color: var(--primary-dark);
}

.dark-theme .markdown-content :deep(code) {
  color: var(--primary-light);
}

.markdown-content :deep(pre) {
  background: var(--bg-warm);
  padding: 16px 18px;
  border-radius: var(--radius-md);
  overflow-x: auto;
  margin: 14px 0;
  border: 1px solid var(--border-light);
}

.markdown-content :deep(pre code) {
  background: none;
  padding: 0;
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-color);
}

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  padding-left: 24px;
  margin: 12px 0;
}

.markdown-content :deep(li) {
  margin: 6px 0;
  color: var(--text-color);
}

.markdown-content :deep(li::marker) {
  color: var(--accent-color);
}

.markdown-content :deep(blockquote) {
  margin: 14px 0;
  padding: 12px 18px;
  background: var(--bg-warm);
  border-left: 4px solid var(--accent-color);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  color: var(--text-color-secondary);
}

.markdown-content :deep(a) {
  color: var(--primary-color);
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: all var(--transition-fast);
}

.markdown-content :deep(a:hover) {
  border-bottom-color: var(--primary-color);
}

.markdown-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 14px 0;
  font-size: 14px;
}

.markdown-content :deep(th),
.markdown-content :deep(td) {
  padding: 10px 14px;
  border: 1px solid var(--border-light);
  text-align: left;
}

.markdown-content :deep(th) {
  background: var(--bg-warm);
  font-weight: 600;
  color: var(--text-color);
}

.markdown-content :deep(tr:nth-child(even)) {
  background: var(--bg-warm);
}

.markdown-content :deep(hr) {
  border: none;
  height: 1px;
  background: var(--border-light);
  margin: 20px 0;
}

/* 导出操作栏 */
.export-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
  padding: 16px 20px;
  background: var(--bg-paper);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
}

.export-label {
  font-size: 14px;
  color: var(--text-color-secondary);
  font-weight: 500;
}

.export-icon {
  margin-right: 4px;
}

/* 响应式 */
@media (max-width: 900px) {
  .docs-layout {
    flex-direction: column;
  }

  .docs-sidebar {
    width: 100%;
    position: static;
  }

  .sidebar-nav {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    padding: 12px;
  }

  .nav-item {
    margin-bottom: 0;
    flex: 1;
    min-width: calc(50% - 4px);
    justify-content: center;
  }
}
</style>