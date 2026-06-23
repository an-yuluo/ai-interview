import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useInterviewStore = defineStore('interview', () => {
  // Configuration
  const config = ref({
    target_position: '',
    target_company: '',
    round_type: 'tech_basic',
    difficulty: 'mid',
    style: 'gentle',
    custom_instructions: '',
  })

  // Session state
  const sessionId = ref('')
  const messages = ref([])          // { role, content, question_number }
  const isStreaming = ref(false)
  const currentStreamingText = ref('')
  const ended = ref(false)
  const questionCount = ref(0)

  // Standard answer state
  const standardAnswer = ref('')
  const isGeneratingAnswer = ref(false)
  const showStandardAnswer = ref(false)

  const maxQuestions = computed(() => {
    const map = { junior: 6, mid: 8, senior: 10 }
    return map[config.value.difficulty] || 8
  })

  const progress = computed(() => {
    if (maxQuestions.value === 0) return 0
    return Math.min(questionCount.value / maxQuestions.value, 1)
  })

  // Start interview — returns a promise that resolves when first question stream finishes
  async function startInterview(resumeData) {
    messages.value = []
    sessionId.value = ''
    ended.value = false
    questionCount.value = 0
    isStreaming.value = true
    currentStreamingText.value = ''

    try {
      const resp = await fetch('/api/interview/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          resume: resumeData,
          config: config.value,
        }),
      })

      const sid = resp.headers.get('X-Session-Id')
      if (sid) sessionId.value = sid

      const reader = resp.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      let fullText = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          try {
            const data = JSON.parse(line.slice(6))
            if (data.type === 'text') {
              fullText += data.content
              currentStreamingText.value = fullText
            } else if (data.type === 'done') {
              if (data.session_id) sessionId.value = data.session_id
            } else if (data.type === 'error') {
              console.error('SSE error:', data.content)
            }
          } catch { /* skip malformed */ }
        }
      }

      // Add the completed message
      messages.value.push({
        role: 'interviewer',
        content: fullText,
        question_number: 1,
      })
      questionCount.value = 1
      currentStreamingText.value = ''
    } catch (e) {
      console.error('Failed to start interview:', e)
      throw e
    } finally {
      isStreaming.value = false
    }
  }

  // Submit answer — returns promise that resolves when response stream finishes
  async function submitAnswer(answerText) {
    // Add user message
    messages.value.push({
      role: 'candidate',
      content: answerText,
      question_number: questionCount.value,
    })

    isStreaming.value = true
    currentStreamingText.value = ''
    let fullText = ''

    try {
      const resp = await fetch('/api/interview/answer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId.value,
          answer: answerText,
        }),
      })

      const reader = resp.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          try {
            const data = JSON.parse(line.slice(6))
            if (data.type === 'text') {
              fullText += data.content
              currentStreamingText.value = fullText
            } else if (data.type === 'done') {
              if (data.ended) ended.value = true
            }
          } catch { /* skip */ }
        }
      }

      messages.value.push({
        role: 'interviewer',
        content: fullText,
        question_number: questionCount.value + 1,
      })
      if (!ended.value) {
        questionCount.value++
      }
      currentStreamingText.value = ''
    } catch (e) {
      console.error('Failed to submit answer:', e)
      throw e
    } finally {
      isStreaming.value = false
    }
  }

  // Request a standard/model answer for the current question (SSE stream)
  async function requestStandardAnswer() {
    if (!sessionId.value) return
    standardAnswer.value = ''
    isGeneratingAnswer.value = true
    showStandardAnswer.value = true

    try {
      const resp = await fetch('/api/interview/standard-answer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId.value, answer: '' }),
      })

      const reader = resp.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      let fullText = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          try {
            const data = JSON.parse(line.slice(6))
            if (data.type === 'text') {
              fullText += data.content
              standardAnswer.value = fullText
            }
          } catch { /* skip */ }
        }
      }
    } catch (e) {
      console.error('Failed to get standard answer:', e)
      standardAnswer.value = '生成标准回答失败，请稍后再试。'
    } finally {
      isGeneratingAnswer.value = false
    }
  }

  // Skip the current question and move to the next one (SSE stream)
  async function skipQuestion() {
    if (!sessionId.value) return

    // Add a "[跳过此题]" message in the local chat
    messages.value.push({
      role: 'candidate',
      content: '[跳过此题]',
      question_number: questionCount.value,
    })

    isStreaming.value = true
    currentStreamingText.value = ''
    let fullText = ''

    try {
      const resp = await fetch('/api/interview/skip', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId.value, answer: '' }),
      })

      const reader = resp.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          try {
            const data = JSON.parse(line.slice(6))
            if (data.type === 'text') {
              fullText += data.content
              currentStreamingText.value = fullText
            } else if (data.type === 'done') {
              if (data.ended) ended.value = true
            }
          } catch { /* skip */ }
        }
      }

      messages.value.push({
        role: 'interviewer',
        content: fullText,
        question_number: questionCount.value + 1,
      })
      if (!ended.value) {
        questionCount.value++
      }
      currentStreamingText.value = ''
    } catch (e) {
      console.error('Failed to skip question:', e)
      throw e
    } finally {
      isStreaming.value = false
    }
  }

  function reset() {
    sessionId.value = ''
    messages.value = []
    isStreaming.value = false
    currentStreamingText.value = ''
    ended.value = false
    questionCount.value = 0
    standardAnswer.value = ''
    isGeneratingAnswer.value = false
    showStandardAnswer.value = false
    config.value = {
      target_position: '',
      target_company: '',
      round_type: 'tech_basic',
      difficulty: 'mid',
      style: 'gentle',
      custom_instructions: '',
    }
  }

  return {
    config, sessionId, messages, isStreaming, currentStreamingText,
    ended, questionCount, maxQuestions, progress,
    standardAnswer, isGeneratingAnswer, showStandardAnswer,
    startInterview, submitAnswer, requestStandardAnswer, skipQuestion, reset,
  }
})
