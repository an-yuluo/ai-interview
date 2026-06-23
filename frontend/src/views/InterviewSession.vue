<template>
  <div class="interview-page">
    <!-- Header -->
    <header class="interview-header">
      <div class="header-left">
        <div class="interviewer-avatar">面</div>
        <div class="header-info">
          <strong>{{ styleLabel }}面试官</strong>
          <span class="header-position">{{ interviewStore.config.target_position }}</span>
        </div>
      </div>
      <div class="header-right">
        <ProgressBar
          :current="interviewStore.questionCount"
          :total="interviewStore.maxQuestions"
          class="header-progress"
        />
      </div>
      <div class="header-actions">
        <button
          class="voice-toggle"
          :class="{ active: voiceMode }"
          @click="toggleVoiceMode"
          :title="voiceMode ? '关闭语音模式' : '开启语音模式（面试官语音播报 + 语音输入）'"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
            <path v-if="voiceMode" d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"/>
            <line v-else x1="23" y1="1" x2="1" y2="23"/>
          </svg>
          <span class="voice-toggle-label">{{ voiceMode ? '语音模式' : '文字模式' }}</span>
        </button>
      </div>
    </header>

    <!-- Voice mode banner -->
    <div v-if="voiceMode" class="voice-banner">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
        <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"/>
      </svg>
      语音模式已开启 — 面试官会朗读问题，你可以用麦克风语音回答
      <button v-if="tts.isSpeaking.value" class="stop-speech-btn" @click="tts.stop()">停止朗读</button>
    </div>

    <!-- Chat Area -->
    <div class="chat-area" ref="chatArea">
      <div
        v-for="(msg, i) in interviewStore.messages"
        :key="i"
        class="message-wrapper"
      >
        <ChatBubble :message="msg" />
        <!-- Replay button for interviewer messages -->
        <button
          v-if="msg.role === 'interviewer' && tts.isSupported.value"
          class="replay-btn"
          :class="{ speaking: isReplaying === i }"
          @click="replayMessage(msg, i)"
          :title="isReplaying === i ? '停止朗读' : '朗读此消息'"
        >
          <svg v-if="isReplaying !== i" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
            <path d="M15.54 8.46a5 5 0 0 1 0 7.07"/>
          </svg>
          <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="6" y="4" width="4" height="16"/>
            <rect x="14" y="4" width="4" height="16"/>
          </svg>
        </button>
      </div>

      <!-- Streaming message (in-progress) -->
      <div v-if="interviewStore.isStreaming && interviewStore.currentStreamingText" class="chat-bubble interviewer">
        <div class="bubble-avatar">
          <div class="avatar-circle interviewer">面</div>
        </div>
        <div class="bubble-content">
          <div class="bubble-label">面试官</div>
          <div class="bubble-text streaming-text" v-html="renderedStreaming"></div>
        </div>
      </div>

      <!-- Typing indicator (before first chunk arrives) -->
      <TypingIndicator v-if="interviewStore.isStreaming && !interviewStore.currentStreamingText" />
    </div>

    <!-- Standard Answer Panel -->
    <div v-if="interviewStore.showStandardAnswer" class="standard-answer-panel">
      <div class="panel-header">
        <div class="panel-title">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
            <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
          </svg>
          标准回答参考
        </div>
        <button class="panel-close" @click="interviewStore.showStandardAnswer = false">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>
      <div class="panel-body">
        <div v-if="interviewStore.isGeneratingAnswer" class="panel-loading">
          <TypingIndicator />
          <span>正在生成标准回答...</span>
        </div>
        <div v-else class="panel-content" v-html="renderedStandardAnswer"></div>
      </div>
    </div>

    <!-- Input Area -->
    <div class="input-area" v-if="!interviewStore.ended">
      <!-- Action toolbar -->
      <div class="action-toolbar">
        <button
          class="action-btn standard-answer-btn"
          :disabled="interviewStore.isStreaming || interviewStore.isGeneratingAnswer"
          @click="handleStandardAnswer"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
            <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
          </svg>
          {{ interviewStore.showStandardAnswer ? '隐藏标准回答' : '查看标准回答' }}
        </button>
        <button
          class="action-btn skip-btn"
          :disabled="interviewStore.isStreaming || interviewStore.isGeneratingAnswer"
          @click="handleSkipQuestion"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="5 4 15 12 5 20 5 4"/>
            <line x1="19" y1="5" x2="19" y2="19"/>
          </svg>
          跳过此题
        </button>
      </div>

      <div class="input-wrapper">
        <!-- Microphone button -->
        <button
          v-if="stt.isSupported.value"
          class="mic-btn"
          :class="{ listening: stt.isListening.value }"
          :disabled="interviewStore.isStreaming"
          @click="toggleMic"
          :title="stt.isListening.value ? '停止录音' : '点击说话'"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
            <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
            <line x1="12" y1="19" x2="12" y2="23"/>
            <line x1="8" y1="23" x2="16" y2="23"/>
          </svg>
          <span v-if="stt.isListening.value" class="mic-pulse"></span>
        </button>

        <div class="text-input-area">
          <textarea
            ref="inputBox"
            class="chat-input"
            v-model="userInput"
            :placeholder="stt.isListening.value ? '正在聆听...' : '输入你的回答...'"
            rows="3"
            :disabled="interviewStore.isStreaming"
            @keydown.enter.exact="handleEnter"
            @keydown.shift.enter="handleShiftEnter"
          ></textarea>

          <!-- Interim speech text overlay -->
          <div v-if="stt.isListening.value && stt.interimTranscript.value" class="interim-text">
            {{ stt.transcript.value }}<span class="interim-highlight">{{ stt.interimTranscript.value }}</span>
          </div>
        </div>

        <button
          class="send-btn"
          :disabled="!canSend"
          @click="sendAnswer"
          title="发送 (Enter)"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="22" y1="2" x2="11" y2="13"/>
            <polygon points="22 2 15 22 11 13 2 9 22 2"/>
          </svg>
        </button>
      </div>

      <!-- Speech error -->
      <p v-if="stt.error.value" class="speech-error">{{ stt.error.value }}</p>

      <p class="input-hint">
        <template v-if="stt.isSupported.value">
          点击麦克风说话 · 或 Enter 发送 · Shift + Enter 换行
        </template>
        <template v-else>
          Enter 发送 · Shift + Enter 换行（当前浏览器不支持语音输入，请使用 Chrome）
        </template>
      </p>
    </div>

    <!-- End Interview -->
    <div class="end-area" v-if="interviewStore.ended">
      <div class="end-card card">
        <h3>面试已结束</h3>
        <p>面试官已完成所有提问，点击下方按钮生成评估报告。</p>
        <div class="end-actions">
          <button class="btn btn-primary btn-lg" :disabled="evalLoading" @click="generateEvaluation">
            {{ evalLoading ? '正在生成报告...' : '生成评估报告 →' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, watch, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { marked } from 'marked'
import { useInterviewStore } from '../stores/interview'
import { useResumeStore } from '../stores/resume'
import { useResultsStore } from '../stores/results'
import { useSpeechRecognition } from '../composables/useSpeechRecognition'
import { useTextToSpeech } from '../composables/useTextToSpeech'
import ChatBubble from '../components/ChatBubble.vue'
import TypingIndicator from '../components/TypingIndicator.vue'
import ProgressBar from '../components/ProgressBar.vue'

const router = useRouter()
const interviewStore = useInterviewStore()
const resumeStore = useResumeStore()
const resultsStore = useResultsStore()

// ── Voice features ──────────────────────────────────────────────────────────
const voiceMode = ref(false)
const isReplaying = ref(-1)

const stt = useSpeechRecognition({
  lang: interviewStore.config.style === 'english' ? 'en-US' : 'zh-CN',
  continuous: true,
  interimResults: true,
})

const tts = useTextToSpeech({ rate: 1.0, pitch: 1.0 })

function toggleVoiceMode() {
  voiceMode.value = !voiceMode.value
  if (!voiceMode.value) {
    tts.stop()
    stt.stop()
  }
}

function toggleMic() {
  if (stt.isListening.value) {
    stt.stop()
    // Append recognized text to input
    if (stt.transcript.value) {
      userInput.value += (userInput.value ? ' ' : '') + stt.transcript.value
    }
    stt.reset()
  } else {
    // Stop any TTS before starting mic to avoid feedback
    tts.stop()
    stt.start()
  }
}

function replayMessage(msg, index) {
  if (isReplaying.value === index) {
    tts.stop()
    isReplaying.value = -1
    return
  }

  isReplaying.value = index
  const lang = interviewStore.config.style === 'english' ? 'en' : 'zh'
  tts.speak(msg.content, { lang })

  // Watch for speech end
  const checkSpeechEnd = setInterval(() => {
    if (!tts.isSpeaking.value) {
      isReplaying.value = -1
      clearInterval(checkSpeechEnd)
    }
  }, 200)
}

// Auto-TTS when voice mode is on and a new interviewer message completes
let lastMessageCount = 0
watch(
  () => interviewStore.messages.length,
  (newCount) => {
    if (voiceMode.value && newCount > lastMessageCount) {
      const lastMsg = interviewStore.messages[newCount - 1]
      if (lastMsg.role === 'interviewer') {
        nextTick(() => {
          const lang = interviewStore.config.style === 'english' ? 'en' : 'zh'
          tts.speak(lastMsg.content, { lang })
        })
      }
    }
    lastMessageCount = newCount
  }
)

// ── Core interview logic ─────────────────────────────────────────────────────
const userInput = ref('')
const evalLoading = ref(false)
const chatArea = ref(null)
const inputBox = ref(null)

const styleLabels = { gentle: '温和引导型', strict: '严厉施压型', english: '全英文' }
const styleLabel = computed(() => styleLabels[interviewStore.config.style] || '')

const canSend = computed(() => {
  return userInput.value.trim().length > 0 && !interviewStore.isStreaming
})

const renderedStreaming = computed(() => {
  if (!interviewStore.currentStreamingText) return ''
  return marked(interviewStore.currentStreamingText) + '<span class="cursor-blink">|</span>'
})

const renderedStandardAnswer = computed(() => {
  if (!interviewStore.standardAnswer) return ''
  return marked(interviewStore.standardAnswer)
})

function handleStandardAnswer() {
  if (interviewStore.showStandardAnswer) {
    interviewStore.showStandardAnswer = false
  } else {
    interviewStore.requestStandardAnswer()
  }
}

async function handleSkipQuestion() {
  try {
    tts.stop()
    stt.stop()
    stt.reset()
    userInput.value = ''
    interviewStore.showStandardAnswer = false
    await interviewStore.skipQuestion()
    nextTick(() => {
      inputBox.value?.focus()
    })
  } catch (e) {
    alert('跳过题目失败：' + e.message)
  }
}

// Auto-scroll
watch(
  () => [interviewStore.messages.length, interviewStore.currentStreamingText],
  () => {
    nextTick(() => {
      if (chatArea.value) {
        chatArea.value.scrollTop = chatArea.value.scrollHeight
      }
    })
  },
  { deep: true }
)

// Auto-TTS for streaming completion in voice mode
let streamEnded = false
watch(
  () => interviewStore.isStreaming,
  (streaming) => {
    if (!streaming && !streamEnded && voiceMode.value) {
      // Stream just finished — speak the latest interviewer message
      const lastMsg = interviewStore.messages[interviewStore.messages.length - 1]
      if (lastMsg && lastMsg.role === 'interviewer') {
        nextTick(() => {
          const lang = interviewStore.config.style === 'english' ? 'en' : 'zh'
          tts.speak(lastMsg.content, { lang })
        })
      }
    }
    streamEnded = !streaming
  }
)

function handleEnter(e) {
  e.preventDefault()
  if (canSend.value) sendAnswer()
}

function handleShiftEnter() {
  // Default: insert newline
}

async function sendAnswer() {
  const answer = userInput.value.trim()
  if (!answer) return

  // Stop any ongoing speech and recognition
  tts.stop()
  stt.stop()
  stt.reset()

  userInput.value = ''
  try {
    await interviewStore.submitAnswer(answer)
    nextTick(() => {
      inputBox.value?.focus()
    })
  } catch (e) {
    alert('提交回答失败：' + e.message)
  }
}

async function generateEvaluation() {
  evalLoading.value = true
  try {
    await resultsStore.generate(
      interviewStore.sessionId,
      resumeStore.data,
      interviewStore.config,
      interviewStore.messages,
    )
    router.push('/results')
  } catch (e) {
    alert('生成报告失败：' + e.message)
  } finally {
    evalLoading.value = false
  }
}

// Cleanup on unmount
onUnmounted(() => {
  tts.stop()
  stt.stop()
})
</script>

<style scoped>
.interview-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
}

/* Header */
.interview-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 20px;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.interviewer-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--color-primary-light);
  color: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 16px;
}
.header-info strong { display: block; font-size: 15px; }
.header-position { font-size: 13px; color: var(--text-secondary); }
.header-right { flex: 1; max-width: 200px; }
.header-actions { flex-shrink: 0; }

