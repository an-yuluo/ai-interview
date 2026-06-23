<template>
  <div class="chat-bubble" :class="[message.role]">
    <div class="bubble-avatar">
      <div class="avatar-circle" :class="message.role">
        {{ message.role === 'interviewer' ? '面' : '我' }}
      </div>
    </div>
    <div class="bubble-content">
      <div class="bubble-label">{{ message.role === 'interviewer' ? '面试官' : '我的回答' }}</div>
      <div class="bubble-text" v-html="renderedContent"></div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { marked } from 'marked'
import hljs from 'highlight.js'

// Configure marked with highlight.js
marked.setOptions({
  highlight: function (code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value
    }
    return hljs.highlightAuto(code).value
  },
  breaks: true,
  gfm: true,
})

const props = defineProps({
  message: { type: Object, required: true },
})

const renderedContent = computed(() => {
  if (!props.message.content) return ''
  return marked(props.message.content)
})
</script>

<style scoped>
.chat-bubble {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  max-width: 85%;
}
.chat-bubble.candidate {
  flex-direction: row-reverse;
  margin-left: auto;
}
.avatar-circle {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  flex-shrink: 0;
}
.avatar-circle.interviewer {
  background: var(--color-primary-light);
  color: var(--color-primary);
}
.avatar-circle.candidate {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}
.bubble-content {
  flex: 1;
  min-width: 0;
}
.bubble-label {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 4px;
}
.bubble-text {
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 15px;
  line-height: 1.7;
  word-break: break-word;
}
.interviewer .bubble-text {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-top-left-radius: 4px;
}
.candidate .bubble-text {
  background: var(--color-primary);
  color: #fff;
  border-top-right-radius: 4px;
}
.candidate .bubble-label {
  text-align: right;
}

/* Markdown content styling */
.bubble-text :deep(p) {
  margin: 0 0 8px;
}
.bubble-text :deep(p:last-child) {
  margin-bottom: 0;
}
.bubble-text :deep(pre) {
  background: #1e293b;
  color: #e2e8f0;
  padding: 14px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 8px 0;
  font-size: 13px;
}
.bubble-text :deep(code) {
  font-family: 'Fira Code', 'Consolas', monospace;
  font-size: 13px;
}
.bubble-text :deep(:not(pre) > code) {
  background: rgba(0,0,0,0.06);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
}
.candidate .bubble-text :deep(:not(pre) > code) {
  background: rgba(255,255,255,0.2);
}
.bubble-text :deep(ul), .bubble-text :deep(ol) {
  padding-left: 20px;
  margin: 4px 0;
}
.bubble-text :deep(strong) {
  font-weight: 600;
}
</style>
