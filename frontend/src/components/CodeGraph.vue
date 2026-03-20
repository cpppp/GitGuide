<template>
  <div class="code-graph">
    <div class="header">
      <h3>📊 代码图谱</h3>
    </div>

    <div v-if="loading" class="loading">
      <el-skeleton :rows="5" animated />
    </div>

    <div v-else-if="error" class="error">
      <el-alert type="error" :title="error" show-icon />
    </div>

    <div v-else class="graph-content">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="目录树" name="tree">
          <div class="tree-container">
            <tree-node :node="graphData.tree" :depth="0" />
          </div>
        </el-tab-pane>

        <el-tab-pane label="文件统计" name="stats">
          <div class="stats-container">
            <el-table :data="statsTableData" style="width: 100%">
              <el-table-column prop="ext" label="文件类型" width="120" />
              <el-table-column prop="count" label="文件数量" width="100" />
              <el-table-column prop="lines" label="代码行数" />
            </el-table>
          </div>
        </el-tab-pane>

        <el-tab-pane label="依赖关系" name="dependencies">
          <div class="dependencies-container">
            <el-tag
              v-for="(dep, index) in graphData.dependencies.imports"
              :key="index"
              class="dependency-tag"
            >
              {{ dep }}
            </el-tag>
            <el-empty v-if="graphData.dependencies.imports.length === 0" description="暂无依赖" />
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'

const props = defineProps({
  jobId: {
    type: String,
    required: true
  }
})

const loading = ref(true)
const error = ref('')
const graphData = ref({
  tree: {},
  stats: {},
  dependencies: { imports: [], modules: [] }
})
const activeTab = ref('tree')

const statsTableData = computed(() => {
  return Object.entries(graphData.value.stats).map(([ext, data]) => ({
    ext: ext || 'other',
    count: data.count,
    lines: data.lines
  }))
})

onMounted(async () => {
  try {
    const response = await fetch(`/api/analyze/${props.jobId}/code-graph`)
    const data = await response.json()
    
    if (data.error) {
      error.value = data.error
    } else {
      graphData.value = data
    }
  } catch (e) {
    error.value = '加载代码图谱失败'
  } finally {
    loading.value = false
  }
})
</script>

<script>
export default {
  name: 'TreeNode',
  props: {
    node: {
      type: Object,
      required: true
    },
    depth: {
      type: Number,
      default: 0
    }
  }
}
</script>

<template>
  <div class="tree-node" :style="{ paddingLeft: depth * 20 + 'px' }">
    <div class="node-content">
      <span v-if="node.type === 'folder'" class="folder-icon">📁</span>
      <span v-else class="file-icon">📄</span>
      <span class="node-name">{{ node.name }}</span>
      <span v-if="node.collapsed" class="collapsed-indicator">...</span>
    </div>
    <div v-if="node.children && node.children.length > 0 && !node.collapsed" class="children">
      <tree-node
        v-for="(child, index) in node.children"
        :key="index"
        :node="child"
        :depth="depth + 1"
      />
    </div>
  </div>
</template>

<style scoped>
.code-graph {
  padding: 20px;
  background: var(--bg-color-secondary, #f5f7fa);
  border-radius: 8px;
}

.header {
  margin-bottom: 20px;
}

.header h3 {
  margin: 0;
}

.loading {
  padding: 20px;
}

.error {
  padding: 20px;
}

.graph-content {
  min-height: 400px;
}

.tree-container {
  padding: 10px;
  font-family: 'Courier New', monospace;
}

.tree-node {
  padding: 4px 0;
}

.node-content {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.2s;
}

.node-content:hover {
  background: var(--bg-color, #f0f0f0);
}

.folder-icon {
  font-size: 16px;
}

.file-icon {
  font-size: 14px;
}

.node-name {
  flex: 1;
  font-size: 14px;
}

.collapsed-indicator {
  color: #999;
  font-size: 12px;
}

.stats-container {
  padding: 20px;
}

.dependencies-container {
  padding: 20px;
}

.dependency-tag {
  margin: 5px;
}
</style>
