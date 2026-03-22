<template>
  <div class="code-atlas">
    <div class="atlas-header">
      <span class="atlas-icon">🗺</span>
      <span class="atlas-title">{{ language === 'zh' ? '代码图谱' : 'Code Atlas' }}</span>
    </div>

    <el-tabs v-model="activeSubTab" class="atlas-tabs">
      <el-tab-pane name="tree">
        <template #label>
          <span class="tab-label"><span class="tab-icon">📁</span> {{ language === 'zh' ? '目录结构' : 'Directory' }}</span>
        </template>
        <div class="tree-container">
          <div v-if="loading" class="loading">
            <span class="loading-spinner"></span>
            <span>{{ language === 'zh' ? '加载中...' : 'Loading...' }}</span>
          </div>
          <div v-else-if="directoryTree" class="tree-view">
            <div class="tree-node" v-html="renderTree(directoryTree)"></div>
          </div>
          <div v-else class="empty">
            <span class="empty-icon">📭</span>
            <span>{{ language === 'zh' ? '暂无目录结构信息' : 'No directory structure' }}</span>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane name="stats">
        <template #label>
          <span class="tab-label"><span class="tab-icon">📊</span> {{ language === 'zh' ? '文件统计' : 'Statistics' }}</span>
        </template>
        <div class="stats-container">
          <div v-if="loading" class="loading">
            <span class="loading-spinner"></span>
            <span>{{ language === 'zh' ? '加载中...' : 'Loading...' }}</span>
          </div>
          <div v-else-if="fileStats.length > 0">
            <div class="stats-grid">
              <div v-for="stat in fileStats" :key="stat.name" class="stat-card">
                <div class="stat-ext">{{ stat.name }}</div>
                <div class="stat-info">
                  <div class="stat-item">
                    <span class="stat-label">{{ language === 'zh' ? '文件数' : 'Files' }}</span>
                    <span class="stat-value">{{ stat.count }}</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-label">{{ language === 'zh' ? '代码行数' : 'Lines' }}</span>
                    <span class="stat-value">{{ formatNumber(stat.lines) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="empty">
            <span class="empty-icon">📭</span>
            <span>{{ language === 'zh' ? '暂无文件统计信息' : 'No file statistics' }}</span>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane name="deps">
        <template #label>
          <span class="tab-label"><span class="tab-icon">🔗</span> {{ language === 'zh' ? '依赖关系' : 'Dependencies' }}</span>
        </template>
        <div class="deps-container">
          <div v-if="loading" class="loading">
            <span class="loading-spinner"></span>
            <span>{{ language === 'zh' ? '加载中...' : 'Loading...' }}</span>
          </div>
          <div v-else-if="dependencies.length > 0">
            <div class="dep-list">
              <div v-for="(dep, index) in dependencies" :key="index" class="dep-item">
                <span class="dep-from">{{ dep.from }}</span>
                <span class="dep-arrow">→</span>
                <span class="dep-to">{{ dep.to }}</span>
              </div>
            </div>
          </div>
          <div v-else class="empty">
            <span class="empty-icon">📭</span>
            <span>{{ language === 'zh' ? '暂无依赖关系信息' : 'No dependencies' }}</span>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
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

const activeSubTab = ref('tree')

const codeGraph = computed(() => {
  if (!props.result?.code_graph) return null
  try {
    if (typeof props.result.code_graph === 'string') {
      return JSON.parse(props.result.code_graph)
    }
    return props.result.code_graph
  } catch {
    return null
  }
})

const directoryTree = computed(() => {
  if (codeGraph.value?.tree) {
    return codeGraph.value.tree
  }
  if (props.result?.directory_structure) {
    try {
      return JSON.parse(props.result.directory_structure)
    } catch {
      return props.result.directory_structure
    }
  }
  return null
})

const fileStats = computed(() => {
  if (codeGraph.value?.stats) {
    const stats = codeGraph.value.stats
    return Object.entries(stats).map(([ext, data]) => ({
      name: ext,
      count: data.count || 0,
      lines: data.lines || 0
    }))
  }
  return props.result?.file_stats || []
})

const dependencies = computed(() => {
  if (codeGraph.value?.dependencies) {
    const deps = codeGraph.value.dependencies
    if (deps.imports) {
      return deps.imports.map(imp => ({
        from: 'project',
        to: imp
      }))
    }
  }
  if (props.result?.dependencies) {
    try {
      return JSON.parse(props.result.dependencies)
    } catch {
      return props.result.dependencies
    }
  }
  return []
})

// 渲染目录树
function renderTree(tree) {
  if (!tree) return ''

  const renderNode = (node, indent = 0) => {
    if (!node || !node.name) return ''

    const padding = indent * 20
    const icon = node.type === 'folder' ? '📁' : '📄'
    const isDir = node.type === 'folder'
    const style = isDir ? 'font-weight: bold;' : ''

    let html = `<div class="tree-item" style="padding-left: ${padding}px;">
      <span class="tree-icon">${icon}</span>
      <span class="tree-name" style="${style}">${node.name}</span>
    </div>`

    if (isDir && node.children && Array.isArray(node.children)) {
      for (const child of node.children) {
        html += renderNode(child, indent + 1)
      }
    }

    return html
  }

  return renderNode(tree)
}

// 格式化数字
function formatNumber(num) {
  if (!num) return '0'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'k'
  return num.toString()
}
</script>

<style scoped>
.code-atlas {
  padding: 10px 0;
}

.atlas-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  padding: 16px 20px;
  background: var(--bg-warm);
  border-radius: var(--radius-md);
}

.atlas-icon {
  font-size: 24px;
}

.atlas-title {
  font-family: 'Noto Serif SC', Georgia, serif;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-color);
}

.atlas-tabs :deep(.el-tabs__item) {
  font-size: 14px;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 6px;
}

.tree-container,
.stats-container,
.deps-container {
  padding: 16px 0;
  max-height: 500px;
  overflow-y: auto;
}

.tree-view {
  font-family: 'Crimson Pro', 'Consolas', monospace;
  font-size: 14px;
  line-height: 1.8;
}

.tree-item {
  display: flex;
  align-items: center;
  padding: 4px 0;
  transition: all var(--transition-fast);
}

.tree-item:hover {
  background: var(--bg-warm);
  border-radius: var(--radius-sm);
}

.tree-icon {
  margin-right: 8px;
  font-size: 14px;
}

.tree-name {
  color: var(--text-color);
  font-size: 13px;
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

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 16px;
}

.stat-card {
  background: var(--bg-warm);
  border-radius: var(--radius-md);
  padding: 16px;
  border: 1px solid var(--border-light);
  transition: all var(--transition-normal);
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.stat-ext {
  font-family: 'Crimson Pro', monospace;
  font-size: 16px;
  font-weight: 600;
  color: var(--primary-color);
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-light);
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-label {
  font-size: 13px;
  color: var(--text-color-muted);
}

.stat-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-color);
}

/* 依赖关系 */
.dep-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.dep-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: var(--bg-warm);
  border-radius: var(--radius-md);
  font-family: 'Crimson Pro', monospace;
  font-size: 14px;
  transition: all var(--transition-normal);
}

.dep-item:hover {
  transform: translateX(4px);
  box-shadow: var(--shadow-sm);
}

.dep-from {
  color: var(--primary-color);
  font-weight: 600;
}

.dep-arrow {
  color: var(--accent-color);
}

.dep-to {
  color: var(--success-color);
  font-weight: 600;
}
</style>