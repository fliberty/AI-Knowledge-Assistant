<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ChatMessage from '../components/ChatMessage.vue'
import { useApi } from '../composables/useApi.js'

const route = useRoute()
const router = useRouter()
const { sendChatStream, getSession, loading } = useApi()

const messageInput = ref('')
const messages = ref([])
const chatContainer = ref(null)
const isTyping = ref(false)
const currentSessionId = ref(null)

const defaultWelcomeMessage = {
  role: 'assistant',
  content: '你好！我是 AI 知识库助手。这是全新的云端持久化对话，您可以随时在左侧边栏找到我！',
  sources: [],
}

async function loadSession(id) {
  loading.value = true
  try {
    const res = await getSession(id)
    if (res && res.data) {
      messages.value = res.data.messages.map(m => ({
        role: m.role,
        content: m.content,
        sources: m.sources ? JSON.parse(m.sources) : []
      }))
      currentSessionId.value = id
    }
  } catch (err) {
    console.warn("Failed to load session:", err)
    messages.value = [defaultWelcomeMessage]
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

// 每次挂载或路由跳转时重新决定该加载什么
onMounted(() => {
  if (route.params.id) {
    loadSession(route.params.id)
  } else {
    // 产生一个临时的 session ID 给这一轮新对话
    currentSessionId.value = window.crypto.randomUUID()
    messages.value = [defaultWelcomeMessage]
  }
})

// 当地址栏参数切换时也要重置聊天窗
watch(() => route.params.id, (newId) => {
  if (newId) {
    loadSession(newId)
  } else {
    currentSessionId.value = window.crypto.randomUUID()
    messages.value = [defaultWelcomeMessage]
  }
})

async function handleSend() {
  const text = messageInput.value.trim()
  if (!text || loading.value) return

  // 记录下是不是新对话的首条消息
  const isFirstMessage = messages.value.length <= 1;

  messages.value.push({ role: 'user', content: text, sources: [] })
  messageInput.value = ''
  await scrollToBottom()

  isTyping.value = true
  await scrollToBottom()

  try {
    // 将当前的 history 纯提取即可
    const historyPayload = messages.value
      .slice(0, -1)
      .map(m => ({ role: m.role, content: m.content }))

    messages.value.push({ role: 'assistant', content: '', sources: [] })
    const msgIndex = messages.value.length - 1

    const res = await sendChatStream(
      text, 
      historyPayload, 
      currentSessionId.value,
      (chunk) => {
        isTyping.value = false 
        messages.value[msgIndex].content += chunk
        scrollToBottom()
      },
      (sources) => {
        messages.value[msgIndex].sources = sources
      }
    )
    isTyping.value = false

    // 如果是一段新对话被建立（即 URL 里原本没有 ID）
    if (isFirstMessage && route.name === 'Chat' && !route.params.id) {
      // 通过 replace 将产生的会话挂回 URL，并且利用事件更新侧边栏（可以抛出一个 window event）
      router.replace({ name: 'Chat', params: { id: currentSessionId.value } })
      window.dispatchEvent(new Event('session-created'))
    }

  } catch {
    isTyping.value = false
    if (messages.value[messages.value.length - 1].content === '') {
      messages.value.pop()
    }
  }

  await scrollToBottom()
}

async function scrollToBottom() {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

const quickActions = [
  '这个系统的架构是什么？',
  '什么是 RAG 工作流？',
  'LangGraph 如何管理状态？',
]

function sendQuickAction(text) {
  messageInput.value = text
  handleSend()
}
</script>

<template>
  <div class="chat">
    <header class="chat__header animate-fade-in-up">
      <div>
        <h1 class="chat__title">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: var(--color-accent-blue);">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
          AI 智能对话
        </h1>
        <p class="text-muted text-sm">基于 LangGraph RAG 工作流的超能知识引擎</p>
      </div>
      <div class="chat__badges">
        <span class="badge badge--blue">GPT-4o</span>
        <span class="badge badge--cyan">RAG</span>
      </div>
    </header>

    <!-- 消息区域 -->
    <div class="chat__messages" ref="chatContainer">
      <ChatMessage
        v-for="(msg, i) in messages"
        :key="i"
        :role="msg.role"
        :content="msg.content"
        :sources="msg.sources"
        :is-typing="isTyping && i === messages.length - 1 && msg.role === 'assistant' && !msg.content"
      />

      <!-- 快捷操作（仅在只有欢迎消息时显示） -->
      <div v-if="messages.length <= 1 && !isTyping" class="quick-actions">
        <p class="text-xs text-muted" style="margin-bottom: var(--space-3); font-weight: 500;">快捷提问：</p>
        <div class="quick-actions__list">
          <button
            v-for="action in quickActions"
            :key="action"
            class="quick-action-btn"
            @click="sendQuickAction(action)"
          >
            {{ action }}
          </button>
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="chat__input-area animate-fade-in-up stagger-2">
      <div class="chat__input-wrap">
        <textarea
          v-model="messageInput"
          class="chat__textarea"
          placeholder="输入你的问题..."
          rows="1"
          @keydown.enter.exact.prevent="handleSend"
        ></textarea>
        <button
          class="btn btn--primary chat__send-btn"
          @click="handleSend"
          :disabled="!messageInput.trim() || loading"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="22" y1="2" x2="11" y2="13"/>
            <polygon points="22 2 15 22 11 13 2 9 22 2"/>
          </svg>
        </button>
      </div>
      <p class="chat__hint text-xs text-muted">Enter 发送 · 基于 LangGraph RAG 工作流处理</p>
    </div>
  </div>
</template>

<style scoped>
.chat {
  display: flex;
  flex-direction: column;
  height: calc(100vh - var(--space-10));
  max-width: 900px;
  width: 100%;
  margin: var(--space-5) auto 0;
}

.chat__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--space-6);
  flex-shrink: 0;
  padding: 0 var(--space-4);
}

.chat__title {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  font-size: var(--text-2xl);
  font-weight: 700;
  margin-bottom: var(--space-1);
}

.chat__badges {
  display: flex;
  gap: var(--space-2);
}

/* ── Messages ── */
.chat__messages {
  flex: 1;
  overflow-y: auto;
  padding: 0 var(--space-4) var(--space-8);
  display: flex;
  flex-direction: column;
  scrollbar-width: thin;
}

/* ── Quick Actions ── */
.quick-actions {
  margin-top: auto;
  padding-top: var(--space-6);
  padding-bottom: var(--space-4);
  animation: fadeIn 0.8s var(--ease-spring) both;
  animation-delay: 0.1s;
}

.quick-actions__list {
  display: flex;
  gap: var(--space-3);
  flex-wrap: wrap;
}

.quick-action-btn {
  font-size: var(--text-sm);
  padding: var(--space-2) var(--space-4);
  background: var(--color-bg-card-solid);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-full);
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all var(--transition-fast);
  font-family: var(--font-sans);
  font-weight: 500;
  box-shadow: var(--shadow-sm);
}

