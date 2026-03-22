<template>
  <div class="example-code">
    <div v-if="loading" class="loading">
      <span class="loading-spinner"></span>
      <span>{{ language === 'zh' ? '加载示例代码...' : 'Loading examples...' }}</span>
    </div>
    <div v-else-if="examples && examples.length > 0" class="examples-list">
      <div v-for="(example, index) in examples" :key="index" class="example-card">
        <div class="example-header">
          <div class="file-info">
            <span class="file-icon">📄</span>
            <span class="filename">{{ example.filename }}</span>
            <el-tag size="small" class="lang-tag">{{ example.language }}</el-tag>
          </div>
        </div>
        <div class="example-content">
          <div v-if="example.snippets && example.snippets.length > 0" class="snippets">
            <el-tag
              v-for="(snippet, i) in example.snippets"
              :key="i"
              class="snippet-tag"
            >
              {{ snippet.name }}
            </el-tag>
          </div>
          <pre class="code-preview"><code>{{ example.preview }}</code></pre>
          <div class="example-meta">
            <span class="meta-item">
              <span class="meta-icon">📏</span>
              {{ language === 'zh' ? '总行数' : 'Lines' }}: {{ example.total_lines }}
            </span>
          </div>
        </div>
      </div>
    </div>
    <div v-else class="empty">
      <span class="empty-icon">📭</span>
      <span>{{ language === 'zh' ? '暂无示例代码' : 'No example code found' }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import { storeToRefs } from 'pinia'

const props = defineProps({
  result: {
    type: Object,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const settingsStore = useSettingsStore()
const { language } = storeToRefs(settingsStore)

const examples = computed(() => {
  if (props.result?.examples) {
    try {
      return typeof props.result.examples === 'string'
        ? JSON.parse(props.result.examples)
        : props.result.examples
    } catch {
      return props.result.examples
    }
  }
  return null
})
</script>

<style scoped>
.example-code {
  padding: 10px 0;
}

.example-header-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  padding: 16px 20px;
  background: var(--bg-warm);
  border-radius: var(--radius-md);
}

.bar-icon {
  font-size: 24px;
}

.bar-title {
  font-family: 'Noto Serif SC', Georgia, serif;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-color);
}

.examples-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.example-card {
  background: var(--bg-paper);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: all var(--transition-normal);
}

.example-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.example-header {
  padding: 16px 20px;
  background: var(--bg-warm);
  border-bottom: 1px solid var(--border-light);
}

.file-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.file-icon {
  font-size: 18px;
}

.filename {
  font-family: 'Crimson Pro', 'Consolas', monospace;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-color);
}

.lang-tag {
  background: var(--bg-paper) !important;
  border-color: var(--border-color) !important;
  color: var(--primary-color) !important;
}

.example-content {
  padding: 16px 20px;
}

.snippets {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.snippet-tag {
  background: var(--bg-warm) !important;
  border-color: var(--border-color) !important;
  color: var(--text-color-secondary) !important;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.snippet-tag:hover {
  background: var(--primary-color) !important;
  color: #fff !important;
  border-color: var(--primary-color) !important;
}

.code-preview {
  background: var(--bg-warm);
  padding: 16px 18px;
  border-radius: var(--radius-md);
  overflow-x: auto;
  font-family: 'Crimson Pro', 'Fira Code', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.6;
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid var(--border-light);
}

.code-preview code {
  white-space: pre;
  color: var(--text-color);
}

.example-meta {
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px solid var(--border-light);
  display: flex;
  justify-content: flex-end;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-color-muted);
}

.meta-icon {
  font-size: 14px;
}

.loading,
.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 40px;
  color: var(--text-color-muted);
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid var(--border-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-icon {
  font-size: 32px;
  opacity: 0.4;
}
</style>