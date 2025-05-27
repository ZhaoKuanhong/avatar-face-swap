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