.quick-action-btn:hover {
  background: var(--color-bg-secondary);
  border-color: rgba(37, 99, 235, 0.3);
  color: var(--color-accent-blue);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

/* ── Input ── */
.chat__input-area {
  padding: var(--space-4);
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(24px) saturate(200%);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-2xl);
  box-shadow: var(--shadow-lg), 0 -10px 40px -10px rgba(0,0,0,0.03);
  flex-shrink: 0;
  margin-bottom: var(--space-6);
  transition: box-shadow var(--transition-base);
}
.chat__input-area:focus-within {
  box-shadow: var(--shadow-xl), 0 -10px 40px -10px rgba(0,0,0,0.04), 0 0 0 1px rgba(37, 99, 235, 0.1);
}

.chat__input-wrap {
  display: flex;
  align-items: flex-end;
  gap: var(--space-3);
}

.chat__textarea {
  flex: 1;
  resize: none;
  border: none;
  background: transparent;
  color: var(--color-text-title);
  font-family: var(--font-sans);
  font-size: 1.05rem;
  line-height: 1.5;
  padding: var(--space-2) 0;
  outline: none;
  max-height: 200px;
}

.chat__textarea::placeholder {
  color: var(--color-text-muted);
}

.chat__send-btn {
  padding: 10px;
  border-radius: var(--radius-lg);
  flex-shrink: 0;
  align-self: flex-end;
  margin-bottom: 2px;
}

.chat__send-btn:disabled {
  opacity: 0.5;
  background: var(--color-bg-secondary);
  color: var(--color-text-muted);
  box-shadow: none;
}

.chat__hint {
  margin-top: var(--space-3);
  text-align: center;
}
</style>
