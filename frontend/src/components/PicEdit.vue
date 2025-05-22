<template>
  <div class="editor-layout">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <div class="toolbar-section">
        <div class="logo-area">
          <span class="title">图片编辑器</span>
          <el-tag size="small" type="info">{{ loadedFacesCount }} 个人脸</el-tag>
        </div>
      </div>

      <div class="toolbar-section center-tools">
        <!-- 缩放控制 -->
        <div class="zoom-controls">
          <el-button-group size="small">
            <el-button @click="zoomOut" :disabled="zoomLevel <= 0.1" title="缩小" :icon="Minus"></el-button>
            <el-button @click="zoomIn" :disabled="zoomLevel >= 3" title="放大" :icon="Plus"></el-button>
          </el-button-group>
          <span class="zoom-display">{{ Math.round(zoomLevel * 100) }}%</span>
          <el-button size="small" @click="resetZoom" title="重置缩放" :icon="RefreshLeft"></el-button>
        </div>

        <!-- 操作控制 -->
<!--        <div class="action-controls">-->
<!--          <el-button-group size="small">-->
<!--            <el-button @click="undo" :disabled="!canUndo" title="撤销" :icon="Back"></el-button>-->
<!--            <el-button @click="redo" :disabled="!canRedo" title="重做" :icon="Right"></el-button>-->
<!--          </el-button-group>-->
<!--        </div>-->
      </div>

      <div class="toolbar-section">
        <!-- 视图控制 -->
        <div class="view-controls">
          <el-button size="small" @click="toggleFullscreen" :type="isFullscreen ? 'primary' : ''" title="全屏" :icon="FullScreen"></el-button>
        </div>

        <!-- 导出控制 -->
        <div class="export-controls">
          <el-dropdown @command="handleExport" size="small">
            <el-button type="primary" :loading="exporting" :disabled="!canvasReady" :icon="Download">
              导出
              <ArrowDown class="el-icon--right" />
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="png-high">PNG (高质量)</el-dropdown-item>
                <el-dropdown-item command="png-medium">PNG (中等质量)</el-dropdown-item>
                <el-dropdown-item command="jpg-high">JPG (高质量)</el-dropdown-item>
                <el-dropdown-item command="jpg-medium">JPG (中等质量)</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </div>

    <!-- 主编辑区域 -->
    <div class="editor-main" :class="{ 'fullscreen': isFullscreen }">
      <!-- 画布容器 -->
      <div class="canvas-container" ref="canvasContainer">
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-overlay">
          <div class="loading-content">
            <div class="loading-spinner"></div>
            <div class="loading-text">{{ loadingText }}</div>
            <div class="progress-container">
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: `${loadingProgress}%` }"></div>
              </div>
              <span class="progress-text">{{ loadingProgress }}%</span>
            </div>
            <div class="loading-details">{{ loadingDetails }}</div>
          </div>
        </div>

        <!-- 画布 -->
        <div class="canvas-wrapper" :style="canvasWrapperStyle">
          <canvas
              ref="canvasRef"
              :class="{ 'canvas-loading': loading }"
              @wheel="handleWheel"
          />
        </div>

        <!-- 画布控制工具 -->
        <div class="canvas-controls" v-show="canvasReady && !loading">
          <div class="canvas-toolbar">
            <el-tooltip content="适应屏幕" placement="left">
              <el-button size="small" @click="fitToScreen" circle :icon="FullScreen"></el-button>
            </el-tooltip>
            <el-tooltip content="实际大小" placement="left">
              <el-button size="small" @click="actualSize" circle :icon="View"></el-button>
            </el-tooltip>
            <el-tooltip content="居中显示" placement="left">
              <el-button size="small" @click="centerCanvas" circle :icon="Location"></el-button>
            </el-tooltip>
          </div>
        </div>

        <!-- 快捷键提示 -->
        <div class="shortcuts-hint" v-show="showShortcuts">
          <div class="shortcut-item">
            <kbd>Delete</kbd> 删除选中对象
          </div>
