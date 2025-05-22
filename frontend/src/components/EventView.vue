<template>
  <div class="event-view-container">
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">活动预览</h1>
        <p class="page-subtitle">查看活动图片和人脸采集结果</p>
      </div>
      <div class="header-decoration">
        <span class="note">♪</span>
        <span class="note">♫</span>
      </div>
    </div>

    <div class="event-pic-section">
      <el-card class="pic-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <i class="el-icon-picture-outline"></i>
            <span>活动原图</span>
          </div>
        </template>

        <div class="pic-container" v-loading="!eventPicUrl">
          <el-image
              v-if="eventPicUrl"
              :src="eventPicUrl"
              class="event-image"
              fit="contain"
              :preview-src-list="[eventPicUrl]"
              lazy
          >
            <template #error>
              <div class="image-error">
                <i class="el-icon-picture-outline"></i>
                <p>图片加载失败</p>
              </div>
            </template>
          </el-image>

          <div v-else class="image-loading">
            <i class="el-icon-loading"></i>
            <p>加载中...</p>
          </div>
        </div>
      </el-card>
    </div>

    <div class="faces-section">
      <div class="section-header">
        <h2 class="section-title">
          <i class="el-icon-user"></i>
          人脸采集结果
        </h2>
        <el-tag v-if="faces.length > 0" type="success" size="large">
          共 {{ faces.length }} 个人脸
        </el-tag>
      </div>

      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="3" animated />
      </div>

      <div v-else-if="faces.length === 0" class="empty-container">
        <el-empty description="暂无人脸数据">
          <template #image>
            <i class="el-icon-user-solid empty-icon"></i>
          </template>
        </el-empty>
      </div>

      <div v-else class="faces-grid">
        <el-card
            v-for="(face, index) in faces"
            :key="face"
            class="face-card"
            shadow="hover"
            :body-style="{ padding: '20px' }"
        >
          <template #header>
            <div class="face-card-header">
              <div class="face-title">
                <span class="face-number">{{ `人脸 ${index + 1}` }}</span>
                <span v-if="faceNicknameMap[face]" class="face-nickname">{{ faceNicknameMap[face] }}</span>
              </div>
              <el-tag size="small" type="info">{{ face }}</el-tag>
            </div>
          </template>

          <div class="face-content">
            <div class="face-comparison">
              <!-- 原始人脸 -->
              <div class="face-item original-face">
                <div class="face-label">
                  <i class="el-icon-crop"></i>
                  <span>识别裁剪</span>
                </div>
                <div class="image-wrapper">
                  <el-image
                      v-if="faceUrlMap[face]"
                      :src="faceUrlMap[face]"
                      :alt="face"
                      class="face-image"
                      fit="cover"
                      lazy
                  >
                    <template #error>
                      <div class="image-error-small">
                        <i class="el-icon-picture-outline"></i>
                      </div>
                    </template>
                  </el-image>
                  <div v-else class="image-placeholder">
                    <i class="el-icon-loading"></i>
                  </div>
                </div>
              </div>

              <!-- 箭头指示 -->
              <div class="arrow-indicator">
                <i class="el-icon-right"></i>
              </div>

              <!-- 用户上传头像 -->
              <div class="face-item uploaded-avatar">
                <div class="face-label">
                  <i class="el-icon-upload"></i>
                  <span>用户头像</span>
                </div>
                <div class="image-wrapper">
                  <el-image
                      v-if="avatarUrlMap[face]"
                      :src="avatarUrlMap[face]"
                      alt="用户头像"
                      class="face-image"
                      fit="cover"
                      lazy
                  >
                    <template #error>
                      <div class="image-error-small">
                        <i class="el-icon-picture-outline"></i>
                      </div>
                    </template>
                  </el-image>
                  <div v-else class="image-placeholder no-upload">
                    <i class="el-icon-question"></i>
                    <span>未上传</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 状态指示 -->
            <div class="face-status">
              <el-tag
                  :type="avatarUrlMap[face] ? 'success' : 'info'"
                  size="small"
                  :icon="avatarUrlMap[face] ? 'el-icon-check' : 'el-icon-time'"
              >
                {{ avatarUrlMap[face] ? '已完成' : '待上传' }}
              </el-tag>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 统计信息 -->
    <div class="stats-section" v-if="faces.length > 0">
      <el-card class="stats-card">
        <div class="stats-content">
          <div class="stat-item">
            <div class="stat-number">{{ faces.length }}</div>
            <div class="stat-label">识别人脸</div>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <div class="stat-number">{{ uploadedCount }}</div>
            <div class="stat-label">已上传</div>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <div class="stat-number">{{ Math.round((uploadedCount / faces.length) * 100) }}%</div>
            <div class="stat-label">完成率</div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { apiClient } from '@/api/axios';
