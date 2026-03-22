<template>
  <div class="chat">
    <div v-if="!store.result" class="empty-state">
      <div class="empty-illustration">
        <svg viewBox="0 0 120 120" class="empty-svg">
          <defs>
            <linearGradient id="chatEmptyGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" style="stop-color:#3d5a6c" />
              <stop offset="100%" style="stop-color:#2c3e4a" />
            </linearGradient>
          </defs>
          <circle cx="60" cy="50" r="30" fill="none" stroke="url(#chatEmptyGrad)" stroke-width="1.5" opacity="0.3"/>
          <circle cx="50" cy="45" r="5" fill="url(#chatEmptyGrad)" opacity="0.5"/>
          <circle cx="70" cy="45" r="5" fill="url(#chatEmptyGrad)" opacity="0.5"/>
          <path d="M45 58 Q60 70 75 58" fill="none" stroke="url(#chatEmptyGrad)" stroke-width="2" stroke-linecap="round" opacity="0.5"/>
          <ellipse cx="60" cy="90" rx="25" ry="8" fill="none" stroke="url(#chatEmptyGrad)" stroke-width="1" opacity="0.2"/>
        </svg>
      </div>
      <el-empty :description="t('chat.noContext', language)">
        <el-button type="primary" @click="$router.push('/')">{{ language === 'zh' ? '去分析' : 'Go to Analyze' }}</el-button>
      </el-empty>
    </div>

    <div v-else class="chat-container">
      <div class="chat-header">
        <div class="header-left">
          <el-button text class="nav-btn" @click="$router.push('/')">
            <span class="nav-icon">←</span>
          </el-button>
          <el-button text class="nav-btn" @click="$router.push('/docs')">
            <span class="nav-icon">📖</span>
          </el-button>
        </div>
        <div class="header-center">
          <h1 class="chat-title">
            <span class="title-icon">💭</span>
            {{ t('chat.title', language) }}
          </h1>
        </div>
        <div class="header-right">
          <el-button text class="clear-btn" @click="handleClearHistory">
            <span class="clear-icon">🗑</span>
          </el-button>
        </div>
      </div>

      <div class="repo-info-bar">
        <div class="repo-badge">
          <span class="badge-icon">📁</span>
          <span class="badge-text">{{ store.result?.repo_info?.full_name }}</span>
        </div>
        <div class="knowledge-status" v-if="isIndexing">
          <el-tag type="info" size="small">
            <span class="status-icon">⏳</span>
            {{ language === 'zh' ? '正在构建索引...' : 'Building index...' }}
          </el-tag>
        </div>
      </div>

      <div class="messages" ref="messagesRef">
        <div v-if="messages.length === 0 && !isIndexing && !isLoading" class="welcome-message">
          <div class="welcome-icon">
            <svg viewBox="0 0 60 60" width="60" height="60">
              <defs>
                <linearGradient id="aiGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style="stop-color:#c4a35a" />
                  <stop offset="100%" style="stop-color:#3d5a6c" />
                </linearGradient>
              </defs>
              <circle cx="30" cy="30" r="28" fill="none" stroke="url(#aiGrad)" stroke-width="1" opacity="0.2"/>
              <circle cx="30" cy="30" r="20" fill="url(#aiGrad)" opacity="0.15"/>
              <path d="M22 28 L28 24 L34 28 L34 36 L28 40 L22 36 Z" fill="url(#aiGrad)" opacity="0.6"/>
              <circle cx="26" cy="28" r="2" fill="url(#aiGrad)"/>
              <circle cx="34" cy="28" r="2" fill="url(#aiGrad)"/>
            </svg>
          </div>
          <p class="welcome-text">{{ language === 'zh' ? '你好！我是 GitGuide AI 助手。' : 'Hello! I am GitGuide AI Assistant.' }}</p>
          <p class="welcome-hint">{{ language === 'zh' ? '你可以问我关于这个项目的问题，例如：' : 'You can ask me questions about this project, for example:' }}</p>
          <ul class="example-list">
            <li @click="handleExampleClick(0)">{{ language === 'zh' ? '如何安装这个项目？' : 'How to install this project?' }}</li>
            <li @click="handleExampleClick(1)">{{ language === 'zh' ? '这个项目的主要功能是什么？' : 'What are the main features?' }}</li>
            <li @click="handleExampleClick(2)">{{ language === 'zh' ? '分析 main.py 文件' : 'Analyze main.py file' }}</li>
          </ul>
        </div>

        <div v-if="isIndexing" class="indexing-message">
          <div class="indexing-icon">🔍</div>
          <p>{{ language === 'zh' ? '正在构建源码索引，请稍候...' : 'Building source code index, please wait...' }}</p>
          <p class="indexing-hint">{{ language === 'zh' ? '首次加载可能需要几分钟' : 'First load may take a few minutes' }}</p>
        </div>

        <transition-group name="message" tag="div">
          <div
            v-for="(msg, index) in renderedMessages"
            :key="index"
            class="message"
            :class="msg.role"
          >
            <div class="message-avatar">
              <span v-if="msg.role === 'user'" class="avatar-icon">👤</span>
              <span v-else class="avatar-icon">🤖</span>
            </div>
            <div class="message-bubble">
              <div class="message-content" v-html="msg.renderedContent"></div>
              <div class="referenced-files" v-if="msg.role === 'assistant' && msg.referencedFiles && msg.referencedFiles.length > 0">
                <span class="ref-label">{{ language === 'zh' ? '引用文件：' : 'Referenced files:' }}</span>
                <span
                  v-for="file in msg.referencedFiles"
                  :key="file"
                  class="ref-file"
                  @click="openFileViewer(file)"
                >
                  📄 {{ file }}
                </span>
              </div>
            </div>
          </div>
        </transition-group>

        <div v-if="isLoading" class="message assistant">
          <div class="message-avatar">
            <span class="avatar-icon">🤖</span>
          </div>
          <div class="message-bubble loading-bubble">
            <div class="loading-indicator">
              <span class="loading-dot"></span>
              <span class="loading-dot"></span>
              <span class="loading-dot"></span>
            </div>
            <span class="loading-text">{{ language === 'zh' ? '思考中...' : 'Thinking...' }}</span>
          </div>
        </div>
      </div>

      <div class="input-area">
        <div class="input-wrapper">
          <div class="file-hint" v-if="detectedFile">
            <span class="hint-icon">📎</span>
            <span class="hint-text">{{ language === 'zh' ? '检测到文件：' : 'Detected file:' }} {{ detectedFile }}</span>
            <el-button text size="small" @click="clearDetectedFile">✕</el-button>
          </div>
          <el-input
            v-model="inputMessage"
            :placeholder="t('chat.placeholder', language)"
            :disabled="isLoading || isIndexing"
            class="chat-input"
            @keyup.enter="handleSend"
          >
            <template #append>
              <div class="input-actions">
                <el-button
                  v-if="isLoading"
                  class="action-btn stop-btn"
                  @click="handleStop"
                  :title="language === 'zh' ? '停止思考' : 'Stop thinking'"
                >
                  <span class="stop-icon">⏹</span>
                </el-button>
                <el-button
                  v-else
                  class="action-btn send-btn"
                  @click="handleSend"
                  :disabled="isIndexing || !inputMessage.trim()"
                >
                  <span class="send-icon">🚀</span>
                </el-button>
              </div>
            </template>
          </el-input>
        </div>

        <div class="quick-questions" v-if="!isIndexing">
          <el-button
            v-for="(q, index) in quickQuestions"
            :key="index"
            size="small"
            class="quick-btn"
            @click="handleExampleClick(index)"
          >
            {{ language === 'zh' ? q.zh : q.en }}
          </el-button>
        </div>
      </div>

      <CodeViewer
        v-model="showCodeViewer"
        :file-path="selectedFile"
        :repo-url="store.repoUrl"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAnalysisStore } from '@/stores/analysis'
