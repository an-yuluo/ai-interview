<template>
  <div
    class="file-uploader"
    :class="{ 'drag-over': isDragOver, 'has-file': !!selectedFile }"
    @dragover.prevent="isDragOver = true"
    @dragleave="isDragOver = false"
    @drop.prevent="handleDrop"
    @click="openFileDialog"
  >
    <input
      ref="fileInput"
      type="file"
      accept=".pdf,.docx"
      style="display: none"
      @change="handleFileSelect"
    />

    <div v-if="!selectedFile" class="uploader-content">
      <div class="uploader-icon">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
          <line x1="12" y1="18" x2="12" y2="12"/>
          <line x1="9" y1="15" x2="15" y2="15"/>
        </svg>
      </div>
      <p class="uploader-title">拖拽简历文件到这里</p>
      <p class="uploader-hint">或点击选择文件 · 支持 PDF、Word (.docx)</p>
    </div>

    <div v-else class="uploader-file">
      <div class="file-icon">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" stroke-width="1.5">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
        </svg>
      </div>
      <div class="file-info">
        <span class="file-name">{{ selectedFile.name }}</span>
        <span class="file-size">{{ formatSize(selectedFile.size) }}</span>
      </div>
      <button class="file-remove" @click.stop="removeFile" title="移除文件">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18"/>
          <line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['file-selected'])

const fileInput = ref(null)
const selectedFile = ref(null)
const isDragOver = ref(false)

function openFileDialog() {
  if (!selectedFile.value) {
    fileInput.value?.click()
  }
}

function handleFileSelect(e) {
  const file = e.target.files[0]
  if (file) selectFile(file)
}

function handleDrop(e) {
  isDragOver.value = false
  const file = e.dataTransfer.files[0]
  if (file) selectFile(file)
}

function selectFile(file) {
  const validTypes = ['application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
  const validExts = ['.pdf', '.docx']
  const ext = '.' + file.name.split('.').pop().toLowerCase()

  if (!validTypes.includes(file.type) && !validExts.includes(ext)) {
    alert('请选择 PDF 或 Word (.docx) 格式的简历文件')
    return
  }

  selectedFile.value = file
  emit('file-selected', file)
}

function removeFile() {
  selectedFile.value = null
  if (fileInput.value) fileInput.value.value = ''
  emit('file-selected', null)
}

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}
</script>

<style scoped>
.file-uploader {
  border: 2px dashed var(--border-color);
  border-radius: 16px;
  padding: 48px 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: var(--bg-card);
}
.file-uploader:hover,
.file-uploader.drag-over {
  border-color: var(--color-primary);
  background: var(--color-primary-light);
}
.file-uploader.has-file {
  cursor: default;
  padding: 20px 24px;
  border-style: solid;
}
.uploader-icon {
  color: var(--text-muted);
  margin-bottom: 16px;
}
.uploader-title {
  font-size: 17px;
  font-weight: 600;
  margin-bottom: 4px;
}
.uploader-hint {
  font-size: 14px;
  color: var(--text-secondary);
}
.uploader-file {
  display: flex;
  align-items: center;
  gap: 12px;
}
.file-info {
  flex: 1;
  text-align: left;
}
.file-name {
  display: block;
  font-weight: 500;
  font-size: 15px;
}
.file-size {
  font-size: 13px;
  color: var(--text-secondary);
}
.file-remove {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: color 0.2s;
}
.file-remove:hover {
  color: var(--color-danger);
}
</style>
