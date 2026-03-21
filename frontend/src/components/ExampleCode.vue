<template>
  <div class="example-code">
    <div v-if="loading" class="loading">{{ language === 'zh' ? '加载示例代码...' : 'Loading examples...' }}</div>
    <div v-else-if="examples && examples.length > 0" class="examples-list">
      <el-card v-for="(example, index) in examples" :key="index" class="example-card">
        <template #header>
          <div class="example-header">
            <span class="filename">{{ example.filename }}</span>
            <el-tag size="small">{{ example.language }}</el-tag>
          </div>
        </template>
        <div class="example-content">
          <div v-if="example.snippets && example.snippets.length > 0" class="snippets">
            <el-tag
              v-for="(snippet, i) in example.snippets"
              :key="i"
              class="snippet-tag"
              type="info"
            >
              {{ snippet.name }}
            </el-tag>
          </div>
          <pre class="code-preview"><code>{{ example.preview }}</code></pre>
          <div class="example-meta">
            <span>{{ language === 'zh' ? '总行数' : 'Total lines' }}: {{ example.total_lines }}</span>
          </div>
        </div>
      </el-card>
    </div>
    <div v-else class="empty">
      {{ language === 'zh' ? '暂无示例代码' : 'No example code found' }}
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

.examples-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.example-card {
  margin-bottom: 10px;
}

.example-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filename {
  font-weight: bold;
  font-family: 'Consolas', monospace;
}

.example-content {
  padding: 10px 0;
}

.snippets {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
}

.snippet-tag {
  cursor: pointer;
}

.code-preview {
  background: var(--code-bg-color, #f5f5f5);
  padding: 15px;
  border-radius: 6px;
  overflow-x: auto;
  font-family: 'Consolas', monospace;
  font-size: 12px;
  line-height: 1.5;
  max-height: 300px;
  overflow-y: auto;
}

.code-preview code {
  white-space: pre;
}

.example-meta {
  margin-top: 10px;
  font-size: 12px;
  color: var(--text-color-secondary, #999);
}

.loading,
.empty {
  text-align: center;
  padding: 40px;
  color: var(--text-color-secondary, #999);
}
</style>