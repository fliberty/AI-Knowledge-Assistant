<script setup>
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

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
</script>

<template>
  <aside class="sidebar">
    <!-- Logo -->
    <div class="sidebar__logo">
      <div class="sidebar__logo-icon">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="url(#logoGrad)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <defs>
            <linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#6366F1" />
              <stop offset="100%" stop-color="#06B6D4" />
            </linearGradient>
          </defs>
          <path d="M12 2a4 4 0 0 0-4 4v2H6a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V10a2 2 0 0 0-2-2h-2V6a4 4 0 0 0-4-4z"/>
          <circle cx="12" cy="15" r="2"/>
        </svg>
      </div>
      <div class="sidebar__logo-text">
        <span class="sidebar__logo-title gradient-text">AI Knowledge</span>
        <span class="sidebar__logo-subtitle">Assistant v0.1</span>
      </div>
    </div>

    <!-- 导航 -->
    <nav class="sidebar__nav">
      <router-link
        v-for="item in navItems"
        :key="item.name"
        :to="item.path"
        class="sidebar__nav-item"
        :class="{ 'sidebar__nav-item--active': route.path === item.path }"
      >
        <span class="sidebar__nav-icon" v-html="item.icon"></span>
        <span class="sidebar__nav-label">{{ item.label }}</span>
        <span v-if="route.path === item.path" class="sidebar__nav-indicator"></span>
      </router-link>
    </nav>

    <!-- 底部状态 -->
    <div class="sidebar__footer">
      <div class="sidebar__status">
        <span class="sidebar__status-dot"></span>
        <span class="sidebar__status-text">系统就绪</span>
      </div>
      <div class="sidebar__version font-mono text-xs text-muted">
        LangGraph + RAG
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
  background: linear-gradient(180deg, rgba(17, 24, 39, 0.95), rgba(11, 15, 26, 0.98));
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  z-index: 100;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}

/* ── Logo ── */
.sidebar__logo {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-6);
  border-bottom: 1px solid var(--color-border);
}

.sidebar__logo-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(99, 102, 241, 0.1);
  border-radius: var(--radius-lg);
  border: 1px solid rgba(99, 102, 241, 0.2);
}

.sidebar__logo-text {
  display: flex;
  flex-direction: column;
}

.sidebar__logo-title {
  font-size: var(--text-sm);
  font-weight: 700;
  font-family: var(--font-mono);
  letter-spacing: 0.02em;
}

.sidebar__logo-subtitle {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  font-family: var(--font-mono);
}

/* ── Navigation ── */
.sidebar__nav {
  flex: 1;
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.sidebar__nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-lg);
  color: var(--color-text-secondary);
  text-decoration: none;
  transition: all var(--transition-fast);
  position: relative;
  cursor: pointer;
  font-size: var(--text-sm);
}

.sidebar__nav-item:hover {
  color: var(--color-text-primary);
  background: rgba(99, 102, 241, 0.06);
}

.sidebar__nav-item--active {
  color: var(--color-text-primary);
  background: rgba(99, 102, 241, 0.1);
}

.sidebar__nav-item--active .sidebar__nav-icon {
  color: var(--color-accent-primary);
}

.sidebar__nav-icon {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.sidebar__nav-indicator {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  background: var(--gradient-primary);
  border-radius: var(--radius-full);
}

/* ── Footer ── */
.sidebar__footer {
  padding: var(--space-4) var(--space-6);
  border-top: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.sidebar__status {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-xs);
  color: var(--color-accent-green);
}

.sidebar__status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-accent-green);
  animation: pulse-glow 2s ease-in-out infinite;
}
</style>
