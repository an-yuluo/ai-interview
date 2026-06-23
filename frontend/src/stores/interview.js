import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const ROUND_LABELS = {
  tech_basic: '初级技术面',
  tech_advanced: '高级架构面',
  hr_behavioral: 'HR 行为面',
}

export const useInterviewStore = defineStore('interview', () => {
  // Configuration
  const config = ref({
    target_position: '',
    target_company: '',
    round_type: 'tech_basic',
    difficulty: 'mid',
    style: 'gentle',
    custom_instructions: '',
    multi_round_enabled: false,
    multi_round_rounds: [],
  })

  // Session state
  const sessionId = ref('')
  const messages = ref([])          // { role, content, question_number, is_follow_up }
  const isStreaming = ref(false)
  const currentStreamingText = ref('')
  const ended = ref(false)
  const questionCount = ref(0)

  // Standard answer state
  const standardAnswer = ref('')
  const isGeneratingAnswer = ref(false)
  const showStandardAnswer = ref(false)

  // Connection state for SSE resilience
  const connectionState = ref('connected')  // 'connected' | 'disconnected' | 'reconnecting'

  // Multi-round state
  const roundTransition = ref(false)
  const nextRoundLabel = ref('')
  const currentRoundIndex = ref(0)
  const totalRounds = ref(0)

  const maxQuestions = computed(() => {
    const map = { junior: 6, mid: 8, senior: 10 }
    return map[config.value.difficulty] || 8
  })

  const progress = computed(() => {
    if (maxQuestions.value === 0) return 0
    return Math.min(questionCount.value / maxQuestions.value, 1)
  })

  const currentRoundLabel = computed(() => {
    if (!config.value.multi_round_enabled || !config.value.multi_round_rounds.length) {
      return ROUND_LABELS[config.value.round_type] || ''
    }
    const rounds = config.value.multi_round_rounds
    return ROUND_LABELS[rounds[currentRoundIndex.value]] || ''
  })

  // ── Reusable SSE consumer ───────────────────────────────────────────
  async function _consumeSSE(url, body, { onText, onDone, onError, onStateUpdate }) {
    connectionState.value = 'connected'
    let fullText = ''

    try {
      const resp = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })

      if (!resp.ok) {
        if (resp.status >= 500) {
          connectionState.value = 'disconnected'
          throw new Error('服务暂时繁忙，请稍后重试')
        }
        throw new Error(`请求失败 (${resp.status})`)
      }

      const sid = resp.headers.get('X-Session-Id')
      if (sid && onStateUpdate) onStateUpdate('session_id', sid)

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
              if (onText) onText(fullText, data.content)
            } else if (data.type === 'done') {
              if (onDone) onDone(data)
            } else if (data.type === 'error') {
              console.error('SSE error:', data.content)
              if (onError) onError(data.content)
            }
          } catch { /* skip malformed */ }
        }
      }

      connectionState.value = 'connected'
      return fullText
    } catch (e) {
      connectionState.value = 'disconnected'
      // Auto-retry once after 2s delay
      if (e.message?.includes('Failed to fetch') || e.message?.includes('NetworkError')) {
        connectionState.value = 'reconnecting'
        await new Promise(r => setTimeout(r, 2000))
        connectionState.value = 'connected'
        try {
          return await _consumeSSE(url, body, { onText, onDone, onError, onStateUpdate })
        } catch {
          connectionState.value = 'disconnected'
          throw new Error('网络连接中断，请检查网络后重试')
        }
      }
      throw e
    }
  }

  // ── Start interview ─────────────────────────────────────────────────
  async function startInterview(resumeData) {
    messages.value = []
    sessionId.value = ''
    ended.value = false
    questionCount.value = 0
    isStreaming.value = true
    currentStreamingText.value = ''
    roundTransition.value = false
    currentRoundIndex.value = 0
    totalRounds.value = config.value.multi_round_enabled ? config.value.multi_round_rounds.length : 0

    try {
      const fullText = await _consumeSSE(
        '/api/interview/start',
        { resume: resumeData, config: config.value },
        {
          onText: (full) => { currentStreamingText.value = full },
          onDone: (data) => {
            if (data.session_id) sessionId.value = data.session_id
          },
          onStateUpdate: (key, val) => {
            if (key === 'session_id') sessionId.value = val
          },
        }
      )

      messages.value.push({
        role: 'interviewer',
        content: fullText,
        question_number: 1,
        is_follow_up: false,
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

  // ── Submit answer ───────────────────────────────────────────────────
  async function submitAnswer(answerText) {
    messages.value.push({
      role: 'candidate',
      content: answerText,
      question_number: questionCount.value,
      is_follow_up: false,
    })

    isStreaming.value = true
    currentStreamingText.value = ''

    try {
      const fullText = await _consumeSSE(
        '/api/interview/answer',
        { session_id: sessionId.value, answer: answerText },
        {
          onText: (full) => { currentStreamingText.value = full },
          onDone: (data) => {
            // Handle round transition
            if (data.round_transition) {
              roundTransition.value = true
              nextRoundLabel.value = ROUND_LABELS[data.next_round] || data.next_round
              currentRoundIndex.value++
              currentStreamingText.value = ''
              return
            }

            if (data.ended) ended.value = true
            // Follow-up: don't increment question count
            const isFollowUp = data.is_follow_up || false
            messages.value.push({
              role: 'interviewer',
              content: fullText,
              question_number: questionCount.value + (isFollowUp ? 0 : 1),
              is_follow_up: isFollowUp,
            })
            if (!ended.value && !isFollowUp) {
              questionCount.value++
            }
          },
        }
      )

      // Fallback: if onDone didn't push and no round transition
      if (!roundTransition.value) {
        if (!messages.value.length || messages.value[messages.value.length - 1].role !== 'interviewer') {
          messages.value.push({
            role: 'interviewer',
            content: fullText,
            question_number: questionCount.value + 1,
            is_follow_up: false,
          })
          if (!ended.value) questionCount.value++
        }
      }
      currentStreamingText.value = ''
    } catch (e) {
      console.error('Failed to submit answer:', e)
      throw e
    } finally {
      isStreaming.value = false
    }
  }

  // ── Start next round (multi-round mode) ─────────────────────────────
  async function startNextRound() {
    roundTransition.value = false
    questionCount.value = 0
    messages.value = []
    isStreaming.value = true
    currentStreamingText.value = ''

    try {
      const fullText = await _consumeSSE(
        '/api/interview/next-round',
        { session_id: sessionId.value, answer: '' },
        {
          onText: (full) => { currentStreamingText.value = full },
          onDone: () => {},
        }
      )

      messages.value.push({
        role: 'interviewer',
        content: fullText,
        question_number: 1,
        is_follow_up: false,
      })
      questionCount.value = 1
      currentStreamingText.value = ''
    } catch (e) {
      console.error('Failed to start next round:', e)
      throw e
    } finally {
      isStreaming.value = false
    }
  }

  // ── Request standard answer ─────────────────────────────────────────
  async function requestStandardAnswer() {
    if (!sessionId.value) return
    standardAnswer.value = ''
    isGeneratingAnswer.value = true
    showStandardAnswer.value = true

    try {
      await _consumeSSE(
        '/api/interview/standard-answer',
        { session_id: sessionId.value, answer: '' },
        {
          onText: (full) => { standardAnswer.value = full },
        }
      )
    } catch (e) {
      console.error('Failed to get standard answer:', e)
      standardAnswer.value = '生成标准回答失败，请稍后再试。'
    } finally {
      isGeneratingAnswer.value = false
    }
  }

  // ── Skip question ───────────────────────────────────────────────────
  async function skipQuestion() {
    if (!sessionId.value) return

    messages.value.push({
      role: 'candidate',
      content: '[跳过此题]',
      question_number: questionCount.value,
      is_follow_up: false,
    })

    isStreaming.value = true
    currentStreamingText.value = ''

    try {
      const fullText = await _consumeSSE(
        '/api/interview/skip',
        { session_id: sessionId.value, answer: '' },
        {
          onText: (full) => { currentStreamingText.value = full },
          onDone: (data) => {
            if (data.ended) ended.value = true
            messages.value.push({
              role: 'interviewer',
              content: fullText,
              question_number: questionCount.value + 1,
              is_follow_up: false,
            })
            if (!ended.value) questionCount.value++
          },
        }
      )

      // Fallback
      if (!messages.value.length || messages.value[messages.value.length - 1].role !== 'interviewer') {
        messages.value.push({
          role: 'interviewer',
          content: fullText,
          question_number: questionCount.value + 1,
          is_follow_up: false,
        })
        if (!ended.value) questionCount.value++
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
    connectionState.value = 'connected'
    roundTransition.value = false
    nextRoundLabel.value = ''
    currentRoundIndex.value = 0
    totalRounds.value = 0
    config.value = {
      target_position: '',
      target_company: '',
      round_type: 'tech_basic',
      difficulty: 'mid',
      style: 'gentle',
      custom_instructions: '',
      multi_round_enabled: false,
      multi_round_rounds: [],
    }
  }

  return {
    config, sessionId, messages, isStreaming, currentStreamingText,
    ended, questionCount, maxQuestions, progress,
    standardAnswer, isGeneratingAnswer, showStandardAnswer,
    connectionState,
    roundTransition, nextRoundLabel, currentRoundIndex, totalRounds, currentRoundLabel,
    startInterview, submitAnswer, requestStandardAnswer, skipQuestion, startNextRound, reset,
  }
})
