<template>
  <div class="chat-bubble interviewer">
    <div class="bubble-avatar">
      <div class="avatar-circle interviewer">面</div>
    </div>
    <div class="bubble-content">
      <div class="bubble-label">面试官</div>
      <div class="bubble-text typing">
        <span class="typing-dots">
          <span class="dot"></span>
          <span class="dot"></span>
          <span class="dot"></span>
        </span>
        <span class="typing-label">正在思考...</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-bubble {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  max-width: 85%;
}
.avatar-circle {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  flex-shrink: 0;
}
.avatar-circle.interviewer {
  background: var(--color-primary-light);
  color: var(--color-primary);
}
.bubble-content { flex: 1; }
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
}
.typing {
  display: flex;
  align-items: center;
  gap: 10px;
}
.typing-dots {
  display: flex;
  gap: 4px;
}
.dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--color-primary);
  animation: bounce 1.2s infinite;
}
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }
.typing-label {
  font-size: 13px;
  color: var(--text-muted);
}
@keyframes bounce {
  0%, 80%, 100% { opacity: 0.3; transform: translateY(0); }
  40% { opacity: 1; transform: translateY(-4px); }
}
</style>
