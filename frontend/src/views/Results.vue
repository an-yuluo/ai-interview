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
        <div class="export-dropdown" :class="{ open: showExportMenu }">
          <button class="btn btn-primary" @click="showExportMenu = !showExportMenu">
            导出报告
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="6 9 12 15 18 9"/>
            </svg>
          </button>
          <div class="export-menu" v-if="showExportMenu">
            <button @click="exportHTML">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
              HTML 报告（可打印/存PDF）
            </button>
            <button @click="exportMarkdown">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
              Markdown 格式
            </button>
            <button @click="exportText">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
              纯文本格式
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useResultsStore } from '../stores/results'
import RadarChart from '../components/RadarChart.vue'
import QuestionReview from '../components/QuestionReview.vue'

const router = useRouter()
const resultsStore = useResultsStore()
const showExportMenu = ref(false)

onMounted(() => {
  if (!resultsStore.data && !resultsStore.loading) {
    router.replace('/')
  }
})

function retryGenerate() {
  router.push('/interview')
}

function startNewInterview() {
  resultsStore.reset()
  router.push('/upload')
}

function exportHTML() {
  showExportMenu.value = false
  const data = resultsStore.data
  const scores = data.radar_scores
  const now = new Date().toLocaleDateString('zh-CN')

  const reviewsHTML = (data.question_reviews || []).map((r, i) => `
    <div class="review-card">
      <h4>第 ${i + 1} 题：${escapeHtml(r.question)}</h4>
      <div class="review-section">
        <div class="label">你的回答：</div>
        <p>${escapeHtml(r.user_answer)}</p>
      </div>
      <div class="review-section highlight">
        <div class="label">亮点：</div>
        <p>${escapeHtml(r.highlights)}</p>
      </div>
      <div class="review-section weakness">
        <div class="label">失分点：</div>
        <p>${escapeHtml(r.weaknesses)}</p>
      </div>
      <div class="review-section better">
        <div class="label">高分示范：</div>
        <p>${escapeHtml(r.better_answer)}</p>
      </div>
    </div>
  `).join('')

  const html = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>AI 模拟面试评估报告</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: -apple-system, "Microsoft YaHei", sans-serif; color: #1a1a2e; line-height: 1.7; padding: 40px; max-width: 800px; margin: 0 auto; }
  h1 { font-size: 28px; margin-bottom: 8px; color: #4f46e5; }
  .meta { color: #666; font-size: 14px; margin-bottom: 32px; }
  .score-box { display: flex; align-items: center; gap: 16px; background: #f8f9ff; border: 1px solid #e0e7ff; border-radius: 12px; padding: 20px 24px; margin-bottom: 24px; }
  .score-num { font-size: 52px; font-weight: 800; color: #4f46e5; line-height: 1; }
  .score-detail { flex: 1; }
  .comment { color: #555; font-size: 15px; }
  h2 { font-size: 20px; margin: 28px 0 12px; padding-bottom: 8px; border-bottom: 2px solid #e0e7ff; }
  h3 { font-size: 16px; margin-bottom: 8px; color: #333; }
  .scores-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin-bottom: 24px; }
  .score-item { text-align: center; padding: 12px; background: #f8f9ff; border-radius: 8px; }
  .score-item .val { font-size: 24px; font-weight: 700; color: #4f46e5; }
  .score-item .name { font-size: 12px; color: #666; margin-top: 4px; }
  .tag-list { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; }
  .tag { padding: 6px 14px; border-radius: 16px; font-size: 14px; }
  .tag.green { background: #dcfce7; color: #166534; }
  .tag.red { background: #fee2e2; color: #991b1b; }
  .review-card { background: #fafafa; border: 1px solid #e5e7eb; border-radius: 10px; padding: 16px 20px; margin-bottom: 16px; }
  .review-card h4 { font-size: 15px; color: #333; margin-bottom: 10px; }
  .review-section { margin-bottom: 8px; font-size: 14px; }
  .review-section .label { font-weight: 600; color: #555; margin-bottom: 2px; }
  .review-section.highlight .label { color: #059669; }
  .review-section.weakness .label { color: #dc2626; }
  .review-section.better .label { color: #4f46e5; }
  .review-section p { color: #444; }
  @media print {
    body { padding: 20px; }
    .no-print { display: none; }
  }
</style>
</head>
<body>
<h1>AI 模拟面试评估报告</h1>
<div class="meta">生成日期：${now}</div>

<div class="score-box">
  <div class="score-num">${data.overall_score}</div>
  <div class="score-detail">
    <div style="font-size:16px;font-weight:600;">综合评分 / 10</div>
    <div class="comment">${escapeHtml(data.overall_comment)}</div>
  </div>
</div>

<h2>维度评分</h2>
<div class="scores-grid">
  <div class="score-item"><div class="val">${scores.technical_depth}</div><div class="name">技术深度</div></div>
  <div class="score-item"><div class="val">${scores.project_experience}</div><div class="name">项目经验</div></div>
  <div class="score-item"><div class="val">${scores.communication}</div><div class="name">沟通表达</div></div>
  <div class="score-item"><div class="val">${scores.problem_solving}</div><div class="name">问题解决</div></div>
  <div class="score-item"><div class="val">${scores.adaptability}</div><div class="name">应变能力</div></div>
</div>

${data.strengths?.length ? `<h2>优势</h2><div class="tag-list">${data.strengths.map(s => `<span class="tag green">${escapeHtml(s)}</span>`).join('')}</div>` : ''}

${data.blind_spots?.length ? `<h2>能力盲区</h2><div class="tag-list">${data.blind_spots.map(b => `<span class="tag red">${escapeHtml(b)}</span>`).join('')}</div>` : ''}

${reviewsHTML ? `<h2>逐题复盘</h2>${reviewsHTML}` : ''}

<div class="no-print" style="text-align:center;margin-top:32px;padding-top:16px;border-top:1px solid #e5e7eb;">
  <button onclick="window.print()" style="padding:10px 32px;background:#4f46e5;color:#fff;border:none;border-radius:8px;font-size:15px;cursor:pointer;">打印 / 保存为 PDF</button>
</div>
</body></html>`

  const w = window.open('', '_blank')
  if (w) {
    w.document.write(html)
    w.document.close()
  }
}

function exportMarkdown() {
  showExportMenu.value = false
  const data = resultsStore.data
  const scores = data.radar_scores

  let md = `# AI 模拟面试评估报告\n\n`
  md += `> 综合评分：**${data.overall_score}/10**\n\n`
  md += `${data.overall_comment}\n\n`
  md += `## 维度评分\n\n`
  md += `| 维度 | 评分 |\n|------|------|\n`
  md += `| 技术深度 | ${scores.technical_depth}/10 |\n`
  md += `| 项目经验 | ${scores.project_experience}/10 |\n`
  md += `| 沟通表达 | ${scores.communication}/10 |\n`
  md += `| 问题解决 | ${scores.problem_solving}/10 |\n`
  md += `| 应变能力 | ${scores.adaptability}/10 |\n\n`

  if (data.strengths?.length) {
    md += `## 优势\n\n`
    data.strengths.forEach(s => md += `- ${s}\n`)
    md += '\n'
  }
  if (data.blind_spots?.length) {
    md += `## 能力盲区\n\n`
    data.blind_spots.forEach(b => md += `- ${b}\n`)
    md += '\n'
  }
  if (data.question_reviews?.length) {
    md += `## 逐题复盘\n\n`
    data.question_reviews.forEach((r, i) => {
      md += `### 第 ${i + 1} 题：${r.question}\n\n`
      md += `**你的回答：** ${r.user_answer}\n\n`
      md += `**亮点：** ${r.highlights}\n\n`
      md += `**失分点：** ${r.weaknesses}\n\n`
      md += `**高分示范：** ${r.better_answer}\n\n---\n\n`
    })
  }

  downloadBlob(md, '面试评估报告.md', 'text/markdown;charset=utf-8')
}

function exportText() {
  showExportMenu.value = false
  const data = resultsStore.data
  const scores = data.radar_scores

  let text = `=== AI 模拟面试评估报告 ===\n\n`
  text += `综合评分: ${data.overall_score}/10\n${data.overall_comment}\n\n`
  text += `--- 维度评分 ---\n`
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

  downloadBlob(text, '面试评估报告.txt', 'text/plain;charset=utf-8')
}

function downloadBlob(content, filename, type) {
  const blob = new Blob([content], { type })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

function escapeHtml(str) {
  if (!str) return ''
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')
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

/* Export dropdown */
.export-dropdown {
  position: relative;
}
.export-dropdown .btn-primary {
  display: flex;
  align-items: center;
  gap: 6px;
}
.export-menu {
  position: absolute;
  bottom: 100%;
  right: 0;
  margin-bottom: 6px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
  min-width: 220px;
  overflow: hidden;
  z-index: 10;
}
.export-menu button {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 10px 16px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 14px;
  color: var(--text-primary);
  text-align: left;
  transition: background 0.15s;
}
.export-menu button:hover {
  background: var(--color-primary-light);
  color: var(--color-primary);
}
.export-menu button svg {
  color: var(--text-muted);
  flex-shrink: 0;
}
</style>
