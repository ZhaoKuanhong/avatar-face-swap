<template>
  <div class="event-container">
    <div class="event-header">
      <h1 class="event-title">"{{ description }}"大头自助采集</h1>
      <div class="steps-container">
        <el-steps :active="currentStep" finish-status="success" simple>
          <el-step title="选择大头" />
          <el-step title="上传头像" />
          <el-step title="确认" />
          <el-step title="完成" />
        </el-steps>
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
            <h3>输入 QQ 号获取头像</h3>
            <el-row :gutter="20">
              <el-col :span="16">
                <el-input type="number" v-model="qqNumber" placeholder="输入你的 QQ 号"/>
              </el-col>
              <el-col :span="8">
                <el-button @click="fetchQQAvatar" :disabled="!qqNumber || !selectedFace || qqAvatarLoading">
                  {{ qqAvatarLoading ? '获取中...' : '获取 QQ 头像' }}
                </el-button>
              </el-col>
            </el-row>
            <div v-if="isAvatarSelected">
                  <h4>QQ 头像预览:</h4>
                  <div>
                    <img :src="qqAvatarUrl" alt="QQ Avatar" style="max-width: 100px; max-height: 100px;"/>
                  </div>
            </div>

            <div class="step-actions">
              <el-button
                  color="#FF3377"
                  type="primary"
                  :disabled="!isAvatarSelected"
                  @click="completeProcess"
              >
                下一步 <i class="el-icon-check"></i>
              </el-button>
            </div>
          </div>

          <!-- Step 3: Confirm -->
          <div v-show="currentStep === 2" class="step-panel confirm-panel">
            <div class="success-icon">
              <i class="el-icon-check"></i>
            </div>
            <h2>请确认您的选择</h2>
            <p>请确认二者准确无误</p>
            <div class="preview-container">
              <div class="preview-item">
                <img :src="selectedFaceUrl" alt="选择的大头" />
                <p>您选择的大头</p>
              </div>
              <div class="arrow">
                <i class="el-icon-right"></i>
              </div>
              <div class="preview-item">
                <img :src="qqAvatarUrl" alt="上传的头像" />
                <p>您上传的头像</p>
              </div>
            </div>
            <div class="step-actions">
              <el-button @click="resetProcess">重新选择</el-button>
              <el-button color="#FF3377" type="primary" @click="uploadQQAvatar">上传</el-button>
            </div>
          </div>

          <!-- 第四步：完成 -->
          <div v-show="currentStep === 3" class="step-panel success-panel">
            <div class="success-icon">
              <i class="el-icon-check"></i>
            </div>
            <el-result
              :icon="uploadResult"
              :title="uploadMessage"
            />
            <div class="step-actions">
              <el-button color="#FF3377" type="primary" @click="resetProcess">完成另一个</el-button>
              <el-button @click="backToHome">返回首页</el-button>
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
import { ref } from 'vue';
import FaceSelector from '../components/FaceSelector.vue';
import { apiClient } from "@/api/axios.js";
import { useRouter } from 'vue-router';

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
:root {
  --bg-color: linear-gradient(135deg, #ffecf2 0%, #fff5fa 100%);
  --card-bg: #ffffff;
  --text-color: #333;
  --border-color: #eee;
  --primary-color: #FF3377;
  --step-text-color: #333;
}

.dark {
  --bg-color: #121212;
  --card-bg: #ead8d8;
  --text-color: #f5f5f5;
  --border-color: #444;
  --primary-color: #ff6699;
  --step-text-color: #ffffff;
}


.event-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-color);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.event-header {
  background: linear-gradient(135deg, rgba(255, 51, 119, 0.9), #ff3377);
  color: white;
  padding: 1.5rem;
  text-align: center;
  box-shadow: 0 4px 15px rgba(255, 51, 119, 0.2);
  position: relative;
  z-index: 10;
}

.event-title {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 1rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
}

.steps-container {
  max-width: 700px;
  margin: 0 auto;
  background: rgba(255, 255, 255, 0.2);
  padding: 0.8rem;
  border-radius: 8px;
}

.event-content {
  flex: 1;
  padding: 2rem;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  position: relative;
}

.content-card {
  background: var(--card-bg);
  border-color: var(--border-color);
  border-radius: 12px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.05);
  width: 100%;
  max-width: 900px;
  overflow: hidden;
  position: relative;
  z-index: 5;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: rgba(255, 221, 238, 0.3);
  border-bottom: 1px solid rgba(255, 51, 119, 0.1);
}

.step-indicator {
  display: flex;
  align-items: center;
}

.step-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  background: #FF3377;
  color: white;
  border-radius: 50%;
  font-weight: bold;
  margin-right: 10px;
}

.step-text {
  font-size: 1.1rem;
  color: var(--step-text-color);
}

.step-content {
  padding: 2rem;
}

.step-panel {
  animation: fadeIn 0.5s ease-out;
}

.step-actions {
  margin-top: 2rem;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid #eee;
  padding-top: 1.5rem;
}

.confirm-panel {
  text-align: center;
  padding: 2rem 0;
}

.success-panel {
  text-align: center;
  padding: 2rem 0;
}

.success-icon {
  font-size: 4rem;
  color: #52c41a;
  margin-bottom: 1rem;
}

.preview-container {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 2rem 0;
  flex-wrap: wrap;
}

.preview-item {
  padding: 1rem;
  border: 1px solid #eee;
  border-radius: 8px;
  margin: 0 1rem;
  width: 150px;
}

.preview-item img {
  width: 120px;
  height: 120px;
  object-fit: cover;
  border-radius: 4px;
  display: block;
  margin: 0 auto 10px;
}

.arrow {
  font-size: 2rem;
  color: #ccc;
  margin: 0 1rem;
}

.event-footer {
  background: #333;
  color: rgba(255, 255, 255, 0.7);
  text-align: center;
  padding: 1.5rem;
  position: relative;
  z-index: 10;
}

.footer-content {
  position: relative;
  z-index: 2;
}

.notes-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 1;
}

.note {
  position: absolute;
  color: rgba(255, 221, 238, 0.1);
  font-size: 2rem;
  animation: float 6s ease-in-out infinite;
}

.note-1 {
  top: 20%;
  left: 10%;
  animation-delay: 0s;
  font-size: 2.5rem;
}

.note-2 {
  top: 40%;
  right: 15%;
  animation-delay: 1s;
  font-size: 2rem;
}

.note-3 {
  bottom: 30%;
  left: 40%;
  animation-delay: 2s;
  font-size: 3rem;
}

/* 动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

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

/* ElementPlus 组件样式覆盖 */

:deep(.el-steps--simple) {
  background: transparent;
}

:deep(.el-step__title.is-process) {
  color: white;
  font-weight: bold;
}

:deep(.el-step__title.is-wait) {
  color: rgba(255, 255, 255, 0.7);
}

:deep(.el-step__head.is-process) {
  color: white;
  border-color: white;
}

:deep(.el-result__title p) {
  color: var(--step-text-color)
}

@media (max-width: 768px) {
  .event-content {
    padding: 1rem;
  }

  .step-content {
    padding: 1rem;
  }

  .event-title {
    font-size: 1.5rem;
  }

  .preview-container {
    flex-direction: column;
  }

  .preview-item {
    margin: 1rem 0;
  }

  .arrow {
    transform: rotate(90deg);
    margin: 0.5rem 0;
  }
}
</style>