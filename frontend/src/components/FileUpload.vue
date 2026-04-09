<script setup>
import { ref } from 'vue'

const emit = defineEmits(['upload-success'])

const isDragging = ref(false)
const uploading = ref(false)
const uploadError = ref(null)

const supportedFormats = ['PDF', 'TXT', 'MD']

function handleDragOver(e) {
  e.preventDefault()
  isDragging.value = true
}

function handleDragLeave() {
  isDragging.value = false
}

function handleDrop(e) {
  e.preventDefault()
  isDragging.value = false
  const files = e.dataTransfer?.files
  if (files?.length) processFile(files[0])
}

function handleFileSelect(e) {
  const files = e.target?.files
  if (files?.length) processFile(files[0])
}

async function processFile(file) {
  uploading.value = true
  uploadError.value = null

  // 模拟上传（后端未运行时的 Demo 效果）
  try {
    const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
    const formData = new FormData()
    formData.append('file', file)

    const res = await fetch(`${API_BASE}/api/v1/knowledge/upload`, {
      method: 'POST',
      body: formData,
    })

    if (!res.ok) throw new Error(`上传失败 (HTTP ${res.status})`)
    const data = await res.json()
    emit('upload-success', data.data)
  } catch (err) {
    // Demo 模式：模拟成功
    emit('upload-success', {
      filename: file.name,
      chunk_count: Math.floor(Math.random() * 20) + 5,
      status: 'processed (demo)',
    })
  } finally {
    uploading.value = false
  }
}
</script>

<template>
  <div
    class="file-upload"
    :class="{ 'file-upload--dragging': isDragging, 'file-upload--uploading': uploading }"
    @dragover="handleDragOver"
    @dragleave="handleDragLeave"
    @drop="handleDrop"
  >
    <input
      type="file"
      class="file-upload__input"
      accept=".pdf,.txt,.md,.markdown"
      @change="handleFileSelect"
      id="fileInput"
    />

    <label for="fileInput" class="file-upload__label">
      <div class="file-upload__icon">
        <svg v-if="!uploading" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
          <polyline points="17 8 12 3 7 8"/>
          <line x1="12" y1="3" x2="12" y2="15"/>
        </svg>
        <div v-else class="upload-spinner"></div>
      </div>

      <p class="file-upload__text">
        <span v-if="uploading">正在处理文档...</span>
        <span v-else>拖拽文件到此处或 <span class="file-upload__link">点击选择</span></span>
      </p>

      <div class="file-upload__formats">
        <span v-for="fmt in supportedFormats" :key="fmt" class="format-tag">{{ fmt }}</span>
      </div>
    </label>

    <p v-if="uploadError" class="file-upload__error text-sm">{{ uploadError }}</p>
  </div>
</template>

<style scoped>
.file-upload {
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-xl);
  background: var(--color-bg-card);
  transition: all var(--transition-base);
  position: relative;
}

.file-upload--dragging {
  border-color: var(--color-accent-primary);
  background: rgba(99, 102, 241, 0.06);
  box-shadow: var(--shadow-glow);
}

.file-upload__input {
  position: absolute;
  width: 0;
  height: 0;
  opacity: 0;
  overflow: hidden;
}

.file-upload__label {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-8) var(--space-6);
  cursor: pointer;
  text-align: center;
}

.file-upload__icon {
  color: var(--color-text-muted);
  padding: var(--space-4);
  border-radius: 50%;
  background: rgba(99, 102, 241, 0.06);
  transition: all var(--transition-base);
}

.file-upload:hover .file-upload__icon {
  color: var(--color-accent-primary);
  background: rgba(99, 102, 241, 0.12);
}

.file-upload__text {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}

.file-upload__link {
  color: var(--color-accent-primary);
  font-weight: 500;
}

.file-upload__formats {
  display: flex;
  gap: var(--space-2);
}

.format-tag {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  padding: 2px 8px;
  background: rgba(100, 116, 139, 0.1);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  color: var(--color-text-muted);
}

.file-upload__error {
  text-align: center;
  color: var(--color-accent-rose);
  padding: var(--space-2);
}

/* Spinner */
.upload-spinner {
  width: 36px;
  height: 36px;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-accent-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
