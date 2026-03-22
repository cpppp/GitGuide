<template>
  <el-drawer
    v-model="visible"
    :title="filePath"
    size="70%"
    direction="rtl"
    :before-close="handleClose"
  >
    <div class="code-viewer" v-if="fileData">
      <div class="file-header">
        <div class="file-info">
          <span class="file-icon">📄</span>
          <span class="file-path">{{ fileData.file_path }}</span>
          <el-tag size="small" class="language-tag">{{ fileData.language }}</el-tag>
        </div>
        <div class="file-stats">
          <span class="stat-item">{{ fileData.line_count }} lines</span>
        </div>
      </div>

      <div class="symbols-nav" v-if="fileData.symbols && fileData.symbols.length > 0">
        <span class="symbols-label">Symbols:</span>
        <el-tag
          v-for="sym in fileData.symbols.slice(0, 10)"
          :key="sym.name"
          size="small"
          class="symbol-tag"
          @click="scrollToSymbol(sym.line_number)"
        >
          {{ sym.name }} ({{ sym.type }})
        </el-tag>
      </div>

      <div class="code-container">
        <pre class="code-pre"><code class="code-block" :class="`language-${fileData.language}`" v-html="highlightedCode"></code></pre>
      </div>
    </div>

    <div class="loading-state" v-else-if="loading">
      <el-icon class="loading-icon"><Loading /></el-icon>
      <span>Loading file content...</span>
    </div>

    <div class="error-state" v-else-if="error">
      <el-icon><WarningFilled /></el-icon>
      <span>{{ error }}</span>
    </div>
  </el-drawer>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Loading, WarningFilled } from '@element-plus/icons-vue'
import { getFileContent } from '@/api/chat'
import { useAnalysisStore } from '@/stores/analysis'
import Prism from 'prismjs'
import 'prismjs/components/prism-python'
import 'prismjs/components/prism-javascript'
import 'prismjs/components/prism-typescript'
import 'prismjs/components/prism-java'
import 'prismjs/components/prism-go'
import 'prismjs/components/prism-rust'
import 'prismjs/components/prism-c'
import 'prismjs/components/prism-cpp'

const props = defineProps({
  modelValue: Boolean,
  filePath: String,
  repoUrl: String
})

const emit = defineEmits(['update:modelValue'])

const store = useAnalysisStore()
const loading = ref(false)
const error = ref(null)
const fileData = ref(null)

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const languageMap = {
  'python': 'python',
  'javascript': 'javascript',
  'typescript': 'typescript',
  'java': 'java',
  'go': 'go',
  'rust': 'rust',
  'c': 'c',
  'cpp': 'cpp'
}

const highlightedCode = computed(() => {
  if (!fileData.value) return ''

  const lang = languageMap[fileData.value.language] || 'plaintext'
  const code = fileData.value.content

  const lines = code.split('\n')
  const numberedLines = lines.map((line, i) => {
    return `<span class="line-number">${i + 1}</span>${escapeHtml(line) || ' '}`
  }).join('\n')

  try {
    if (Prism.languages[lang]) {
      return Prism.highlight(numberedLines, Prism.languages[lang], lang)
    }
  } catch (e) {
    console.error('Prism highlight error:', e)
  }

  return numberedLines
})

function escapeHtml(text) {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  }
  return text.replace(/[&<>"']/g, m => map[m])
}

async function loadFileContent() {
  if (!props.filePath || !props.repoUrl) return

  loading.value = true
  error.value = null

  try {
    const response = await getFileContent(props.repoUrl, props.filePath)
    if (response.data.success) {
      fileData.value = response.data
    } else {
      error.value = response.data.error || 'Failed to load file'
    }
  } catch (e) {
    error.value = e.message || 'Failed to load file'
  } finally {
    loading.value = false
  }
}

function scrollToSymbol(lineNumber) {
  const codeContainer = document.querySelector('.code-container')
  if (codeContainer) {
    const lineHeight = 24
    codeContainer.scrollTop = (lineNumber - 1) * lineHeight
  }
}

function handleClose() {
  visible.value = false
}

watch(() => props.modelValue, (newVal) => {
  if (newVal && props.filePath) {
    loadFileContent()
  }
})

watch(() => props.filePath, (newVal) => {
  if (newVal && props.modelValue) {
    loadFileContent()
  }
})
</script>

<style scoped>
.code-viewer {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 0 16px;
}

.file-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid var(--border-light);
  margin-bottom: 12px;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-icon {
  font-size: 18px;
}

.file-path {
  font-family: 'Crimson Pro', monospace;
  font-size: 14px;
  color: var(--text-color);
}

.language-tag {
  background: var(--primary-color) !important;
  color: #fff !important;
  border: none !important;
}

.file-stats {
  display: flex;
  gap: 12px;
  color: var(--text-color-muted);
  font-size: 13px;
}

.symbols-nav {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  padding: 8px 0;
  border-bottom: 1px solid var(--border-light);
  margin-bottom: 12px;
}

.symbols-label {
  font-size: 12px;
  color: var(--text-color-muted);
  line-height: 24px;
}

.symbol-tag {
  cursor: pointer;
  transition: all 0.2s;
}

.symbol-tag:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.code-container {
  flex: 1;
  overflow: auto;
  background: #1e1e1e;
  border-radius: 8px;
}

.code-pre {
  margin: 0;
  padding: 16px;
  font-family: 'Fira Code', 'Crimson Pro', monospace;
  font-size: 13px;
  line-height: 24px;
  overflow-x: auto;
}

.code-block {
  font-family: inherit;
  white-space: pre;
}

.code-block :deep(.line-number) {
  display: inline-block;
  width: 40px;
  text-align: right;
  padding-right: 16px;
  color: #666;
  user-select: none;
}

.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  gap: 12px;
  color: var(--text-color-muted);
}

.loading-icon {
  font-size: 32px;
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
