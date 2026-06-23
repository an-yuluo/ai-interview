<template>
  <div class="page">
    <button class="back-btn" @click="router.push('/')">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="15 18 9 12 15 6"/>
      </svg>
      返回首页
    </button>

    <h1 class="page-title">面试历史</h1>
    <p class="page-subtitle">回顾你的每次模拟面试，追踪进步轨迹</p>

    <!-- Loading -->
    <div v-if="historyStore.loading && !historyStore.records.length" class="loading-state">
      <div class="spinner"></div>
      <span>加载中...</span>
    </div>

    <!-- Error -->
    <div v-else-if="historyStore.error" class="error-state">
      <p>{{ historyStore.error }}</p>
      <button class="btn btn-secondary" @click="historyStore.fetchRecords()">重试</button>
    </div>

    <!-- Empty state -->
    <div v-else-if="!historyStore.records.length" class="empty-state card">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
        <line x1="3" y1="9" x2="21" y2="9"/>
        <line x1="9" y1="21" x2="9" y2="9"/>
      </svg>
      <h3>暂无面试记录</h3>
      <p>完成一次模拟面试后，记录会自动保存在这里</p>
      <button class="btn btn-primary" @click="router.push('/upload')">开始面试</button>
    </div>

    <!-- Records list -->
    <div v-else class="records-list">
      <div
        v-for="record in historyStore.records"
        :key="record.id"
        class="record-card card"
        :class="{ expanded: expandedId === record.id }"
        @click="toggleExpand(record.id)"
      >
        <div class="record-header">
          <div class="record-info">
            <div class="record-date">{{ formatDate(record.created_at) }}</div>
            <div class="record-position">
              <strong>{{ record.target_position }}</strong>
              <span v-if="record.round_label" class="round-badge">{{ record.round_label }}</span>
            </div>
            <div class="record-meta">
              {{ record.resume_name }} · {{ record.question_count }} 题
            </div>
          </div>
          <div class="record-score">
            <div class="score-value" :class="scoreClass(record.overall_score)">
              {{ record.overall_score.toFixed(1) }}
            </div>
            <div class="score-label">/ 10</div>
          </div>
        </div>

        <!-- Expanded detail -->
        <transition name="slide">
          <div v-if="expandedId === record.id" class="record-detail">
            <div v-if="historyStore.loading" class="detail-loading">
              <div class="spinner"></div>
            </div>
            <div v-else-if="historyStore.selectedRecord" class="detail-content">
              <!-- Radar chart -->
              <div class="detail-section">
                <h4>能力雷达图</h4>
                <RadarChart
                  v-if="historyStore.selectedRecord.radar_scores"
                  :scores="historyStore.selectedRecord.radar_scores"
                  height="280px"
                />
              </div>

              <!-- Strengths -->
              <div class="detail-section" v-if="historyStore.selectedRecord.strengths?.length">
                <h4>优势</h4>
                <ul class="strength-list">
                  <li v-for="(s, i) in historyStore.selectedRecord.strengths" :key="i">
                    <span class="badge green">+</span> {{ s }}
                  </li>
                </ul>
              </div>

              <!-- Blind spots -->
              <div class="detail-section" v-if="historyStore.selectedRecord.blind_spots?.length">
                <h4>盲区</h4>
                <ul class="blindspot-list">
                  <li v-for="(b, i) in historyStore.selectedRecord.blind_spots" :key="i">
                    <span class="badge red">!</span> {{ b }}
                  </li>
                </ul>
              </div>

              <!-- Comment -->
              <div class="detail-section" v-if="historyStore.selectedRecord.overall_comment">
                <h4>综合评语</h4>
                <p class="comment-text">{{ historyStore.selectedRecord.overall_comment }}</p>
              </div>

              <!-- Actions -->
              <div class="detail-actions">
                <button class="btn btn-secondary btn-sm" @click.stop="historyStore.deleteRecord(record.id)">
                  删除记录
                </button>
              </div>
            </div>
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useHistoryStore } from '../stores/history'
import RadarChart from '../components/RadarChart.vue'

const router = useRouter()
const historyStore = useHistoryStore()
const expandedId = ref(null)

onMounted(() => {
  historyStore.fetchRecords()
})

function toggleExpand(id) {
  if (expandedId.value === id) {
    expandedId.value = null
  } else {
    expandedId.value = id
    historyStore.fetchDetail(id)
  }
}

function formatDate(isoStr) {
  try {
    const d = new Date(isoStr)
    return d.toLocaleDateString('zh-CN', {
      year: 'numeric', month: 'long', day: 'numeric',
      hour: '2-digit', minute: '2-digit',
    })
  } catch {
    return isoStr
  }
}

function scoreClass(score) {
  if (score >= 8) return 'score-high'
  if (score >= 6) return 'score-mid'
  return 'score-low'
}
</script>

<style scoped>
.loading-state, .error-state {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
}
.spinner {
  width: 24px; height: 24px;
  border: 3px solid var(--border-color);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 12px;
}
@keyframes spin { to { transform: rotate(360deg); } }

.empty-state {
  text-align: center;
  padding: 48px 24px;
}
.empty-state svg { color: var(--text-muted); margin-bottom: 16px; }
.empty-state h3 { margin-bottom: 8px; }
.empty-state p { color: var(--text-secondary); margin-bottom: 20px; }

.records-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.record-card {
  cursor: pointer;
  transition: all 0.2s;
  overflow: hidden;
}
.record-card:hover {
  border-color: var(--color-primary);
  box-shadow: 0 2px 8px rgba(79,70,229,0.08);
}
.record-card.expanded {
  border-color: var(--color-primary);
}

.record-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.record-date {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 4px;
}
.record-position {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}
.record-position strong { font-size: 16px; }
.round-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
  background: var(--color-primary-light);
  color: var(--color-primary);
  font-weight: 500;
}
.record-meta {
  font-size: 13px;
  color: var(--text-secondary);
}

.record-score {
  text-align: center;
  flex-shrink: 0;
}
.score-value {
  font-size: 28px;
  font-weight: 800;
  line-height: 1;
}
.score-high { color: #059669; }
.score-mid { color: #d97706; }
.score-low { color: #dc2626; }
.score-label {
  font-size: 12px;
  color: var(--text-muted);
}

.record-detail {
  border-top: 1px solid var(--border-color);
  margin-top: 12px;
  padding-top: 16px;
}
.detail-loading {
  text-align: center;
  padding: 24px;
}
.detail-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.detail-section h4 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--text-primary);
}
.strength-list, .blindspot-list {
  list-style: none;
  padding: 0;
}
.strength-list li, .blindspot-list li {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 4px;
}
.badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
  margin-top: 3px;
}
.badge.green {
  background: #dcfce7;
  color: #166534;
}
.badge.red {
  background: #fee2e2;
  color: #991b1b;
}
.comment-text {
  font-size: 14px;
  line-height: 1.7;
  color: var(--text-secondary);
}
.detail-actions {
  display: flex;
  justify-content: flex-end;
  padding-top: 8px;
}
.btn-sm {
  font-size: 12px;
  padding: 4px 12px;
}

.slide-enter-active, .slide-leave-active {
  transition: all 0.3s ease;
  max-height: 800px;
  overflow: hidden;
}
.slide-enter-from, .slide-leave-to {
  max-height: 0;
  opacity: 0;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 14px;
  padding: 4px 0;
  margin-bottom: 12px;
  transition: color 0.2s;
}
.back-btn:hover { color: var(--color-primary); }
</style>