/* Voice toggle button */
.voice-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border: 1.5px solid var(--border-color);
  border-radius: 20px;
  background: var(--bg-card);
  cursor: pointer;
  font-size: 13px;
  color: var(--text-secondary);
  transition: all 0.2s;
}
.voice-toggle:hover {
  border-color: var(--color-primary);
}
.voice-toggle.active {
  border-color: var(--color-primary);
  background: var(--color-primary-light);
  color: var(--color-primary);
  font-weight: 500;
}

/* Voice banner */
.voice-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 20px;
  background: var(--color-primary-light);
  color: var(--color-primary);
  font-size: 13px;
  flex-shrink: 0;
}
.stop-speech-btn {
  margin-left: auto;
  background: var(--color-primary);
  color: #fff;
  border: none;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  cursor: pointer;
}

/* Message wrapper with replay */
.message-wrapper {
  position: relative;
  max-width: 800px;
  margin: 0 auto;
}
.replay-btn {
  position: absolute;
  top: 0;
  right: -36px;
  width: 28px;
  height: 28px;
  border: 1px solid var(--border-color);
  border-radius: 50%;
  background: var(--bg-card);
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  opacity: 0;
}
.message-wrapper:hover .replay-btn {
  opacity: 1;
}
.replay-btn:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}
.replay-btn.speaking {
  opacity: 1;
  border-color: var(--color-primary);
  color: var(--color-primary);
  animation: pulse-ring 1.5s infinite;
}

