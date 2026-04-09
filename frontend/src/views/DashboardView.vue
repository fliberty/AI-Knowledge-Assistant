<script setup>
import { ref, onMounted } from 'vue'
import { useApi } from '../composables/useApi.js'

const { healthCheck } = useApi()
const systemStatus = ref('checking')
const statusText = ref('正在检查...')

onMounted(async () => {
  try {
    await healthCheck()
    systemStatus.value = 'online'
    statusText.value = '运行中'
  } catch {
    systemStatus.value = 'offline'
    statusText.value = '未连接'
  }
})

const techStack = [
  { name: 'FastAPI', desc: 'Web 框架', color: 'cyan', version: '0.115+' },
  { name: 'LangChain', desc: 'LLM 编排', color: 'indigo', version: '0.3+' },
  { name: 'LangGraph', desc: '工作流引擎', color: 'indigo', version: '0.2+' },
  { name: 'OpenAI', desc: 'GPT-4o / Embedding', color: 'green', version: 'Latest' },
  { name: 'Qdrant', desc: '向量数据库', color: 'rose', version: '1.12+' },
  { name: 'Pydantic', desc: '数据校验', color: 'amber', version: 'v2' },
]

const apiEndpoints = [
  { method: 'GET', path: '/health', desc: '健康检查' },
  { method: 'POST', path: '/api/v1/knowledge/upload', desc: '上传知识文档' },
  { method: 'POST', path: '/api/v1/knowledge/search', desc: '语义搜索' },
  { method: 'POST', path: '/api/v1/chat', desc: '知识库问答' },
]

const architectureLayers = [
  { name: 'API Layer', desc: 'FastAPI 路由 + 依赖注入', icon: '⟶', modules: ['router.py', 'deps.py', 'endpoints/'] },
  { name: 'Agent Layer', desc: 'LangGraph RAG 工作流', icon: '⟶', modules: ['rag_agent.py', 'graph.py'] },
  { name: 'Service Layer', desc: 'Qdrant + LLM 封装', icon: '⟶', modules: ['vector_store.py', 'llm.py'] },
  { name: 'Data Processing', desc: '文档加载 & 分块', icon: '⟶', modules: ['loader.py', 'chunker.py'] },
  { name: 'Core', desc: '配置管理 + 结构化日志', icon: '◉', modules: ['config.py', 'logging.py'] },
]
</script>