import { useSettingsStore } from '@/stores/settings'
import { storeToRefs } from 'pinia'
import { sendChat, getChatHistory, clearChatHistory, buildKnowledgeBase as buildKB } from '@/api/chat'
import { ElMessage } from 'element-plus'
import { t } from '@/i18n'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import CodeViewer from '@/components/CodeViewer.vue'

const router = useRouter()
const store = useAnalysisStore()
const settingsStore = useSettingsStore()
const { language } = storeToRefs(settingsStore)

const inputMessage = ref('')
const messages = ref([])
const isLoading = ref(false)
const isIndexing = ref(false)
const messagesRef = ref(null)
const knowledgeBaseReady = ref(false)
const showCodeViewer = ref(false)
const selectedFile = ref('')
const detectedFile = ref('')

const renderedMessages = computed(() => {
  return messages.value.map(msg => ({
    ...msg,
    renderedContent: msg.role === 'assistant'
      ? DOMPurify.sanitize(marked(msg.content || ''))
      : msg.content
  }))
})

const quickQuestions = [
  { zh: '如何安装这个项目？', en: 'How to install this project?' },
  { zh: '这个项目的主要功能是什么？', en: 'What are the main features?' },
  { zh: '分析 main.py 文件', en: 'Analyze main.py file' }
]

