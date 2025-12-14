<template>
  <body>
  <div class="bg-layer"></div>
  <div class="gradient-overlay"></div>
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
      <div class="admin-login-link">
        <a href="#" @click.prevent="adminLogin">管理员登录</a>
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
      Copyright (C) 2025 Faspand & Mio for 広東工業大学アイドル研究部
    </footer>
  </div>
  </body>
</template>

<script setup>
import { apiClient } from "@/api/axios.js";
import { onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const router = useRouter();
const route = useRoute();

const token = ref('');
const loading = ref(false);
const errorMessage = ref('');

const goToAbout = () => {
      router.push('/about');
};

const adminLogin = () => {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5001';
  window.location.href = `${baseUrl}/api/login`;
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
  position: relative;
  overflow: hidden;
}

.bg-layer {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: url("@/assets/img/bg.jpg") no-repeat center center;
  background-size: cover;
  filter: brightness(0.98);
  z-index: 0;
}

.gradient-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    135deg,
    rgba(202, 169, 168, 0.15) 0%,
    rgba(131, 198, 233, 0.15) 20%,
    rgba(244, 192, 137, 0.15) 40%,
    rgba(238, 169, 150, 0.15) 60%,
    rgba(233, 174, 178, 0.15) 80%,
    rgba(234, 149, 152, 0.15) 100%
  );
  z-index: 0;
}

.container {
  width: 100%;
  min-height: 100vh;
  min-height: 100dvh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 1;
  padding: 1rem;
}

.login-card {
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  background: rgba(196, 30, 58, 0.25);
  border-radius: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2.5rem 2rem;
  width: 100%;
  max-width: 380px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 10px 25px rgba(196, 30, 58, 0.15);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  animation: fadeIn 0.8s ease-out;
  position: relative;
  z-index: 10;
}

@media (hover: hover) {
  .login-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 30px rgba(196, 30, 58, 0.25);
  }
}

.avatar-container {
  width: 88px;
  height: 88px;
  border-radius: 50%;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.25rem;
  box-shadow: 0 5px 15px rgba(196, 30, 58, 0.2);
  flex-shrink: 0;
}

.avatar-logo {
  width: 68px;
  height: 68px;
  object-fit: contain;
}

