<script setup>
import { computed } from 'vue'
import { marked } from 'marked'
import hljs from 'highlight.js'

// Configure marked with highlight.js
marked.setOptions({
  highlight: function (code, lang) {
    const language = hljs.getLanguage(lang) ? lang : 'plaintext'
    return hljs.highlight(code, { language }).value
  },
  breaks: true,
  gfm: true
})

const props = defineProps({
  role: { type: String, required: true },
  content: { type: String, required: true },
  sources: { type: Array, default: () => [] },
  isTyping: { type: Boolean, default: false },
})

const showSources = defineModel('showSources', { default: false })

const renderedContent = computed(() => {
  if (!props.content) return ''
  return marked.parse(props.content)
})
</script>

<template>
  <div class="message" :class="`message--${role}`">
    <div class="message__avatar">
      <!-- User avatar -->
      <svg v-if="role === 'user'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
        <circle cx="12" cy="7" r="4"/>
      </svg>
      <!-- AI avatar -->
      <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 2a4 4 0 0 0-4 4v2H6a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V10a2 2 0 0 0-2-2h-2V6a4 4 0 0 0-4-4z"/>
        <circle cx="12" cy="15" r="2"/>
      </svg>
    </div>

    <div class="message__body">
      <span class="message__role text-xs font-mono text-muted">
        {{ role === 'user' ? 'You' : 'AI Assistant' }}
      </span>

      <div class="message__content">
        <div v-if="!isTyping" class="markdown-body" v-html="renderedContent"></div>
        <p v-else class="typing-indicator">
          <span class="typing-dot"></span>
          <span class="typing-dot"></span>
          <span class="typing-dot"></span>
        </p>
      </div>

      <!-- 来源引用 -->
      <div v-if="sources.length && role === 'assistant'" class="message__sources">
        <button class="sources-toggle text-xs font-mono" @click="showSources = !showSources">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
          </svg>
          {{ sources.length }} 个引用来源，包含详细上下文
          <span class="sources-arrow" :class="{ 'sources-arrow--open': showSources }">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
          </span>
        </button>

        <transition name="slide">
          <div v-if="showSources" class="sources-panel">
            <div v-for="(src, i) in sources" :key="i" class="source-item">
              <span class="source-tag badge badge--blue font-mono">{{ src.source }}</span>
              <p class="text-xs text-secondary" style="margin-top: var(--space-2); line-height: 1.5;">{{ src.content }}</p>
            </div>
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<style scoped>
.message {
  display: flex;
  gap: var(--space-4);
  padding: var(--space-5) 0;
  animation: fadeInUp 0.4s var(--ease-spring) both;
  border-bottom: 1px solid rgba(0,0,0,0.02);
}

.message:last-child {
  border-bottom: none;
}

.message__avatar {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 2px;
  box-shadow: var(--shadow-sm);
  background: white;
}

.message--user .message__avatar {
  background: var(--color-bg-secondary);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
}

.message--assistant .message__avatar {
  background: var(--gradient-brand);
  color: #FFFFFF;
}

.message__body {
  flex: 1;
  min-width: 0;
}

.message__role {
  display: block;
  margin-bottom: var(--space-1);
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.message__content {
  font-size: 1rem;
  line-height: 1.75;
  color: var(--color-text-title);
}

.message--user .message__content {
  color: var(--color-text-primary);
  font-weight: 400;
}

/* ── Typing ── */
.typing-indicator {
  display: flex;
  gap: 5px;
  padding: var(--space-3) 0;
}

.typing-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--color-accent-blue);
  animation: typingBounce 1.4s ease-in-out infinite;
}

.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes typingBounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.3; }
  30% { transform: translateY(-4px); opacity: 1; }
}

/* ── Sources ── */
.message__sources {
  margin-top: var(--space-4);
}

.sources-toggle {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  background: rgba(37, 99, 235, 0.04);
  border: 1px solid rgba(37, 99, 235, 0.1);
  border-radius: var(--radius-md);
  color: var(--color-accent-blue);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.sources-toggle:hover {
  background: rgba(37, 99, 235, 0.08);
}

.sources-arrow {
  transition: transform var(--transition-fast);
  display: inline-flex;
  align-items: center;
}

.sources-arrow--open {
  transform: rotate(90deg);
}

.sources-panel {
  margin-top: var(--space-2);
  padding: var(--space-4);
  background: #FAFAFA;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.01);
}

.source-item {
  padding: var(--space-3) 0;
  border-bottom: 1px solid var(--color-border);
}
.source-item:first-child { padding-top: 0; }
.source-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

/* ── Slide transition ── */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s var(--ease-spring);
  overflow: hidden;
}
.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  max-height: 0;
  transform: translateY(-5px);
}
.slide-enter-to,
.slide-leave-from {
  opacity: 1;
  max-height: 800px;
  transform: translateY(0);
}
</style>