/* Chat Area */
.chat-area {
  flex: 1;
  overflow-y: auto;
  padding: 24px 60px;
}

/* Streaming bubble */
.chat-bubble {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  max-width: 85%;
}
.bubble-avatar { flex-shrink: 0; }
.avatar-circle {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
}
.avatar-circle.interviewer {
  background: var(--color-primary-light);
  color: var(--color-primary);
}
.bubble-content { flex: 1; min-width: 0; }
.bubble-label {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 4px;
}
.bubble-text {
  padding: 12px 16px;
  border-radius: 12px;
  border-top-left-radius: 4px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  font-size: 15px;
  line-height: 1.7;
}
.streaming-text :deep(.cursor-blink) {
  animation: blink 1s infinite;
  color: var(--color-primary);
  font-weight: 700;
}
@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}
.bubble-text :deep(p) { margin: 0 0 8px; }
.bubble-text :deep(p:last-child) { margin-bottom: 0; }
.bubble-text :deep(pre) {
  background: #1e293b; color: #e2e8f0;
  padding: 14px; border-radius: 8px;
  overflow-x: auto; margin: 8px 0; font-size: 13px;
}
.bubble-text :deep(code) {
  font-family: 'Fira Code', 'Consolas', monospace; font-size: 13px;
}
.bubble-text :deep(:not(pre) > code) {
  background: rgba(0,0,0,0.06); padding: 2px 6px; border-radius: 4px;
}

