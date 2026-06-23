<template>
  <div class="question-review card" :class="{ expanded: isExpanded }">
    <div class="review-header" @click="isExpanded = !isExpanded">
      <div class="review-q-num">第 {{ index + 1 }} 题</div>
      <div class="review-question">{{ review.question }}</div>
      <div class="review-toggle">{{ isExpanded ? '收起' : '展开详情' }}</div>
    </div>

    <transition name="slide">
      <div v-if="isExpanded" class="review-body">
        <div class="review-section">
          <h4 class="section-label your-answer">你的回答</h4>
          <p class="section-content">{{ review.user_answer }}</p>
        </div>

        <div class="review-section">
          <h4 class="section-label highlights">亮点</h4>
          <p class="section-content positive">{{ review.highlights }}</p>
        </div>

        <div class="review-section">
          <h4 class="section-label weaknesses">失分点</h4>
          <p class="section-content negative">{{ review.weaknesses }}</p>
        </div>

        <div class="review-section">
          <h4 class="section-label better">高分回答示范</h4>
          <div class="section-content better-answer">{{ review.better_answer }}</div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  review: { type: Object, required: true },
  index: { type: Number, required: true },
})

const isExpanded = ref(false)
</script>

<style scoped>
.question-review {
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 12px;
}
.question-review:hover {
  border-color: var(--color-primary);
}
.review-header {
  display: flex;
  align-items: center;
  gap: 12px;
}
.review-q-num {
  background: var(--color-primary-light);
  color: var(--color-primary);
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
}
.review-question {
  flex: 1;
  font-size: 15px;
  font-weight: 500;
}
.review-toggle {
  font-size: 13px;
  color: var(--color-primary);
  white-space: nowrap;
}
.review-body {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}
.review-section {
  margin-bottom: 16px;
}
.review-section:last-child {
  margin-bottom: 0;
}
.section-label {
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 6px;
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
}
.section-label.your-answer {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}
.section-label.highlights {
  background: #d1fae5;
  color: #065f46;
}
.section-label.weaknesses {
  background: #fee2e2;
  color: #991b1b;
}
.section-label.better {
  background: var(--color-primary-light);
  color: var(--color-primary);
}
.section-content {
  font-size: 14px;
  line-height: 1.7;
  color: var(--text-secondary);
}
.section-content.positive { color: #065f46; }
.section-content.negative { color: #991b1b; }
.better-answer {
  background: #f8fafc;
  border-left: 3px solid var(--color-primary);
  padding: 12px 16px;
  border-radius: 0 8px 8px 0;
  color: var(--text-primary);
}

.slide-enter-active, .slide-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}
.slide-enter-from, .slide-leave-to {
  opacity: 0;
  max-height: 0;
}
.slide-enter-to, .slide-leave-from {
  opacity: 1;
  max-height: 2000px;
}
</style>
