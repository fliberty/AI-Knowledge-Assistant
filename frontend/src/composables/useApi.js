import { ref } from 'vue'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

/**
 * API 调用封装 composable
 */
export function useApi() {
  const loading = ref(false)
  const error = ref(null)

  async function request(endpoint, options = {}) {
    loading.value = true
    error.value = null

    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      return await response.json()
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function healthCheck() {
    return request('/health')
  }

  async function uploadDocument(file) {
    loading.value = true
    error.value = null

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch(`${API_BASE}/api/v1/knowledge/upload`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      return await response.json()
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function searchKnowledge(query, topK = 5) {
    return request('/api/v1/knowledge/search', {
      method: 'POST',
      body: JSON.stringify({ query, top_k: topK }),
    })
  }

  async function sendChat(message, sessionId = null) {
    const body = {
      message,
      use_knowledge_base: true,
    }
    if (sessionId) {
      body.session_id = sessionId
    }

    return request('/api/v1/chat', {
      method: 'POST',
      body: JSON.stringify(body),
    })
  }

  return {
    loading,
    error,
    healthCheck,
    uploadDocument,
    searchKnowledge,
    sendChat,
  }
}
