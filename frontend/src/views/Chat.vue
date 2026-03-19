<template>
  <div class="chat">
    <div class="header">
      <el-button text @click="$router.push('/')">← 返回首页</el-button>
      <el-button text @click="$router.push('/docs')">📚 文档</el-button>
      <h1 class="title">💬 AI 问答</h1>
    </div>

    <div v-if="!store.result" class="empty-state">
      <el-empty description="暂无分析结果，请先分析仓库">
        <el-button type="primary" @click="$router.push('/')">去分析</el-button>
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
          <p>你好！我是 GitGuide AI 助手。</p>
          <p>你可以问我关于这个项目的问题，例如：</p>
          <ul>
            <li>如何安装这个项目？</li>
            <li>这个项目的主要功能是什么？</li>
            <li>如何运行这个项目？</li>
          </ul>
        </div>

        <div
          v-for="(msg, index) in messages"
          :key="index"
          class="message"
          :class="msg.role"
        >
          <div class="message-avatar">
            {{ msg.role === 'user' ? '👤' : '🤖' }}
          </div>
          <div class="message-content">
            {{ msg.content }}
          </div>
        </div>

        <div v-if="isLoading" class="message assistant">
          <div class="message-avatar">🤖</div>
          <div class="message-content">
            <span class="loading-dots">思考中...</span>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="input-area">
        <el-input
          v-model="inputMessage"
          placeholder="问关于这个项目的问题..."
          :disabled="isLoading"
          @keyup.enter="handleSend"
        >
          <template #append>
            <el-button :loading="isLoading" @click="handleSend">发送</el-button>
          </template>
        </el-input>
      </div>

      <!-- 快捷问题 -->
      <div class="quick-questions">
        <el-button
          v-for="q in quickQuestions"
          :key="q"
          size="small"
          text
          @click="inputMessage = q"
        >
          {{ q }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAnalysisStore } from '@/stores/analysis'
import { sendChat } from '@/api/chat'
import { ElMessage } from 'element-plus'

const router = useRouter()
const store = useAnalysisStore()

const inputMessage = ref('')
const messages = ref([])
const isLoading = ref(false)
const messagesRef = ref(null)

const quickQuestions = [
  '如何安装这个项目？',
  '如何运行这个项目？',
  '这个项目的主要功能是什么？',
  '项目使用了什么技术栈？'
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
      messages.value.push({ role: 'assistant', content: '抱歉，我遇到了问题，请稍后重试。' })
    }
  } catch (e) {
    ElMessage.error('请求失败: ' + (e.response?.data?.detail || e.message))
    messages.value.push({ role: 'assistant', content: '抱歉，服务出错 了。' })
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

onMounted(() => {
  if (!store.result) {
    ElMessage.warning('请先分析仓库')
    router.push('/')
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
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
}

.repo-badge {
  padding: 10px 20px;
  background: #f5f7fa;
  border-bottom: 1px solid #eee;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.welcome-message {
  color: #666;
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
  background: #409eff;
  color: #fff;
}

.message.assistant .message-content {
  background: #f5f7fa;
  color: #333;
}

.loading-dots {
  color: #999;
}

.input-area {
  padding: 15px 20px;
  border-top: 1px solid #eee;
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