<template>
  <el-container class="container">
    <el-header class="header">
      <h1 class="header-title">"{{ description }}"大头自助采集</h1>
    </el-header>
    <el-main class="main">
      <face-selector :event-id="event_id" @face-selected="handleFaceSelected" />
      <uploader :event-id="event_id" :selected-face="selectedFace" :selected-face-url="selectedFaceUrl"  @avatar-uploaded="handleAvatarUploaded" />
    </el-main>
    <el-footer class="footer">
      <div>Copyright (C) 2025 Faspand for GDUT BanGDream Fan Club</div>
      <div>「BanGDream!」は株式会社ブシロードの登録商標です。</div>
    </el-footer>
  </el-container>
</template>

<script>
import FaceSelector from '../components/FaceSelector.vue';
import Uploader from '../components/Uploader.vue';

export default {
  components: {
    FaceSelector,
    Uploader,
  },
  props: {
    event_id: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      selectedFace: null,
      uploadedAvatar: null,
      selectedFaceUrl: null,
      description: localStorage.getItem('description')
    };
  },
  methods: {
    handleFaceSelected(face, url) {
      this.selectedFace = face;
      this.selectedFaceUrl = url;
    },
    handleAvatarUploaded(filename) {
      this.uploadedAvatar = filename;
    },
  },
};
</script>

<style>
container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: linear-gradient(135deg, rgba(115, 9, 9, 0.71), #ff1414);
  color: white;
  padding: 1rem;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
}

.header-title {
  font-size: 1.8rem;
  font-weight: bold;
  margin: 0;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
}

.main {
  flex: 1;
  max-width: 1200px;
  min-width: 50vw;
  margin: 80px auto 20px;
  padding: 2rem;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.05);
}

.footer {
  width: 100vw;
  background-color: #f8f9fa;
  color: #666;
  text-align: center;
  padding: 1rem;
  font-size: 0.9rem;
  border-top: 1px solid #eee;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-title {
    font-size: 1.4rem;
  }

  .main {
    padding: 1rem;
    margin: 60px 10px 10px;
    border-radius: 0;
    box-shadow: none;
  }
}

/* 添加一些动画效果 */
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

.main {
  animation: fadeIn 0.5s ease-out;
}
</style>
<style>
@media (prefers-color-scheme: dark) {
  body {
    background-color: #121212;
    color: #e0e0e0;
  }

  .header {
    background: linear-gradient(135deg, rgba(255, 85, 85, 0.8), #ff3333);
    color: #fff;
  }

  .main {
    background-color: #1e1e1e;
    color: #e0e0e0;
    box-shadow: 0 0 10px rgba(255, 255, 255, 0.05);
  }

  .footer {
    background-color: #1a1a1a;
    color: #aaa;
    border-top: 1px solid #333;
  }
}
</style>