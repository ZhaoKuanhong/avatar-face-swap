<template>
  <div class="about-container">
    <div class="gradient-overlay"></div>
    <div class="about-content">
      <div class="back-button">
        <el-button @click="goBack" type="text" class="back-btn">
          <i class="el-icon-arrow-left"></i>
          返回
        </el-button>
      </div>

      <div class="page-header">
        <div class="header-decoration">
          <span class="note note-1">♪</span>
          <span class="note note-2">♫</span>
          <span class="note note-3">♬</span>
        </div>
        <h1 class="page-title">关于我们</h1>
        <p class="page-subtitle">About Us</p>
      </div>

      <!-- 主要内容区域 -->
      <div class="content-sections">

        <!-- 社团介绍 -->
        <el-card class="section-card club-section" shadow="hover">
          <div class="club-intro">
            <div class="club-logo">
              <img src="../assets/img/logo.png" alt="GDUT BanGDream Fan Club" />
            </div>
            <div class="club-info">
              <h2 class="club-name">GDUT BanGDream Fan Club</h2>
              <p class="club-description">
                广东工业大学BanGDream同好会，聚集了热爱バンドリ（和nsy）的人们。
                我们会组织各类音游活动、观影聚会和团建活动。希望大家在这里分享快乐，共同成长。
              </p>
              <div class="club-features">
                <div class="feature-item">
                  <i class="el-icon-star-on"></i>
                  <span>音游交流</span>
                </div>
                <div class="feature-item">
                  <i class="el-icon-camera"></i>
                  <span>线下聚会</span>
                </div>
                <div class="feature-item">
                  <i class="el-icon-trophy"></i>
                  <span>团建活动</span>
                </div>
                <div class="feature-item">
                  <i class="el-icon-chat-dot-round"></i>
                  <span>同好交流</span>
                </div>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 项目介绍 -->
        <el-card class="section-card project-section" shadow="hover">
          <h3 class="section-title">
            <i class="el-icon-monitor"></i>
            项目介绍
          </h3>
          <div class="project-info">
            <p>
              <strong>团建大头覆盖</strong> 是为了方便社团成员进行团建活动而开发的智能换脸工具。
              采用opencv进行人脸识别，能够自动识别和替换合影中的人脸位置，方便p大头。
            </p>
            <div class="tech-stack">
              <div class="tech-item">
                <span class="tech-label">前端</span>
                <span class="tech-value">Vue 3 + Element Plus</span>
              </div>
              <div class="tech-item">
                <span class="tech-label">后端</span>
                <span class="tech-value">Python Flask</span>
              </div>
              <div class="tech-item">
                <span class="tech-label">机器学习</span>
                <span class="tech-value">OpenCV + dlib</span>
              </div>
              <div class="tech-item">
                <span class="tech-label">图像处理</span>
                <span class="tech-value">Fabric.js</span>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 开发团队 -->
        <el-card class="section-card team-section" shadow="hover">
          <h3 class="section-title">
            <i class="el-icon-user"></i>
            开发者
          </h3>
          <div class="developers-grid">
            <div class="developer-card">
              <div class="avatar-container">
                <img src="/faspand.png" alt="Faspand" class="developer-avatar" />
                <div class="avatar-ring"></div>
              </div>
              <h4 class="developer-name">Faspand</h4>
              <p class="developer-role">「みんなと繋がりたい」</p>
              <p class="developer-description">
                负责系统架构设计、后端开发与算法集成。
              </p>
            </div>

            <div class="developer-card">
              <div class="avatar-container">
                <img src="/mio.jpg" alt="Mio" class="developer-avatar" />
                <div class="avatar-ring"></div>
              </div>
              <h4 class="developer-name">Mio</h4>
              <p class="developer-role">列車は必ず次の駅へ</p>
              <p class="developer-description">
                负责用户界面设计与前端开发，集合前后端模块功能。
              </p>
            </div>
          </div>
        </el-card>

        <el-card class="section-card copyright-section" shadow="hover">
          <div class="copyright-content">
            <div class="copyright-main">
              <p class="copyright-text">
                Copyright © 2025 Faspand & Mio for GDUT BanGDream Fan Club
              </p>
              <p class="copyright-disclaimer">
                「BanGDream!」は株式会社ブシロードの登録商標です。
              </p>
            </div>
            <div class="version-info">
              <span class="version-tag">v4.0.0-beta</span>
            </div>
          </div>
        </el-card>

      </div>
    </div>

    <!-- 背景装饰 -->
    <div class="background-decoration">
      <div class="floating-notes">
        <span class="bg-note note-bg-1">♪</span>
        <span class="bg-note note-bg-2">♫</span>
        <span class="bg-note note-bg-3">♬</span>
        <span class="bg-note note-bg-4">♩</span>
        <span class="bg-note note-bg-5">♪</span>
        <span class="bg-note note-bg-6">♫</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';

