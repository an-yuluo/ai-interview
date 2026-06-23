<template>
  <div class="home-page">
    <nav class="top-nav">
      <div class="nav-brand">AI 模拟面试</div>
    </nav>

    <section class="hero">
      <h1 class="hero-title">
        用 AI 面试官<br/>
        <span class="hero-highlight">提前演练，自信上场</span>
      </h1>
      <p class="hero-desc">
        上传简历 → 选择面试场景 → AI 面试官实时提问 → 多维度评分与逐题复盘
      </p>
      <button class="btn btn-primary btn-lg" @click="goToUpload">
        开始模拟面试
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="5" y1="12" x2="19" y2="12"/>
          <polyline points="12 5 19 12 12 19"/>
        </svg>
      </button>
      <button class="btn btn-secondary btn-lg history-btn" @click="router.push('/history')">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <polyline points="12 6 12 12 16 14"/>
        </svg>
        面试历史
      </button>
    </section>

    <section class="features">
      <div class="feature-card" v-for="feat in features" :key="feat.title">
        <div class="feature-icon" v-html="feat.icon"></div>
        <h3>{{ feat.title }}</h3>
        <p>{{ feat.desc }}</p>
      </div>
    </section>

    <section class="flow">
      <h2 class="section-heading">完整面试流程</h2>
      <div class="flow-steps">
        <div class="flow-step" v-for="(step, i) in steps" :key="i">
          <div class="step-num">{{ i + 1 }}</div>
          <div class="step-text">
            <strong>{{ step.title }}</strong>
            <span>{{ step.desc }}</span>
          </div>
        </div>
      </div>
    </section>

    <footer class="home-footer">
      <p>AI Mock Interview System v1.0</p>
    </footer>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
const goToUpload = () => router.push('/upload')

const features = [
  {
    title: '简历智能解析',
    desc: '上传 PDF/Word 简历，AI 自动提取技能栈、工作经历、项目难点',
    icon: '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>',
  },
  {
    title: '自定义面试场景',
    desc: '选择目标岗位、面试轮次、难度和面试官风格，针对性练习',
    icon: '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>',
  },
  {
    title: '流式对话体验',
    desc: '面试官实时流式提问，打字机效果，沉浸式模拟真实面试',
    icon: '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
  },
  {
    title: '多维雷达图评分',
    desc: '技术深度、项目经验、沟通表达、问题解决、应变能力全维度打分',
    icon: '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>',
  },
  {
    title: '逐题复盘示范',
    desc: '每道题点评亮点与失分点，生成高分回答示范供你背诵',
    icon: '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>',
  },
  {
    title: '能力盲区分析',
    desc: '汇总面试表现，找出软肋和优势，给出针对性提升建议',
    icon: '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
  },
]

const steps = [
  { title: '上传简历', desc: 'PDF / Word 格式' },
  { title: 'AI 解析', desc: '自动提取关键信息' },
  { title: '配置场景', desc: '岗位、轮次、风格' },
  { title: '模拟面试', desc: '流式对话交互' },
  { title: '评分复盘', desc: '雷达图 + 逐题点评' },
]
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #f8fafc 0%, #eef2ff 50%, #f8fafc 100%);
}
.top-nav {
  padding: 16px 24px;
  display: flex;
  align-items: center;
}
.nav-brand {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-primary);
}

.hero {
  text-align: center;
  padding: 80px 20px 60px;
  max-width: 680px;
  margin: 0 auto;
  position: relative;
}
.hero::before {
  content: '';
  position: absolute;
  top: -40px;
  left: 50%;
  transform: translateX(-50%);
  width: 600px;
  height: 600px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(79,70,229,0.06) 0%, transparent 70%);
  pointer-events: none;
  animation: heroPulse 6s ease-in-out infinite;
}
@keyframes heroPulse {
  0%, 100% { transform: translateX(-50%) scale(1); opacity: 0.6; }
  50% { transform: translateX(-50%) scale(1.1); opacity: 1; }
}
.hero-title {
  font-size: 44px;
  font-weight: 800;
  line-height: 1.2;
  margin-bottom: 16px;
  position: relative;
}
.hero-highlight {
  background: linear-gradient(135deg, #4f46e5, #7c3aed, #4f46e5);
  background-size: 200% auto;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: gradientShift 4s ease-in-out infinite;
}
@keyframes gradientShift {
  0%, 100% { background-position: 0% center; }
  50% { background-position: 100% center; }
}
.hero-desc {
  font-size: 17px;
  color: var(--text-secondary);
  margin-bottom: 32px;
  line-height: 1.6;
}

.btn-secondary {
  background: var(--bg-card);
  color: var(--color-primary);
  border: 1.5px solid var(--color-primary);
}
.btn-secondary:hover {
  background: var(--color-primary-light);
}
.history-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
}

.features {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  max-width: 960px;
  margin: 0 auto;
  padding: 40px 20px;
}
.feature-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 24px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}
.feature-card::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--color-primary-gradient);
  transform: scaleX(0);
  transition: transform 0.3s ease;
}
.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  border-color: rgba(79, 70, 229, 0.2);
}
.feature-card:hover::after {
  transform: scaleX(1);
}
.feature-icon {
  color: var(--color-primary);
  margin-bottom: 12px;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary-light);
  border-radius: 12px;
}
.feature-card h3 {
  font-size: 16px;
  margin-bottom: 6px;
}
.feature-card p {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.flow {
  max-width: 960px;
  margin: 0 auto;
  padding: 60px 20px;
  text-align: center;
}
.section-heading {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 32px;
}
.flow-steps {
  display: flex;
  justify-content: center;
  gap: 16px;
  flex-wrap: wrap;
  position: relative;
}
.flow-step {
  display: flex;
  align-items: center;
  gap: 10px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 14px 20px;
  transition: all 0.2s;
}
.flow-step:hover {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-md);
}
.step-num {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--color-primary);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 15px;
  flex-shrink: 0;
}
.step-text {
  text-align: left;
}
.step-text strong {
  display: block;
  font-size: 15px;
}
.step-text span {
  font-size: 13px;
  color: var(--text-secondary);
}

.home-footer {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-muted);
  font-size: 13px;
}

@media (max-width: 768px) {
  .hero-title { font-size: 32px; }
  .features { grid-template-columns: 1fr; }
  .flow-steps { flex-direction: column; align-items: center; }
}
</style>
