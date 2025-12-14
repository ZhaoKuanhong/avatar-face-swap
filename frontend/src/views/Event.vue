<template>
  <div class="event-container">
    <div class="event-header">
      <h1 class="event-title">"{{ description }}"大头自助采集</h1>
      <div class="steps-container">
        <div class="modern-steps">
          <div 
            v-for="(step, index) in stepItems" 
            :key="index"
            class="step-item"
            :class="{
              'is-active': currentStep === index,
              'is-completed': currentStep > index,
              'is-pending': currentStep < index
            }"
          >
            <div class="step-icon">
              <svg v-if="currentStep > index" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              <span v-else>{{ index + 1 }}</span>
            </div>
            <span v-if="currentStep === index" class="step-title">{{ step.title }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="event-content">
      <div class="content-card">
        <div class="card-header">
          <div class="step-indicator">
            <span class="step-number">{{ currentStep + 1 }}</span>
            <span class="step-text">{{ stepTexts[currentStep] }}</span>
          </div>
          <el-button v-if="currentStep > 0" @click="prevStep" plain size="small">
            <i class="el-icon-arrow-left"></i> 返回
          </el-button>
        </div>

        <div class="step-content">
          <!-- 第一步：选择大头 -->
          <div v-show="currentStep === 0" class="step-panel">
            <face-selector
                :event-id="event_id"
                @face-selected="handleFaceSelected"
            />
            <div class="step-actions">
              <el-button
                  color="#FF3377"
                  type="primary"
                  :disabled="!selectedFace"
                  @click="nextStep"
              >
                下一步 <i class="el-icon-arrow-right"></i>
              </el-button>
            </div>
          </div>

          <!-- 第二步：choose头像 -->
          <div v-show="currentStep === 1" class="step-panel">
            <h3 class="section-title">输入 QQ 号获取头像</h3>
            <div class="qq-input-row">
              <el-input 
                type="number" 
                v-model="qqNumber" 
                placeholder="输入你的 QQ 号"
                size="large"
                class="qq-input"
                @keyup.enter="fetchQQAvatar"
              />
              <el-button 
                size="large"
                class="fetch-btn"
                @click="fetchQQAvatar" 
                :disabled="!qqNumber || !selectedFace || qqAvatarLoading"
                :loading="qqAvatarLoading"
              >
                获取头像
              </el-button>
            </div>
            <div v-if="isAvatarSelected" class="avatar-preview-section">
              <p class="preview-label">QQ 头像预览</p>
              <div class="avatar-preview-wrapper">
                <img :src="qqAvatarUrl" alt="QQ Avatar" class="avatar-preview-img"/>
              </div>
            </div>
            <div class="step-actions">
              <el-button
                  color="#FF3377"
                  type="primary"
                  size="large"
                  :disabled="!isAvatarSelected"
                  @click="completeProcess"
              >
                下一步
              </el-button>
            </div>
          </div>

          <!-- Step 3: Confirm -->
          <div v-show="currentStep === 2" class="step-panel confirm-panel">
            <h2 class="confirm-title">请确认您的选择</h2>
            <p class="confirm-subtitle">请确认二者准确无误</p>
            <div class="preview-container">
              <div class="preview-item">
                <img :src="selectedFaceUrl" alt="选择的大头" />
                <span class="preview-label">您选择的大头</span>
              </div>
              <div class="arrow-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M5 12h14M12 5l7 7-7 7"/>
                </svg>
              </div>
              <div class="preview-item">
                <img :src="qqAvatarUrl" alt="上传的头像" />
                <span class="preview-label">您上传的头像</span>
              </div>
            </div>
            <div class="step-actions">
              <el-button size="large" @click="resetProcess">重新选择</el-button>
              <el-button color="#FF3377" type="primary" size="large" @click="uploadQQAvatar" :loading="qqAvatarUploading">确认上传</el-button>
            </div>
          </div>

          <!-- 第四步：完成 -->
          <div v-show="currentStep === 3" class="step-panel success-panel">
            <el-result
              :icon="uploadResult"
              :title="uploadMessage"
            />
            <div class="step-actions success-actions">
              <el-button color="#FF3377" type="primary" size="large" @click="resetProcess">完成另一个</el-button>
              <el-button size="large" @click="backToHome">返回首页</el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="event-footer">
      <div class="notes-decoration">
        <span class="note note-1">♪</span>
        <span class="note note-2">♫</span>
        <span class="note note-3">♬</span>
      </div>
      <div class="footer-content">
        <div>Copyright (C) 2025 Faspand & Mio for GDUT BanGDream Fan Club</div>
        <div>「BanGDream!」は株式会社ブシロードの登録商標です。</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { apiClient } from "@/api/axios.js";
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import FaceSelector from '../components/FaceSelector.vue';

// 接收 props
const props = defineProps({
  event_id: {
    type: String,
    required: true
  }
});

const emit = defineEmits(['avatar-uploaded']);

const selectedFace = ref(null);
const uploadedAvatar = ref(null);
const selectedFaceUrl = ref(null);
const uploadedAvatarUrl = ref(null);
const description = ref(localStorage.getItem('description') || '活动');
const currentStep = ref(0);
const isAvatarSelected = ref(false);
const isUploadCompleted = ref(false);

const stepTexts = [
    '请在下方选择您的大头位置',
    '请上传您的头像',
    '请再确认一次喵~',
    '完成！'
];

const stepItems = [
  { title: '选择大头' },
  { title: '上传头像' },
  { title: '确认' },
  { title: '完成' }
];

const handleFaceSelected = (face, url) => {
  selectedFace.value = face;
  selectedFaceUrl.value = url;
};

const handleAvatarSelected = (filename, url) => {
  console.log('Avatar uploaded:', filename, url);
  uploadedAvatar.value = filename;
  uploadedAvatarUrl.value = url || null;
  isAvatarSelected.value = true;
};

const handleAvatarUploaded = (filename, url) => {
  console.log('Avatar uploaded:', filename, url);
  uploadedAvatar.value = filename;
  uploadedAvatarUrl.value = url || null;
  isUploadCompleted.value = true;
};

const nextStep = () => {
  if (currentStep.value < 2) currentStep.value++;
};

const prevStep = () => {
  if (currentStep.value > 0) currentStep.value--;
};

const completeProcess = () => {
  currentStep.value = 2;
};

const resetProcess = () => {
  selectedFace.value = null;
  uploadedAvatar.value = null;
  selectedFaceUrl.value = null;
  uploadedAvatarUrl.value = null;
  currentStep.value = 0;
};

const router = useRouter();
const backToHome = () => {
  router.push('/event');
};

// 以下为 QQ 头像上传相关逻辑
const qqAvatarUrl = ref('');
const qqNumber = ref('');
const uploadMessage = ref('');
const uploadError = ref('');
const uploadedImageUrl = ref(null);
const uploadedFilename = ref(null);
const uploadButton = ref('primary');
const qqAvatarUploading = ref(false);
const uploadResult = ref('');
const qqAvatarError = ref('');
const qqAvatarLoading = ref(false);
const confirmDialogVisible = ref(false);
const uploadDialogVisible = ref(false);

const fetchQQAvatar = async () => {
      if (!qqNumber.value) {
        qqAvatarError.value = '请输入 QQ 号';
        return;
      }
      qqAvatarLoading.value = true;
      qqAvatarError.value = '';
      qqAvatarUrl.value = `https://q1.qlogo.cn/g?b=qq&nk=${qqNumber.value}&s=640`;
      qqAvatarLoading.value = false;
      isAvatarSelected.value = true;
      // 浏览器的 <img> 标签会处理图片的加载和错误
    };

const uploadQQAvatar = async () => {
  if (!qqAvatarUrl.value) {
    uploadError.value = '请先获取 QQ 头像';
    return;
  }
  if (!selectedFace.value) {
    uploadError.value = '请先选择一张脸';
    return;
  }

  qqAvatarUploading.value = true;
  uploadMessage.value = '';
  uploadError.value = '';
  uploadedImageUrl.value = null;
  uploadedFilename.value = null;
  uploadButton.value = 'primary';

  try {
    const res = await apiClient.post(`/upload-qq-avatar/${props.event_id}/${selectedFace.value}`, {
      qqNumber: qqNumber.value,
      faceId: selectedFace.value,
      eventId: props.event_id,
    });

    uploadMessage.value = res.data.message;
    uploadedImageUrl.value = qqAvatarUrl.value;
    uploadedFilename.value = res.data.filename;
    currentStep.value = 3;
    uploadResult.value = 'success';
    emit('avatar-uploaded', res.data.filename);
  } catch (err) {
    console.error('上传 QQ 头像失败:', err);
    uploadError.value = '上传 QQ 头像失败，请稍后重试。';
    uploadResult.value = 'error';
    if (err.response?.data?.error) {
      uploadError.value = err.response.data.error;
    }
  } finally {
    qqAvatarUploading.value = false;
    confirmDialogVisible.value = false;
    uploadDialogVisible.value = true;
  }
};
</script>

<style scoped>
.event-container {
  --primary-color: #FF3377;
  --card-bg: #ffffff;
  --text-color: #333;
  --border-color: #eee;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #ffecf2 0%, #fff5fa 100%);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.event-header {
  background: linear-gradient(135deg, rgba(255, 51, 119, 0.9), #ff3377);
  color: white;
  padding: 1.25rem 1rem;
  text-align: center;
  box-shadow: 0 4px 15px rgba(255, 51, 119, 0.2);
  position: relative;
  z-index: 10;
}

.event-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 0.75rem;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.15);
}

