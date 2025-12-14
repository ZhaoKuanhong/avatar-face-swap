<template>
  <div class="face-selector">
    <h2 class="selector-title">选择你的大头</h2>

    <div v-if="faces.length > 0" class="face-list">
      <div
        v-for="(face, index) in faces"
        :key="face"
        class="face-item"
        @click="selectFace(face)"
        :class="{ selected: selectedFace === face }"
      >
        <div class="face-image-wrapper">
          <img
            v-if="faceUrlMap[face]"
            :src="faceUrlMap[face]"
            :alt="face"
            class="face-image"
            loading="lazy"
          />
          <div v-else class="face-loading">
            <div class="loading-spinner-small"></div>
          </div>
          <div class="face-check" v-if="selectedFace === face">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
          </div>
        </div>
        <span class="face-label">{{ index + 1 }}</span>
      </div>
    </div>
    <div v-else-if="loading" class="loading-skeleton">
      <div class="skeleton-grid">
        <div v-for="i in 8" :key="i" class="skeleton-item">
          <el-skeleton animated>
            <template #template>
              <el-skeleton-item variant="image" class="skeleton-image" />
              <el-skeleton-item variant="text" class="skeleton-text" />
            </template>
          </el-skeleton>
        </div>
      </div>
    </div>
    <div v-else class="empty-state">
      <p>没有找到任何人脸图片</p>
    </div>
    <div v-if="selectedFace" class="selection-hint">
      <span>已选择第 {{ faces.indexOf(selectedFace) + 1 }} 个人脸</span>
    </div>
  </div>
</template>

<script setup>
import { apiClient } from '@/api/axios';
import pLimit from 'p-limit';
import { defineEmits, defineProps, onBeforeUnmount, onMounted, ref } from 'vue';

const props = defineProps({
  eventId: {
    type: String,
    required: true,
  },
});

const emit = defineEmits(['face-selected']);

const faces = ref([]);
const faceUrlMap = ref({});
const loading = ref(false);
const selectedFace = ref(null);
const selectedFaceUrl = ref(null);

onMounted(() => {
  fetchFaces();
});

onBeforeUnmount(() => {
  Object.values(faceUrlMap.value).forEach(url => URL.revokeObjectURL(url));
});

async function fetchFaces() {
  loading.value = true;
  try {
    const response = await apiClient.get(`/events/${props.eventId}/faces`);
    faces.value = response.data.faces;

    if (faces.value.length === 0) {
      return;
    }

    const limit = pLimit(5);

    const loadTasks = faces.value.map(face =>
        limit(() => loadFaceImage(face))
    );

    await Promise.all(loadTasks);

  } catch (error) {
    console.error('获取人脸列表失败:', error);
    faces.value = [];
  } finally {
    loading.value = false;
  }
}

async function loadFaceImage(face) {
  try {
    const response = await apiClient.get(`/events/${props.eventId}/faces/${face}`, {
      responseType: 'blob',
    });
    const blobUrl = URL.createObjectURL(response.data);
    faceUrlMap.value[face] = blobUrl;
  } catch (err) {
    console.error(`加载图片 ${face} 失败`, err);
  }
}

function selectFace(face) {
  selectedFace.value = face;
  selectedFaceUrl.value = faceUrlMap.value[face];
  emit('face-selected', selectedFace.value, selectedFaceUrl.value);
}
</script>

<style scoped>
.face-selector {
  width: 100%;
}

.selector-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 1rem;
  text-align: center;
}

.face-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(90px, 1fr));
  gap: 12px;
  padding: 4px;
}

.face-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: #fff;
  border: 2px solid #eee;
  border-radius: 12px;
  padding: 10px 8px 8px;
  cursor: pointer;
  transition: all 0.25s ease;
  -webkit-tap-highlight-color: transparent;
}

.face-item:hover {
  border-color: #FF3377;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 51, 119, 0.15);
}

.face-item.selected {
  border-color: #FF3377;
  background: linear-gradient(135deg, #fff5f8 0%, #fff 100%);
  box-shadow: 0 4px 16px rgba(255, 51, 119, 0.25);
  transform: translateY(-2px);
}

.face-image-wrapper {
  position: relative;
  width: 100%;
  aspect-ratio: 1;
  max-width: 80px;
  margin: 0 auto;
}

.face-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
}

.face-check {
  position: absolute;
  bottom: -6px;
  right: -6px;
  width: 24px;
  height: 24px;
  background: #FF3377;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(255, 51, 119, 0.4);
}

.face-check svg {
  width: 14px;
  height: 14px;
  color: white;
}

.face-label {
  font-size: 13px;
  font-weight: 500;
  color: #666;
  margin-top: 8px;
}

.face-item.selected .face-label {
  color: #FF3377;
  font-weight: 600;
}

.loading-skeleton {
  padding: 4px;
}

.skeleton-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(90px, 1fr));
  gap: 12px;
}

.skeleton-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px 8px 8px;
  background: #fff;
  border-radius: 12px;
  border: 2px solid #eee;
}

.skeleton-image {
  width: 100% !important;
  max-width: 80px !important;
  aspect-ratio: 1 !important;
  border-radius: 8px !important;
}

.skeleton-text {
  width: 40px !important;
  margin-top: 8px !important;
}

.face-loading {
  width: 100%;
  aspect-ratio: 1;
  max-width: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f8f8;
  border-radius: 8px;
}

.loading-spinner-small {
  width: 24px;
  height: 24px;
  border: 2px solid #eee;
  border-top-color: #FF3377;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: #999;
}

.selection-hint {
  text-align: center;
  margin-top: 1rem;
  padding: 8px 16px;
  background: linear-gradient(135deg, #fff5f8 0%, #fff 100%);
  border-radius: 20px;
  color: #FF3377;
  font-weight: 500;
  font-size: 14px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 480px) {
  .face-list {
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
  }
  
  .face-item {
    padding: 8px 6px 6px;
    border-radius: 10px;
  }
  
  .face-check {
    width: 20px;
    height: 20px;
    bottom: -4px;
    right: -4px;
  }
  
  .face-check svg {
    width: 12px;
    height: 12px;
  }
  
  .face-label {
    font-size: 12px;
    margin-top: 6px;
  }
}

@media (min-width: 481px) and (max-width: 768px) {
  .face-list {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (min-width: 769px) {
  .face-list {
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  }
  
  .face-image-wrapper {
    max-width: 90px;
  }
}
</style>
