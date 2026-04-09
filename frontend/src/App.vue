<script setup>
import AppSidebar from './components/AppSidebar.vue'
</script>

<template>
  <div class="app-layout">
    <!-- 背景光晕 -->
    <div class="bg-glow bg-glow--top"></div>
    <div class="bg-glow bg-glow--bottom"></div>

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
}

.main-content {
  flex: 1;
  margin-left: var(--sidebar-width);
  padding: var(--space-8) var(--space-10);
  position: relative;
  overflow-y: auto;
  max-height: 100vh;
}

/* 背景光晕 */
.bg-glow {
  position: fixed;
  border-radius: 50%;
  pointer-events: none;
  z-index: 0;
  filter: blur(100px);
}

.bg-glow--top {
  width: 600px;
  height: 600px;
  top: -200px;
  right: -100px;
  background: rgba(99, 102, 241, 0.08);
}

.bg-glow--bottom {
  width: 500px;
  height: 500px;
  bottom: -150px;
  left: 200px;
  background: rgba(6, 182, 212, 0.06);
}

/* 页面切换动画 */
.page-enter-active {
  animation: fadeInUp 0.35s ease both;
}

.page-leave-active {
  animation: fadeIn 0.2s ease reverse both;
}
</style>