.steps-container {
  max-width: 600px;
  margin: 0 auto;
}

.modern-steps {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border-radius: 24px;
  transition: all 0.3s ease;
}

.step-item.is-active {
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.step-item.is-completed .step-icon {
  background: rgba(255, 255, 255, 0.9);
  color: var(--primary-color);
}

.step-item.is-pending .step-icon {
  background: rgba(255, 255, 255, 0.3);
  color: rgba(255, 255, 255, 0.7);
}

.step-icon {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  font-weight: 600;
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.step-item.is-active .step-icon {
  background: var(--primary-color);
  color: white;
}

.step-icon svg {
  width: 16px;
  height: 16px;
}

.step-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--primary-color);
  white-space: nowrap;
}

.event-content {
  flex: 1;
  padding: 1rem;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.content-card {
  background: var(--card-bg);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  width: 100%;
  max-width: 640px;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.875rem 1rem;
  background: rgba(255, 221, 238, 0.3);
  border-bottom: 1px solid rgba(255, 51, 119, 0.1);
}

.step-indicator {
  display: flex;
  align-items: center;
  gap: 0.625rem;
}

.step-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: var(--primary-color);
  color: white;
  border-radius: 50%;
  font-weight: 700;
  font-size: 0.875rem;
  flex-shrink: 0;
}