const router = useRouter();

const goBack = () => {
  router.go(-1);
};
</script>

<style scoped>
.about-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #ffecf2 0%, #fff5fa 100%);
  padding: 20px;
  position: relative;
  overflow-x: hidden;
}

.gradient-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    135deg,
    rgba(202, 169, 168, 0.1) 0%,
    rgba(131, 198, 233, 0.1) 20%,
    rgba(244, 192, 137, 0.1) 40%,
    rgba(238, 169, 150, 0.1) 60%,
    rgba(233, 174, 178, 0.1) 80%,
    rgba(234, 149, 152, 0.1) 100%
  );
  z-index: 1;
  pointer-events: none;
}

.about-content {
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
  z-index: 2;
}

.back-button {
  margin-bottom: 20px;
}

.back-btn {
  color: #C41E3A;
  font-size: 16px;
  padding: 8px 16px;
  border-radius: 20px;
  transition: all 0.4s ease;
  background: rgba(196, 30, 58, 0.05);
}

.back-btn:hover {
  background: linear-gradient(
    90deg,
    rgba(202, 169, 168, 0.3),
    rgba(131, 198, 233, 0.3),
    rgba(244, 192, 137, 0.3),
    rgba(238, 169, 150, 0.3),
    rgba(233, 174, 178, 0.3),
    rgba(234, 149, 152, 0.3)
  );
  transform: translateX(-5px);
  color: white;
}

/* 页面头部 */
.page-header {
  text-align: center;
  margin-bottom: 40px;
  position: relative;
  padding: 40px 0;
}

.header-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  pointer-events: none;
}

.header-decoration .note {
  position: absolute;
  color: rgba(196, 30, 58, 0.1);
  font-size: 3rem;
  animation: float 6s ease-in-out infinite;
}

.note-1 {
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.note-2 {
  top: 20%;
  right: 15%;
  animation-delay: 2s;
}

.note-3 {
  bottom: 10%;
  left: 50%;
  animation-delay: 4s;
}

.page-title {
  font-size: 3rem;
  font-weight: bold;
  color: #C41E3A;
  margin-bottom: 8px;
  text-shadow: 0 2px 4px rgba(196, 30, 58, 0.1);
  position: relative;
  z-index: 2;
}

.page-subtitle {
  font-size: 1.2rem;
  color: #666;
  font-style: italic;
  position: relative;
  z-index: 2;
}

/* 内容区域 */
.content-sections {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.section-card {
  border-radius: 16px;
  border: none;
  box-shadow: 0 8px 24px rgba(196, 30, 58, 0.1);
  transition: all 0.4s ease;
}

.section-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(196, 30, 58, 0.15);
}

.section-title {
  display: flex;
  align-items: center;
  font-size: 1.5rem;
  color: #333;
  margin-bottom: 20px;
  font-weight: 600;
}

.section-title i {
  margin-right: 10px;
  color: #C41E3A;
  font-size: 1.6rem;
}

/* 社团介绍部分 */
.club-intro {
  display: flex;
  align-items: center;
  gap: 30px;
}

.club-logo {
  flex-shrink: 0;
}

.club-logo img {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid #FFE8F1;
  box-shadow: 0 8px 20px rgba(196, 30, 58, 0.2);
}

.club-info {
  flex: 1;
}

.club-name {
  font-size: 2rem;
  color: #C41E3A;
  margin-bottom: 15px;
  font-weight: bold;
}

.club-description {
  font-size: 1rem;
  line-height: 1.8;
  color: #555;
  margin-bottom: 20px;
}

.club-features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 15px;
}

.feature-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  background: rgba(196, 30, 58, 0.05);
  border-radius: 20px;
  font-size: 0.9rem;
  color: #333;
  transition: all 0.4s ease;
}

.feature-item:hover {
  background: linear-gradient(
    90deg,
    rgba(202, 169, 168, 0.2),
    rgba(131, 198, 233, 0.2),
    rgba(244, 192, 137, 0.2)
  );
  transform: translateY(-2px);
}

.feature-item i {
  margin-right: 8px;
  color: #C41E3A;
}

/* 项目介绍部分 */
.project-info p {
  font-size: 1rem;
  line-height: 1.8;
  color: #555;
  margin-bottom: 25px;
}

