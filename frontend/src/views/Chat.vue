<template>
  <div class="chat">
    <div class="header">
      <el-button text @click="$router.push('/')">← {{ language === 'zh' ? '返回首页' : 'Back' }}</el-button>
      <el-button text @click="$router.push('/docs')">📚 {{ language === 'zh' ? '文档' : 'Docs' }}</el-button>
      <h1 class="title">💬 {{ t('chat.title', language) }}</h1>
      <el-button v-if="messages.length > 0" type="danger" text @click="handleClearHistory">
        🗑️ {{ language === 'zh' ? '清除记录' : 'Clear History' }}
      </el-button>
    </div>

    <div v-if="!store.result" class="empty-state">
      <el-empty :description="t('chat.noContext', language)">
        <el-button type="primary" @click="$router.push('/')">{{ language === 'zh' ? '去分析' : 'Go to Analyze' }}</el-button>
      </el-empty>
    </div>

    <div v-else class="chat-container">
      <!-- 仓库信息 -->
      <div class="repo-badge">
        <el-tag>{{ store.result?.repo_info?.full_name }}</el-tag>
      </div>

      <!-- 聊天消息 -->
      <div class="messages" ref="messagesRef">
        <div v-if="messages.length === 0" class="welcome-message">
          <p>{{ language === 'zh' ? '你好！我是 GitGuide AI 助手。' : 'Hello! I am GitGuide AI Assistant.' }}</p>
          <p>{{ language === 'zh' ? '你可以问我关于这个项目的问题，例如：' : 'You can ask me questions about this project, for example:' }}</p>
          <ul>
            <li>{{ language === 'zh' ? '如何安装这个项目？' : 'How to install this project?' }}</li>
            <li>{{ language === 'zh' ? '这个项目的主要功能是什么？' : 'What are the main features of this project?' }}</li>
            <li>{{ language === 'zh' ? '如何运行这个项目？' : 'How to run this project?' }}</li>
          </ul>
        </div>

        <div
          v-for="(msg, index) in renderedMessages"
          :key="index"
          class="message"
          :class="msg.role"
        >
          <div class="message-avatar">
            {{ msg.role === 'user' ? '👤' : '🤖' }}
          </div>
          <div class="message-content" v-html="msg.renderedContent"></div>
        </div>

        <div v-if="isLoading" class="message assistant">
          <div class="message-avatar">🤖</div>
          <div class="message-content">
            <span class="loading-dots">{{ language === 'zh' ? '思考中...' : 'Thinking...' }}</span>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="input-area">
        <el-input
          v-model="inputMessage"
          :placeholder="t('chat.placeholder', language)"
          :disabled="isLoading"
          @keyup.enter="handleSend"
        >
          <template #append>
            <el-button :loading="isLoading" @click="handleSend">{{ t('chat.send', language) }}</el-button>
          </template>
        </el-input>
      </div>

      <!-- 快捷问题 -->
      <div class="quick-questions">
        <el-button
          v-for="q in quickQuestions"
          :key="q.zh"
          size="small"
          text
          @click="inputMessage = language === 'zh' ? q.zh : q.en"
        >
          {{ language === 'zh' ? q.zh : q.en }}
        </el-button>
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
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  height: calc(100vh - 40px);
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.title {
  margin: 0;
}

.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--bg-color-secondary, #fff);
  border-radius: 8px;
  overflow: hidden;
}

.repo-badge {
  padding: 10px 20px;
  background: var(--bg-color, #f5f7fa);
  border-bottom: 1px solid var(--border-color, #eee);
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.welcome-message {
  color: var(--text-color-secondary, #666);
  line-height: 1.8;
}

.welcome-message ul {
  padding-left: 20px;
}

.message {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.message-avatar {
  font-size: 24px;
  flex-shrink: 0;
}

.message-content {
  flex: 1;
  padding: 12px 16px;
  border-radius: 8px;
  line-height: 1.5;
  white-space: pre-wrap;
}

.message.user .message-content {
  background: var(--primary-color, #409eff);
  color: #fff;
}

.message.assistant .message-content {
  background: var(--bg-color, #f5f7fa);
  color: var(--text-color, #333);
}

.loading-dots {
  color: #999;
}

.input-area {
  padding: 15px 20px;
  border-top: 1px solid var(--border-color, #eee);
}

.input-area .el-input {
  width: 100%;
}

.quick-questions {
  padding: 0 20px 15px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
</style>