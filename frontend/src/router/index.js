import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/DashboardView.vue'),
    meta: { title: '系统概览', icon: 'dashboard' },
  },
  {
    path: '/knowledge',
    name: 'Knowledge',
    component: () => import('../views/KnowledgeView.vue'),
    meta: { title: '知识库管理', icon: 'database' },
  },
  {
    path: '/chat/:id?',
    name: 'Chat',
    component: () => import('../views/ChatView.vue'),
    meta: { title: 'AI 对话', icon: 'message' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  document.title = `${to.meta.title || 'AI Knowledge Assistant'} — AI Knowledge Assistant`
})

export default router