<!--          <div class="shortcut-item">-->
<!--            <kbd>Ctrl+Z</kbd> 撤销-->
<!--          </div>-->
<!--          <div class="shortcut-item">-->
<!--            <kbd>Ctrl+Y</kbd> 重做-->
<!--          </div>-->
          <div class="shortcut-item">
            <kbd>滚轮</kbd> 缩放画布
          </div>
          <div class="shortcut-item">
            <kbd>+/-</kbd> 缩放按钮
          </div>
        </div>
      </div>
    </div>

    <!-- 状态栏 -->
    <div class="status-bar">
      <div class="status-left">
        <span class="status-item">
          <i class="el-icon-picture"></i>
          {{ canvasWidth }} × {{ canvasHeight }}
        </span>
        <span class="status-item" v-if="selectedObject">
          <Edit />
          {{ getSelectedObjectName() }}
        </span>
      </div>
      <div class="status-right">
        <span class="status-item">
          <Timer />
          {{ formatTime(lastModified) }}
        </span>
        <el-button
            size="small"
            type="text"
            @click="showShortcuts = !showShortcuts"
            :class="{ active: showShortcuts }"
        >
          <QuestionFilled /> 快捷键
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount, computed, nextTick } from 'vue'
import * as fabric from 'fabric'
import { useRoute } from 'vue-router'
import { apiClient } from "@/api/axios.js"
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Picture, Minus, Plus, RefreshLeft, Back, Right,
  FullScreen, Download, ArrowDown, View, Location,
  Edit, Timer, QuestionFilled
} from '@element-plus/icons-vue'

const route = useRoute()
const eventId = route.params.event_id

defineProps({
  eventId: {
    type: String,
    required: true
  }
})

// 基础状态
const canvasRef = ref(null)
const canvasContainer = ref(null)
const canvasWidth = ref(0)
const canvasHeight = ref(0)
const canvas = ref(null)
const canvasReady = ref(false)

// 加载状态
const loading = ref(false)
const loadingText = ref('')
const loadingProgress = ref(0)
const loadingDetails = ref('')
const loadedFacesCount = ref(0)

// UI状态
const isFullscreen = ref(false)
const showShortcuts = ref(false)
const selectedObject = ref(null)
const lastModified = ref(new Date())

// 缩放和视图
const zoomLevel = ref(1)
const panX = ref(0)
const panY = ref(0)

// 导出状态
const exporting = ref(false)

// 操作历史
const history = ref([])
const historyIndex = ref(-1)
const maxHistorySize = 50

// 并发控制
class ConcurrentLoader {
  constructor(concurrency = 6) {
    this.concurrency = concurrency
    this.queue = []
    this.running = 0
  }

  async load(tasks, onProgress = null) {
    return new Promise((resolve) => {
      const results = new Array(tasks.length)
      let completed = 0

      const processBatch = () => {
        while (this.running < this.concurrency && this.queue.length > 0) {
          const { task, index } = this.queue.shift()
          this.running++

          task().then((result) => {
            results[index] = result
            completed++
            this.running--

            if (onProgress) {
              onProgress(completed, tasks.length)
            }

            if (completed === tasks.length) {
              resolve(results.filter(r => r && !r.error))
            } else {
              processBatch()
            }
          }).catch((error) => {
            console.warn(`Task ${index} failed:`, error)
            results[index] = { error }
            completed++
            this.running--

            if (onProgress) {
              onProgress(completed, tasks.length)
            }

            if (completed === tasks.length) {
              resolve(results.filter(r => r && !r.error))
            } else {
              processBatch()
            }
          })
        }
      }

      tasks.forEach((task, index) => {
        this.queue.push({ task, index })
      })

      processBatch()
    })
  }
}

// 计算属性
const canUndo = computed(() => historyIndex.value > 0)
const canRedo = computed(() => historyIndex.value < history.value.length - 1)

const canvasWrapperStyle = computed(() => ({
  transform: `scale(${zoomLevel.value}) translate(${panX.value}px, ${panY.value}px)`,
  transformOrigin: 'center center'
}))

// API函数
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

const fetchFacesInfo = async () => {
  const res = await apiClient.get(`/events/${eventId}/faces/info`)
  return res.data.faces
}

const fetchFaceImage = async (filename) => {
  try {
    // 首先尝试获取用户上传的头像
    const res = await apiClient.get(`/events/${eventId}/faces/upload/${filename}`, {
      responseType: 'blob'
    })
    return URL.createObjectURL(res.data)
  } catch (err) {
    console.warn(`User uploaded image ${filename} not found, using default`)
    // 如果没有上传的头像，使用默认图片
    return '/default-face.png'
  }
}

