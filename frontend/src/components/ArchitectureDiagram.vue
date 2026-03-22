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
      <div :id="diagramId" class="mermaid"></div>
    </div>
    <div v-else class="empty">
      {{ language === 'zh' ? '暂无架构图信息' : 'No architecture diagram available' }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import { storeToRefs } from 'pinia'
import mermaid from 'mermaid'

const props = defineProps({
  result: {
    type: Object,
    default: null
  }
})

const settingsStore = useSettingsStore()
const { language } = storeToRefs(settingsStore)

const copied = ref(false)

mermaid.initialize({
  startOnLoad: false,
  theme: 'base',
  themeVariables: {
    primaryColor: '#3d5a6c',
    primaryTextColor: '#2c3e4a',
    primaryBorderColor: '#3d5a6c',
    lineColor: '#8b7355',
    secondaryColor: '#c4a35a',
    tertiaryColor: '#f5f5f5'
  },
  flowchart: {
    useMaxWidth: true,
    htmlLabels: true
  }
})

const mermaidCode = computed(() => {
  if (props.result?.mermaid_architecture) {
    return props.result.mermaid_architecture
  }
  if (props.result?.directory_structure) {
    return generateFromTree(props.result.directory_structure)
  }
  return null
})

const generateDiagramId = () => `mermaid-${Math.random().toString(36).substr(2, 9)}`
const diagramId = ref(generateDiagramId())

async function renderDiagram() {
  if (!mermaidCode.value) return

  await nextTick()

  const container = document.getElementById(diagramId.value)
  if (!container) {
    console.warn('Mermaid container not found:', diagramId.value)
    return
  }

  try {
    const { svg } = await mermaid.render(
      `mermaid-svg-${Date.now()}`,
      mermaidCode.value
    )
    container.innerHTML = svg
  } catch (error) {
    console.error('Mermaid render error:', error)
    container.innerHTML = `<pre class="mermaid-error">${mermaidCode.value}</pre>`
  }
}

onMounted(() => {
  renderDiagram()
})

watch(mermaidCode, () => {
  renderDiagram()
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

.mermaid {
  background: var(--code-bg-color, #f5f5f5);
  padding: 15px;
  border-radius: 6px;
  overflow-x: auto;
}

.mermaid svg {
  max-width: 100%;
  height: auto;
}

.mermaid-error {
  color: var(--danger-color, #a6555d);
  white-space: pre-wrap;
  word-break: break-word;
}

.empty {
  text-align: center;
  padding: 40px;
  color: var(--text-color-secondary, #999);
}
</style>