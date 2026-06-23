import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useHistoryStore = defineStore('history', () => {
  const records = ref([])
  const loading = ref(false)
  const error = ref('')
  const selectedRecord = ref(null)

  async function fetchRecords() {
    loading.value = true
    error.value = ''
    try {
      const resp = await fetch('/api/history')
      const data = await resp.json()
      if (data.success) {
        records.value = data.records
      } else {
        error.value = data.error || '加载失败'
      }
    } catch (e) {
      error.value = '网络错误'
    } finally {
      loading.value = false
    }
  }

  async function fetchDetail(id) {
    loading.value = true
    error.value = ''
    selectedRecord.value = null
    try {
      const resp = await fetch(`/api/history/${id}`)
      const data = await resp.json()
      if (data.success) {
        selectedRecord.value = data.record
      } else {
        error.value = data.error || '加载失败'
      }
    } catch (e) {
      error.value = '网络错误'
    } finally {
      loading.value = false
    }
  }

  async function deleteRecord(id) {
    try {
      const resp = await fetch(`/api/history/${id}`, { method: 'DELETE' })
      const data = await resp.json()
      if (data.success) {
        records.value = records.value.filter(r => r.id !== id)
        if (selectedRecord.value?.id === id) selectedRecord.value = null
      }
    } catch (e) {
      error.value = '删除失败'
    }
  }

  function reset() {
    records.value = []
    selectedRecord.value = null
    error.value = ''
    loading.value = false
  }

  return { records, loading, error, selectedRecord, fetchRecords, fetchDetail, deleteRecord, reset }
})