/* Standard Answer Panel */
.standard-answer-panel {
  flex-shrink: 0;
  max-height: 40vh;
  background: var(--bg-card);
  border-top: 2px solid #f59e0b;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 20px;
  background: #fffbeb;
  border-bottom: 1px solid #fde68a;
}
.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #92400e;
}
.panel-close {
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: #92400e;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}
.panel-close:hover { background: #fde68a; }
.panel-body {
  flex: 1;
  overflow-y: auto;
  padding: 14px 20px;
}
.panel-loading {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #92400e;
  font-size: 14px;
}
.panel-content {
  font-size: 14px;
  line-height: 1.7;
  color: var(--text-primary);
}
.panel-content :deep(p) { margin: 0 0 10px; }
.panel-content :deep(p:last-child) { margin-bottom: 0; }
.panel-content :deep(pre) {
  background: #1e293b; color: #e2e8f0;
  padding: 12px; border-radius: 8px;
  overflow-x: auto; margin: 8px 0; font-size: 13px;
}
.panel-content :deep(code) {
  font-family: 'Fira Code', 'Consolas', monospace; font-size: 13px;
}
.panel-content :deep(:not(pre) > code) {
  background: rgba(245, 158, 11, 0.1); padding: 2px 6px; border-radius: 4px; color: #92400e;
}
.panel-content :deep(strong) { color: #92400e; }

/* Action Toolbar */
.action-toolbar {
  max-width: 800px;
  margin: 0 auto 8px;
  display: flex;
  gap: 8px;
}
.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border: 1px solid var(--border-color);
  border-radius: 18px;
  background: var(--bg-primary);
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}
.action-btn:hover:not(:disabled) {
  border-color: var(--color-primary);
  color: var(--color-primary);
  background: var(--color-primary-light);
}
.action-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.skip-btn:hover:not(:disabled) {
  border-color: #f59e0b;
  color: #92400e;
  background: #fffbeb;
}

/* Input Area */
.input-area {
  flex-shrink: 0;
  padding: 12px 20px 16px;
  background: var(--bg-card);
  border-top: 1px solid var(--border-color);
}
.input-wrapper {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  gap: 10px;
  align-items: flex-end;
}

/* Microphone button */
.mic-btn {
  width: 44px;
  height: 44px;
  border: 2px solid var(--border-color);
  border-radius: 50%;
  background: var(--bg-card);
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  position: relative;
  transition: all 0.2s;
}
.mic-btn:hover:not(:disabled) {
  border-color: var(--color-danger);
  color: var(--color-danger);
}
.mic-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.mic-btn.listening {
  border-color: var(--color-danger);
  color: var(--color-danger);
  background: #fef2f2;
}
.mic-pulse {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 2px solid var(--color-danger);
  animation: pulse-ring 1.5s infinite;
}
@keyframes pulse-ring {
  0% { transform: scale(1); opacity: 1; }
  100% { transform: scale(1.5); opacity: 0; }
}

/* Text input area */
.text-input-area {
  flex: 1;
  position: relative;
}
.chat-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  font-size: 15px;
  font-family: inherit;
  resize: none;
  outline: none;
  background: var(--bg-primary);
  color: var(--text-primary);
  line-height: 1.5;
  transition: border-color 0.2s;
}
.chat-input:focus {
  border-color: var(--color-primary);
}
.chat-input:disabled { opacity: 0.6; }

/* Interim speech recognition text */
.interim-text {
  position: absolute;
  bottom: 100%;
  left: 0;
  right: 0;
  padding: 8px 12px;
  background: #fefce8;
  border: 1px solid #fde68a;
  border-radius: 8px;
  font-size: 14px;
  color: var(--text-primary);
  margin-bottom: 6px;
  max-height: 80px;
  overflow-y: auto;
}
.interim-highlight {
  color: var(--color-primary);
  font-style: italic;
}

/* Send button */
.send-btn {
  width: 44px;
  height: 44px;
  border: none;
  border-radius: 12px;
  background: var(--color-primary);
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.2s;
}
.send-btn:hover:not(:disabled) {
  background: var(--color-primary-hover);
}
.send-btn:disabled { opacity: 0.4; cursor: not-allowed; }

.speech-error {
  text-align: center;
  font-size: 12px;
  color: var(--color-danger);
  margin-top: 4px;
}
.input-hint {
  text-align: center;
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 6px;
}

/* End Area */
.end-area {
  flex-shrink: 0;
  padding: 16px 20px;
  background: var(--bg-card);
  border-top: 1px solid var(--border-color);
}
.end-card {
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
}
.end-card h3 { font-size: 18px; margin-bottom: 8px; }
.end-card p { color: var(--text-secondary); margin-bottom: 16px; }
.end-actions { display: flex; justify-content: center; }

@media (max-width: 768px) {
  .chat-area { padding: 16px 20px; }
  .replay-btn { right: -4px; top: -4px; opacity: 1; }
  .voice-toggle-label { display: none; }
}
</style>
