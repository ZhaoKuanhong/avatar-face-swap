<template>
  <div>
    <h2>选择你的大头</h2>

    <div v-if="faces.length > 0" class="face-list">
      <div
        v-for="face in faces"
        :key="face"
        class="face-item"
        @click="selectFace(face)"
        :class="{ selected: selectedFace === face }"
      >
        <img
          v-if="faceUrlMap[face]"
          :src="faceUrlMap[face]"
          :alt="face"
          class="face-image"
          style="height: 100px"
        />
        <p>{{ face }}</p>
      </div>
    </div>
    <p v-else-if="loading">加载人脸中...</p>
    <p v-else>没有找到任何人脸图片。</p>
    <p v-if="selectedFace">你选择了: {{ selectedFace }}</p>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { apiClient } from '@/api/axios';
import {  defineProps, defineEmits } from 'vue';

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
    await Promise.all(faces.value.map(loadFaceImage));
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
.face-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 10px;
}

.face-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 8px;
  cursor: pointer;
  transition: border-color 0.3s ease-in-out, box-shadow 0.3s ease-in-out;
}

.face-item.selected {
  border-color: #409EFF;
  box-shadow: 0 0 8px rgba(64, 158, 255, 0.7);
}

.face-image {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 4px;
  margin-bottom: 5px;
}

.face-name {
  font-size: 12px;
  text-align: center;
  margin-top: 0;
}
</style>
