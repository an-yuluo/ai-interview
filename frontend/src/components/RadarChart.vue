<template>
  <div ref="chartRef" class="radar-chart" :style="{ width: width, height: height }"></div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  scores: { type: Object, required: true },
  width: { type: String, default: '100%' },
  height: { type: String, default: '380px' },
})

const chartRef = ref(null)
let chart = null

const LABELS = {
  technical_depth: '技术深度',
  project_experience: '项目经验',
  communication: '沟通表达',
  problem_solving: '问题解决',
  adaptability: '应变能力',
}

function renderChart() {
  if (!chartRef.value) return

  if (!chart) {
    chart = echarts.init(chartRef.value)
  }

  const indicators = Object.keys(LABELS).map(key => ({
    name: LABELS[key],
    max: 10,
  }))

  const values = Object.keys(LABELS).map(key => props.scores[key] || 0)

  chart.setOption({
    radar: {
      indicator: indicators,
      shape: 'polygon',
      splitNumber: 5,
      axisName: {
        color: '#64748b',
        fontSize: 13,
      },
      splitLine: { lineStyle: { color: '#e2e8f0' } },
      splitArea: {
        areaStyle: {
          color: ['#f8fafc', '#f1f5f9', '#e2e8f0', '#f1f5f9', '#f8fafc'],
        },
      },
      axisLine: { lineStyle: { color: '#e2e8f0' } },
    },
    series: [{
      type: 'radar',
      data: [{
        value: values,
        name: '面试评分',
        symbol: 'circle',
        symbolSize: 6,
        areaStyle: {
          color: 'rgba(79, 70, 229, 0.15)',
        },
        lineStyle: {
          color: '#4f46e5',
          width: 2,
        },
        itemStyle: {
          color: '#4f46e5',
        },
      }],
    }],
    tooltip: {
      trigger: 'item',
      formatter: function (params) {
        let html = '<div style="font-weight:600;margin-bottom:4px">面试评分</div>'
        indicators.forEach((ind, i) => {
          html += `${ind.name}: <b>${values[i]}</b>/10<br/>`
        })
        return html
      },
    },
  })
}

onMounted(renderChart)
watch(() => props.scores, renderChart, { deep: true })
</script>

<style scoped>
.radar-chart {
  margin: 0 auto;
}
</style>