import { useRoute } from "vue-router";
import { ref, onMounted, computed, onBeforeUnmount } from 'vue';

const route = useRoute();
const eventId = route.params.event_id;
const faces = ref([]);
const faceUrlMap = ref({});
const avatarUrlMap = ref({});
const faceQQMap = ref({});
const faceNicknameMap = ref({});
const loading = ref(false);
const eventPicUrl = ref(null);

// 计算已上传的数量
const uploadedCount = computed(() => {
  return Object.keys(avatarUrlMap.value).length;
});

const fetchEventPic = async () => {
  try {
    const res = await apiClient.get(`/events/${eventId}/pic`, {
      responseType: 'blob'
    });
    eventPicUrl.value = URL.createObjectURL(res.data);
  } catch (error) {
    console.error('获取活动图片失败:', error);
  }
};

async function fetchFaces() {
  loading.value = true;
  try {
    const response = await apiClient.get(`/events/${eventId}/faces`);
    faces.value = response.data.faces;
    await Promise.all(faces.value.map(loadFaceImage));
    await Promise.all(faces.value.map(loadAvatarImage));
    await Promise.all(faces.value.map(loadFaceQQInfo));
  } catch (error) {
    console.error('获取人脸列表失败:', error);
    faces.value = [];
  } finally {
    loading.value = false;
  }
}

async function loadFaceImage(face) {
  try {
    const response = await apiClient.get(`/events/${eventId}/faces/${face}`, {
      responseType: 'blob',
    });
    const blobUrl = URL.createObjectURL(response.data);
    faceUrlMap.value[face] = blobUrl;
  } catch (err) {
    console.error(`加载图片 ${face} 失败`, err);
  }
}

async function loadAvatarImage(face) {
  try {
    const response = await apiClient.get(`/events/${eventId}/faces/upload/${face}`, {
      responseType: 'blob',
    });
    const avatarBlobUrl = URL.createObjectURL(response.data);
    avatarUrlMap.value[face] = avatarBlobUrl;
  } catch (err) {
    // 用户可能还没上传，这是正常的
    console.debug(`用户头像 ${face} 未上传或加载失败`);
  }
}

async function loadFaceQQInfo(face) {
  try {
    const response = await apiClient.get(`/events/${eventId}/faces/${face}/info`);
    const qqNumber = response.data.qq_number;
    if (qqNumber) {
      faceQQMap.value[face] = qqNumber;
      await fetchQQNickname(face, qqNumber);
    }
  } catch (err) {
    console.debug(`获取 ${face} 的QQ信息失败`, err);
  }
}

async function fetchQQNickname(face, qqNumber) {
  try {
    const response = await apiClient.get(`/events/${eventId}/qq-nickname/${qqNumber}`);
    if (response.data.success && response.data.nickname) {
      faceNicknameMap.value[face] = response.data.nickname;
    } else {
      faceNicknameMap.value[face] = `QQ用户${qqNumber}`;
    }
  } catch (err) {
    console.debug(`获取QQ昵称失败`, err);
    faceNicknameMap.value[face] = `QQ用户${qqNumber}`;
  }
}

onMounted(() => {
  fetchEventPic();
  fetchFaces();
});

// 清理 blob URLs
onBeforeUnmount(() => {
  if (eventPicUrl.value) {
    URL.revokeObjectURL(eventPicUrl.value);
  }
  Object.values(faceUrlMap.value).forEach(url => URL.revokeObjectURL(url));
  Object.values(avatarUrlMap.value).forEach(url => URL.revokeObjectURL(url));
});
</script>

<style scoped>
.event-view-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #ffecf2 0%, #fff5fa 100%);
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* 页面头部 */
.page-header {
  text-align: center;
  margin-bottom: 30px;
  position: relative;
  padding: 20px 0;
}

.header-content {
  position: relative;
  z-index: 2;
}

.page-title {
  font-size: 2.5rem;
  font-weight: bold;
  color: #FF3377;
  margin-bottom: 8px;
  text-shadow: 0 2px 4px rgba(255, 51, 119, 0.1);
}

.page-subtitle {
  font-size: 1.1rem;
  color: #666;
  margin: 0;
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
  color: rgba(255, 51, 119, 0.1);
  font-size: 3rem;
  animation: float 6s ease-in-out infinite;
}

.header-decoration .note:first-child {
  top: 20%;
  left: 20%;
  animation-delay: 0s;
}

.header-decoration .note:last-child {
  top: 30%;
  right: 20%;
  animation-delay: 2s;
}

/* 活动图片展示区域 */
.event-pic-section {
  margin-bottom: 40px;
}

