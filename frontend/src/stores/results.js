import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useResultsStore = defineStore('results', () => {
  const loading = ref(false)
  const data = ref(null)    // EvaluationResult
  const error = ref('')

  async function generate(sessionId, resumeData, config, messages) {
    loading.value = true
    error.value = ''

    try {
      const resp = await fetch('/api/evaluation/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          resume: resumeData,
          config,
          messages,
        }),
      })
      const result = await resp.json()

      if (result.success) {
        data.value = result.data
      } else {
        error.value = result.error || '评估生成失败'
      }
    } catch (e) {
      error.value = '网络请求失败，请检查后端服务是否启动。'
    } finally {
      loading.value = false
    }
  }

  function reset() {
    data.value = null
    loading.value = false
    error.value = ''
  }

  return { loading, data, error, generate, reset }
})
