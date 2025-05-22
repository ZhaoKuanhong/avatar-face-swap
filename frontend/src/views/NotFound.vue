<template>
  <div class="not-found-container">
    <div class="error-content">
      <h1 class="error-code">404</h1>
      <div class="band-character">
        <img src="@/assets/img/anon-404.gif" alt="Kasumi surprised" class="character-image">
      </div>
      <h2 class="error-message">Oops! Mygo了吗？</h2>
      <p class="error-description">
        像找不到正确的音符一样，这个页面似乎不存在...
      </p>
      <div class="action-buttons">
        <el-button type="danger" class="back-button" @click="goHome">
          <i class="el-icon-arrow-left"></i> 回到主页
        </el-button>
      </div>
    </div>
    <div class="music-notes">
      <span class="note note-1">♪</span>
      <span class="note note-2">♫</span>
      <span class="note note-3">♬</span>
      <span class="note note-4">♩</span>
      <span class="note note-5">♪</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotFound',
  methods: {
    goHome() {
      this.$router.push('/event');
    }
  }
}
</script>

<style scoped>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  overflow-x: hidden;
}

#app {
  height: 100%;
  width: 100%;
}

.not-found-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  width: 100vw;
  background: linear-gradient(135deg, #66AADD 0%, #3388BB 50%, #226699 100%);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  overflow: hidden;
  position: relative;
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.error-content {
  text-align: center;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(5px);
  max-width: 500px;
  width: 90%;
  z-index: 10;
  animation: fadeIn 0.8s ease-out;
}

.error-code {
  font-size: 8rem;
  margin: 0;
  background: linear-gradient(to right, #22c0ff, #3388BB);
  -webkit-background-clip: text;
  color: transparent;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
}

.band-character {
  margin: 1rem 0;
}

.character-image {
  max-width: 200px;
  animation: bounce 2s ease infinite;
}

.error-message {
  font-size: 2rem;
  color: #3388BB;
  margin-top: 1rem;
}

.error-description {
  color: #5d4037;
  margin-bottom: 2rem;
}

.action-buttons {
  margin-top: 1.5rem;
}

.back-button {
  font-size: 1.1rem;
  padding: 12px 24px;
  background: linear-gradient(45deg, #22c0ff, #3388BB) !important;
  border: none !important;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.back-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 7px 14px rgba(0, 0, 0, 0.2);
}

.music-notes {
  position: absolute;
  width: 100%;
  height: 100%;
  z-index: 1;
}

.note {
  position: absolute;
  color: rgba(255, 255, 255, 0.7);
  font-size: 2rem;
  animation: float 6s ease-in-out infinite;
}

.note-1 {
  top: 20%;
  left: 10%;
  animation-delay: 0s;
  font-size: 3rem;
}

.note-2 {
  top: 30%;
  right: 15%;
  animation-delay: 1s;
  font-size: 2.5rem;
}

.note-3 {
  bottom: 30%;
  left: 20%;
  animation-delay: 2s;
  font-size: 4rem;
}

.note-4 {
  bottom: 20%;
  right: 10%;
  animation-delay: 3s;
  font-size: 3.5rem;
}

.note-5 {
  top: 50%;
  left: 50%;
  animation-delay: 4s;
  font-size: 3rem;
}

@keyframes float {
  0% {
    transform: translateY(0) rotate(0deg);
    opacity: 0.7;
  }
  50% {
    transform: translateY(-20px) rotate(10deg);
    opacity: 1;
  }
  100% {
    transform: translateY(0) rotate(0deg);
    opacity: 0.7;
  }
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-15px);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .error-code {
    font-size: 6rem;
  }

  .error-message {
    font-size: 1.5rem;
  }

  .character-image {
    max-width: 150px;
  }
}

/* dark mode */
@media (prefers-color-scheme: dark) {
  .not-found-container {
    background: linear-gradient(135deg, #4a148c 0%, #7b1fa2 50%, #512da8 100%);
  }

  .error-content {
    background: rgba(30, 30, 30, 0.8);
  }

  .error-message {
    color: #ec407a;
  }

  .error-description {
    color: #e0e0e0;
  }

  .note {
    color: rgba(255, 255, 255, 0.5);
  }
}
</style>