// 历史记录管理
const saveState = () => {
  if (!canvas.value) return

  const state = {
    objects: canvas.value.toJSON(['id', 'layerType']),
    timestamp: Date.now()
  }

  // 清除重做历史
  if (historyIndex.value < history.value.length - 1) {
    history.value = history.value.slice(0, historyIndex.value + 1)
  }

  history.value.push(state)

  // 限制历史记录大小
  if (history.value.length > maxHistorySize) {
    history.value.shift()
  } else {
    historyIndex.value++
  }

  lastModified.value = new Date()
}

const undo = () => {
  if (!canUndo.value || !canvas.value) return

  historyIndex.value--
  const state = history.value[historyIndex.value]

  canvas.value.loadFromJSON(state.objects, () => {
    canvas.value.renderAll()
  })
}

const redo = () => {
  if (!canRedo.value || !canvas.value) return

  historyIndex.value++
  const state = history.value[historyIndex.value]

  canvas.value.loadFromJSON(state.objects, () => {
    canvas.value.renderAll()
  })
}

// 缩放控制
const zoomIn = () => {
  if (zoomLevel.value < 3) {
    zoomLevel.value = Math.min(3, zoomLevel.value * 1.2)
  }
}

const zoomOut = () => {
  if (zoomLevel.value > 0.1) {
    zoomLevel.value = Math.max(0.1, zoomLevel.value / 1.2)
  }
}

const resetZoom = () => {
  zoomLevel.value = 1
  panX.value = 0
  panY.value = 0
}

const fitToScreen = () => {
  if (!canvasContainer.value || !canvas.value) return

  const container = canvasContainer.value
  const containerWidth = container.clientWidth - 40
  const containerHeight = container.clientHeight - 40

  const scaleX = containerWidth / canvasWidth.value
  const scaleY = containerHeight / canvasHeight.value

  zoomLevel.value = Math.min(scaleX, scaleY, 1)
  panX.value = 0
  panY.value = 0
}

const actualSize = () => {
  zoomLevel.value = 1
  panX.value = 0
  panY.value = 0
}

const centerCanvas = () => {
  panX.value = 0
  panY.value = 0
}

// 修复的滚轮缩放
const handleWheel = (e) => {
  e.preventDefault()
  e.stopPropagation()

  const delta = e.deltaY > 0 ? 0.9 : 1.1
  const newZoom = Math.max(0.1, Math.min(3, zoomLevel.value * delta))
  zoomLevel.value = newZoom
}

// 全屏控制
const toggleFullscreen = () => {
  isFullscreen.value = !isFullscreen.value

  nextTick(() => {
    if (isFullscreen.value) {
      document.documentElement.requestFullscreen?.()
    } else {
      document.exitFullscreen?.()
    }
  })
}

// 导出功能
const handleExport = async (command) => {
  if (!canvas.value || !canvasReady.value) return

  exporting.value = true

  try {
    const [format, quality] = command.split('-')
    let options = {}

    if (format === 'png') {
      options = {
        format: 'png',
        quality: quality === 'high' ? 1.0 : 0.8
      }
    } else {
      options = {
        format: 'jpeg',
        quality: quality === 'high' ? 0.95 : 0.8
      }
    }

    const dataUrl = canvas.value.toDataURL(options)
    const link = document.createElement('a')
    link.href = dataUrl
    link.download = `composed_image_${eventId}_${Date.now()}.${format === 'jpg' ? 'jpg' : 'png'}`

    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    ElMessage.success('图片导出成功')

  } catch (error) {
    console.error('Export failed:', error)
    ElMessage.error('导出失败，请重试')
  } finally {
    exporting.value = false
  }
}

// 工具函数
const getSelectedObjectName = () => {
  if (!selectedObject.value) return ''
  if (selectedObject.value.layerType === 'background') return '背景图片'
  return selectedObject.value.id ? `人脸 ${selectedObject.value.id}` : '未知对象'
}

