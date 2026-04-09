<script setup>
const props = defineProps({
  role: { type: String, required: true },
  content: { type: String, required: true },
  sources: { type: Array, default: () => [] },
  isTyping: { type: Boolean, default: false },
})

const showSources = defineModel('showSources', { default: false })
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
        <p v-if="!isTyping">{{ content }}</p>
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
          {{ sources.length }} 个引用来源
          <span class="sources-arrow" :class="{ 'sources-arrow--open': showSources }">▸</span>
        </button>

        <transition name="slide">
          <div v-if="showSources" class="sources-panel">
            <div v-for="(src, i) in sources" :key="i" class="source-item">
              <span class="source-tag badge badge--indigo font-mono">{{ src.source }}</span>
              <p class="text-xs text-muted" style="margin-top: var(--space-1);">{{ src.content }}</p>
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
  gap: var(--space-3);
  padding: var(--space-4) 0;
  animation: fadeInUp 0.3s ease both;
}

.message__avatar {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 2px;
}

.message--user .message__avatar {
  background: rgba(100, 116, 139, 0.15);
  color: var(--color-text-secondary);
}

.message--assistant .message__avatar {
  background: rgba(99, 102, 241, 0.15);
  color: var(--color-accent-primary);
}

.message__body {
  flex: 1;
  min-width: 0;
}

.message__role {
  display: block;
  margin-bottom: var(--space-1);
}

.message__content {
  font-size: var(--text-sm);
  line-height: 1.75;
  color: var(--color-text-primary);
}

.message--user .message__content {
  color: var(--color-text-secondary);
}

/* ── Typing ── */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: var(--space-2) 0;
}

.typing-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-accent-primary);
  animation: typingBounce 1.2s ease-in-out infinite;
}

.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes typingBounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-6px); opacity: 1; }
}

/* ── Sources ── */
.message__sources {
  margin-top: var(--space-3);
}

.sources-toggle {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  background: rgba(99, 102, 241, 0.06);
  border: 1px solid rgba(99, 102, 241, 0.15);
  border-radius: var(--radius-md);
  color: #A5B4FC;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.sources-toggle:hover {
  background: rgba(99, 102, 241, 0.12);
}

.sources-arrow {
  transition: transform var(--transition-fast);
  display: inline-block;
}

.sources-arrow--open {
  transform: rotate(90deg);
}

.sources-panel {
  margin-top: var(--space-3);
  padding: var(--space-3);
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
}

.source-item {
  padding: var(--space-2) 0;
  border-bottom: 1px solid var(--color-border);
}

.source-item:last-child {
  border-bottom: none;
}

/* ── Slide transition ── */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.25s ease;
  overflow: hidden;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  max-height: 0;
}

.slide-enter-to,
.slide-leave-from {
  opacity: 1;
  max-height: 500px;
}
</style>
