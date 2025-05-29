<template>
   <el-skeleton style="width: 240px; margin: auto;" :loading="loading" animated>
      <template #template>
        <el-skeleton-item variant="image" style="width: 200px; height: 200px" />
        <div style="padding: 10px">
          <el-skeleton-item style="font-size: 15px" />
        </div>
      </template>
   </el-skeleton>

  <div ref="qrcodeContainer"
       v-if="!loading"
       class="qrcode-wrapper">
    <qrcode-vue
      v-if="extraUrl"
      :value="extraUrl"
      :size="200"
      :level="'M'"
    />
    <p v-else>加载中...</p>
    <p style="font-size: 15px">活动名称：{{ props.description }}</p>
  </div>
  <el-button type="primary" @click="downloadQrCode" :icon="Download">Download</el-button>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue' // Import watch
import QrcodeVue from 'qrcode.vue'
import { apiClient } from "@/api/axios.js";
import {Download} from "@element-plus/icons-vue";

const props = defineProps({
  eventId: {
    type: [String, Number],
    required: true,
  },
  description: {
    type: String,
    required: false,
  }
});

const qrcodeContainer = ref();

function downloadQrCode() {
  const canvas = qrcodeContainer.value.querySelector("canvas");
  if (!canvas) {
    console.error("未找到二维码 canvas 元素");
    return;
  }

  const qrSize = canvas.width; // 通常为 200
  const textHeight = 30; // 为文字留空间
  const totalHeight = qrSize + textHeight;

  // 创建一个新 canvas
  const combinedCanvas = document.createElement("canvas");
  combinedCanvas.width = qrSize;
  combinedCanvas.height = totalHeight;

  const ctx = combinedCanvas.getContext("2d");
  if (!ctx) {
    console.error("无法获取 Canvas 上下文");
    return;
  }

  // 绘制原二维码
  ctx.drawImage(canvas, 0, 0);

  // 设置文字样式
  ctx.font = "16px sans-serif";
  ctx.fillStyle = "#000";
  ctx.textAlign = "center";

  // 添加文字（居中显示在下方）
  ctx.fillText(props.description || '', qrSize / 2, qrSize + 20);

  // 下载组合后的图片
  const link = document.createElement("a");
  link.download = "qr-code-with-text.png";
  link.href = combinedCanvas.toDataURL("image/png");
  link.click();
}

const extraUrl = ref('');

// Function to fetch the token and update extraUrl
const fetchToken = async (id) => {
  if (id === '') { // Don't fetch if eventId is not yet available
    extraUrl.value = ''; // Clear previous QR code or show loading
    return;
  }
  try {
    const res = await apiClient.get(`/events/${id}/token`);
    const token = res.data?.token;
    if (token) {
      extraUrl.value = `https://${window.location.hostname}/event?auth_token=${token}`;
    } else {
      extraUrl.value = ''; // Clear QR if no token
      console.error(res.data?.error || '未获取到链接');
    }
  } catch (error) {
    extraUrl.value = ''; // Clear QR on error
    console.error('获取二维码链接失败:', error);
  }
};

const loading = ref(false)
// Watch for changes in props.eventId
watch(() => props.eventId, async (newEventId, oldEventId) => {
  if (newEventId !== oldEventId) {// Ensure it actually changed
    loading.value = true;
    await fetchToken(newEventId);
    loading.value = false;
  }
}, { immediate: true }); // 'immediate: true' will run the watcher once on component mount

// onMounted is no longer strictly necessary for the initial fetch if using immediate watcher,
// but can be kept if there are other mount-specific tasks.
// If fetchToken is only called by the watcher (with immediate:true),
// onMounted can be simplified or removed if it only contained fetchToken.
/*
onMounted(async () => {
  // Initial fetch is now handled by the watcher with immediate: true
  // await fetchToken(props.eventId);
});
*/
</script>

<style scoped>
.qrcode-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
</style>