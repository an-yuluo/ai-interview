import { ref, onUnmounted } from 'vue'

/**
 * Browser SpeechSynthesis API — Text to Speech (TTS)
 * Reads interviewer messages aloud for immersive experience.
 */
export function useTextToSpeech(options = {}) {
  const { rate = 1.0, pitch = 1.0, volume = 1.0 } = options

  const isSpeaking = ref(false)
  const isSupported = ref(false)
  const currentVoice = ref(null)
  const availableVoices = ref([])

  let synth = null
  let utterance = null

  if ('speechSynthesis' in window) {
    isSupported.value = true
    synth = window.speechSynthesis

    // Load voices (they load async in some browsers)
    const loadVoices = () => {
      const voices = synth.getVoices()
      availableVoices.value = voices.map(v => ({
        name: v.name,
        lang: v.lang,
        voice: v,
      }))

      // Pick a good default Chinese voice
      const zhVoice = voices.find(v => v.lang.startsWith('zh') && v.localService)
        || voices.find(v => v.lang.startsWith('zh'))
        || voices.find(v => v.lang.startsWith('en'))
      if (zhVoice) {
        currentVoice.value = zhVoice
      }
    }

    loadVoices()
    if (synth.onvoiceschanged !== undefined) {
      synth.onvoiceschanged = loadVoices
    }
  }

  /**
   * Strip markdown syntax for cleaner speech output.
   */
  function stripMarkdown(text) {
    return text
      .replace(/```[\s\S]*?```/g, '（代码片段）')  // code blocks
      .replace(/`([^`]+)`/g, '$1')                  // inline code
      .replace(/!\[.*?\]\(.*?\)/g, '')               // images
      .replace(/\[([^\]]+)\]\(.*?\)/g, '$1')         // links → keep text
      .replace(/#{1,6}\s/g, '')                      // headings
      .replace(/\*\*([^*]+)\*\*/g, '$1')             // bold
      .replace(/\*([^*]+)\*/g, '$1')                 // italic
      .replace(/~~([^~]+)~~/g, '$1')                 // strikethrough
      .replace(/>\s/g, '')                           // blockquotes
      .replace(/[-*+]\s/g, '')                       // list markers
      .replace(/\d+\.\s/g, '')                       // numbered lists
      .replace(/\n{2,}/g, '。')                      // double newlines → period
      .replace(/\n/g, '，')                          // single newline → comma
      .replace(/\s{2,}/g, ' ')                       // collapse spaces
      .trim()
  }

  function speak(text, opts = {}) {
    if (!synth) return

    stop()  // cancel any ongoing speech

    const cleanText = stripMarkdown(text)
    if (!cleanText) return

    utterance = new SpeechSynthesisUtterance(cleanText)
    utterance.rate = opts.rate || rate
    utterance.pitch = opts.pitch || pitch
    utterance.volume = opts.volume || volume

    // Pick voice based on language
    if (opts.lang === 'en' || opts.lang === 'en-US') {
      const enVoice = availableVoices.value.find(v => v.lang.startsWith('en'))
      if (enVoice) utterance.voice = enVoice.voice
      utterance.lang = 'en-US'
    } else {
      if (currentVoice.value) utterance.voice = currentVoice.value
      utterance.lang = currentVoice.value?.lang || 'zh-CN'
    }

    utterance.onstart = () => { isSpeaking.value = true }
    utterance.onend = () => { isSpeaking.value = false }
    utterance.onerror = () => { isSpeaking.value = false }

    synth.speak(utterance)
  }

  function stop() {
    if (synth) {
      synth.cancel()
      isSpeaking.value = false
    }
  }

  function pause() {
    if (synth && synth.speaking) {
      synth.pause()
    }
  }

  function resume() {
    if (synth && synth.paused) {
      synth.resume()
    }
  }

  function setVoice(voice) {
    currentVoice.value = voice
  }

  onUnmounted(() => {
    stop()
  })

  return {
    isSpeaking,
    isSupported,
    availableVoices,
    currentVoice,
    speak,
    stop,
    pause,
    resume,
    setVoice,
    stripMarkdown,
  }
}