.step-text {
  font-size: 0.9375rem;
  color: var(--text-color);
  font-weight: 500;
}

.step-content {
  padding: 1.25rem;
}

.step-panel {
  animation: fadeIn 0.4s ease-out;
}

.section-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 1.25rem;
}

.qq-input-row {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.qq-input {
  flex: 1;
  min-width: 0;
}

.fetch-btn {
  flex-shrink: 0;
  white-space: nowrap;
}

.avatar-preview-section {
  text-align: center;
  padding: 1.25rem;
  background: rgba(255, 51, 119, 0.03);
  border-radius: 12px;
  border: 1px dashed rgba(255, 51, 119, 0.2);
}

.preview-label {
  font-size: 0.875rem;
  color: #666;
  margin: 0 0 0.75rem;
}

.avatar-preview-wrapper {
  display: inline-block;
}

.avatar-preview-img {
  width: 120px;
  height: 120px;
  object-fit: cover;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.step-actions {
  margin-top: 1.5rem;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  border-top: 1px solid var(--border-color);
  padding-top: 1.25rem;
}

.confirm-panel {
  text-align: center;
  padding: 1rem 0;
}

.confirm-panel .step-actions {
  justify-content: center;
}

.confirm-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.5rem;
}

.confirm-subtitle {
  font-size: 0.875rem;
  color: #888;
  margin: 0 0 1.5rem;
}

.preview-container {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin: 1.5rem 0;
}

.preview-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
  background: #fafafa;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  min-width: 130px;
}

