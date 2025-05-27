<template>
  <div class="qrcode-wrapper">
    <qrcode-vue
      v-if="extraUrl"
      :value="extraUrl"
      :size="200"
      :level="'M'"
    />
    <p v-else>加载中...</p>
  </div>
  <p>活动名称：{{ props.description }}</p>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import QrcodeVue from 'qrcode.vue'
import {apiClient} from "@/api/axios.js";

const props = defineProps({
  eventId: {
    type: [String, Number],
    required: true,
  },
  description:{
    type: String,
    required: false,
  }
});


const extraUrl = ref('')

onMounted(async () => {
  extraUrl.value = ''
  try {
    const res = await apiClient.get(`/events/${props.eventId}/token`)
    const token = res.data?.token
    if (token) {
      extraUrl.value = `https://${window.location.hostname}/event?auth_token=${token}`
    } else {
      console.error(res.data?.error || '未获取到链接')
    }
  } catch (error) {
    console.error('获取二维码链接失败:', error)
  }
})
</script>

<style scoped>
.qrcode-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
</style>