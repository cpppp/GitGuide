<template>
  <div class="code-atlas">
    <el-tabs v-model="activeSubTab">
      <el-tab-pane label="目录结构" name="tree">
        <div class="tree-container">
          <div v-if="loading" class="loading">加载中...</div>
          <div v-else-if="directoryTree" class="tree-view">
            <div class="tree-node" v-html="renderTree(directoryTree)"></div>
          </div>
          <div v-else class="empty">暂无目录结构信息</div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="文件统计" name="stats">
        <div class="stats-container">
          <div v-if="loading" class="loading">加载中...</div>
          <div v-else-if="fileStats.length > 0">
            <el-table :data="fileStats" style="width: 100%" max-height="400">
              <el-table-column prop="name" label="文件类型" width="150" />
              <el-table-column prop="count" label="文件数量" width="120" />
              <el-table-column prop="lines" label="代码行数" width="120" />
            </el-table>
          </div>
          <div v-else class="empty">暂无文件统计信息</div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="依赖关系" name="deps">
        <div class="deps-container">
          <div v-if="loading" class="loading">加载中...</div>
          <div v-else-if="dependencies.length > 0">
            <div class="dep-list">
              <el-card v-for="(dep, index) in dependencies" :key="index" class="dep-card">
                <div class="dep-item">
                  <span class="dep-from">{{ dep.from }}</span>
                  <span class="dep-arrow">→</span>
                  <span class="dep-to">{{ dep.to }}</span>
                </div>
              </el-card>
            </div>
          </div>
          <div v-else class="empty">暂无依赖关系信息</div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

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
    let html = ''
    const padding = indent * 20

    if (typeof node === 'object' && node !== null) {
      for (const [name, children] of Object.entries(node)) {
        const isDir = children && typeof children === 'object'
        const icon = isDir ? '📁' : '📄'
        const style = isDir ? 'font-weight: bold;' : ''

        html += `<div class="tree-item" style="padding-left: ${padding}px;">
          <span class="tree-icon">${icon}</span>
          <span class="tree-name" style="${style}">${name}</span>
        </div>`

        if (isDir) {
          html += renderNode(children, indent + 1)
        }
      }
    } else if (Array.isArray(tree)) {
      // 处理数组格式
      for (const item of tree) {
        const icon = item.is_directory ? '📁' : '📄'
        const style = item.is_directory ? 'font-weight: bold;' : ''
        html += `<div class="tree-item" style="padding-left: ${padding}px;">
          <span class="tree-icon">${icon}</span>
          <span class="tree-name" style="${style}">${item.name}</span>
        </div>`
      }
    }

    return html
  }

  return renderNode(tree)
}

// 格式化文件大小
function formatSize(bytes) {
  if (!bytes) return '-'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}
</script>

<style scoped>
.code-atlas {
  padding: 10px 0;
}

.tree-container,
.stats-container,
.deps-container {
  padding: 10px 0;
  max-height: 500px;
  overflow-y: auto;
}

.tree-view {
  font-family: 'Consolas', monospace;
  font-size: 14px;
}

.tree-item {
  display: flex;
  align-items: center;
  padding: 4px 0;
}

.tree-icon {
  margin-right: 8px;
}

.tree-name {
  color: var(--text-color, #333);
}

.loading,
.empty {
  text-align: center;
  padding: 40px;
  color: var(--text-color-secondary, #999);
}

.dep-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.dep-card {
  flex: 1 1 300px;
  max-width: 400px;
}

.dep-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.dep-from {
  color: #409eff;
  font-weight: bold;
}

.dep-arrow {
  color: #909399;
}

.dep-to {
  color: #67c23a;
  font-weight: bold;
}
</style>