.tech-stack {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.tech-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: linear-gradient(135deg, #f8f9fa 0%, #fff 100%);
  border-radius: 8px;
  border-left: 4px solid #C41E3A;
  transition: all 0.4s ease;
}

.tech-item:hover {
  transform: translateX(5px);
  box-shadow: 0 4px 12px rgba(196, 30, 58, 0.1);
}

.tech-label {
  font-weight: 600;
  color: #333;
}

.tech-value {
  color: #666;
  font-size: 0.9rem;
}

/* 开发团队部分 */
.developers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
}

.developer-card {
  text-align: center;
  padding: 20px;
  background: linear-gradient(135deg, #fafbfc 0%, #fff 100%);
  border-radius: 12px;
  border: 1px solid rgba(196, 30, 58, 0.1);
  transition: all 0.4s ease;
}

.developer-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(196, 30, 58, 0.15);
  background: linear-gradient(
    135deg,
    rgba(202, 169, 168, 0.05),
    rgba(131, 198, 233, 0.05),
    rgba(244, 192, 137, 0.05)
  );
}

.avatar-container {
  position: relative;
  display: inline-block;
  margin-bottom: 20px;
}

.developer-avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  position: relative;
  z-index: 2;
}

.avatar-ring {
  position: absolute;
  top: -8px;
  left: -8px;
  right: -8px;
  bottom: -8px;
  border: 3px solid #C41E3A;
  border-radius: 50%;
  opacity: 0.6;
  animation: pulse 3s ease-in-out infinite;
}

.developer-name {
  font-size: 1.4rem;
  color: #333;
  margin-bottom: 8px;
  font-weight: bold;
}

.developer-role {
  font-size: 1rem;
  color: #C41E3A;
  margin-bottom: 15px;
  font-weight: 500;
}

.developer-description {
  font-size: 0.9rem;
  line-height: 1.6;
  color: #666;
  margin-bottom: 20px;
}

.developer-skills {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
}

.skill-tag {
  background: rgba(196, 30, 58, 0.1);
  color: #C41E3A;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
  transition: all 0.3s ease;
}

.skill-tag:hover {
  background: #C41E3A;
  color: white;
  transform: scale(1.05);
}

/* 版权信息部分 */
.copyright-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.copyright-main {
  flex: 1;
}

.copyright-text {
  font-size: 0.9rem;
  color: #333;
  margin-bottom: 5px;
}

.copyright-disclaimer {
  font-size: 0.8rem;
  color: #888;
  font-style: italic;
}

.version-info {
  flex-shrink: 0;
}

.version-tag {
  background: linear-gradient(90deg, #C41E3A 0%, #E63462 100%);
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
  transition: all 0.4s ease;
}

.version-tag:hover {
  background: linear-gradient(
    90deg,
    rgba(202, 169, 168, 0.9),
    rgba(131, 198, 233, 0.9),
    rgba(244, 192, 137, 0.9)
  );
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(196, 30, 58, 0.3);
}

/* 背景装饰 */
.background-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  pointer-events: none;
  overflow: hidden;
}

.floating-notes {
  position: relative;
  width: 100%;
  height: 100%;
}

.bg-note {
  position: absolute;
  color: rgba(196, 30, 58, 0.05);
  font-size: 4rem;
  animation: floatBg 20s ease-in-out infinite;
}

.note-bg-1 {
  top: 10%;
  left: 5%;
  animation-delay: 0s;
}

.note-bg-2 {
  top: 30%;
  right: 10%;
  animation-delay: 3s;
}

.note-bg-3 {
  top: 60%;
  left: 15%;
  animation-delay: 6s;
}

.note-bg-4 {
  top: 80%;
  right: 20%;
  animation-delay: 9s;
}

.note-bg-5 {
  top: 20%;
  left: 70%;
  animation-delay: 12s;
}

.note-bg-6 {
  top: 70%;
  left: 60%;
  animation-delay: 15s;
}

/* 动画效果 */
@keyframes float {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
    opacity: 0.1;
  }
  50% {
    transform: translateY(-10px) rotate(5deg);
    opacity: 0.2;
  }
}

@keyframes floatBg {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
    opacity: 0.03;
  }
  50% {
    transform: translateY(-30px) rotate(10deg);
    opacity: 0.08;
  }
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.6;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.8;
  }
}

/* Element Plus 样式覆盖 */
:deep(.el-card__body) {
  padding: 30px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .about-container {
    padding: 15px;
  }

  .page-title {
    font-size: 2.2rem;
  }

  .club-intro {
    flex-direction: column;
    text-align: center;
    gap: 20px;
  }

  .club-logo img {
    width: 100px;
    height: 100px;
  }

  .developers-grid {
    grid-template-columns: 1fr;
  }

  .copyright-content {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }

  .tech-stack {
    grid-template-columns: 1fr;
  }

  .club-features {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .club-features {
    grid-template-columns: 1fr;
  }

  .feature-item {
    justify-content: center;
  }
}
</style>