.preview-item img {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: 10px;
  margin-bottom: 0.75rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.preview-item .preview-label {
  margin: 0;
}

.arrow-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ccc;
  flex-shrink: 0;
}

.arrow-icon svg {
  width: 32px;
  height: 32px;
}

.success-panel {
  text-align: center;
  padding: 1rem 0;
}

.success-actions {
  justify-content: center;
}

.event-footer {
  background: #333;
  color: rgba(255, 255, 255, 0.7);
  text-align: center;
  padding: 1rem;
  font-size: 0.75rem;
  position: relative;
  z-index: 10;
}

.footer-content {
  position: relative;
  z-index: 2;
  line-height: 1.6;
}

.notes-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 1;
  pointer-events: none;
}

.note {
  position: absolute;
  color: rgba(255, 221, 238, 0.1);
  font-size: 2rem;
  animation: float 6s ease-in-out infinite;
}

.note-1 { top: 20%; left: 10%; animation-delay: 0s; font-size: 2.5rem; }
.note-2 { top: 40%; right: 15%; animation-delay: 1s; font-size: 2rem; }
.note-3 { bottom: 30%; left: 40%; animation-delay: 2s; font-size: 3rem; }

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes float {
  0%, 100% { transform: translateY(0) rotate(0deg); opacity: 0.1; }
  50% { transform: translateY(-10px) rotate(5deg); opacity: 0.2; }
}

:deep(.el-result__title p) {
  color: var(--text-color);
}

:deep(.el-input__inner) {
  font-size: 16px;
}

@media (min-width: 768px) {
  .event-header {
    padding: 1.5rem;
  }

  .event-title {
    font-size: 1.75rem;
  }

  .event-content {
    padding: 2rem;
  }

  .content-card {
    max-width: 800px;
  }

  .step-content {
    padding: 2rem;
  }

  .avatar-preview-img {
    width: 140px;
    height: 140px;
  }

  .preview-item {
    min-width: 160px;
    padding: 1.25rem;
  }

  .preview-item img {
    width: 120px;
    height: 120px;
  }
}

@media (max-width: 480px) {
  .event-header {
    padding: 1rem 0.75rem;
  }

  .event-title {
    font-size: 1.25rem;
    margin-bottom: 0.5rem;
  }

  .modern-steps {
    gap: 0.25rem;
  }

  .step-item {
    padding: 0.375rem 0.5rem;
  }

  .step-item.is-active {
    padding: 0.375rem 0.75rem;
  }

  .step-icon {
    width: 24px;
    height: 24px;
    font-size: 0.75rem;
  }

  .step-icon svg {
    width: 14px;
    height: 14px;
  }

  .step-title {
    font-size: 0.8125rem;
  }

  .event-content {
    padding: 0.75rem;
  }

  .card-header {
    padding: 0.75rem;
  }

  .step-content {
    padding: 1rem;
  }

  .qq-input-row {
    flex-direction: column;
  }

  .fetch-btn {
    width: 100%;
  }

  .preview-container {
    flex-direction: column;
    gap: 0.75rem;
  }

  .preview-item {
    width: 100%;
    max-width: 200px;
  }

  .arrow-icon {
    transform: rotate(90deg);
  }

  .step-actions {
    flex-direction: column-reverse;
    align-items: stretch;
  }

  .step-actions :deep(.el-button) {
    width: 100%;
    margin: 0;
  }

  .confirm-panel .step-actions,
  .success-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .event-footer {
    padding: 0.875rem 0.5rem;
    font-size: 0.6875rem;
  }
}
</style>