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

      <!-- 文档标签页 -->
      <el-card class="docs-card">
        <el-tabs v-model="activeTab" class="doc-tabs" :before-leave="handleTabChange">
          <el-tab-pane name="quick_start">
            <template #label>
              <span class="tab-label"><span class="tab-icon">⚡</span> {{ language === 'zh' ? '快速入门' : 'Quick Start' }}</span>
            </template>
            <div class="markdown-content" v-html="renderMarkdown(store.result?.quick_start || store.result?.learning_doc || '')"></div>
          </el-tab-pane>
          <el-tab-pane name="overview">
            <template #label>
              <span class="tab-label"><span class="tab-icon">📋</span> {{ language === 'zh' ? '项目概览' : 'Overview' }}</span>
            </template>
            <div class="markdown-content" v-html="renderMarkdown(store.result?.overview || '')"></div>
          </el-tab-pane>
          <el-tab-pane name="architecture">
            <template #label>
              <span class="tab-label"><span class="tab-icon">🏛</span> {{ language === 'zh' ? '架构设计' : 'Architecture' }}</span>
            </template>
            <div class="markdown-content" v-html="renderMarkdown(store.result?.architecture || '')"></div>
          </el-tab-pane>
          <el-tab-pane name="install_guide">
            <template #label>
              <span class="tab-label"><span class="tab-icon">⚙</span> {{ language === 'zh' ? '安装部署' : 'Install Guide' }}</span>
            </template>
            <div class="markdown-content" v-html="renderMarkdown(store.result?.install_guide || store.result?.setup_guide || '')"></div>
          </el-tab-pane>
          <el-tab-pane name="usage_tutorial">
            <template #label>
              <span class="tab-label"><span class="tab-icon">📖</span> {{ language === 'zh' ? '使用教程' : 'Tutorial' }}</span>
            </template>
            <div class="markdown-content" v-html="renderMarkdown(store.result?.usage_tutorial || '')"></div>
          </el-tab-pane>
          <el-tab-pane name="dev_guide">
            <template #label>
              <span class="tab-label"><span class="tab-icon">🔧</span> {{ language === 'zh' ? '开发指南' : 'Dev Guide' }}</span>
            </template>
            <div class="markdown-content" v-html="renderMarkdown(store.result?.dev_guide || '')"></div>
          </el-tab-pane>
          <el-tab-pane name="troubleshooting">
            <template #label>
              <span class="tab-label"><span class="tab-icon">🔍</span> {{ language === 'zh' ? '故障排查' : 'Troubleshoot' }}</span>
            </template>
            <div class="markdown-content" v-html="renderMarkdown(store.result?.troubleshooting || '')"></div>
          </el-tab-pane>
          <el-tab-pane name="atlas">
            <template #label>
              <span class="tab-label"><span class="tab-icon">🗺</span> {{ language === 'zh' ? '代码图谱' : 'Code Atlas' }}</span>
            </template>
            <CodeAtlas :result="store.result" :loading="false" />
          </el-tab-pane>
          <el-tab-pane name="examples">
            <template #label>
              <span class="tab-label"><span class="tab-icon">💡</span> {{ language === 'zh' ? '示例代码' : 'Examples' }}</span>
            </template>
            <ExampleCode :result="store.result" :loading="false" />
          </el-tab-pane>
        </el-tabs>

        <!-- 底部操作栏 -->
        <div class="action-bar">
          <el-button type="primary" class="action-btn" @click="$router.push('/chat')">
            <span class="btn-icon">💬</span>
            {{ language === 'zh' ? 'AI 问答' : 'AI Chat' }}
          </el-button>

          <el-dropdown @command="handleExport" trigger="click">
            <el-button class="action-btn">
              <span class="btn-icon">📥</span>
              {{ language === 'zh' ? '导出文档' : 'Export' }}
            </el-button>
            <template #dropdown>
              <el-dropdown-menu class="export-menu">
                <el-dropdown-item command="markdown">
                  <span class="export-icon">📄</span> Markdown
                </el-dropdown-item>
                <el-dropdown-item command="html">
                  <span class="export-icon">🌐</span> HTML
                </el-dropdown-item>
                <el-dropdown-item command="pdf">
                  <span class="export-icon">📑</span> PDF
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-card>
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
  max-width: 1000px;
  margin: 0 auto;
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

/* 文档卡片 */
.docs-card {
  padding: 0 !important;
  overflow: hidden;
}

/* 标签页样式 */
.doc-tabs {
  padding: 0 24px;
}

.doc-tabs :deep(.el-tabs__header) {
  margin: 0;
  padding: 0;
}

.doc-tabs :deep(.el-tabs__nav-wrap::after) {
  height: 1px;
  background: var(--border-light);
}

.doc-tabs :deep(.el-tabs__item) {
  height: 56px;
  line-height: 56px;
  padding: 0 18px;
  font-size: 14px;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 6px;
}

.tab-icon {
  font-size: 15px;
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
  font-size: 1.8em;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 24px;
  padding-bottom: 14px;
  border-bottom: 2px solid var(--border-light);
}

.markdown-content :deep(h2) {
  font-family: 'Noto Serif SC', Georgia, serif;
  font-size: 1.4em;
  font-weight: 600;
  color: var(--text-color);
  margin: 32px 0 16px;
  padding-left: 12px;
  border-left: 3px solid var(--accent-color);
}

.markdown-content :deep(h3) {
  font-size: 1.15em;
  font-weight: 600;
  color: var(--text-color);
  margin: 24px 0 12px;
}

.markdown-content :deep(h4) {
  font-size: 1em;
  font-weight: 600;
  color: var(--text-color-secondary);
  margin: 20px 0 10px;
}

.markdown-content :deep(p) {
  margin: 14px 0;
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
  padding: 18px 20px;
  border-radius: var(--radius-md);
  overflow-x: auto;
  margin: 16px 0;
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
  margin: 8px 0;
  color: var(--text-color);
}

.markdown-content :deep(li::marker) {
  color: var(--accent-color);
}

.markdown-content :deep(blockquote) {
  margin: 16px 0;
  padding: 14px 20px;
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
  margin: 16px 0;
  font-size: 14px;
}

.markdown-content :deep(th),
.markdown-content :deep(td) {
  padding: 12px 16px;
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
  margin: 24px 0;
}

/* 操作栏 */
.action-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 24px;
  background: var(--bg-warm);
  border-top: 1px solid var(--border-light);
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  height: 42px;
}

.btn-icon {
  font-size: 16px;
}

/* 导出菜单 */
.export-menu {
  min-width: 140px;
}

.export-icon {
  margin-right: 8px;
}
</style>