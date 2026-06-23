<template>
  <div class="resume-preview card">
    <div class="preview-header">
      <h2 class="candidate-name">{{ data.name || '未知' }}</h2>
      <span class="candidate-summary">{{ data.summary }}</span>
    </div>

    <div class="preview-section" v-if="data.skills?.length">
      <h3 class="section-title">技能栈</h3>
      <div class="skills-list">
        <span class="skill-tag" v-for="skill in data.skills" :key="skill">{{ skill }}</span>
      </div>
    </div>

    <div class="preview-section" v-if="data.experience?.length">
      <h3 class="section-title">工作经历</h3>
      <div class="exp-item" v-for="(exp, i) in data.experience" :key="i">
        <div class="exp-header">
          <strong>{{ exp.company }}</strong>
          <span class="exp-role">{{ exp.role }}</span>
          <span class="exp-duration">{{ exp.duration }}</span>
        </div>
        <p class="exp-highlights" v-if="exp.highlights">{{ exp.highlights }}</p>
      </div>
    </div>

    <div class="preview-section" v-if="data.projects?.length">
      <h3 class="section-title">项目经历</h3>
      <div class="proj-item" v-for="(proj, i) in data.projects" :key="i">
        <div class="proj-header">
          <strong>{{ proj.name }}</strong>
          <span class="proj-tech" v-if="proj.tech_stack">{{ proj.tech_stack }}</span>
        </div>
        <p class="proj-desc" v-if="proj.description">{{ proj.description }}</p>
      </div>
    </div>

    <div class="preview-section" v-if="data.education">
      <h3 class="section-title">教育背景</h3>
      <div class="edu-item">
        <strong>{{ data.education.school }}</strong>
        <span>{{ data.education.degree }} · {{ data.education.major }}</span>
        <span class="edu-year" v-if="data.education.year">{{ data.education.year }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  data: { type: Object, required: true },
})
</script>

<style scoped>
.resume-preview {
  text-align: left;
}
.preview-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}
.candidate-name {
  font-size: 24px;
  margin-bottom: 4px;
}
.candidate-summary {
  font-size: 14px;
  color: var(--text-secondary);
}
.preview-section {
  margin-bottom: 20px;
}
.section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 10px;
}
.skills-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.skill-tag {
  background: var(--color-primary-light);
  color: var(--color-primary);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}
.exp-item, .proj-item {
  margin-bottom: 12px;
}
.exp-header, .proj-header {
  display: flex;
  align-items: baseline;
  gap: 8px;
  flex-wrap: wrap;
}
.exp-role {
  color: var(--text-secondary);
  font-size: 14px;
}
.exp-duration {
  font-size: 13px;
  color: var(--text-muted);
  margin-left: auto;
}
.exp-highlights, .proj-desc {
  font-size: 14px;
  color: var(--text-secondary);
  margin-top: 4px;
}
.proj-tech {
  font-size: 12px;
  background: var(--bg-tertiary);
  padding: 2px 8px;
  border-radius: 4px;
  color: var(--text-secondary);
}
.edu-item {
  display: flex;
  align-items: baseline;
  gap: 8px;
  flex-wrap: wrap;
}
.edu-year {
  font-size: 13px;
  color: var(--text-muted);
  margin-left: auto;
}
</style>
