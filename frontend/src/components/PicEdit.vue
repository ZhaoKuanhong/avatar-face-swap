<template>
  <div class="editor-container">
    <button @click="exportCanvas" class="export-btn">导出图片</button>
<!--    <canvas ref="canvasRef" :width="canvasWidth" :height="canvasHeight" /> -->
    <canvas ref="canvasRef" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as fabric from 'fabric'
import { useRoute } from 'vue-router';
import { apiClient } from "@/api/axios.js";

const route = useRoute();
const eventId = route.params.event_id;

defineProps({
  eventId: {
    type: String,
    required: true
  }
})


const canvasRef = ref(null)
let canvasWidth = ref(0)
let canvasHeight = ref(0)
const DEFAULT_FACE_URL = '/default-face.png'


let canvas = null

// 获取背景图 Blob 并生成 URL
const fetchBackground = async () => {
  const res = await apiClient.get(`/events/${eventId}/pic`, {
    responseType: 'blob'
  })
  return URL.createObjectURL(res.data)
}

const fetchBackgroundInfo = async () => {
  const res = await apiClient.get(`/events/${eventId}/pic/info`)
  return res.data.pic_info
}

// 获取所有人脸位置信息（JSON）
const fetchFacesInfo = async () => {
  const res = await apiClient.get(`/events/${eventId}/faces/info`)
  return res.data.faces
}

// 获取某个覆盖图 Blob 并生成 URL
const fetchFaceImage = async (filename) => {
  try {
    const res = await apiClient.get(`/events/${eventId}/faces/upload/${filename}`, {
      responseType: 'blob'
    })
    return URL.createObjectURL(res.data)
  } catch (err) {
    console.warn(`跳过 ${filename}，加载失败，使用默认图`)
    return DEFAULT_FACE_URL
  }
}

// 初始化画布
const initCanvas = async () => {
canvas = new fabric.Canvas(canvasRef.value, {
  width: canvasWidth.value,
  height: canvasHeight.value,
  })

  // 1. 设置背景图
  const bgUrl = await fetchBackground()
  console.log('[bgUrl]', bgUrl)
  fabric.FabricImage.fromURL(bgUrl).then((img) => {
    img.set({
      left: 0,
      top: 0,
      selectable: false,
    });
    canvas.add(img);
  });


  // 2. 添加覆盖图层
  const faces = await fetchFacesInfo()
  for (const face of faces) {
    const { filename, coordinates } = face
    const faceUrl = await fetchFaceImage(filename)
    const width = coordinates.x2 - coordinates.x1
    const height = coordinates.y2 - coordinates.y1

    fabric.FabricImage.fromURL(faceUrl).then((img) => {
       console.log('[faceUrl]', faceUrl)
      img.set({
          left: coordinates.x1,
          top: coordinates.y1,
          scaleX: (coordinates.x2 - coordinates.x1) / img.width,
          scaleY: (coordinates.y2 - coordinates.y1) / img.height,
        })
      canvas.add(img);
      canvas.renderAll();
    });

    document.addEventListener('keydown', (e) => {
    if (e.key === 'Delete' || e.key === 'Backspace') {
      const activeObj = canvas.getActiveObject()
      if (activeObj) {
        canvas.remove(activeObj)
      }
    }
  })

   }
}

// 导出合成图片
const exportCanvas = () => {
  const dataUrl = canvas.toDataURL({
    format: 'png',
    quality: 1.0,
  })
  const link = document.createElement('a')
  link.href = dataUrl
  link.download = 'composed_image.png'
  link.click()
}

onMounted(async () => {
  try {
    const bg_info = await fetchBackgroundInfo()
    console.log('[bg_info]', bg_info)
    canvasWidth.value= bg_info.width
    canvasHeight.value = bg_info.height
    await initCanvas()
  } catch (error) {
    console.error('初始化失败:', error)
  }
})

</script>

<style scoped>

canvas {
  border: 1px solid #ccc;
  display: block;
  margin: 0 auto;
  max-width: 100%;
}

.export-btn {
  margin-top: 10px;
  padding: 8px 16px;
  background: #4caf50;
  color: white;
  border: none;
  cursor: pointer;
  border-radius: 4px;
}
</style>