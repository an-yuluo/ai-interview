import { ref, computed } from 'vue'

/**
 * Browser Web Speech API — Speech Recognition (STT)
 * Works in Chrome, Edge. Requires HTTPS in production.
 */
export function useSpeechRecognition(options = {}) {
  const { lang = 'zh-CN', continuous = true, interimResults = true } = options

  const isListening = ref(false)
  const transcript = ref('')           // final accumulated text
  const interimTranscript = ref('')    // in-progress partial text
  const error = ref('')
  const isSupported = ref(false)

  let recognition = null

  // Detect browser support
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
  if (SpeechRecognition) {
    isSupported.value = true
    recognition = new SpeechRecognition()
    recognition.lang = lang
    recognition.continuous = continuous
    recognition.interimResults = interimResults
    recognition.maxAlternatives = 1

    recognition.onresult = (event) => {
      let finalText = ''
      let interim = ''

      for (let i = 0; i < event.results.length; i++) {
        const result = event.results[i]
        if (result.isFinal) {
          finalText += result[0].transcript
        } else {
          interim += result[0].transcript
        }
      }

      transcript.value = finalText
      interimTranscript.value = interim
    }

    recognition.onerror = (event) => {
      const errMessages = {
        'no-speech': '没有检测到语音，请再试一次',
        'audio-capture': '未检测到麦克风，请检查设备',
        'not-allowed': '麦克风权限被拒绝，请在浏览器设置中允许',
        'network': '语音识别网络错误',
        'aborted': '语音识别已中止',
      }
      error.value = errMessages[event.error] || `识别错误: ${event.error}`
      isListening.value = false
    }

    recognition.onend = () => {
      isListening.value = false
    }
  }

  const displayText = computed(() => {
    return transcript.value + interimTranscript.value
  })

  function start() {
    if (!recognition) {
      error.value = '当前浏览器不支持语音识别，请使用 Chrome 或 Edge 浏览器'
      return
    }
    error.value = ''
    transcript.value = ''
    interimTranscript.value = ''
    try {
      recognition.start()
      isListening.value = true
    } catch (e) {
      // Already started
      recognition.stop()
      setTimeout(() => {
        recognition.start()
        isListening.value = true
      }, 100)
    }
  }

  function stop() {
    if (recognition) {
      recognition.stop()
      isListening.value = false
    }
  }

  function toggle() {
    if (isListening.value) {
      stop()
    } else {
      start()
    }
  }

  function reset() {
    stop()
    transcript.value = ''
    interimTranscript.value = ''
    error.value = ''
  }

  return {
    isListening,
    transcript,
    interimTranscript,
    displayText,
    error,
    isSupported,
    start,
    stop,
    toggle,
    reset,
  }
}
