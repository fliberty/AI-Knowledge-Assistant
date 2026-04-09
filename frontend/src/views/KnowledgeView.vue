<script setup>
import { ref, watch, onMounted } from 'vue'
import FileUpload from '../components/FileUpload.vue'
import { useApi } from '../composables/useApi.js'

const { searchKnowledge, loading, error } = useApi()

const searchQuery = ref('')
const searchResults = ref([])
const hasSearched = ref(false)
const uploadedFiles = ref([])

onMounted(() => {
  const saved = localStorage.getItem('knowledge_uploaded_files')
  if (saved) {
    try {
      uploadedFiles.value = JSON.parse(saved)
    } catch {
      // ignore
    }
  }
})

watch(uploadedFiles, (newVal) => {
  localStorage.setItem('knowledge_uploaded_files', JSON.stringify(newVal))
}, { deep: true })

async function handleSearch() {
  if (!searchQuery.value.trim()) return
  hasSearched.value = true
  try {
    const res = await searchKnowledge(searchQuery.value)
    searchResults.value = res.data?.results || []
  } catch {
    searchResults.value = []
  }
}

function handleUploadSuccess(result) {
  uploadedFiles.value.unshift({
    filename: result.filename,
    chunks: result.chunk_count,
    status: result.status,
    time: new Date().toLocaleTimeString(),
  })
}
</script>

<template>
  <div class="knowledge">
    <header class="knowledge__header animate-fade-in-up">
      <h1 class="knowledge__title">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: var(--color-accent-secondary);">
          <ellipse cx="12" cy="5" rx="9" ry="3"/>
          <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>
          <path d="M3 12c0 1.66 4 3 9 3s9-1.34 9-3"/>
        </svg>
        知识库管理
      </h1>
      <p class="text-muted">上传文档到向量数据库，或执行语义搜索</p>
    </header>

    <div class="knowledge__grid">
      <!-- 上传区域 -->
      <section class="animate-fade-in-up stagger-1">
        <h2 class="section-title">文档上传</h2>
        <FileUpload @upload-success="handleUploadSuccess" />

        <!-- 已上传文件列表 -->
        <div v-if="uploadedFiles.length" class="uploaded-list">
          <h3 class="text-sm" style="margin-bottom: var(--space-3); color: var(--color-text-secondary);">
            已处理文档
          </h3>
          <div v-for="(file, i) in uploadedFiles" :key="i" class="uploaded-item glass-card">
            <div class="uploaded-item__info">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: var(--color-accent-green);">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
              </svg>
              <span class="font-mono text-sm">{{ file.filename }}</span>
            </div>
            <div class="uploaded-item__meta">
              <span class="badge badge--green">{{ file.chunks }} 个分块</span>
              <span class="text-xs text-muted">{{ file.time }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 搜索区域 -->
      <section class="animate-fade-in-up stagger-2">
        <h2 class="section-title">语义搜索</h2>
        <div class="search-box glass-card">
          <div class="search-input-wrap">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="search-icon">
              <circle cx="11" cy="11" r="8"/>
              <path d="m21 21-4.3-4.3"/>
            </svg>
            <input
              v-model="searchQuery"
              type="text"
              class="input search-input"
              placeholder="输入查询内容，基于语义进行搜索..."
              @keyup.enter="handleSearch"
            />
            <button class="btn btn--primary" @click="handleSearch" :disabled="loading">
              {{ loading ? '搜索中...' : '搜索' }}
            </button>
          </div>
        </div>

        <!-- 搜索结果 -->
        <div v-if="hasSearched" class="search-results">
          <p v-if="error" class="search-error text-sm">
            <span style="color: var(--color-accent-rose);">搜索出错：{{ error }}</span>
          </p>

          <p v-else-if="searchResults.length === 0" class="search-empty text-muted text-sm">
            未找到相关结果。请尝试不同的查询语句。
          </p>

          <div v-else class="results-list">
            <p class="text-sm text-muted" style="margin-bottom: var(--space-3);">
              找到 {{ searchResults.length }} 条结果
            </p>
            <div v-for="(result, i) in searchResults" :key="i" class="result-card glass-card">
              <div class="result-card__header">
                <span class="badge badge--cyan font-mono">{{ (result.score * 100).toFixed(1) }}%</span>
                <span class="text-xs text-muted font-mono">{{ result.source }}</span>
              </div>
              <p class="result-card__content text-sm">{{ result.content }}</p>
            </div>
          </div>
        </div>

        <!-- 搜索提示（未搜索时） -->
        <div v-else class="search-hint glass-card">
          <div class="search-hint__icon">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="color: var(--color-text-muted);">
              <circle cx="11" cy="11" r="8"/>
              <path d="m21 21-4.3-4.3"/>
            </svg>
          </div>
          <p class="text-muted text-sm">输入查询语句，系统将基于向量相似度进行语义检索</p>
          <div class="search-hint__examples">
            <span class="hint-tag" @click="searchQuery = '如何使用 LangGraph 构建工作流？'">如何使用 LangGraph？</span>
            <span class="hint-tag" @click="searchQuery = '什么是 RAG 架构的优势？'">RAG 架构优势</span>
            <span class="hint-tag" @click="searchQuery = 'Qdrant 向量数据库的特点'">Qdrant 特点</span>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.knowledge {
  max-width: 1400px;
  width: 100%;
  margin: var(--space-4) auto;
  padding: 0 var(--space-8);
}

.knowledge__header {
  margin-bottom: var(--space-8);
}

.knowledge__title {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  font-size: var(--text-3xl);
  font-weight: 700;
  font-family: var(--font-display);
  letter-spacing: -0.02em;
  margin-bottom: var(--space-3);
}

.knowledge__grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-10);
}

