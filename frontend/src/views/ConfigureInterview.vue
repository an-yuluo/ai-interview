<template>
  <div class="page">
    <button class="btn btn-secondary back-btn" @click="$router.push('/upload')">← 返回上一步</button>

    <h1 class="page-title">配置面试场景</h1>
    <p class="page-subtitle">根据你的需求定制面试场景，越精准越接近真实面试</p>

    <div class="config-form">
      <!-- Target Position -->
      <div class="form-group">
        <label>目标岗位 <span class="required">*</span></label>
        <input class="input" v-model="config.target_position" placeholder="例：后端开发、前端工程师、数据分析师" />
      </div>

      <!-- Target Company -->
      <div class="form-group">
        <label>目标公司</label>
        <input class="input" v-model="config.target_company" placeholder="例：字节跳动、阿里巴巴、腾讯（选填）" />
      </div>

      <!-- Interview Round -->
      <div class="form-group">
        <label>面试轮次</label>

        <!-- Multi-round toggle -->
        <div class="multi-round-toggle" @click="toggleMultiRound">
          <div class="toggle-switch" :class="{ on: config.multi_round_enabled }">
            <div class="toggle-knob"></div>
          </div>
          <span class="toggle-label">多轮连续面试模式</span>
          <span class="toggle-hint">连续进行多轮面试，最终综合评分</span>
        </div>

        <!-- Multi-round: select rounds -->
        <div v-if="config.multi_round_enabled" class="multi-round-select">
          <p class="multi-round-hint">选择面试轮次（按顺序进行）：</p>
          <div class="round-check-list">
            <label
              v-for="opt in roundOptions"
              :key="opt.value"
              class="round-check-item"
              :class="{ checked: selectedRounds.includes(opt.value) }"
            >
              <input type="checkbox" :value="opt.value" v-model="selectedRounds" />
              <span class="check-label">{{ opt.label }}</span>
            </label>
          </div>
          <p class="multi-round-hint" v-if="selectedRounds.length >= 2">
            已选 {{ selectedRounds.length }} 轮：{{ selectedRounds.map(r => roundLabelMap[r]).join(' → ') }}
          </p>
        </div>

        <!-- Single round selection -->
        <div v-else class="option-group">
          <button
            v-for="opt in roundOptions"
            :key="opt.value"
            class="option-btn"
            :class="{ active: config.round_type === opt.value }"
            @click="config.round_type = opt.value"
          >
            {{ opt.label }}
          </button>
        </div>
      </div>

      <!-- Difficulty -->
      <div class="form-group">
        <label>难度等级</label>
        <div class="option-group">
          <button
            v-for="opt in difficultyOptions"
            :key="opt.value"
            class="option-btn"
            :class="{ active: config.difficulty === opt.value }"
            @click="config.difficulty = opt.value"
          >
            <span class="opt-label">{{ opt.label }}</span>
            <span class="opt-desc">{{ opt.desc }}</span>
          </button>
        </div>
      </div>

      <!-- Interviewer Style -->
      <div class="form-group">
        <label>面试官风格</label>
        <div class="option-group style-group">
          <button
            v-for="opt in styleOptions"
            :key="opt.value"
            class="option-btn style-btn"
            :class="{ active: config.style === opt.value }"
            @click="config.style = opt.value"
          >
            <span class="style-icon">{{ opt.icon }}</span>
            <span class="opt-label">{{ opt.label }}</span>
            <span class="opt-desc">{{ opt.desc }}</span>
          </button>
        </div>
      </div>

      <!-- Custom Instructions -->
      <div class="form-group">
        <label>额外指令</label>
        <textarea
          class="input textarea"
          v-model="config.custom_instructions"
          placeholder="例：重点考察分布式系统设计能力，多用算法题考察..."
          rows="3"
        ></textarea>
      </div>
    </div>

    <div class="action-area">
      <button class="btn btn-secondary" @click="$router.push('/upload')">修改简历</button>
      <button class="btn btn-primary btn-lg" :disabled="!canStart" @click="startInterview">
        开始面试 →
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useResumeStore } from '../stores/resume'
import { useInterviewStore } from '../stores/interview'

const router = useRouter()
const resumeStore = useResumeStore()
const interviewStore = useInterviewStore()
const config = interviewStore.config

// Redirect if no resume
onMounted(() => {
  if (!resumeStore.data) router.replace('/upload')
})