const exampleQuestions = [
  { zh: '如何安装这个项目？', en: 'How to install this project?' },
  { zh: '这个项目的主要功能是什么？', en: 'What are the main features?' },
  { zh: '分析 main.py 文件', en: 'Analyze main.py file' }
]

function extractFilePath(query) {
  const patterns = [
    /(?:analyze|分析|查看|look at|show me)\s+([^\s]+\.(?:py|js|ts|jsx|tsx|java|go|rs|cpp|c|h|hpp|cs|rb|php|swift|kt|scala))/i,
    /([^\s]+\.(?:py|js|ts|jsx|tsx|java|go|rs|cpp|c|h|hpp|cs|rb|php|swift|kt|scala))/i,
  ]

  for (const pattern of patterns) {
    const match = query.match(pattern)
    if (match) {
      return match[1]
    }
  }
  return null
}

function handleExampleClick(index) {
  if (isIndexing.value || isLoading.value) return

  const q = exampleQuestions[index]
  if (!q) return

  const question = language.value === 'zh' ? q.zh : q.en
  inputMessage.value = question

  nextTick(() => {
    handleSend()
  })
}

async function handleSend() {
  if (!inputMessage.value.trim() || isLoading.value || isIndexing.value) return

  const query = inputMessage.value.trim()
  inputMessage.value = ''

  detectedFile.value = extractFilePath(query) || ''

  messages.value.push({ role: 'user', content: query })
  scrollToBottom()

  isLoading.value = true

  try {
    const history = messages.value.map(m => ({
      role: m.role,
      content: m.content
    }))

    const response = await sendChat(
      store.repoUrl,
      query,
      history,
      detectedFile.value || null
    )

    if (response.data.success) {
      messages.value.push({
        role: 'assistant',
        content: response.data.response,
        referencedFiles: response.data.referenced_files || []
      })
    } else {
      ElMessage.error(response.data.response)
      messages.value.push({
        role: 'assistant',
        content: language.value === 'zh' ? '抱歉，我遇到了问题，请稍后重试。' : 'Sorry, I encountered an issue. Please try again later.'
      })
    }
  } catch (e) {
    ElMessage.error(language.value === 'zh' ? '请求失败: ' : 'Request failed: ' + (e.response?.data?.detail || e.message))
    messages.value.push({
      role: 'assistant',
      content: language.value === 'zh' ? '抱歉，服务出错了。' : 'Sorry, an error occurred.'
    })
  }

  isLoading.value = false
  detectedFile.value = ''
  scrollToBottom()
}

function handleStop() {
  isLoading.value = false
  messages.value.push({
    role: 'assistant',
    content: language.value === 'zh' ? '思考已中止。请尝试其他问题。' : 'Thinking stopped. Please try another question.'
  })
  scrollToBottom()
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

async function handleClearHistory() {
  try {
    const { ElMessageBox } = await import('element-plus')

    await ElMessageBox.confirm(
      language.value === 'zh' ? '确定要清除所有对话记录吗？' : 'Are you sure to clear all chat history?',
      language.value === 'zh' ? '确认清除' : 'Confirm Clear',
      {
        confirmButtonText: language.value === 'zh' ? '确定' : 'Confirm',
        cancelButtonText: language.value === 'zh' ? '取消' : 'Cancel',
        type: 'warning'
      }
    )

    await clearChatHistory(store.repoUrl)
    messages.value = []
    ElMessage.success(language.value === 'zh' ? '对话记录已清除' : 'Chat history cleared')
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(language.value === 'zh' ? '清除失败' : 'Clear failed')
    }
  }
}