.section-title {
  font-size: var(--text-lg);
  font-weight: 600;
  font-family: var(--font-display);
  margin-bottom: var(--space-4);
  color: var(--color-text-title);
}

/* ── Upload List ── */
.uploaded-list {
  margin-top: var(--space-8);
  background: var(--color-bg-card-solid);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  padding: var(--space-5);
  box-shadow: var(--shadow-sm);
}

.uploaded-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3) 0;
  border-bottom: 1px solid var(--color-border);
}

.uploaded-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.uploaded-item__info {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  color: var(--color-text-primary);
}

.uploaded-item__meta {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

/* ── Search ── */
.search-box {
  padding: var(--space-4);
  background: var(--color-bg-card-solid);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-2xl);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-base);
}

.search-box:focus-within {
  box-shadow: var(--shadow-md), 0 0 0 1px rgba(37, 99, 235, 0.1);
  transform: translateY(-2px);
}

.search-input-wrap {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  position: relative;
}

.search-icon {
  color: var(--color-text-muted);
  flex-shrink: 0;
  margin-left: 4px;
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  padding: var(--space-2) 0;
  font-size: 1.05rem;
  color: var(--color-text-title);
}

.search-input:focus {
  box-shadow: none;
}

.search-results {
  margin-top: var(--space-6);
}

.search-empty,
.search-error {
  padding: var(--space-10) var(--space-4);
  text-align: center;
  background: var(--color-bg-card-solid);
  border-radius: var(--radius-xl);
  border: 1px dashed var(--color-border);
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.result-card {
  padding: var(--space-5);
  background: var(--color-bg-card-solid);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
}

.result-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-3);
}

.result-card__content {
  color: var(--color-text-secondary);
  line-height: 1.7;
}

/* ── Search Hint ── */
.search-hint {
  margin-top: var(--space-6);
  text-align: center;
  padding: var(--space-10) var(--space-8);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-6);
  background: var(--color-bg-card-solid);
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-2xl);
}

.search-hint__examples {
  display: flex;
  gap: var(--space-3);
  flex-wrap: wrap;
  justify-content: center;
}

.hint-tag {
  font-size: var(--text-xs);
  font-weight: 500;
  padding: var(--space-2) var(--space-4);
  background: rgba(37, 99, 235, 0.05);
  border: 1px solid rgba(37, 99, 235, 0.1);
  border-radius: var(--radius-full);
  color: var(--color-accent-blue);
  cursor: pointer;
  transition: all var(--transition-fast);
  font-family: var(--font-sans);
}

.hint-tag:hover {
  background: rgba(37, 99, 235, 0.1);
  border-color: rgba(37, 99, 235, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.1);
}

@media (max-width: 900px) {
  .knowledge__grid {
    grid-template-columns: 1fr;
  }
}
</style>
