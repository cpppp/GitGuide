<template>
  <div class="architecture-diagram">
    <div v-if="mermaidCode" class="diagram-container">
      <div class="diagram-actions">
        <el-button size="small" @click="copyToClipboard">
          {{ copied ? (language === 'zh' ? '已复制' : 'Copied') : (language === 'zh' ? '复制代码' : 'Copy') }}
        </el-button>
        <el-button size="small" type="primary" @click="openMermaidEditor">
          {{ language === 'zh' ? '在线预览' : 'Preview Online' }}
        </el-button>
      </div>
      <pre class="mermaid-code"><code>{{ mermaidCode }}</code></pre>
    </div>
    <div v-else class="empty">
      {{ language === 'zh' ? '暂无架构图信息' : 'No architecture diagram available' }}
    </div>
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
  }
})

const settingsStore = useSettingsStore()
const { language } = storeToRefs(settingsStore)

const copied = ref(false)

const mermaidCode = computed(() => {
  // 从结果中提取 mermaid 架构图代码
  if (props.result?.mermaid_architecture) {
    return props.result.mermaid_architecture
  }
  // 如果没有预生成的架构图，根据目录结构生成
  if (props.result?.directory_structure) {
    return generateFromTree(props.result.directory_structure)
  }
  return null
})

function generateFromTree(directoryStructure) {
  let tree
  try {
    tree = typeof directoryStructure === 'string'
      ? JSON.parse(directoryStructure)
      : directoryStructure
  } catch {
    tree = directoryStructure
  }

  const lines = ['flowchart TD', '    Root["项目根目录"]']

  function addNodes(node, parentId, depth = 0) {
    if (depth > 2) return

    if (typeof node === 'object' && node !== null) {
      for (const [name, children] of Object.entries(node)) {
        const nodeId = name.replace(/[^a-zA-Z0-9]/g, '_')
        const isDir = children && typeof children === 'object'

        if (isDir) {
          lines.push(`    ${nodeId}["${name}"]`)
          lines.push(`    ${parentId} --> ${nodeId}`)
          addNodes(children, nodeId, depth + 1)
        }
      }
    }
  }

  if (tree) {
    addNodes(tree, 'Root')
  }

  return lines.join('\n')
}

function copyToClipboard() {
  if (mermaidCode.value) {
    navigator.clipboard.writeText(mermaidCode.value)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  }
}

function openMermaidEditor() {
  if (mermaidCode.value) {
    const encoded = encodeURIComponent(mermaidCode.value)
    window.open(`https://mermaid.live/edit?text=${encoded}`, '_blank')
  }
}
</script>

<style scoped>
.architecture-diagram {
  padding: 10px 0;
}

.diagram-container {
  border: 1px solid var(--border-color, #eee);
  border-radius: 8px;
  padding: 15px;
  background: var(--bg-color, #fff);
}

.diagram-actions {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.mermaid-code {
  background: var(--code-bg-color, #f5f5f5);
  padding: 15px;
  border-radius: 6px;
  overflow-x: auto;
  font-family: 'Consolas', monospace;
  font-size: 12px;
  line-height: 1.5;
}

.mermaid-code code {
  white-space: pre;
}

.empty {
  text-align: center;
  padding: 40px;
  color: var(--text-color-secondary, #999);
}
</style>