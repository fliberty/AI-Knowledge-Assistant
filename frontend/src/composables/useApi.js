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

  async function sendChat(message, history = [], sessionId = null) {
    const body = {
      message,
      history,
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

  async function sendChatStream(message, history = [], sessionId = null, onChunk = null, onSources = null) {
    const body = { message, history, use_knowledge_base: true }
    if (sessionId) body.session_id = sessionId

    loading.value = true
    error.value = null

    try {
      const response = await fetch(`${API_BASE}/api/v1/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      })

      if (!response.ok) throw new Error(`HTTP ${response.status}`)

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let finalSessionId = null
      let buffer = ''
      let currentEvent = null

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        
        // Keep the last partial line in the buffer
        buffer = lines.pop()
        
        for (const line of lines) {
          if (line.startsWith('event: ')) {
            currentEvent = line.substring(7).trim()
          } else if (line.startsWith('data: ')) {
            const dataStr = line.substring(6).trim()
            if (!dataStr || dataStr === '{}') continue
            
            try {
              const data = JSON.parse(dataStr)
              if (currentEvent === 'start' && data.session_id) {
                finalSessionId = data.session_id
              } else if (currentEvent === 'sources' && data.sources && onSources) {
                onSources(data.sources)
              } else if (currentEvent === 'message' && data.chunk && onChunk) {
                onChunk(data.chunk)
              }
            } catch (e) {
              // ignore parse errors for partial json
            }
          }
        }
      }
      return { session_id: finalSessionId }
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    error,
    healthCheck,
    uploadDocument,
    searchKnowledge,
    sendChat,
    sendChatStream,
    getSessions: () => request('/api/v1/sessions'),
    getSession: (id) => request(`/api/v1/sessions/${id}`),
    deleteSession: (id) => request(`/api/v1/sessions/${id}`, { method: 'DELETE' }),
  }
}