const formatTime = (date) => {
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 键盘事件
const setupKeyboardEvents = () => {
  const handleKeyDown = (e) => {
    // 防止在输入框中触发
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
      return
    }

    if ((e.key === 'Delete' || e.key === 'Backspace') && selectedObject.value) {
      e.preventDefault()
      if (selectedObject.value.layerType !== 'background') {
        canvas.value.remove(selectedObject.value)
        selectedObject.value = null
        canvas.value.renderAll()
        saveState()
      }
    } else if (e.ctrlKey || e.metaKey) {
      if (e.key === 'z' && !e.shiftKey) {
        e.preventDefault()
        undo()
      } else if ((e.key === 'y') || (e.key === 'z' && e.shiftKey)) {
        e.preventDefault()
        redo()
      }
    } else if (e.key === '+' || e.key === '=') {
      e.preventDefault()
      zoomIn()
    } else if (e.key === '-') {
      e.preventDefault()
      zoomOut()
    }
  }

  document.addEventListener('keydown', handleKeyDown)

  return () => {
    document.removeEventListener('keydown', handleKeyDown)
  }
}

// 初始化Canvas
const initCanvas = async () => {
  try {
    loading.value = true
    loadingText.value = '正在初始化编辑器...'
    loadingProgress.value = 0

    // 获取背景信息
    loadingDetails.value = '获取背景图片信息'
    const bgInfo = await fetchBackgroundInfo()
    canvasWidth.value = bgInfo.width
    canvasHeight.value = bgInfo.height
    loadingProgress.value = 10

    // 创建Canvas
    loadingDetails.value = '创建画布'
    await nextTick()

    canvas.value = new fabric.Canvas(canvasRef.value, {
      width: canvasWidth.value,
      height: canvasHeight.value,
      backgroundColor: '#ffffff'
    })

    loadingProgress.value = 20

    // 加载背景图
    loadingDetails.value = '加载背景图片'
    const bgUrl = await fetchBackground()

    const bgImg = await fabric.FabricImage.fromURL(bgUrl)
    bgImg.set({
      left: 0,
      top: 0,
      selectable: false,
      evented: false,
      layerType: 'background',
      id: 'background'
    })

    canvas.value.add(bgImg)
    loadingProgress.value = 40

    // 获取人脸信息
    loadingDetails.value = '获取人脸信息'
    const facesInfo = await fetchFacesInfo()
    loadingProgress.value = 50

    if (facesInfo.length === 0) {
      loadingProgress.value = 100
      canvasReady.value = true
      saveState()
      return
    }

    // 批量加载人脸图片
    loadingDetails.value = '加载人脸图片'
    const loader = new ConcurrentLoader(6)

    const loadTasks = facesInfo.map((face, index) => {
      return async () => {
        const { filename, coordinates } = face
        const faceUrl = await fetchFaceImage(filename)

        const img = await fabric.FabricImage.fromURL(faceUrl)

        img.set({
          left: coordinates.x1,
          top: coordinates.y1,
          scaleX: (coordinates.x2 - coordinates.x1) / img.width,
          scaleY: (coordinates.y2 - coordinates.y1) / img.height,
          id: `face_${index + 1}`,
          layerType: 'face'
        })

        return img
      }
    })

    const faceImages = await loader.load(loadTasks, (completed, total) => {
      const progress = 50 + (completed / total) * 40
      loadingProgress.value = progress
      loadingDetails.value = `加载人脸图片 ${completed}/${total}`
    })

    loadingProgress.value = 90
    loadingDetails.value = '添加图层到画布'

    // 添加到Canvas
    faceImages.forEach(img => {
      if (img) {
        canvas.value.add(img)
        loadedFacesCount.value++
      }
    })

    loadingProgress.value = 95
    loadingDetails.value = '完成初始化'

    // 渲染画布
    canvas.value.renderAll()

    // 设置事件监听
    canvas.value.on('selection:created', (e) => {
      selectedObject.value = e.target
    })

    canvas.value.on('selection:updated', (e) => {
      selectedObject.value = e.target
    })

    canvas.value.on('selection:cleared', () => {
      selectedObject.value = null
    })

    canvas.value.on('object:modified', () => {
      saveState()
    })

    loadingProgress.value = 100
    canvasReady.value = true

    // 保存初始状态
    saveState()

    // 自动适应屏幕
    setTimeout(() => {
      fitToScreen()
    }, 500)

    console.log(`编辑器初始化完成，共加载 ${loadedFacesCount.value} 个人脸图层`)

  } catch (error) {
    console.error('初始化失败:', error)
    ElMessage.error('初始化失败，请刷新页面重试')
  } finally {
    setTimeout(() => {
      loading.value = false
    }, 800)
  }
}