.pic-card {
  max-width: 1000px;
  margin: 0 auto;
  border-radius: 16px;
  overflow: hidden;
  border: none;
  box-shadow: 0 8px 24px rgba(255, 51, 119, 0.1);
}

.card-header {
  display: flex;
  align-items: center;
  font-size: 1.2rem;
  font-weight: 600;
  color: #FF3377;
}

.card-header i {
  margin-right: 8px;
  font-size: 1.4rem;
}

.pic-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
  background: #fafafa;
  border-radius: 8px;
  overflow: hidden;
}

.event-image {
  max-width: 100%;
  max-height: 600px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  cursor: zoom-in;
}

.image-error, .image-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #999;
  padding: 40px;
}

.image-error i, .image-loading i {
  font-size: 3rem;
  margin-bottom: 10px;
}

/* 人脸展示区域 */
.faces-section {
  margin-bottom: 40px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 0 10px;
}

.section-title {
  font-size: 1.8rem;
  font-weight: 600;
  color: #333;
  margin: 0;
  display: flex;
  align-items: center;
}

.section-title i {
  margin-right: 10px;
  color: #FF3377;
}

.loading-container {
  background: white;
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.empty-container {
  background: white;
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  text-align: center;
}

.empty-icon {
  font-size: 4rem;
  color: #ddd;
}

/* 人脸网格布局 */
.faces-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
}

.face-card {
  border-radius: 16px;
  border: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  overflow: hidden;
}

.face-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(255, 51, 119, 0.15);
}

.face-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.face-title {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.face-number {
  font-weight: 600;
  color: #333;
  font-size: 1.1rem;
}

.face-nickname {
  font-size: 0.9rem;
  color: #FF3377;
  font-weight: 500;
  margin-top: 2px;
}

.face-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.face-comparison {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}

.face-item {
  flex: 1;
  text-align: center;
}

.face-label {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
  font-size: 0.9rem;
  color: #666;
  font-weight: 500;
}

.face-label i {
  margin-right: 6px;
  color: #FF3377;
}

.image-wrapper {
  width: 120px;
  height: 120px;
  margin: 0 auto;
  border-radius: 12px;
  overflow: hidden;
  border: 3px solid #f0f0f0;
  transition: border-color 0.3s ease;
}

.original-face .image-wrapper {
  border-color: #e8f4fd;
}

.uploaded-avatar .image-wrapper {
  border-color: #e8f8e8;
}

.face-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f9f9f9;
  color: #ccc;
}

.image-placeholder.no-upload {
  background: #fafafa;
  color: #999;
}

.image-placeholder span {
  font-size: 0.8rem;
  margin-top: 4px;
}

.image-error-small {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  color: #ccc;
}

.arrow-indicator {
  font-size: 1.5rem;
  color: #FF3377;
  margin: 0 10px;
}

.face-status {
  text-align: center;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
}

/* 统计信息 */
.stats-section {
  margin-top: 40px;
}

.stats-card {
  max-width: 600px;
  margin: 0 auto;
  border-radius: 16px;
  border: none;
  box-shadow: 0 4px 12px rgba(255, 51, 119, 0.1);
}

.stats-content {
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding: 10px 0;
}

.stat-item {
  text-align: center;
  flex: 1;
}

.stat-number {
  font-size: 2rem;
  font-weight: bold;
  color: #FF3377;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 0.9rem;
  color: #666;
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: #eee;
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

:deep(.el-card__header) {
  background: rgba(255, 51, 119, 0.05);
  border-bottom: 1px solid rgba(255, 51, 119, 0.1);
  padding: 16px 20px;
}

:deep(.el-tag--success) {
  background-color: rgba(103, 194, 58, 0.1);
  border-color: rgba(103, 194, 58, 0.2);
  color: #67c23a;
}

:deep(.el-tag--info) {
  background-color: rgba(144, 147, 153, 0.1);
  border-color: rgba(144, 147, 153, 0.2);
  color: #909399;
}

@media (max-width: 768px) {
  .event-view-container {
    padding: 15px;
  }

  .page-title {
    font-size: 2rem;
  }

  .faces-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }

  .face-comparison {
    flex-direction: column;
    gap: 15px;
  }

  .arrow-indicator {
    transform: rotate(90deg);
    margin: 10px 0;
  }

  .stats-content {
    flex-direction: column;
    gap: 20px;
  }

  .stat-divider {
    width: 40px;
    height: 1px;
  }

  .section-header {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
}

@media (max-width: 480px) {
  .image-wrapper {
    width: 100px;
    height: 100px;
  }

  .face-comparison {
    gap: 10px;
  }

  .pic-container {
    min-height: 250px;
  }
}
</style>