.login-card > h2 {
  color: white;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.input-container {
  width: 100%;
  margin-bottom: 1.25rem;
  position: relative;
  z-index: 11;
}

.input-container > label {
  display: block;
  color: white;
  margin-bottom: 0.5rem;
  font-size: 0.9375rem;
  font-weight: 500;
}

.password-field {
  position: relative;
  width: 100%;
}

.password-field input {
  width: 100%;
  height: 52px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 10px;
  padding: 0 48px 0 16px;
  color: white;
  font-size: 16px;
  transition: all 0.3s;
  position: relative;
  z-index: 12;
  -webkit-appearance: none;
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
  z-index: 12;
  pointer-events: none;
}

.button-container {
  width: 100%;
  margin-top: 1rem;
  position: relative;
  z-index: 11;
}

.verify-btn {
  width: 100%;
  height: 52px;
  background: linear-gradient(90deg, #C41E3A 0%, #E63462 50%, #C41E3A 100%);
  background-size: 200% 100%;
  background-position: 0% 0%;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.4s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 12;
  -webkit-tap-highlight-color: transparent;
}

@media (hover: hover) {
  .verify-btn:hover:not(:disabled) {
    background: linear-gradient(
      90deg,
      #caa9a8 0%,
      #83c6e9 16.67%,
      #f4c089 33.33%,
      #eea996 50%,
      #e9aeb2 66.67%,
      #ea9598 83.33%,
      #caa9a8 100%
    );
    background-size: 200% 100%;
    animation: gradient-shift 3s ease infinite;
    transform: translateY(-2px);
    box-shadow: 0 5px 20px rgba(196, 30, 58, 0.4);
  }
}

.verify-btn:active:not(:disabled) {
  transform: translateY(0px);
  box-shadow: 0 2px 10px rgba(196, 30, 58, 0.6);
}

.verify-btn:disabled {
  background: rgba(196, 30, 58, 0.5);
  cursor: not-allowed;
}

@keyframes gradient-shift {
  0% { background-position: 0% 0%; }
  50% { background-position: 100% 0%; }
  100% { background-position: 0% 0%; }
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

.dot:nth-child(1) { animation-delay: -0.32s; }
.dot:nth-child(2) { animation-delay: -0.16s; }

.error-message {
  margin-top: 1rem;
  color: #ffffff;
  font-size: 0.875rem;
  text-align: center;
  padding: 0.625rem 0.875rem;
  background: rgba(255, 71, 87, 0.5);
  border-radius: 8px;
  width: 100%;
  animation: shake 0.5s;
  z-index: 11;
}

.admin-login-link {
  margin-top: 1rem;
  text-align: center;
}

.admin-login-link a {
  color: rgba(255, 255, 255, 0.85);
  font-size: 0.875rem;
  text-decoration: none;
  transition: color 0.3s ease;
  padding: 0.5rem;
  display: inline-block;
}

.admin-login-link a:hover {
  color: #ffffff;
  text-decoration: underline;
}

.music-notes {
  position: absolute;
  width: 100%;
  height: 100%;
  z-index: 1;
  pointer-events: none;
  overflow: hidden;
}

.note {
  position: absolute;
  color: rgba(255, 221, 238, 0.5);
  font-size: 3rem;
  animation: float 6s ease-in-out infinite;
  pointer-events: none;
}

.note-1 { top: 20%; left: 10%; animation-delay: 0s; font-size: 4rem; }
.note-2 { top: 30%; right: 15%; animation-delay: 1s; font-size: 3.5rem; }
.note-3 { bottom: 25%; left: 20%; animation-delay: 2s; font-size: 4.5rem; }

.footer {
  position: absolute;
  bottom: 1rem;
  left: 0;
  right: 0;
  font-size: 0.75rem;
  text-align: center;
  color: rgba(255, 255, 255, 0.7);
  z-index: 10;
  padding: 0 1rem;
}

.about-link {
  position: absolute;
  top: max(1rem, env(safe-area-inset-top, 1rem));
  right: 1rem;
  z-index: 15;
}

.about-btn {
  background: linear-gradient(45deg, rgba(196, 30, 58, 0.8), rgba(230, 52, 98, 0.8));
  border: 1px solid rgba(196, 30, 58, 0.6);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.875rem;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  transition: all 0.4s ease;
  box-shadow: 0 4px 15px rgba(196, 30, 58, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  line-height: 1;
  -webkit-tap-highlight-color: transparent;
}

.about-btn svg {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
}

@media (hover: hover) {
  .about-btn:hover {
    background: linear-gradient(
      45deg,
      rgba(202, 169, 168, 0.9),
      rgba(131, 198, 233, 0.9),
      rgba(244, 192, 137, 0.9),
      rgba(238, 169, 150, 0.9),
      rgba(233, 174, 178, 0.9),
      rgba(234, 149, 152, 0.9)
    );
    border-color: rgba(255, 255, 255, 0.4);
    box-shadow: 0 6px 20px rgba(196, 30, 58, 0.4);
    transform: translateY(-3px);
  }
}

.about-btn:active {
  transform: translateY(-1px);
  box-shadow: 0 3px 12px rgba(196, 30, 58, 0.5);
}

@keyframes float {
  0%, 100% { transform: translateY(0) rotate(0deg); opacity: 0.5; }
  50% { transform: translateY(-20px) rotate(10deg); opacity: 0.7; }
}

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
  20%, 40%, 60%, 80% { transform: translateX(5px); }
}

@media (max-width: 480px) {
  .container {
    padding: 0.75rem;
    justify-content: center;
  }

  .login-card {
    padding: 2rem 1.5rem;
    border-radius: 16px;
  }

  .avatar-container {
    width: 72px;
    height: 72px;
    margin-bottom: 1rem;
  }

  .avatar-logo {
    width: 56px;
    height: 56px;
  }

  .login-card > h2 {
    font-size: 1.25rem;
    margin-bottom: 1.25rem;
  }

  .note-1 { font-size: 2.5rem; }
  .note-2 { font-size: 2rem; }
  .note-3 { font-size: 3rem; }

  .footer {
    font-size: 0.625rem;
    bottom: 0.75rem;
  }

  .about-btn {
    padding: 0.5rem 0.875rem;
    font-size: 0.8125rem;
  }
}

@media (max-height: 600px) {
  .login-card {
    padding: 1.5rem;
  }

  .avatar-container {
    width: 64px;
    height: 64px;
    margin-bottom: 0.75rem;
  }

  .avatar-logo {
    width: 48px;
    height: 48px;
  }

  .login-card > h2 {
    font-size: 1.125rem;
    margin-bottom: 1rem;
  }

  .input-container {
    margin-bottom: 1rem;
  }

  .password-field input,
  .verify-btn {
    height: 46px;
  }
}

@media (prefers-color-scheme: dark) {
  .login-card {
    background: rgba(80, 20, 40, 0.7);
  }

  .verify-btn {
    background: #E63462;
  }

  .verify-btn:hover:not(:disabled) {
    background: #C41E3A;
  }
}
</style>
