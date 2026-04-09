<script setup>
import AppSidebar from './components/AppSidebar.vue'
</script>

<template>
  <div class="app-layout">
    <!-- 极轻的高级科技感散景光效 -->
    <div class="bg-glow bg-glow--hero blob-anim"></div>
    <div class="bg-glow bg-glow--accent blob-anim-reverse"></div>

    <AppSidebar />

    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="page" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<style>
.app-layout {
  display: flex;
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  background-color: var(--color-bg-mesh);
}

.main-content {
  flex: 1;
  margin-left: var(--sidebar-width);
  /* 使用更大的侧边距，更高级的空间留白 */
  padding: 0 var(--space-12);
  position: relative;
  overflow-y: auto;
  max-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* ── Apple-like 极柔光环散景 ── */
.bg-glow {
  position: fixed;
  border-radius: 50%;
  pointer-events: none;
  z-index: 0;
  filter: blur(140px);
  opacity: 0.8;
}

.bg-glow--hero {
  width: 800px;
  height: 800px;
  top: -300px;
  right: -200px;
  background: radial-gradient(circle, rgba(124, 58, 237, 0.08) 0%, rgba(37, 99, 235, 0.03) 100%);
}

.bg-glow--accent {
  width: 700px;
  height: 700px;
  bottom: -200px;
  left: 10vw;
  background: radial-gradient(circle, rgba(6, 182, 212, 0.06) 0%, rgba(5, 150, 105, 0.03) 100%);
}

@keyframes blob-drift {
  0%   { transform: translate(0px, 0px) scale(1); }
  33%  { transform: translate(30px, -50px) scale(1.1); }
  66%  { transform: translate(-20px, 20px) scale(0.9); }
  100% { transform: translate(0px, 0px) scale(1); }
}
@keyframes blob-drift-reverse {
  0%   { transform: translate(0px, 0px) scale(1); }
  33%  { transform: translate(-30px, 50px) scale(0.95); }
  66%  { transform: translate(20px, -20px) scale(1.05); }
  100% { transform: translate(0px, 0px) scale(1); }
}

.blob-anim {
  animation: blob-drift 25s ease-in-out infinite;
}
.blob-anim-reverse {
  animation: blob-drift-reverse 20s ease-in-out infinite;
}

/* 页面切换高级流畅动画 */
.page-enter-active {
  animation: fadeInUp 0.4s var(--ease-spring) both;
}

.page-leave-active {
  animation: fadeInScale 0.25s var(--ease-smooth) reverse both;
}
</style>
