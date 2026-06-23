<template>
  <div class="progress-bar-container">
    <div class="progress-info">
      <span class="progress-label">{{ label }}</span>
      <span class="progress-count">{{ current }}/{{ total }}</span>
    </div>
    <div class="progress-track">
      <div class="progress-fill" :style="{ width: percentage + '%' }"></div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  current: { type: Number, default: 0 },
  total: { type: Number, default: 1 },
  label: { type: String, default: '面试进度' },
})

const percentage = computed(() => {
  if (props.total <= 0) return 0
  return Math.min((props.current / props.total) * 100, 100)
})
</script>

<style scoped>
.progress-bar-container {
  width: 100%;
}
.progress-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
  font-size: 13px;
}
.progress-label {
  color: var(--text-secondary);
}
.progress-count {
  font-weight: 600;
  color: var(--color-primary);
}
.progress-track {
  height: 6px;
  background: var(--bg-tertiary);
  border-radius: 3px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-primary), #818cf8);
  border-radius: 3px;
  transition: width 0.5s ease;
}
</style>