async function buildKnowledgeBase() {
  isIndexing.value = true

  try {
    const response = await buildKB(store.repoUrl)
    if (response.data.success) {
      knowledgeBaseReady.value = true
    } else {
      knowledgeBaseReady.value = true
      console.warn('Knowledge base build warning:', response.data.error)
    }
  } catch (e) {
    console.warn('Knowledge base build failed, will use fallback:', e)
    knowledgeBaseReady.value = true
  } finally {
    isIndexing.value = false
  }
}

function openFileViewer(file) {
  selectedFile.value = file
  showCodeViewer.value = true
}

function clearDetectedFile() {
  detectedFile.value = ''
}

onMounted(async () => {
  if (!store.result) {
    ElMessage.warning(language.value === 'zh' ? '请先分析仓库' : 'Please analyze a repo first')
    router.push('/')
  } else {
    buildKnowledgeBase()

    try {
      const response = await getChatHistory(store.repoUrl)
      if (response.data.messages) {
        messages.value = response.data.messages
      }
    } catch (e) {
      console.error('Failed to load chat history:', e)
    }
  }
})
</script>

<style scoped>
.chat {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
  height: calc(100vh - 40px);
  display: flex;
  flex-direction: column;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.empty-illustration {
  width: 120px;
  height: 120px;
  margin-bottom: 24px;
  opacity: 0.5;
}

.empty-svg {
  width: 100%;
  height: 100%;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--bg-paper);
  border-radius: var(--radius-lg);
  overflow: hidden;
  border: 1px solid var(--border-light);
  box-shadow: var(--shadow-sm);
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  background: var(--bg-warm);
  border-bottom: 1px solid var(--border-light);
}

.header-left,
.header-right {
  display: flex;
  align-items: center;
  gap: 4px;
}

.header-center {
  flex: 1;
  text-align: center;
}

.chat-title {
  font-family: 'Noto Serif SC', Georgia, serif;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.title-icon {
  font-size: 20px;
}

.nav-btn {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md) !important;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-color-secondary) !important;
  transition: all var(--transition-normal);
}

.nav-btn:hover {
  background: var(--bg-paper) !important;
  color: var(--text-color) !important;
}

.nav-icon {
  font-size: 18px;
}

.clear-btn {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md) !important;
  color: var(--text-color-muted) !important;
  transition: all var(--transition-normal);
}

.clear-btn:hover {
  color: var(--danger-color) !important;
  background: rgba(166, 93, 93, 0.1) !important;
}

.repo-info-bar {
  padding: 12px 20px;
  background: var(--bg-color);
  border-bottom: 1px solid var(--border-light);
  display: flex;
  align-items: center;
  gap: 12px;
}

.repo-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: var(--bg-warm);
  border-radius: var(--radius-md);
  font-size: 13px;
  color: var(--text-color-secondary);
}

.badge-icon {
  font-size: 14px;
}

.badge-text {
  font-family: 'Crimson Pro', monospace;
  font-weight: 500;
}

.knowledge-status {
  display: flex;
  align-items: center;
}

.status-icon {
  margin-right: 4px;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.welcome-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 40px 20px;
  color: var(--text-color-secondary);
}

.welcome-icon {
  margin-bottom: 20px;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}

.welcome-text {
  font-size: 18px;
  font-weight: 500;
  color: var(--text-color);
  margin: 0 0 8px;
}

.welcome-hint {
  font-size: 14px;
  color: var(--text-color-muted);
  margin: 0 0 16px;
}

.example-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
  text-align: left;
  width: 100%;
  max-width: 300px;
}

.example-list li {
  padding: 10px 16px;
  background: var(--bg-warm);
  border-radius: var(--radius-md);
  font-size: 14px;
  color: var(--primary-color);
  transition: all var(--transition-normal);
  cursor: pointer;
}

.example-list li:hover {
  background: var(--primary-color);
  color: #fff;
  transform: translateX(4px);
}

.indexing-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 20px;
  color: var(--text-color-secondary);
}

.indexing-icon {
  font-size: 48px;
  margin-bottom: 16px;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.7; transform: scale(0.95); }
}

