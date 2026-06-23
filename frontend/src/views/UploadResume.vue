<template>
  <div class="page">
    <button class="btn btn-secondary back-btn" @click="$router.push('/')">← 返回首页</button>

    <h1 class="page-title">上传简历</h1>
    <p class="page-subtitle">上传你的 PDF 或 Word 简历，AI 将自动提取关键信息</p>

    <FileUploader @file-selected="onFileSelected" />

    <div v-if="store.loading" class="status-area">
      <div class="loading-spinner"></div>
      <p>AI 正在解析你的简历...</p>
    </div>

    <div v-if="store.error" class="error-area card">
      <p>{{ store.error }}</p>
    </div>

    <ResumePreview v-if="store.data" :data="store.data" class="resume-card" />

    <div v-if="store.data" class="action-area">
      <button class="btn btn-secondary" @click="store.reset()">重新上传</button>
      <button class="btn btn-primary btn-lg" @click="goToConfigure">
        下一步：配置面试场景 →
      </button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useResumeStore } from '../stores/resume'
import FileUploader from '../components/FileUploader.vue'
import ResumePreview from '../components/ResumePreview.vue'

const router = useRouter()
const store = useResumeStore()

function onFileSelected(file) {
  if (file) {
    store.uploadAndParse(file)
  }
}

function goToConfigure() {
  router.push('/configure')
}
</script>

<style scoped>
.back-btn {
  margin-bottom: 24px;
  font-size: 14px;
  padding: 8px 16px;
}
.status-area {
  text-align: center;
  padding: 40px 20px;
}
.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 12px;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
.error-area {
  border-color: var(--color-danger);
  color: var(--color-danger);
  margin-top: 16px;
}
.resume-card {
  margin-top: 24px;
}
.action-area {
  display: flex;
  justify-content: space-between;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
}
</style>
