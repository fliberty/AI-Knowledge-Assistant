<script setup>
import { ref, nextTick, onMounted, watch } from 'vue'
import ChatMessage from '../components/ChatMessage.vue'
import { useApi } from '../composables/useApi.js'

const { sendChat, loading } = useApi()

const messageInput = ref('')
const messages = ref([])
const chatContainer = ref(null)
const isTyping = ref(false)
const currentSessionId = ref(null)

// 欢迎消息与读取缓存的聊天记录
onMounted(() => {
  const savedMessages = localStorage.getItem('chat_messages')
  const savedSessionId = localStorage.getItem('chat_session_id')
  
  if (savedSessionId) {
    currentSessionId.value = savedSessionId
  }

  if (savedMessages) {
    try {
      messages.value = JSON.parse(savedMessages)
    } catch {
      messages.value = []
    }
  }

  if (messages.value.length === 0) {
    messages.value.push({
      role: 'assistant',
      content: '你好！我是 AI 知识库助手。你可以向我提问任何已上传到知识库中的内容，我会基于 RAG 检索增强架构为你提供精准回答。',
      sources: [],
    })
  } else {
    scrollToBottom()
  }
})

// 自动向本地存储保存记录
watch(messages, (newVal) => {
  localStorage.setItem('chat_messages', JSON.stringify(newVal))
}, { deep: true })

watch(currentSessionId, (newVal) => {
  if (newVal) {
    localStorage.setItem('chat_session_id', newVal)
  }
})

async function handleSend() {
  const text = messageInput.value.trim()
  if (!text || loading.value) return

  // 添加用户消息
  messages.value.push({ role: 'user', content: text, sources: [] })
  messageInput.value = ''
  await scrollToBottom()

  // 显示打字指示
  isTyping.value = true
  await scrollToBottom()

  try {
    const res = await sendChat(text, currentSessionId.value)
    isTyping.value = false

    if (res.data?.session_id && !currentSessionId.value) {
      currentSessionId.value = res.data.session_id
    }

    messages.value.push({
      role: 'assistant',
      content: res.data?.answer || '抱歉，暂时无法回答。',
      sources: res.data?.sources || [],
    })
  } catch {
    isTyping.value = false

    // Demo 模式：模拟回复
    await simulateTyping()
    messages.value.push({
      role: 'assistant',
      content: generateDemoResponse(text),
      sources: [
        { source: 'architecture.md', content: 'RAG (Retrieval-Augmented Generation) 架构通过检索相关文档来增强 LLM 的回答质量...' },
        { source: 'langgraph-guide.pdf', content: 'LangGraph 使用 StateGraph 定义工作流，节点函数处理状态转换...' },
      ],
    })
  }

  await scrollToBottom()
}

function generateDemoResponse(query) {
  const responses = {
    default: `关于「${query}」，基于知识库中的文档检索，我找到了以下信息：\n\n本系统采用 RAG（Retrieval-Augmented Generation）架构，通过 LangGraph 编排工作流：首先从 Qdrant 向量数据库中检索与查询最相关的文档片段，然后评估其相关性，最后基于筛选后的上下文生成精准回答。\n\n这种架构确保了回答的准确性和可追溯性，每个回答都附有信息来源引用。`,
  }
  return responses.default
}

async function simulateTyping() {
  return new Promise(resolve => setTimeout(resolve, 1200))
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
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: var(--color-accent-primary);">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
          AI 对话
        </h1>
        <p class="text-muted text-sm">基于知识库的智能问答 · LangGraph RAG 工作流</p>
      </div>
      <div class="chat__badges">
        <span class="badge badge--indigo">GPT-4o</span>
        <span class="badge badge--cyan">RAG</span>
      </div>
    </header>

    <!-- 消息区域 -->
    <div class="chat__messages glass-card" ref="chatContainer">
      <ChatMessage
        v-for="(msg, i) in messages"
        :key="i"
        :role="msg.role"
        :content="msg.content"
        :sources="msg.sources"
      />

      <ChatMessage
        v-if="isTyping"
        role="assistant"
        content=""
        :is-typing="true"
      />

      <!-- 快捷操作（仅在只有欢迎消息时显示） -->
      <div v-if="messages.length <= 1 && !isTyping" class="quick-actions">
        <p class="text-xs text-muted" style="margin-bottom: var(--space-2);">试试这些问题：</p>
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
    <div class="chat__input-area glass-card animate-fade-in-up stagger-2">
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
  height: calc(100vh - var(--space-16));
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
}

.chat__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--space-4);
  flex-shrink: 0;
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
  padding: var(--space-4) var(--space-6);
  margin-bottom: var(--space-4);
  display: flex;
  flex-direction: column;
}

.chat__messages:hover {
  transform: none;
  box-shadow: none;
}

/* ── Quick Actions ── */
.quick-actions {
  margin-top: auto;
  padding-top: var(--space-4);
}

.quick-actions__list {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.quick-action-btn {
  font-size: var(--text-xs);
  padding: var(--space-2) var(--space-4);
  background: rgba(99, 102, 241, 0.06);
  border: 1px solid rgba(99, 102, 241, 0.15);
  border-radius: var(--radius-full);
  color: #A5B4FC;
  cursor: pointer;
  transition: all var(--transition-fast);
  font-family: var(--font-sans);
}

.quick-action-btn:hover {
  background: rgba(99, 102, 241, 0.12);
  border-color: rgba(99, 102, 241, 0.3);
  transform: translateY(-1px);
}

/* ── Input ── */
.chat__input-area {
  padding: var(--space-4);
  flex-shrink: 0;
}

.chat__input-area:hover {
  transform: none;
  box-shadow: none;
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
  color: var(--color-text-primary);
  font-family: var(--font-sans);
  font-size: var(--text-sm);
  line-height: 1.5;
  padding: var(--space-2) 0;
  outline: none;
  max-height: 120px;
}

.chat__textarea::placeholder {
  color: var(--color-text-muted);
}

.chat__send-btn {
  padding: var(--space-2) var(--space-3);
  flex-shrink: 0;
}

.chat__send-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  box-shadow: none;
}

.chat__hint {
  margin-top: var(--space-2);
}
</style>
