<template>
  <div class="page">
    <!-- Loading state -->
    <div v-if="resultsStore.loading" class="loading-state">
      <div class="loading-spinner"></div>
      <h2>AI 正在生成评估报告...</h2>
      <p>分析你的面试表现，这可能需要几十秒</p>
    </div>

    <!-- Error state -->
    <div v-else-if="resultsStore.error" class="card error-card">
      <h3>报告生成失败</h3>
      <p>{{ resultsStore.error }}</p>
      <button class="btn btn-primary" @click="retryGenerate">重试</button>
    </div>

    <!-- Results -->
    <div v-else-if="resultsStore.data" class="results-content">
      <!-- Score Overview -->
      <section class="score-overview card">
        <div class="score-header">
          <h2>面试评估报告</h2>
          <div class="overall-score">
            <span class="score-num">{{ resultsStore.data.overall_score }}</span>
            <span class="score-label">/10 综合评分</span>
          </div>
        </div>
        <p class="overall-comment">{{ resultsStore.data.overall_comment }}</p>
        <RadarChart :scores="resultsStore.data.radar_scores" />
      </section>

      <!-- Strengths -->
      <section class="strengths-section card" v-if="resultsStore.data.strengths?.length">
        <h3 class="section-title">
          <span class="title-icon positive">+</span>
          你的优势
        </h3>
        <ul class="insight-list positive">
          <li v-for="(s, i) in resultsStore.data.strengths" :key="i">{{ s }}</li>
        </ul>
      </section>

      <!-- Blind Spots -->
      <section class="blindspots-section card" v-if="resultsStore.data.blind_spots?.length">
        <h3 class="section-title">
          <span class="title-icon negative">!</span>
          能力盲区
        </h3>
        <ul class="insight-list negative">
          <li v-for="(b, i) in resultsStore.data.blind_spots" :key="i">{{ b }}</li>
        </ul>
      </section>

      <!-- Question Reviews -->
      <section class="reviews-section" v-if="resultsStore.data.question_reviews?.length">
        <h3 class="section-title-main">逐题复盘</h3>
        <QuestionReview
          v-for="(review, i) in resultsStore.data.question_reviews"
          :key="i"
          :review="review"
          :index="i"
        />
      </section>

      <!-- Actions -->
      <div class="action-area">
        <button class="btn btn-secondary" @click="startNewInterview">开始新的面试</button>
        <button class="btn btn-primary" @click="exportReport">导出报告</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useResultsStore } from '../stores/results'
import RadarChart from '../components/RadarChart.vue'
import QuestionReview from '../components/QuestionReview.vue'

const router = useRouter()
const resultsStore = useResultsStore()

onMounted(() => {
  if (!resultsStore.data && !resultsStore.loading) {
    router.replace('/')
  }
})

function retryGenerate() {
  // Re-trigger from interview page
  router.push('/interview')
}

function startNewInterview() {
  resultsStore.reset()
  router.push('/upload')
}

function exportReport() {
  // Simple text export for MVP
  const data = resultsStore.data
  let text = `=== AI 模拟面试评估报告 ===\n\n`
  text += `综合评分: ${data.overall_score}/10\n`
  text += `${data.overall_comment}\n\n`

  text += `--- 维度评分 ---\n`
  const scores = data.radar_scores
  text += `技术深度: ${scores.technical_depth}/10\n`
  text += `项目经验: ${scores.project_experience}/10\n`
  text += `沟通表达: ${scores.communication}/10\n`
  text += `问题解决: ${scores.problem_solving}/10\n`
  text += `应变能力: ${scores.adaptability}/10\n\n`

  if (data.strengths?.length) {
    text += `--- 优势 ---\n`
    data.strengths.forEach(s => text += `- ${s}\n`)
    text += '\n'
  }

  if (data.blind_spots?.length) {
    text += `--- 能力盲区 ---\n`
    data.blind_spots.forEach(b => text += `- ${b}\n`)
    text += '\n'
  }

  if (data.question_reviews?.length) {
    text += `--- 逐题复盘 ---\n\n`
    data.question_reviews.forEach((r, i) => {
      text += `【第 ${i + 1} 题】${r.question}\n`
      text += `你的回答: ${r.user_answer}\n`
      text += `亮点: ${r.highlights}\n`
      text += `失分点: ${r.weaknesses}\n`
      text += `高分示范: ${r.better_answer}\n\n`
    })
  }

  const blob = new Blob([text], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = '面试评估报告.txt'
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.loading-state {
  text-align: center;
  padding: 80px 20px;
}
.loading-spinner {
  width: 48px;
  height: 48px;
  border: 3px solid var(--border-color);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 16px;
}
@keyframes spin { to { transform: rotate(360deg); } }
.loading-state h2 {
  font-size: 20px;
  margin-bottom: 8px;
}
.loading-state p {
  color: var(--text-secondary);
}

.error-card {
  text-align: center;
  border-color: var(--color-danger);
}
.error-card h3 { margin-bottom: 8px; color: var(--color-danger); }
.error-card p { margin-bottom: 16px; color: var(--text-secondary); }

/* Score Overview */
.score-overview {
  margin-bottom: 24px;
}
.score-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}
.score-header h2 {
  font-size: 24px;
}
.overall-score {
  text-align: right;
}
.score-num {
  font-size: 42px;
  font-weight: 800;
  color: var(--color-primary);
  line-height: 1;
}
.score-label {
  display: block;
  font-size: 13px;
  color: var(--text-secondary);
}
.overall-comment {
  color: var(--text-secondary);
  font-size: 15px;
  line-height: 1.6;
  margin-bottom: 8px;
}

/* Sections */
.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  margin-bottom: 12px;
}
.section-title-main {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 16px;
}
.title-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
}
.title-icon.positive {
  background: #d1fae5;
  color: #065f46;
}
.title-icon.negative {
  background: #fee2e2;
  color: #991b1b;
}
.insight-list {
  list-style: none;
  padding: 0;
}
.insight-list li {
  padding: 8px 12px;
  border-radius: 8px;
  margin-bottom: 8px;
  font-size: 14px;
  line-height: 1.6;
}
.insight-list.positive li {
  background: #f0fdf4;
  color: #166534;
}
.insight-list.negative li {
  background: #fef2f2;
  color: #991b1b;
}

.strengths-section, .blindspots-section {
  margin-bottom: 24px;
}
.reviews-section {
  margin-bottom: 32px;
}

.action-area {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
}
</style>
