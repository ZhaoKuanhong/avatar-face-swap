<template>
  <body>
  <div class="container">
    <div class="login-card">
      <div class="avatar-container">
        <img src="../assets/img/fc-logo.png" alt="GDUT BanGDream Fan Club" class="avatar-logo">
      </div>
      <h2>团建大头覆盖</h2>
      <div class="input-container">
        <label for="password">活动口令</label>
        <div class="password-field">
          <input type="password" v-model="token" placeholder="请输入活动专属口令">
          <div class="password-icon">
            <i class="fas fa-lock"></i>
          </div>
        </div>
      </div>
      <div class="button-container">
        <button @click="verifyToken" :disabled="loading || !token" class="verify-btn" :class="{'loading': loading}">
          <span v-if="!loading">进入活动</span>
          <span v-else class="loading-indicator">
                            <span class="dot"></span>
                            <span class="dot"></span>
                            <span class="dot"></span>
                        </span>
        </button>
      </div>
      <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
    </div>
    <div class="music-notes">
      <span class="note note-1">♪</span>
      <span class="note note-2">♫</span>
      <span class="note note-3">♬</span>
    </div>
    <div class="about-link">
      <button @click="goToAbout" class="about-btn">
        <InfoFilled />
        关于我们
      </button>
    </div>
    <footer class="footer">
      Copyright (C) 2025 Faspand & Mio for GDUT BanGDream Fan Club
    </footer>
  </div>
  </body>
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router';
import { apiClient } from "@/api/axios.js";
import { ref, onMounted } from 'vue';

const router = useRouter();
const route = useRoute();

const token = ref('');
const loading = ref(false);
const errorMessage = ref('');

const goToAbout = () => {
      router.push('/about');
};

const verifyToken = async () => {
  if (!token.value) return;

  errorMessage.value = '';
  loading.value = true;

  try {
    const response = await apiClient.post('/verify', { token: token.value });
    if (response.data.token) {
      localStorage.setItem('token', response.data.token);
    }
    if (response.data.description) {
      localStorage.setItem('description', response.data.description);
    }
    await router.push(`/event/${response.data.event_id}`);
  } catch (error) {
    errorMessage.value = error.response?.data?.error || '验证失败，请重试';
  } finally {
    loading.value = false;
  }
};

// 页面加载时检查 URL 是否带有 auth_token 参数
onMounted(() => {
  const authToken = route.query.auth_token;
  if (authToken) {
    token.value = authToken;
    verifyToken();
  }
});
</script>


<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  width: 100vw;
  background: url("@/assets/img/bg.jpg") no-repeat center center;
  background-size: cover;
  position: relative;
}

.container {
  width: 100%;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
}

.login-card {
  backdrop-filter: blur(10px);
  background: rgba(255, 51, 119, 0.15);
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 30px;
  width: 350px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 10px 25px rgba(255, 51, 119, 0.15);
  transition: all 0.3s ease;
  animation: fadeIn 0.8s ease-out;
  position: relative;
  z-index: 10; /* 确保卡片在音符上方 */
}

.login-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 30px rgba(255, 51, 119, 0.25);
}

.avatar-container {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
  box-shadow: 0 5px 15px rgba(255, 51, 119, 0.2);
}

.avatar-logo {
  width: 80px;
  height: 80px;
  object-fit: contain;
}

