import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { startAnalyze, getTaskStatus, cancelAnalysis } from '@/api/analyze'
import { createWebSocket } from '@/api/analyze'

export const useAnalysisStore = defineStore('analysis', () => {
  // 状态
  const jobId = ref('')
  const status = ref('idle') // idle, pending, running, completed, failed, cancelled
  const progress = ref(0)
  const progressMessage = ref('')
  const stageKey = ref('')
  const result = ref(null)
  const error = ref('')
  const repoUrl = ref('')
  const mode = ref('fast')

  // WebSocket
  let ws = null
  let statusPolling = null

  // 计算属性
  const isAnalyzing = computed(() => status.value === 'pending' || status.value === 'running')
  const isCompleted = computed(() => status.value === 'completed')
  const isFailed = computed(() => status.value === 'failed')

  // 启动分析
  async function start(url) {
    repoUrl.value = url
    error.value = ''
    result.value = null

    try {
      const response = await startAnalyze(url)
      jobId.value = response.data.job_id
      status.value = 'pending'
      progress.value = 0
      progressMessage.value = '正在启动分析...'

      // 连接 WebSocket
      connectWebSocket()

      // 备用：轮询状态
      startPolling()
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
      status.value = 'failed'
    }
  }

  // 连接 WebSocket
  function connectWebSocket() {
    ws = createWebSocket(jobId.value)

    ws.onopen = () => {
      console.log('WebSocket connected')
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)

      if (data.type === 'status' || data.type === 'progress') {
        updateStatus(data)
      } else if (data.type === 'result') {
        status.value = 'completed'
        result.value = data.result
        progress.value = 100
        progressMessage.value = '分析完成！'
        stopPolling()
        window.dispatchEvent(new CustomEvent('analysis-completed', { detail: data.result }))
      } else if (data.type === 'error') {
        status.value = 'failed'
        error.value = data.error
        stopPolling()
      } else if (data.type === 'cancelled') {
        status.value = 'cancelled'
        stopPolling()
      }
    }

    ws.onerror = (e) => {
      console.error('WebSocket error:', e)
    }

    ws.onclose = () => {
      console.log('WebSocket closed')
    }
  }

  // 更新状态
  function updateStatus(data) {
    if (data.status) status.value = data.status
    if (data.progress !== undefined) progress.value = data.progress
    if (data.message) progressMessage.value = data.message
    if (data.stage_key) stageKey.value = data.stage_key
  }

  // 轮询状态（降低频率到 6 秒，减少服务器压力）
  function startPolling() {
    statusPolling = setInterval(async () => {
      if (!jobId.value) return

      try {
        const response = await getTaskStatus(jobId.value)
        const task = response.data

        status.value = task.status
        progress.value = task.progress
        progressMessage.value = task.progress_message

        // 从 progress_message 推断 stageKey
        if (task.progress_message) {
          const msg = task.progress_message
          if (msg.includes('验证仓库')) stageKey.value = 'validating'
          else if (msg.includes('获取仓库信息')) stageKey.value = 'getting_repo_info'
          else if (msg.includes('生成学习文档')) stageKey.value = 'generating_learning_doc'
          else if (msg.includes('生成启动指南')) stageKey.value = 'generating_setup_guide'
          else if (msg.includes('整理结果')) stageKey.value = 'finalizing'
          else if (msg.includes('完成')) stageKey.value = 'completed'
        }

        if (task.status === 'completed') {
          result.value = task.result
          stopPolling()
          // 触发完成事件（通过自定义事件通知组件）
          window.dispatchEvent(new CustomEvent('analysis-completed', { detail: task.result }))
        } else if (task.status === 'failed') {
          error.value = task.error
          stopPolling()
        } else if (task.status === 'cancelled') {
          stopPolling()
        }
      } catch (e) {
        console.error('Polling error:', e)
      }
    }, 6000)
  }

  function stopPolling() {
    if (statusPolling) {
      clearInterval(statusPolling)
      statusPolling = null
    }
    if (ws) {
      ws.close()
      ws = null
    }
  }

  // 取消分析
  async function cancel() {
    try {
      await cancelAnalysis(jobId.value)
      status.value = 'cancelled'
      stopPolling()
    } catch (e) {
      error.value = e.message
    }
  }

  // 重置
  function reset() {
    stopPolling()
    jobId.value = ''
    status.value = 'idle'
    progress.value = 0
    progressMessage.value = ''
    stageKey.value = ''
    result.value = null
    error.value = ''
    repoUrl.value = ''
  }

  // 设置仓库 URL
  function setRepoUrl(url) {
    repoUrl.value = url
  }

  // 设置结果
  function setResult(data) {
    result.value = data
    status.value = 'completed'
  }

  return {
    // 状态
    jobId,
    status,
    progress,
    progressMessage,
    stageKey,
    result,
    error,
    repoUrl,
    mode,
    // 计算属性
    isAnalyzing,
    isCompleted,
    isFailed,
    // 方法
    start,
    cancel,
    reset,
    setRepoUrl,
    setResult
  }
})