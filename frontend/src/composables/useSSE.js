import { ref } from 'vue'

/**
 * Composable for consuming SSE streams via fetch (POST-compatible).
 * Unlike EventSource, this works with POST requests and custom headers.
 */
export function useSSE() {
  const isStreaming = ref(false)
  const text = ref('')
  const error = ref('')

  async function consume(url, body, { onChunk, onDone, onError } = {}) {
    isStreaming.value = true
    text.value = ''
    error.value = ''

    try {
      const resp = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })

      if (!resp.ok) {
        throw new Error(`HTTP ${resp.status}: ${resp.statusText}`)
      }

      const reader = resp.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      let fullText = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          try {
            const data = JSON.parse(line.slice(6))
            if (data.type === 'text') {
              fullText += data.content
              text.value = fullText
              onChunk?.(data.content, fullText)
            } else if (data.type === 'done') {
              onDone?.(data)
            } else if (data.type === 'error') {
              error.value = data.content
              onError?.(data.content)
            }
          } catch { /* skip malformed lines */ }
        }
      }

      // Process remaining buffer
      if (buffer.startsWith('data: ')) {
        try {
          const data = JSON.parse(buffer.slice(6))
          if (data.type === 'text') {
            fullText += data.content
            text.value = fullText
          } else if (data.type === 'done') {
            onDone?.(data)
          }
        } catch { /* skip */ }
      }

      return fullText
    } catch (e) {
      error.value = e.message
      onError?.(e.message)
      throw e
    } finally {
      isStreaming.value = false
    }
  }

  function reset() {
    text.value = ''
    error.value = ''
    isStreaming.value = false
  }

  return { isStreaming, text, error, consume, reset }
}
