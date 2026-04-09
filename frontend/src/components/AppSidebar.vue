<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useApi } from '../composables/useApi.js'

const router = useRouter()
const route = useRoute()
const { getSessions, deleteSession } = useApi()

const navItems = [
  {
    name: 'Dashboard',
    path: '/',
    label: '系统概览',
    icon: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>`,
  },
  {
    name: 'Knowledge',
    path: '/knowledge',
    label: '知识库管理',
    icon: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/><path d="M3 12c0 1.66 4 3 9 3s9-1.34 9-3"/></svg>`,
  },
  {
    name: 'Chat',
    path: '/chat',
    label: 'AI 对话',
    icon: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>`,
  },
]

const sessions = ref([])

async function loadSessions() {
  try {
    const res = await getSessions()
    if (res && res.data) {
      sessions.value = res.data
    }
  } catch(e) {
    console.error("加载会话列表失败:", e)
  }
}

async function handleDelete(id) {
  try {
    await deleteSession(id)
    if (route.params.id === id) {
      router.push('/chat')
    }
    await loadSessions()
  } catch (e) {
    console.error('删除会话失败', e)
  }
}

function handleNewChat() {
  router.push('/chat')
}

onMounted(() => {
  loadSessions()
  window.addEventListener('session-created', loadSessions)
})

onUnmounted(() => {
  window.removeEventListener('session-created', loadSessions)
})
</script>

<template>
  <aside class="sidebar">
    <!-- Logo -->
    <div class="sidebar__logo">
      <div class="sidebar__logo-icon">
        <svg width="26" height="26" viewBox="0 0 24 24" fill="none" class="brand-iso" stroke="url(#logoGradLight)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <defs>
            <linearGradient id="logoGradLight" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#7C3AED" />
              <stop offset="100%" stop-color="#2563EB" />
            </linearGradient>
          </defs>
          <path d="M12 2a4 4 0 0 0-4 4v2H6a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V10a2 2 0 0 0-2-2h-2V6a4 4 0 0 0-4-4z"/>
          <circle cx="12" cy="15" r="2" fill="currentColor" stroke="none" />
        </svg>
      </div>
      <div class="sidebar__logo-text">
        <span class="sidebar__logo-title gradient-text">AI Knowledge</span>
        <span class="sidebar__logo-subtitle">Assistant Pro</span>
      </div>
    </div>

    <!-- 导航 -->
    <nav class="sidebar__nav">
      <router-link
        v-for="item in navItems"
        :key="item.name"
        :to="item.path"
        class="sidebar__nav-item"
        :class="{ 'sidebar__nav-item--active': route.path === item.path || (item.name === 'Chat' && route.name === 'Chat') }"
      >
        <span class="sidebar__nav-icon" v-html="item.icon"></span>
        <span class="sidebar__nav-label">{{ item.label }}</span>
        
        <span class="sidebar__nav-bg"></span>
      </router-link>
    </nav>

    <!-- 会话历史记录 -->
    <div class="sidebar__history">
      <div class="sidebar__history-header">
        <span class="history-label">最近会话</span>
        <button class="new-chat-btn" @click="handleNewChat" aria-label="新建对话" title="新建对话">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
        </button>
      </div>
      <div class="sidebar__history-list">
        <div 
          v-for="session in sessions" 
          :key="session.id"
          class="history-item"
          :class="{'history-item--active': route.params.id === session.id}"
          @click="router.push(`/chat/${session.id}`)"
        >
          <span class="history-item-title">{{ session.title }}</span>
          <button class="delete-btn" @click.stop="handleDelete(session.id)" aria-label="删除" title="删除该会话">
             <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
          </button>
        </div>
      </div>
    </div>

    <!-- 底部状态 -->
    <div class="sidebar__footer">
      <div class="sidebar__user-badge">
        <div class="avatar">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
        </div>
        <div class="info">
          <span class="name">Administrator</span>
          <span class="status">
            <span class="status-dot"></span>
            Online System
          </span>
        </div>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  width: var(--sidebar-width);
  height: 100vh;
  background: rgba(255, 255, 255, 0.7);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  z-index: 100;
  backdrop-filter: blur(24px) saturate(200%);
  -webkit-backdrop-filter: blur(24px) saturate(200%);
  box-shadow: 1px 0 10px rgba(0, 0, 0, 0.01);
}

/* ── Logo ── */
.sidebar__logo {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-6) var(--space-5);
  border-bottom: 1px solid rgba(0, 0, 0, 0.03);
}

.sidebar__logo-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #FFFFFF;
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
  color: #7C3AED;
}
.brand-iso {
  transition: transform 0.6s var(--ease-spring);
}
.sidebar__logo:hover .brand-iso {
  transform: rotate(10deg) scale(1.05);
}

.sidebar__logo-text {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.sidebar__logo-title {
  font-size: var(--text-base);
  line-height: 1.1;
  font-family: var(--font-display);
  letter-spacing: -0.01em;
}

.sidebar__logo-subtitle {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  font-weight: 500;
  letter-spacing: 0.02em;
}

/* ── Navigation ── */
.sidebar__nav {
  padding: var(--space-5) var(--space-3) var(--space-2);
  display: flex;
  flex-direction: column;
  gap: 6px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.03);
}

.sidebar__nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: 10px var(--space-4);
  border-radius: var(--radius-lg);
  color: var(--color-text-secondary);
  text-decoration: none;
  position: relative;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 500;
  border: 1px solid transparent;
  transition: all var(--transition-fast);
  z-index: 1;
}

.sidebar__nav-icon {
  display: flex;
  align-items: center;
  flex-shrink: 0;
  transition: color var(--transition-fast);
}

.sidebar__nav-bg {
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: var(--color-bg-secondary);
  opacity: 0;
  z-index: -1;
  transform: scale(0.95);
  transition: all var(--transition-fast);
}

.sidebar__nav-item:hover {
  color: var(--color-text-primary);
}

.sidebar__nav-item:hover .sidebar__nav-bg {
  opacity: 1;
  transform: scale(1);
}

.sidebar__nav-item--active {
  color: var(--color-accent-blue);
  background: #FFFFFF;
  border: 1px solid rgba(37, 99, 235, 0.1);
  box-shadow: var(--shadow-sm), inset 0 2px 4px rgba(0,0,0,0.01);
}
.sidebar__nav-item--active .sidebar__nav-icon {
  color: var(--color-accent-blue);
}
.sidebar__nav-item--active:hover .sidebar__nav-bg {
  opacity: 0; 
}


/* ── History List ── */
.sidebar__history {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: var(--space-3) 0;
}

.sidebar__history-header {
  padding: 0 var(--space-5) var(--space-2);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.history-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-muted);
  letter-spacing: 0.05em;
}

.new-chat-btn {
  background: transparent;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  padding: 4px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}
.new-chat-btn:hover {
  background: var(--color-bg-secondary);
  color: var(--color-text-primary);
}

.sidebar__history-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 var(--space-3);
  scrollbar-width: none;
}
.sidebar__history-list::-webkit-scrollbar {
  display: none;
}

.history-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px var(--space-3);
  margin-bottom: 2px;
  border-radius: var(--radius-md);
  cursor: pointer;
  color: var(--color-text-secondary);
  font-size: 0.85rem;
  transition: all var(--transition-fast);
}

.history-item:hover {
  background: rgba(0,0,0,0.02);
  color: var(--color-text-primary);
}

.history-item-title {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}

.delete-btn {
  background: transparent;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  padding: 4px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: all var(--transition-fast);
}
.history-item:hover .delete-btn {
  opacity: 1;
}
.delete-btn:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #EF4444;
}

.history-item--active,
.history-item--active:hover {
  background: var(--color-bg-secondary);
  color: var(--color-text-primary);
  font-weight: 500;
}


/* ── Footer ── */
.sidebar__footer {
  padding: var(--space-4);
  background: rgba(255, 255, 255, 0.4);
  border-top: 1px solid rgba(0, 0, 0, 0.03);
}

.sidebar__user-badge {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: background var(--transition-fast);
}
.sidebar__user-badge:hover {
  background: var(--color-bg-secondary);
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--gradient-brand);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: inset 0 2px 4px rgba(255, 255, 255, 0.2);
}

.info {
  display: flex;
  flex-direction: column;
}

.info .name {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.info .status {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-accent-green);
  box-shadow: 0 0 0 2px rgba(5, 150, 105, 0.2);
}
</style>