const roundOptions = [
  { value: 'tech_basic', label: '初级技术面' },
  { value: 'tech_advanced', label: '高级架构面' },
  { value: 'hr_behavioral', label: 'HR 行为面' },
]

const roundLabelMap = {
  tech_basic: '初级技术面',
  tech_advanced: '高级架构面',
  hr_behavioral: 'HR 行为面',
}

const selectedRounds = ref(['tech_basic', 'tech_advanced', 'hr_behavioral'])

function toggleMultiRound() {
  config.multi_round_enabled = !config.multi_round_enabled
  if (!config.multi_round_enabled) {
    // Reset to single round mode
    config.multi_round_rounds = []
  }
}

const difficultyOptions = [
  { value: 'junior', label: '初级', desc: '5-6 题' },
  { value: 'mid', label: '中级', desc: '7-8 题' },
  { value: 'senior', label: '高级', desc: '9-10 题' },
]

const styleOptions = [
  { value: 'gentle', icon: '🤝', label: '温和引导型', desc: '鼓励为主，适当提示' },
  { value: 'strict', icon: '🔥', label: '严厉施压型', desc: '质疑追问，考验抗压' },
  { value: 'english', icon: '🌍', label: '外企全英文', desc: '全程英文面试' },
]

const canStart = computed(() => {
  if (!config.target_position.trim()) return false
  if (config.multi_round_enabled && selectedRounds.value.length < 2) return false
  return true
})

async function startInterview() {
  if (config.multi_round_enabled) {
    config.multi_round_rounds = [...selectedRounds.value]
    config.round_type = selectedRounds.value[0]
  }
  await interviewStore.startInterview(resumeStore.data)
  router.push('/interview')
}
</script>

<style scoped>
.back-btn {
  margin-bottom: 24px;
  font-size: 14px;
  padding: 8px 16px;
}
.config-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.form-group label {
  display: block;
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 8px;
}
.required { color: var(--color-danger); }
.textarea {
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
}
.option-group {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
.option-btn {
  padding: 10px 18px;
  border: 1.5px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-card);
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
  min-width: 100px;
}
.option-btn:hover {
  border-color: var(--color-primary);
}
.option-btn.active {
  border-color: var(--color-primary);
  background: var(--color-primary-light);
  color: var(--color-primary);
}
.opt-label {
  display: block;
  font-weight: 500;
  font-size: 15px;
}
.opt-desc {
  display: block;
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 2px;
}
.style-group {
  gap: 12px;
}
.style-btn {
  flex: 1;
  min-width: 160px;
  padding: 16px;
}
.style-icon {
  font-size: 28px;
  display: block;
  margin-bottom: 8px;
}
.action-area {
  display: flex;
  justify-content: space-between;
  margin-top: 40px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
}

/* Multi-round toggle */
.multi-round-toggle {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: var(--bg-card);
  border: 1.5px solid var(--border-color);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 12px;
}
.multi-round-toggle:hover {
  border-color: var(--color-primary);
}
.toggle-switch {
  width: 40px;
  height: 22px;
  background: #d1d5db;
  border-radius: 11px;
  position: relative;
  transition: background 0.2s;
  flex-shrink: 0;
}
.toggle-switch.on {
  background: var(--color-primary);
}
.toggle-knob {
  width: 18px;
  height: 18px;
  background: #fff;
  border-radius: 50%;
  position: absolute;
  top: 2px;
  left: 2px;
  transition: transform 0.2s;
}
.toggle-switch.on .toggle-knob {
  transform: translateX(18px);
}
.toggle-label {
  font-weight: 500;
  font-size: 15px;
}
.toggle-hint {
  font-size: 12px;
  color: var(--text-muted);
  margin-left: auto;
}

/* Multi-round round selection */
.multi-round-select {
  padding: 12px 16px;
  background: var(--color-primary-light);
  border: 1px solid var(--color-primary);
  border-radius: 10px;
}
.multi-round-hint {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}
.round-check-list {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}
.round-check-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: var(--bg-card);
  border: 1.5px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
}
.round-check-item:hover {
  border-color: var(--color-primary);
}
.round-check-item.checked {
  border-color: var(--color-primary);
  background: var(--color-primary-light);
  color: var(--color-primary);
}
.round-check-item input[type="checkbox"] {
  accent-color: var(--color-primary);
}
</style>
