<script setup>
import { apiClient } from '@/api/axios';
import { useRoute } from "vue-router";
import { ref, onMounted } from 'vue';

const route = useRoute();
const eventId = route.params.event_id;
const faces = ref([]);
const faceUrlMap = ref({});
const avatarUrlMap = ref({});
const loading = ref(false);

const eventPicUrl = ref(null);

const fetchEventPic = async () => {
  const res = await apiClient.get(`/events/${eventId}/pic`, {
    responseType: 'blob'
  })
  eventPicUrl.value = URL.createObjectURL(res.data)
}

async function fetchFaces() {
  loading.value = true;
  try {
    const response = await apiClient.get(`/events/${eventId}/faces`);
    faces.value = response.data.faces;
    await Promise.all(faces.value.map(loadFaceImage));
    await Promise.all(faces.value.map(loadAvatarImage));
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
    console.error(`加载图片 ${face} 失败`, err);
  }
}

onMounted(() => {
  fetchEventPic();
  fetchFaces();
});

</script>

<template>
  <div class="eventPic">
    <el-image style="max-width: 80vw; max-height: 500px" :src="eventPicUrl"/>
  </div>
  <div class="cropped-faces">
    <div v-if="faces.length > 0" class="face-list">
      <div
        v-for="face in faces"
        :key="face"
        class="face-item"
      >
        <p>{{ face }}</p>
        <img
          v-if="faceUrlMap[face]"
          :src="faceUrlMap[face]"
          :alt="face"
          class="face-image"
          style="height: 100px"
        />
        <img
          v-if="avatarUrlMap[face]"
          :src="avatarUrlMap[face]"
          alt="avatar"
          class="face-image"
          style="height: 100px"
        />

      </div>
    </div>
  </div>

</template>

<style scoped>
.eventPic {
  /* Ensures the event picture takes full width and is centered */
  width: 100%;
  display: flex;
  justify-content: center;
  margin-bottom: 20px; /* Adds some space below the image */
}

.cropped-faces {
  /* Centers the grid of face pairs */
  width: 100%;
  display: flex;
  justify-content: center;
}

.face-list {
  /* Use CSS Grid to arrange face pairs in two columns */
  display: grid;
  grid-template-columns: repeat(2, 1fr); /* Creates two columns of equal width for pairs */
  gap: 30px; /* Space between face pairs and between rows */
  max-width: 80vw; /* Constrain the width of the face list */
  width: 100%; /* Ensure the grid takes available width within its container */
}

.face-item {
  /* Each face-item will now contain a pair of images and a name */
  display: flex;
  flex-direction: column; /* Stacks the name above the image pair */
  align-items: center; /* Centers content horizontally within the item */
  text-align: center; /* Centers the name text */
  padding: 10px;
  border: 1px solid #eee; /* Optional: Add a subtle border */
  border-radius: 8px; /* Optional: Slightly rounded corners */
}

.face-images-pair {
  display: flex; /* Uses flexbox to place the two images side-by-side */
  justify-content: center; /* Centers the pair of images if they don't fill the space */
  align-items: flex-start; /* Aligns images to the top if they have different heights */
  gap: 15px; /* Space between the big head and avatar images */
  margin-top: 10px; /* Space between the name and the image pair */
}

.face-image {
  /* Styles for both big head and avatar images */
  width: 100px; /* Fixed width for consistency */
  height: 100px; /* Fixed height for consistency */
  object-fit: contain; /* Ensures the entire image is visible, no cropping */
  border-radius: 0; /* Remove circular cropping */
}
</style>
