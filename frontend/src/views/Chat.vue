<template>
  <div class="chat">
    <!-- 空状态 -->
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
      <!-- 顶部导航 -->
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
          <el-button v-if="messages.length > 0" text class="clear-btn" @click="handleClearHistory">
            <span class="clear-icon">🗑</span>
          </el-button>
        </div>
      </div>

      <!-- 仓库信息 -->
      <div class="repo-info-bar">
        <div class="repo-badge">
          <span class="badge-icon">📁</span>
          <span class="badge-text">{{ store.result?.repo_info?.full_name }}</span>
        </div>
      </div>

      <!-- 消息区域 -->
      <div class="messages" ref="messagesRef">
        <div v-if="messages.length === 0" class="welcome-message">
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
            <li>{{ language === 'zh' ? '如何安装这个项目？' : 'How to install this project?' }}</li>
            <li>{{ language === 'zh' ? '这个项目的主要功能是什么？' : 'What are the main features?' }}</li>
            <li>{{ language === 'zh' ? '如何运行这个项目？' : 'How to run this project?' }}</li>
          </ul>
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

      <!-- 输入区域 -->
      <div class="input-area">
        <div class="input-wrapper">
          <el-input
            v-model="inputMessage"
            :placeholder="t('chat.placeholder', language)"
            :disabled="isLoading"
            class="chat-input"
            @keyup.enter="handleSend"
          >
            <template #append>
              <el-button :loading="isLoading" class="send-btn" @click="handleSend">
                <span v-if="!isLoading" class="send-icon">➤</span>
              </el-button>
            </template>
          </el-input>
        </div>

        <!-- 快捷问题 -->
        <div class="quick-questions">
          <el-button
            v-for="q in quickQuestions"
            :key="q.zh"
            size="small"
            class="quick-btn"
            @click="inputMessage = language === 'zh' ? q.zh : q.en"
          >
            {{ language === 'zh' ? q.zh : q.en }}
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAnalysisStore } from '@/stores/analysis'
import { useSettingsStore } from '@/stores/settings'
import { storeToRefs } from 'pinia'
import { sendChat, getChatHistory, clearChatHistory } from '@/api/chat'
import { ElMessage } from 'element-plus'
import { t } from '@/i18n'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const router = useRouter()
const store = useAnalysisStore()
const settingsStore = useSettingsStore()
const { language } = storeToRefs(settingsStore)

const inputMessage = ref('')
const messages = ref([])
const isLoading = ref(false)
const messagesRef = ref(null)

const renderedMessages = computed(() => {
  return messages.value.map(msg => ({
    ...msg,
    renderedContent: msg.role === 'assistant' 
      ? DOMPurify.sanitize(marked(msg.content))
      : msg.content
  }))
})

// 快捷问题: [中文, 英文]
const quickQuestions = [
  { zh: '如何安装这个项目？', en: 'How to install this project?' },
  { zh: '如何运行这个项目？', en: 'How to run this project?' },
  { zh: '这个项目的主要功能是什么？', en: 'What are the main features of this project?' },
  { zh: '项目使用了什么技术栈？', en: 'What tech stack does this project use?' }
]

async function handleSend() {
  if (!inputMessage.value.trim() || isLoading.value) return

  const query = inputMessage.value.trim()
  inputMessage.value = ''

  // 添加用户消息
  messages.value.push({ role: 'user', content: query })
  scrollToBottom()

  isLoading.value = true

  try {
    const history = messages.value.map(m => ({
      role: m.role,
      content: m.content
    }))

    const response = await sendChat(store.repoUrl, query, history)

    if (response.data.success) {
      messages.value.push({ role: 'assistant', content: response.data.response })
    } else {
      ElMessage.error(response.data.response)
      messages.value.push({ role: 'assistant', content: language.value === 'zh' ? '抱歉，我遇到了问题，请稍后重试。' : 'Sorry, I encountered an issue. Please try again later.' })
    }
  } catch (e) {
    ElMessage.error(language.value === 'zh' ? '请求失败: ' : 'Request failed: ' + (e.response?.data?.detail || e.message))
    messages.value.push({ role: 'assistant', content: language.value === 'zh' ? '抱歉，服务出错了。' : 'Sorry, an error occurred.' })
  }

  isLoading.value = false
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

onMounted(async () => {
  if (!store.result) {
    ElMessage.warning(language.value === 'zh' ? '请先分析仓库' : 'Please analyze a repo first')
    router.push('/')
  } else {
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

/* 空状态 */
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

/* 聊天容器 */
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

/* 聊天头部 */
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

/* 仓库信息栏 */
.repo-info-bar {
  padding: 12px 20px;
  background: var(--bg-color);
  border-bottom: 1px solid var(--border-light);
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

/* 消息区域 */
.messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 欢迎消息 */
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
}

.example-list li {
  padding: 10px 16px;
  background: var(--bg-warm);
  border-radius: var(--radius-md);
  font-size: 14px;
  color: var(--primary-color);
  transition: all var(--transition-normal);
}

.example-list li:hover {
  background: var(--primary-color);
  color: #fff;
  transform: translateX(4px);
}

/* 消息 */
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

/* 加载状态 */
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

/* 输入区域 */
.input-area {
  padding: 16px 20px 20px;
  background: var(--bg-warm);
  border-top: 1px solid var(--border-light);
}

.input-wrapper {
  margin-bottom: 12px;
}

.chat-input {
  width: 100%;
}

.chat-input :deep(.el-input__wrapper) {
  padding: 6px 12px !important;
}

.send-btn {
  min-width: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.send-icon {
  font-size: 16px;
  color: var(--primary-color);
}

/* 快捷问题 */
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

/* 消息过渡动画 */
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