<template>
  <div class="dashboard">
    <!-- 页面标题 -->
    <header class="dashboard__header animate-fade-in-up">
      <div>
        <h1 class="dashboard__title">
          <span class="gradient-text">AI Knowledge Assistant</span>
        </h1>
        <p class="dashboard__subtitle text-muted">
          企业级知识库智能助手 — 基于 LangGraph + RAG 架构
        </p>
      </div>
      <div class="dashboard__status-card glass-card" :class="`status--${systemStatus}`">
        <span class="status-dot" :class="`dot--${systemStatus}`"></span>
        <span class="font-mono text-sm">{{ statusText }}</span>
      </div>
    </header>

    <!-- 架构概览 -->
    <section class="animate-fade-in-up stagger-1">
      <h2 class="section-title">系统架构</h2>
      <div class="architecture">
        <div
          v-for="(layer, i) in architectureLayers"
          :key="layer.name"
          class="arch-layer glass-card"
        >
          <div class="arch-layer__header">
            <span class="arch-layer__name font-mono">{{ layer.name }}</span>
            <span class="arch-layer__arrow" v-if="i < architectureLayers.length - 1">↓</span>
          </div>
          <p class="arch-layer__desc text-muted text-sm">{{ layer.desc }}</p>
          <div class="arch-layer__modules">
            <code v-for="mod in layer.modules" :key="mod" class="arch-module">{{ mod }}</code>
          </div>
        </div>
      </div>
    </section>

    <!-- 技术栈 -->
    <section class="animate-fade-in-up stagger-2">
      <h2 class="section-title">技术栈</h2>
      <div class="tech-grid">
        <div v-for="tech in techStack" :key="tech.name" class="tech-card glass-card">
          <div class="tech-card__top">
            <span class="tech-card__name font-mono">{{ tech.name }}</span>
            <span :class="`badge badge--${tech.color}`">{{ tech.version }}</span>
          </div>
          <p class="tech-card__desc text-muted text-sm">{{ tech.desc }}</p>
        </div>
      </div>
    </section>

    <!-- API 端点 -->
    <section class="animate-fade-in-up stagger-3">
      <h2 class="section-title">API 端点</h2>
      <div class="api-table glass-card">
        <div class="api-row api-row--header">
          <span class="api-col api-col--method">方法</span>
          <span class="api-col api-col--path">路径</span>
          <span class="api-col api-col--desc">说明</span>
        </div>
        <div v-for="ep in apiEndpoints" :key="ep.path" class="api-row">
          <span class="api-col api-col--method">
            <span :class="['method-badge', `method--${ep.method.toLowerCase()}`]">{{ ep.method }}</span>
          </span>
          <code class="api-col api-col--path font-mono text-sm">{{ ep.path }}</code>
          <span class="api-col api-col--desc text-muted text-sm">{{ ep.desc }}</span>
        </div>
      </div>
    </section>

    <!-- RAG 工作流 -->
    <section class="animate-fade-in-up stagger-4">
      <h2 class="section-title">RAG 工作流</h2>
      <div class="workflow glass-card">
        <div class="workflow__nodes">
          <div class="workflow__node workflow__node--start">
            <span class="workflow__node-label font-mono">Query</span>
          </div>
          <span class="workflow__arrow">→</span>
          <div class="workflow__node workflow__node--process">
            <span class="workflow__node-label font-mono">Retrieve</span>
            <span class="text-xs text-muted">向量检索</span>
          </div>
          <span class="workflow__arrow">→</span>
          <div class="workflow__node workflow__node--process">
            <span class="workflow__node-label font-mono">Grade</span>
            <span class="text-xs text-muted">相关性评估</span>
          </div>
          <span class="workflow__arrow">→</span>
          <div class="workflow__node workflow__node--decision">
            <span class="workflow__node-label font-mono">Retry?</span>
            <span class="text-xs text-muted">条件判断</span>
          </div>
          <span class="workflow__arrow">→</span>
          <div class="workflow__node workflow__node--end">
            <span class="workflow__node-label font-mono">Generate</span>
            <span class="text-xs text-muted">生成回答</span>
          </div>
        </div>
        <div class="workflow__retry-line">
          <span class="text-xs font-mono text-muted">↻ 重试路径 (retry_count &lt; max_retries)</span>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.dashboard {
  max-width: 1400px;
  width: 100%;
  margin: var(--space-4) auto;
  padding: 0 var(--space-8);
}

.dashboard__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--space-10);
  background: transparent;
}

.dashboard__title {
  font-size: var(--text-4xl);
  font-weight: 700;
  font-family: var(--font-display);
  letter-spacing: -0.02em;
  line-height: 1.2;
  margin-bottom: var(--space-2);
}

.dashboard__subtitle {
  font-size: var(--text-base);
  font-weight: 500;
  color: var(--color-text-secondary);
}

.dashboard__status-card {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-5);
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.dot--online {
  background: var(--color-accent-green);
  animation: pulse-soft 2s ease-in-out infinite;
  box-shadow: 0 0 0 2px rgba(5, 150, 105, 0.2);
}

.dot--offline {
  background: var(--color-accent-rose);
  box-shadow: 0 0 0 2px rgba(225, 29, 72, 0.2);
}

.dot--checking {
  background: var(--color-accent-amber);
  animation: pulse-soft 1s ease-in-out infinite;
}

.status--online { border-color: rgba(5, 150, 105, 0.2); }
.status--offline { border-color: rgba(225, 29, 72, 0.2); }