// 生命周期
onMounted(async () => {
  await initCanvas()
  const cleanupKeyboard = setupKeyboardEvents()

  onBeforeUnmount(() => {
    cleanupKeyboard()
    if (canvas.value) {
      canvas.value.dispose()
    }
  })
})

// 监听全屏状态变化
document.addEventListener('fullscreenchange', () => {
  isFullscreen.value = !!document.fullscreenElement
})
</script>

<style scoped>
.editor-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f7fa;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
}

/* 工具栏样式 */
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  background: white;
  border-bottom: 1px solid #e4e7ed;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  z-index: 1000;
}

.toolbar-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #303133;
}

.logo-area i {
  font-size: 20px;
  color: #409eff;
}

.center-tools {
  flex: 1;
  justify-content: center;
  max-width: 600px;
}

.zoom-controls, .action-controls, .view-controls, .export-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.zoom-display {
  min-width: 60px;
  font-size: 12px;
  color: #606266;
  text-align: center;
  font-weight: 500;
}

/* 主编辑区域 */
.editor-main {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.editor-main.fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 9999;
  background: #f5f7fa;
}

/* 画布容器 */
.canvas-container {
  flex: 1;
  position: relative;
  overflow: hidden;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
}

.canvas-wrapper {
  transition: transform 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

canvas {
  border: 1px solid #d1d5db;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  background: white;
  max-width: calc(100% - 40px);
  max-height: calc(100% - 40px);
  cursor: grab;
}

canvas:active {
  cursor: grabbing;
}

.canvas-loading {
  opacity: 0.7;
  pointer-events: none;
}

/* 加载状态 */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(245, 247, 250, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-content {
  text-align: center;
  padding: 32px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  min-width: 300px;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #e4e7ed;
  border-top: 4px solid #409eff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

.loading-text {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 16px;
}

.progress-container {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #409eff, #79bbff);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 12px;
  color: #606266;
  min-width: 40px;
  text-align: right;
}

.loading-details {
  font-size: 12px;
  color: #909399;
}

/* 画布控制工具 */
.canvas-controls {
  position: absolute;
  top: 16px;
  right: 16px;
  z-index: 100;
}

.canvas-toolbar {
  background: white;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 4px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

/* 快捷键提示 */
.shortcuts-hint {
  position: absolute;
  bottom: 16px;
  left: 16px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 12px;
  border-radius: 6px;
  font-size: 12px;
  z-index: 100;
}

.shortcut-item {
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.shortcut-item:last-child {
  margin-bottom: 0;
}

kbd {
  background: rgba(255, 255, 255, 0.2);
  padding: 2px 6px;
  border-radius: 3px;
  font-family: monospace;
  font-size: 11px;
}

/* 状态栏 */
.status-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  background: white;
  border-top: 1px solid #e4e7ed;
  font-size: 12px;
  color: #606266;
}

.status-left, .status-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.status-item i {
  font-size: 14px;
}

/* 动画 */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .center-tools {
    max-width: 400px;
  }

  .toolbar-section {
    gap: 8px;
  }
}

@media (max-width: 768px) {
  .toolbar {
    flex-wrap: wrap;
    padding: 8px;
  }

  .center-tools {
    order: 3;
    width: 100%;
    justify-content: center;
    margin-top: 8px;
  }

  .shortcuts-hint {
    display: none;
  }

  canvas {
    max-width: calc(100% - 20px);
    max-height: calc(100% - 20px);
  }
}

/* Element Plus 组件样式覆盖 */
:deep(.el-button--small) {
  padding: 7px 15px;
}

:deep(.el-button-group .el-button) {
  margin: 0;
}

:deep(.el-tag--small) {
  height: 20px;
}

:deep(.el-tooltip__popper) {
  font-size: 12px;
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .editor-layout {
    background: #1a1a1a;
  }

  .toolbar, .status-bar {
    background: #2d2d2d;
    border-color: #404040;
    color: #e4e7ed;
  }

  .canvas-container {
    background: #1a1a1a;
  }

  canvas {
    border-color: #404040;
  }

  .canvas-toolbar {
    background: #2d2d2d;
    border: 1px solid #404040;
  }

  .loading-content {
    background: #2d2d2d;
    color: #e4e7ed;
  }
}
</style>