import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useResumeStore = defineStore('resume', () => {
  const data = ref(null)          // parsed resume data
  const rawFile = ref(null)       // original file
  const loading = ref(false)
  const error = ref('')

  async function uploadAndParse(file) {
    loading.value = true
    error.value = ''
    rawFile.value = file

    const formData = new FormData()
    formData.append('file', file)

    try {
      const resp = await fetch('/api/resume/parse', {
        method: 'POST',
        body: formData,
      })
      const result = await resp.json()

      if (result.success) {
        data.value = result.data
      } else {
        error.value = result.error || '解析失败'
      }
    } catch (e) {
      error.value = '网络请求失败，请检查后端服务是否启动。'
    } finally {
      loading.value = false
    }
  }

  function updateData(newData) {
    data.value = { ...data.value, ...newData }
  }

  function reset() {
    data.value = null
    rawFile.value = null
    loading.value = false
    error.value = ''
  }

  return { data, rawFile, loading, error, uploadAndParse, updateData, reset }
})
