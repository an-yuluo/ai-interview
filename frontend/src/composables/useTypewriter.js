import { ref, watch } from 'vue'

/**
 * Simple typewriter effect: watches a source string and reveals it character by character.
 */
export function useTypewriter(source, { speed = 20 } = {}) {
  const displayed = ref('')
  const isTyping = ref(false)
  let timer = null

  function stop() {
    if (timer) {
      clearInterval(timer)
      timer = null
    }
    isTyping.value = false
  }

  watch(source, (newVal) => {
    if (!newVal) {
      displayed.value = ''
      stop()
      return
    }

    // If new text is longer, continue from current position
    displayed.value = newVal
  }, { immediate: true })

  return { displayed, isTyping, stop }
}