/* ── Section ── */
.section-title {
  font-family: var(--font-display);
  font-size: var(--text-lg);
  font-weight: 600;
  margin-bottom: var(--space-4);
  color: var(--color-text-title);
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
}

section {
  margin-bottom: var(--space-10);
}

/* ── Architecture ── */
.architecture {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.arch-layer {
  padding: var(--space-5);
  background: var(--color-bg-card-solid);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
}

.arch-layer__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-2);
}

.arch-layer__name {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-accent-blue);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.arch-layer__arrow {
  color: var(--color-text-muted);
  font-size: var(--text-lg);
}

.arch-layer__modules {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
  margin-top: var(--space-4);
}

.arch-module {
  font-size: var(--text-xs);
  padding: var(--space-1) var(--space-3);
  background: rgba(37, 99, 235, 0.04);
  border: 1px solid rgba(37, 99, 235, 0.1);
  border-radius: var(--radius-full);
  color: var(--color-accent-blue);
  font-family: var(--font-mono);
  font-weight: 500;
}

/* ── Tech Grid ── */
.tech-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-4);
}

.tech-card {
  padding: var(--space-5);
  background: var(--color-bg-card-solid);
  border: 1px solid var(--color-border);
}

.tech-card__top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-2);
}

.tech-card__name {
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--color-text-title);
  font-family: var(--font-display);
}

/* ── API Table ── */
.api-table {
  padding: 0;
  overflow: hidden;
  background: var(--color-bg-card-solid);
  border: 1px solid var(--color-border);
}

.api-row {
  display: grid;
  grid-template-columns: 80px 1fr 1fr;
  gap: var(--space-4);
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid var(--color-border);
  align-items: center;
}

.api-row:last-child {
  border-bottom: none;
}

.api-row--header {
  background: #F8FAFC;
  font-size: var(--text-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-secondary);
}

.method-badge {
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
  padding: 4px 8px;
  border-radius: var(--radius-md);
  text-align: center;
}

.method--get {
  background: rgba(5, 150, 105, 0.1);
  color: #059669;
}

.method--post {
  background: rgba(37, 99, 235, 0.1);
  color: #2563EB;
}

/* ── Workflow ── */
.workflow {
  padding: var(--space-8);
  background: var(--color-bg-card-solid);
  border: 1px solid var(--color-border);
}

.workflow__nodes {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  justify-content: center;
  flex-wrap: wrap;
}

.workflow__node {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-3) var(--space-6);
  border-radius: var(--radius-xl);
  border: 1px solid var(--color-border);
  min-width: 120px;
  text-align: center;
  background: #FFFFFF;
  box-shadow: 0 1px 3px rgba(0,0,0,0.02);
  position: relative;
}

.workflow__node::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  opacity: 0.1;
  pointer-events: none;
}

.workflow__node--start::after { background: var(--color-accent-blue); }
.workflow__node--process::after { background: var(--color-accent-purple); }
.workflow__node--decision::after { background: var(--color-accent-amber); }
.workflow__node--end::after { background: var(--color-accent-green); }

.workflow__node-label {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text-title);
}

.workflow__arrow {
  color: var(--color-text-muted);
  font-size: var(--text-xl);
  font-family: var(--font-mono);
  opacity: 0.5;
}

.workflow__retry-line {
  text-align: center;
  margin-top: var(--space-6);
  padding-top: var(--space-4);
  border-top: 1px dashed rgba(15, 23, 42, 0.15);
}

/* ── 响应式 ── */
@media (max-width: 768px) {
  .tech-grid { grid-template-columns: 1fr; }
  .dashboard__header { flex-direction: column; gap: var(--space-4); }
  .api-row { grid-template-columns: 60px 1fr; }
  .api-col--desc { display: none; }
  .workflow__nodes { flex-direction: column; }
  .workflow__arrow { transform: rotate(90deg); }
}
</style>