.indexing-message p {
  margin: 0 0 8px;
  font-size: 16px;
}

.indexing-hint {
  font-size: 13px;
  color: var(--text-color-muted);
}

.message {
  display: flex;
  gap: 12px;
  max-width: 85%;
}

.message.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-warm);
  border-radius: 50%;
}

.avatar-icon {
  font-size: 18px;
}

.message.assistant .message-avatar {
  background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
}

.message.assistant .avatar-icon {
  filter: grayscale(1) invert(1);
}

.message-bubble {
  padding: 14px 18px;
  border-radius: var(--radius-lg);
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.message.user .message-bubble {
  background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
  color: #fff;
  border-bottom-right-radius: 4px;
}

.message.assistant .message-bubble {
  background: var(--bg-warm);
  color: var(--text-color);
  border-bottom-left-radius: 4px;
}

.message-content {
  font-size: 14px;
}

.message-content :deep(p) {
  margin: 0 0 8px;
}

.message-content :deep(p:last-child) {
  margin-bottom: 0;
}

.message-content :deep(code) {
  background: rgba(0, 0, 0, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
  font-family: 'Crimson Pro', monospace;
}

.message-content :deep(pre) {
  background: rgba(0, 0, 0, 0.15);
  padding: 12px;
  border-radius: var(--radius-sm);
  overflow-x: auto;
  margin: 8px 0;
}

.message-content :deep(pre code) {
  background: none;
  padding: 0;
}

.message-content :deep(ul),
.message-content :deep(ol) {
  padding-left: 20px;
  margin: 8px 0;
}

.referenced-files {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border-light);
}

.ref-label {
  font-size: 12px;
  color: var(--text-color-muted);
  line-height: 24px;
}

.ref-file {
  font-size: 12px;
  color: var(--primary-color);
  cursor: pointer;
  padding: 2px 8px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 4px;
  transition: all 0.2s;
}

.ref-file:hover {
  background: var(--primary-color);
  color: #fff;
}

.loading-bubble {
  display: flex;
  align-items: center;
  gap: 12px;
}

.loading-indicator {
  display: flex;
  gap: 4px;
}

.loading-dot {
  width: 8px;
  height: 8px;
  background: var(--text-color-muted);
  border-radius: 50%;
  animation: bounce 1.4s ease-in-out infinite;
}

.loading-dot:nth-child(1) { animation-delay: 0s; }
.loading-dot:nth-child(2) { animation-delay: 0.2s; }
.loading-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-8px); }
}

.loading-text {
  font-size: 13px;
  color: var(--text-color-muted);
}

.input-area {
  padding: 16px 20px 20px;
  background: var(--bg-warm);
  border-top: 1px solid var(--border-light);
}

.input-wrapper {
  margin-bottom: 12px;
}

.file-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: var(--radius-md);
  margin-bottom: 8px;
  font-size: 13px;
  color: var(--text-color-secondary);
}

.hint-icon {
  font-size: 14px;
}

.hint-text {
  flex: 1;
  font-family: 'Crimson Pro', monospace;
}

.chat-input {
  width: 100%;
}

.chat-input :deep(.el-input__wrapper) {
  padding: 6px 12px !important;
}

.action-btn {
  min-width: 44px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none !important;
  border-radius: var(--radius-md) !important;
  transition: all 0.2s ease;
}

.send-btn {
  background: linear-gradient(135deg, var(--primary-color), var(--primary-dark)) !important;
  cursor: pointer !important;
}

.send-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed !important;
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.send-icon {
  font-size: 16px;
  color: #fff;
}

.input-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 4px;
  background: transparent !important;
}

.stop-btn {
  background: var(--danger-color) !important;
}

.stop-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stop-icon {
  font-size: 14px;
  color: #fff;
}

.quick-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.quick-btn {
  font-size: 13px;
  padding: 6px 14px;
  background: var(--bg-paper) !important;
  border-color: var(--border-color) !important;
  color: var(--text-color-secondary) !important;
}

.quick-btn:hover {
  border-color: var(--primary-color) !important;
  color: var(--primary-color) !important;
}

.message-enter-active {
  transition: all 0.3s ease;
}

.message-leave-active {
  transition: all 0.2s ease;
}

.message-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.message-leave-to {
  opacity: 0;
}
</style>