.login-card > h2 {
  color: white;
  margin-bottom: 24px;
  font-size: 28px;
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.input-container {
  width: 100%;
  margin-bottom: 20px;
  position: relative; /* 确保相对定位 */
  z-index: 11; /* 确保在前景 */
}

.input-container > label {
  display: block;
  color: white;
  margin-bottom: 8px;
  font-size: 16px;
  font-weight: 500;
}

.password-field {
  position: relative;
  width: 100%;
}

.password-field input {
  width: 100%;
  height: 50px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  padding: 0 50px 0 16px;
  color: white;
  font-size: 16px;
  transition: all 0.3s;
  position: relative; /* 确保相对定位 */
  z-index: 12; /* 提高 z-index 确保可点击 */
}

.password-field input::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

.password-field input:focus {
  outline: none;
  border-color: rgba(255, 221, 238, 0.8);
  background: rgba(255, 255, 255, 0.2);
}

.password-icon {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: rgba(255, 255, 255, 0.6);
  z-index: 12; /* 匹配输入框 */
}

.button-container {
  width: 100%;
  margin-top: 16px;
  position: relative; /* 确保相对定位 */
  z-index: 11; /* 确保在前景 */
}

.verify-btn {
  width: 100%;
  height: 50px;
  background: #FF3377;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative; /* 确保相对定位 */
  z-index: 12; /* 提高 z-index 确保可点击 */
}

.verify-btn:hover:not(:disabled) {
  background: #FF1166;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(255, 51, 119, 0.4);
}

.verify-btn:disabled {
  background: rgba(255, 51, 119, 0.5);
  cursor: not-allowed;
}

.loading-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
}

.dot {
  width: 8px;
  height: 8px;
  background: white;
  border-radius: 50%;
  margin: 0 4px;
  animation: bounce 1.4s infinite ease-in-out both;
}

.dot:nth-child(1) {
  animation-delay: -0.32s;
}

.dot:nth-child(2) {
  animation-delay: -0.16s;
}

.error-message {
  margin-top: 16px;
  color: #ffffff;
  font-size: 14px;
  text-align: center;
  padding: 8px 12px;
  background: rgba(255, 71, 87, 0.5);
  border-radius: 4px;
  width: 100%;
  animation: shake 0.5s;
  z-index: 11;
}

.music-notes {
  position: absolute;
  width: 100%;
  height: 100%;
  z-index: 1;
  pointer-events: none;
}

.note {
  position: absolute;
  color: rgba(255, 221, 238, 0.5);
  font-size: 3rem;
  animation: float 6s ease-in-out infinite;
  pointer-events: none;
}

.note-1 {
  top: 20%;
  left: 10%;
  animation-delay: 0s;
  font-size: 4rem;
}

.note-2 {
  top: 30%;
  right: 15%;
  animation-delay: 1s;
  font-size: 3.5rem;
}

.note-3 {
  bottom: 25%;
  left: 20%;
  animation-delay: 2s;
  font-size: 4.5rem;
}

.footer {
  position: absolute;
  bottom: 20px;
  font-size: 14px;
  text-align: center;
  z-index: 10;
}

.about-link {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 15;
}

.about-btn {
  background: linear-gradient(45deg, rgba(255, 51, 119, 0.8), rgba(255, 102, 153, 0.8));
  border: 1px solid rgba(255, 51, 119, 0.6);
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(255, 51, 119, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 6px;
  line-height: 1;
}

.about-btn svg {
  width: 14px;
  height: 14px;
  vertical-align: middle;
  flex-shrink: 0;
}

.about-btn:hover {
  background: linear-gradient(45deg, #FF3377, #ff6699);
  border-color: #FF3377;
  box-shadow: 0 6px 20px rgba(255, 51, 119, 0.4);
  transform: translateY(-3px);
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
    opacity: 0.5;
  }
  50% {
    transform: translateY(-20px) rotate(10deg);
    opacity: 0.7;
  }
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
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

@keyframes shake {
  0%, 100% {
    transform: translateX(0);
  }
  10%, 30%, 50%, 70%, 90% {
    transform: translateX(-5px);
  }
  20%, 40%, 60%, 80% {
    transform: translateX(5px);
  }
}

@media (max-width: 480px) {
  .login-card {
    width: 90%;
    max-width: 350px;
    padding: 30px 20px;
  }

  .avatar-container {
    width: 80px;
    height: 80px;
  }

  .avatar-logo {
    width: 60px;
    height: 60px;
  }
}

/* dark mode */
@media (prefers-color-scheme: dark) {
  .login-card {
    background: rgba(80, 20, 40, 0.7);
  }

  .verify-btn {
    background: #FF4488;
  }

  .verify-btn:hover:not(:disabled) {
    background: #FF3377;
  }
}
</style>
