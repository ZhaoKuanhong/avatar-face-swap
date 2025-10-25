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
            <el-button @click="zoomOut" :disabled="stageScale <= 0.1" title="缩小" :icon="Minus"></el-button>
            <el-button @click="zoomIn" :disabled="stageScale >= 3" title="放大" :icon="Plus"></el-button>
          </el-button-group>
          <span class="zoom-display">{{ Math.round(stageScale * 100) }}%</span>
          <el-button size="small" @click="resetZoom" title="重置缩放" :icon="RefreshLeft"></el-button>
        </div>

        <!-- 操作控制 -->
        <div class="action-controls">
          <el-button-group size="small">
            <el-button @click="undo" :disabled="!canUndo" title="撤销" :icon="Back"></el-button>
            <el-button @click="redo" :disabled="!canRedo" title="重做" :icon="Right"></el-button>
          </el-button-group>
        </div>

        <!-- 手动添加人脸控制 -->
        <div class="manual-face-controls">
          <el-button 
            size="small" 
            @click="toggleManualFaceMode" 
            :type="isManualFaceMode ? 'primary' : ''"
            :icon="Plus"
            title="手动添加人脸"
          >
            添加人脸
          </el-button>
        </div>
      </div>

      <div class="toolbar-section">
        <!-- 视图控制 -->
        <div class="view-controls">
          <el-button size="small" @click="toggleFullscreen" :type="isFullscreen ? 'primary' : ''" title="全屏" :icon="FullScreen"></el-button>
        </div>

        <!-- 导出控制 -->
        <div class="export-controls">
          <el-dropdown @command="handleExport" size="small">
            <el-button type="primary" :loading="exporting" :disabled="!stageReady" :icon="Download">
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

        <!-- Konva 画布 -->
        <div class="stage-wrapper">
          <v-stage
              ref="stage"
              :config="stageConfig"
              @wheel="handleWheel"
              @mousedown="handleStageMouseDown"
              @mousemove="updateDrawingFace"
              @mouseup="finishDrawingFace"
              @touchstart="handleStageMouseDown"
              @touchmove="updateDrawingFace"
              @touchend="finishDrawingFace"
          >
            <v-layer ref="bgLayer">
              <!-- 背景图 -->
              <v-image
                  v-if="backgroundImage"
                  :config="backgroundConfig"
              />
            </v-layer>

            <v-layer ref="faceLayer">
              <!-- 人脸图片 -->
              <v-image
                  v-for="face in faceImages"
                  :key="face.id"
                  :config="face.config"
                  @click="handleFaceClick"
                  @tap="handleFaceClick"
                  @dragstart="handleFaceDragStart"
                  @dragend="handleFaceDragEnd"
                  @transformend="handleFaceTransform"
              />
            </v-layer>

            <v-layer ref="uiLayer">
              <!-- 变换控制器 -->
              <v-transformer
                  ref="transformer"
                   :config="transformerConfig"
              />
              
              <!-- 手动绘制人脸框 -->
              <v-rect
                  v-if="drawingRect"
                  :config="drawingRect"
              />
            </v-layer>
          </v-stage>
        </div>

        <!-- 画布控制工具 -->
        <div class="canvas-controls" v-show="stageReady && !loading">
          <div class="canvas-toolbar">
            <el-tooltip content="适应屏幕" placement="left">
              <el-button size="small" @click="fitToScreen" circle :icon="FullScreen"></el-button>
            </el-tooltip>
            <el-tooltip content="实际大小" placement="left">
              <el-button size="small" @click="actualSize" circle :icon="View"></el-button>
            </el-tooltip>
            <el-tooltip content="居中显示" placement="left">
              <el-button size="small" @click="centerStage" circle :icon="Location"></el-button>
            </el-tooltip>
          </div>
        </div>

        <!-- 快捷键提示 -->
        <div class="shortcuts-hint" v-show="showShortcuts">
          <div class="shortcut-item">
            <kbd>Delete</kbd> 删除选中对象
          </div>
          <div class="shortcut-item">
            <kbd>Ctrl+Z</kbd> 撤销
          </div>
          <div class="shortcut-item">
            <kbd>Ctrl+Y</kbd> 重做
          </div>
          <div class="shortcut-item">
            <kbd>滚轮</kbd> 缩放画布
          </div>
          <div class="shortcut-item">
            <kbd>+/-</kbd> 缩放按钮
          </div>
          <div class="shortcut-item" v-if="isManualFaceMode">
            <kbd>拖拽</kbd> 绘制人脸框
          </div>
        </div>
        
        <!-- 手动添加模式提示 -->
        <div class="manual-mode-hint" v-show="isManualFaceMode">
          <div class="hint-content">
            <div class="hint-icon">✨</div>
            <div class="hint-text">
              <strong>手动添加人脸模式</strong><br>
              在图片上拖拽绘制矩形框选人脸区域
            </div>
            <div class="hint-actions">
              <el-button size="small" @click="toggleManualFaceMode">退出模式</el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 状态栏 -->
    <div class="status-bar">
      <div class="status-left">
        <span class="status-item">
          <Edit />
          {{ canvasWidth }} × {{ canvasHeight }}
        </span>
        <span class="status-item" v-if="selectedFace">
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
import { apiClient } from "@/api/axios.js"
import {
    ArrowDown,
    Back,
    Download,
    Edit,
    FullScreen,
    Location,
    Minus, Plus,
    QuestionFilled,
    RefreshLeft,
    Right,
    Timer,
    View
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const eventId = route.params.event_id

defineProps({
  eventId: {
    type: String,
    required: true
  }
})

// 基础状态
const canvasContainer = ref(null)
const stage = ref(null)
const layer = ref(null)
const transformer = ref(null)
const canvasWidth = ref(0)
const canvasHeight = ref(0)
const stageReady = ref(false)

// 加载状态
const loading = ref(false)
const loadingText = ref('')
const loadingProgress = ref(0)
const loadingDetails = ref('')
const loadedFacesCount = ref(0)

// UI状态
const isFullscreen = ref(false)
const showShortcuts = ref(false)
const selectedFace = ref(null)
const lastModified = ref(new Date())
const isManualFaceMode = ref(false)
const isDrawing = ref(false)
const drawingStartPos = ref({ x: 0, y: 0 })
const drawingCurrentPos = ref({ x: 0, y: 0 })
const drawingRect = ref(null)

// 缩放和视图
const stageScale = ref(1)
const stageX = ref(0)
const stageY = ref(0)

// 导出状态
const exporting = ref(false)

// 历史记录管理
const history = ref([])
const historyIndex = ref(-1)
const isUndoRedo = ref(false) // 防止撤回/重做时触发新的历史记录

// Konva 相关状态
const backgroundImage = ref(null)
const faceImages = ref([])

// Stage 配置
const stageConfig = computed(() => ({
  width: canvasContainer.value?.clientWidth || 800,
  height: canvasContainer.value?.clientHeight || 600,
  scaleX: stageScale.value,
  scaleY: stageScale.value,
  x: stageX.value,
  y: stageY.value,
  draggable: !isManualFaceMode.value // 手动添加人脸模式下禁用拖拽
}))

// 背景图配置
const backgroundConfig = computed(() => ({
  image: backgroundImage.value,
  x: 0,
  y: 0,
  listening: false
}))

// 计算属性
const canUndo = computed(() => historyIndex.value > 0)
const canRedo = computed(() => historyIndex.value < history.value.length - 1)

// 变换器配置
const transformerConfig = ref({
  rotateEnabled: true,
  borderStroke: '#FF3377',
  borderStrokeWidth: 2,
  anchorStroke: '#FF3377',
  anchorFill: '#FF3377',
  anchorSize: 12,
  keepRatio: false,
  enabledAnchors: ['top-left', 'top-right', 'bottom-left', 'bottom-right', 'middle-left', 'middle-right', 'top-center', 'bottom-center']
})

// 并发控制类
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
    const res = await apiClient.get(`/events/${eventId}/faces/upload/${filename}`, {
      responseType: 'blob'
    })
    return URL.createObjectURL(res.data)
  } catch (err) {
    console.warn(`User uploaded image ${filename} not found, using default`)
    return '/default-face.png'  // 使用SVG默认头像
  }
}
// 历史记录管理
const saveState = () => {
  if (isUndoRedo.value || !stageReady.value) return // 防止撤回/重做时保存状态

  const state = {
    faces: faceImages.value.map(face => ({
      ...face,
      config: { ...face.config }
    })),
    timestamp: Date.now()
  }

  // 清除重做历史
  if (historyIndex.value < history.value.length - 1) {
    history.value = history.value.slice(0, historyIndex.value + 1)
  }

  history.value.push(state)

  // 限制历史记录大小
  const maxHistorySize = 50
  if (history.value.length > maxHistorySize) {
    history.value.shift()
  } else {
    historyIndex.value++
  }

  lastModified.value = new Date()
}

const undo = () => {
  if (!canUndo.value) return

  isUndoRedo.value = true
  historyIndex.value--
  const state = history.value[historyIndex.value]

  faceImages.value = state.faces.map(face => ({
    ...face,
    config: { ...face.config }
  }))

  // 清除选择
  if (transformer.value?.getNode()) {
    transformer.value.getNode().nodes([])
  }
  selectedFace.value = null

  setTimeout(() => {
    isUndoRedo.value = false
  }, 100)
}

const redo = () => {
  if (!canRedo.value) return

  isUndoRedo.value = true
  historyIndex.value++
  const state = history.value[historyIndex.value]

  faceImages.value = state.faces.map(face => ({
    ...face,
    config: { ...face.config }
  }))

  // 清除选择
  if (transformer.value?.getNode()) {
    transformer.value.getNode().nodes([])
  }
  selectedFace.value = null

  setTimeout(() => {
    isUndoRedo.value = false
  }, 100)
}

// 图片加载辅助函数
const loadImage = (src) => {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.crossOrigin = 'anonymous'
    img.onload = () => resolve(img)
    img.onerror = reject
    img.src = src
  })
}

// 缩放控制
const zoomIn = () => {
  if (stageScale.value < 3) {
    stageScale.value = Math.min(3, stageScale.value * 1.2)
  }
}

const zoomOut = () => {
  if (stageScale.value > 0.1) {
    stageScale.value = Math.max(0.1, stageScale.value / 1.2)
  }
}

const resetZoom = () => {
  stageScale.value = 1
  stageX.value = 0
  stageY.value = 0
}

const fitToScreen = () => {
  if (!canvasContainer.value) return

  const container = canvasContainer.value
  const containerWidth = container.clientWidth - 40
  const containerHeight = container.clientHeight - 40

  const scaleX = containerWidth / canvasWidth.value
  const scaleY = containerHeight / canvasHeight.value

  stageScale.value = Math.min(scaleX, scaleY, 1)
  stageX.value = 0
  stageY.value = 0
}

const actualSize = () => {
  stageScale.value = 1
  stageX.value = 0
  stageY.value = 0
}

const centerStage = () => {
  stageX.value = 0
  stageY.value = 0
}

// 滚轮缩放
const handleWheel = (e) => {
  e.evt.preventDefault()

  const scaleBy = 1.1
  const stage = e.target.getStage()
  const oldScale = stage.scaleX()
  const pointer = stage.getPointerPosition()

  const mousePointTo = {
    x: (pointer.x - stage.x()) / oldScale,
    y: (pointer.y - stage.y()) / oldScale,
  }

  const newScale = e.evt.deltaY > 0 ? oldScale / scaleBy : oldScale * scaleBy
  const clampedScale = Math.max(0.1, Math.min(3, newScale))

  stageScale.value = clampedScale
  
  // 在手动添加人脸模式下，保持画布位置不变，避免干扰绘制操作
  if (!isManualFaceMode.value) {
    stageX.value = pointer.x - mousePointTo.x * clampedScale
    stageY.value = pointer.y - mousePointTo.y * clampedScale
  }
}

// 事件处理
const handleStageMouseDown = (e) => {
  // 如果是手动添加人脸模式
  if (isManualFaceMode.value && e.target === e.target.getStage()) {
    startDrawingFace(e)
    return
  }
  
  // 点击空白区域取消选择
  if (e.target === e.target.getStage()) {
    if (transformer.value?.getNode()) {
      transformer.value.getNode().nodes([])
    }
    selectedFace.value = null
  }
}

const handleFaceClick = (e) => {
  const clickedNode = e.target
  selectedFace.value = clickedNode
  clickedNode.moveToTop()

  // 设置变换器
  const transformerNode = transformer.value.getStage();
  transformerNode.nodes([clickedNode]);

  lastModified.value = new Date()
}

const handleFaceDragStart = (e) => {
  selectedFace.value = e.target
  // 确保变换器绑定到当前拖拽的对象
  if (transformer.value?.getNode()) {
    transformer.value.getNode().nodes([e.target])
  }
}

const handleFaceDragEnd = (e) => {
  lastModified.value = new Date()
  saveState() // 添加状态保存
}

const handleFaceTransform = (e) => {
  lastModified.value = new Date()
  saveState() // 添加状态保存
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
  if (!stage.value || !stageReady.value) return;

  exporting.value = true;
  const stageNode = stage.value.getNode();

  // 1. 保存当前视图状态 (尺寸, 缩放, 位置, 选中对象)
  const currentScale = stageScale.value;
  const currentX = stageX.value;
  const currentY = stageY.value;
  const currentWidth = stageNode.width();
  const currentHeight = stageNode.height();
  const currentSelection = selectedFace.value;

  try {
    // 临时取消选择以避免导出选择框
    if (transformer.value?.getNode()) {
      transformer.value.getNode().nodes([]);
    }
    selectedFace.value = null;

    // 2. 临时重置 Stage 以进行全尺寸、无缩放的导出
    stageScale.value = 1;
    stageX.value = 0;
    stageY.value = 0;
    // 直接设置 Konva Stage 的尺寸为背景图的原始尺寸
    stageNode.width(canvasWidth.value);
    stageNode.height(canvasHeight.value);

    // 3. 等待 Vue 和 Konva 应用上述更改
    await nextTick();

    // 4. 配置并执行导出
    const [format, quality] = command.split('-');
    const pixelRatio = quality === 'high' ? 2 : 1;
    const mimeType = format === 'png' ? 'image/png' : 'image/jpeg';
    const qualityValue = quality === 'high' ? 0.95 : 0.8;

    const dataUrl = stageNode.toDataURL({
      mimeType,
      quality: qualityValue,
      pixelRatio,
      // 显式定义导出区域为背景图的完整尺寸，确保万无一失
      x: 0,
      y: 0,
      width: canvasWidth.value,
      height: canvasHeight.value,
    });

    // 创建链接并触发下载
    const link = document.createElement('a');
    link.href = dataUrl;
    link.download = `composed_image_${eventId}_${Date.now()}.${format}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    ElMessage.success('图片导出成功');

  } catch (error) {
    console.error('Export failed:', error);
    ElMessage.error('导出失败，请重试');
  } finally {
    // 5. 无论成功与否，在 finally 块中恢复用户的原始视图状态

    // 恢复 Stage 的原始尺寸和视图
    stageNode.width(currentWidth);
    stageNode.height(currentHeight);
    stageScale.value = currentScale;
    stageX.value = currentX;
    stageY.value = currentY;

    // 恢复之前的选中状态
    if (currentSelection && transformer.value?.getNode()) {
      selectedFace.value = currentSelection;
      transformer.value.getNode().nodes([currentSelection]);
    }

    // 等待UI恢复
    await nextTick();

    exporting.value = false;
  }
};

// 手动添加人脸相关函数
const toggleManualFaceMode = () => {
  isManualFaceMode.value = !isManualFaceMode.value
  if (isManualFaceMode.value) {
    // 进入手动模式时清除选择
    if (transformer.value?.getNode()) {
      transformer.value.getNode().nodes([])
    }
    selectedFace.value = null
    
    // 改变鼠标样式
    const stageContainer = stage.value?.getNode()?.container()
    if (stageContainer) {
      stageContainer.style.cursor = 'crosshair'
    }
    
    // 显示手动模式提示
    ElMessage.info('已进入手动添加人脸模式，此时画布固定不可拖拽')
  } else {
    // 退出手动模式
    cleanupDrawing()
    const stageContainer = stage.value?.getNode()?.container()
    if (stageContainer) {
      stageContainer.style.cursor = 'default'
    }
    
    ElMessage.success('已退出手动添加人脸模式，画布现在可以拖拽')
  }
}

const startDrawingFace = (e) => {
  if (!isManualFaceMode.value) return
  
  const stageNode = stage.value.getNode()
  const pos = stageNode.getPointerPosition()
  
  // 转换屏幕坐标到画布坐标
  const x = (pos.x - stageX.value) / stageScale.value
  const y = (pos.y - stageY.value) / stageScale.value
  
  drawingStartPos.value = { x, y }
  drawingCurrentPos.value = { x, y }
  isDrawing.value = true
  
  // 创建绘制矩形
  drawingRect.value = {
    x: x,
    y: y,
    width: 0,
    height: 0,
    stroke: '#FF3377',
    strokeWidth: 2,
    fill: 'rgba(255, 51, 119, 0.2)',
    dash: [5, 5],
    listening: false
  }
}

const updateDrawingFace = (e) => {
  if (!isDrawing.value || !isManualFaceMode.value) return
  
  const stageNode = stage.value.getNode()
  const pos = stageNode.getPointerPosition()
  
  // 转换屏幕坐标到画布坐标
  const x = (pos.x - stageX.value) / stageScale.value
  const y = (pos.y - stageY.value) / stageScale.value
  
  drawingCurrentPos.value = { x, y }
  
  if (drawingRect.value) {
    const startX = drawingStartPos.value.x
    const startY = drawingStartPos.value.y
    
    const rectX = Math.min(startX, x)
    const rectY = Math.min(startY, y)
    const rectW = Math.abs(x - startX)
    const rectH = Math.abs(y - startY)
    
    drawingRect.value = {
      ...drawingRect.value,
      x: rectX,
      y: rectY,
      width: rectW,
      height: rectH
    }
  }
}

const finishDrawingFace = async (e) => {
  if (!isDrawing.value || !isManualFaceMode.value) return
  
  const rectX = drawingRect.value.x
  const rectY = drawingRect.value.y
  const rectW = drawingRect.value.width
  const rectH = drawingRect.value.height
  
  // 检查矩形是否足够大
  if (rectW < 20 || rectH < 20) {
    ElMessage.warning('人脸区域太小，请绘制一个更大的区域')
    cleanupDrawing()
    return
  }
  
  // 确保坐标在画布范围内
  const x1 = Math.max(0, Math.round(rectX))
  const y1 = Math.max(0, Math.round(rectY))
  const x2 = Math.min(canvasWidth.value, Math.round(rectX + rectW))
  const y2 = Math.min(canvasHeight.value, Math.round(rectY + rectH))
  
  try {
    // 调用API添加人脸
    const response = await apiClient.post(`/events/${eventId}/faces/add-manual`, {
      x1, y1, x2, y2,
      face_id: `manual_${Date.now()}`
    })
    
    const faceInfo = response.data.face_info
    
    // 添加到本地人脸列表
    await addManualFaceToStage(faceInfo)
    
    ElMessage.success('人脸添加成功！')
    loadedFacesCount.value++
    lastModified.value = new Date()
    saveState()
    
  } catch (error) {
    console.error('添加人脸失败:', error)
    ElMessage.error('添加人脸失败：' + (error.response?.data?.error || '服务器错误'))
  } finally {
    cleanupDrawing()
  }
}

const addManualFaceToStage = async (faceInfo) => {
  try {
    // 创建默认人脸图像（使用SVG占位符）
    const defaultFaceUrl = '/default-face.png'  // 使用SVG默认头像
    const img = await loadImage(defaultFaceUrl)
    
    const { coordinates } = faceInfo
    
    const newFace = {
      id: faceInfo.face_id,      config: {
        id: faceInfo.face_id,
        image: img,
        x: coordinates.x1,
        y: coordinates.y1,
        scaleX: (coordinates.x2 - coordinates.x1) / img.width,
        scaleY: (coordinates.y2 - coordinates.y1) / img.height,
        draggable: true,
        name: 'face',
        opacity: 0.7  // 手动添加的稍微透明，表示需要上传头像
      }
    }
    
    faceImages.value.push(newFace)
    
  } catch (error) {
    console.error('添加人脸到舞台失败:', error)
    // 使用简单的矩形作为占位符
    const { coordinates } = faceInfo
    
    const newFace = {
      id: faceInfo.face_id,
      config: {
        id: faceInfo.face_id,
        x: coordinates.x1,
        y: coordinates.y1,
        width: coordinates.x2 - coordinates.x1,
        height: coordinates.y2 - coordinates.y1,
        fill: 'rgba(255, 51, 119, 0.3)',
        stroke: '#FF3377',
        strokeWidth: 2,
        draggable: true,
        name: 'face'
      }
    }
    
    faceImages.value.push(newFace)
  }
}

const cleanupDrawing = () => {
  isDrawing.value = false
  drawingRect.value = null
  drawingStartPos.value = { x: 0, y: 0 }
  drawingCurrentPos.value = { x: 0, y: 0 }
}

// 工具函数
const getSelectedObjectName = () => {
  if (!selectedFace.value) return ''
  const id = selectedFace.value.attrs.id
  return id ? `人脸 ${id}` : '未知对象'
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
    // 检查是否在输入框中
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
      return
    }

    // 阻止浏览器默认行为
    if (e.ctrlKey || e.metaKey) {
      if (e.key === 'z' || e.key === 'y') {
        e.preventDefault()
      }
    }

    if ((e.key === 'Delete' || e.key === 'Backspace') && selectedFace.value) {
      e.preventDefault()
      // 删除选中的人脸
      const faceId = selectedFace.value.attrs.id
      const index = faceImages.value.findIndex(f => f.id === faceId)
      if (index > -1) {
        faceImages.value.splice(index, 1)
        selectedFace.value = null
        if (transformer.value?.getNode()) {
          transformer.value.getNode().nodes([])
        }
        loadedFacesCount.value--
        lastModified.value = new Date()
        saveState() // 添加状态保存
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

  // 绑定到 window 确保能捕获到事件
  window.addEventListener('keydown', handleKeyDown, true)

  return () => {
    window.removeEventListener('keydown', handleKeyDown, true)
  }
}

// 初始化Stage
const initStage = async () => {
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

    // 等待下一帧确保DOM更新
    await nextTick()

    loadingProgress.value = 20

    // 加载背景图
    loadingDetails.value = '加载背景图片'
    const bgUrl = await fetchBackground()
    backgroundImage.value = await loadImage(bgUrl)
    loadingProgress.value = 40

    // 获取人脸信息
    loadingDetails.value = '获取人脸信息'
    const facesInfo = await fetchFacesInfo()
    loadingProgress.value = 50

    if (facesInfo.length === 0) {
      loadingProgress.value = 100
      stageReady.value = true
      return
    }

    // 批量加载人脸图片
    loadingDetails.value = '加载人脸图片'
    const loader = new ConcurrentLoader(6)

    const loadTasks = facesInfo.map((face, index) => {
      return async () => {
        const { filename, coordinates } = face
        const faceUrl = await fetchFaceImage(filename)
        const img = await loadImage(faceUrl)

        return {
          id: `face_${index + 1}`,
          config: {
            id: `face_${index + 1}`,
            image: img,
            x: coordinates.x1,
            y: coordinates.y1,
            scaleX: (coordinates.x2 - coordinates.x1) / img.width,
            scaleY: (coordinates.y2 - coordinates.y1) / img.height,
            draggable: true,
            name: 'face'
          }
        }
      }
    })

    const faces = await loader.load(loadTasks, (completed, total) => {
      const progress = 50 + (completed / total) * 40
      loadingProgress.value = progress
      loadingDetails.value = `加载人脸图片 ${completed}/${total}`
    })

    loadingProgress.value = 90
    loadingDetails.value = '完成初始化'

    // 添加人脸到舞台
    faceImages.value = faces
    loadedFacesCount.value = faces.length

    loadingProgress.value = 100
    stageReady.value = true

    // 自动适应屏幕
    setTimeout(() => {
      fitToScreen()
    }, 500)

    console.log(`编辑器初始化完成，共加载 ${loadedFacesCount.value} 个人脸图层`)

    // 保存初始状态
    setTimeout(() => {
      saveState()
    }, 1000)

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
  await initStage()
  const cleanupKeyboard = setupKeyboardEvents()

  onBeforeUnmount(() => {
    cleanupKeyboard()
  })
})

// 监听全屏状态变化
document.addEventListener('fullscreenchange', () => {
  isFullscreen.value = !!document.fullscreenElement
})
</script>

<style scoped>
/* 基础布局 */
.editor-layout {
  display: flex;
  flex-direction: column;
  height: 87vh;
  width: 100%;
  max-width: 100%; /* 🔥 防止被子元素撑开 */
  background: linear-gradient(135deg, rgba(255, 236, 242, 0.3) 0%, rgba(255, 245, 250, 0.3) 100%);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
  overflow: hidden;
  box-sizing: border-box;
  min-width: 0; /* 🔥 允许 flex 子元素缩小 */
}

/* 工具栏样式 */
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0.85));
  border-bottom: 1px solid rgba(196, 30, 58, 0.15);
  box-shadow: 0 4px 16px rgba(196, 30, 58, 0.1);
  z-index: 1000;
  backdrop-filter: blur(10px);
  min-width: 0; /* 🔥 允许工具栏缩小 */
  box-sizing: border-box;
}

.toolbar-section {
  display: flex;
  align-items: center;
  gap: 20px;
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 600;
  color: #1e293b;
}

.title {
  font-size: 18px;
  color: #C41E3A;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(196, 30, 58, 0.1);
}

.center-tools {
  flex: 1;
  justify-content: center;
  max-width: 700px;
}

.zoom-controls, .action-controls, .view-controls, .export-controls, .manual-face-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.zoom-display {
  min-width: 65px;
  font-size: 13px;
  color: #64748b;
  text-align: center;
  font-weight: 600;
  background: rgba(148, 163, 184, 0.1);
  padding: 4px 8px;
  border-radius: 6px;
}

/* 主编辑区域 */
.editor-main {
  flex: 1;
  display: flex;
  overflow: hidden;
  position: relative;
  width: 100%;
  max-width: 100%; /* 🔥 防止被子元素撑开 */
  min-width: 0; /* 🔥 允许 flex 子元素缩小 */
  box-sizing: border-box;
}

.editor-main.fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 9999;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
}

/* 画布容器 */
.canvas-container {
  flex: 1;
  position: relative;
  overflow: hidden !important; /* 🔥 强制隐藏溢出 */
  background: linear-gradient(135deg, rgba(255, 245, 250, 0.5) 0%, rgba(255, 236, 242, 0.5) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  width: 100%;
  max-width: 100%; /* 🔥 防止被子元素撑开 */
  min-width: 0; /* 🔥 允许 flex 子元素缩小 */
  box-sizing: border-box;
}

/* Stage 包裹层 - 关键：防止内容溢出 */
.stage-wrapper {
  position: relative;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  background: #ffffff;
  overflow: hidden !important; /* 🔥 强制隐藏溢出 */
  transition: all 0.3s ease;
  /* 🔥 填满父容器 */
  width: 100%;
  height: 100%;
  max-width: 100%;
  max-height: 100%;
  box-sizing: border-box;
}

.stage-wrapper:hover {
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

/* 🔥 确保 Konva 生成的容器也填满并被限制 */
.stage-wrapper > div {
  overflow: hidden !important;
  max-width: 100% !important;
  max-height: 100% !important;
  width: 100% !important;
  height: 100% !important;
  box-sizing: border-box;
}

/* 加载状态 */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(248, 250, 252, 0.95) 0%, rgba(241, 245, 249, 0.95) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(8px);
}

.loading-content {
  text-align: center;
  padding: 40px;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.12);
  min-width: 350px;
  border: 1px solid #e2e8f0;
}

.loading-spinner {
  width: 56px;
  height: 56px;
  border: 4px solid #e2e8f0;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

.loading-text {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 20px;
}

.progress-container {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 12px;
}

.progress-bar {
  flex: 1;
  height: 10px;
  background: #e2e8f0;
  border-radius: 6px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #6366f1);
  border-radius: 6px;
  transition: width 0.3s ease;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.progress-text {
  font-size: 13px;
  color: #64748b;
  min-width: 45px;
  text-align: right;
  font-weight: 600;
}

.loading-details {
  font-size: 13px;
  color: #94a3b8;
  margin-top: 8px;
}

/* 画布控制工具 */
.canvas-controls {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 100;
}

.canvas-toolbar {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  border: 1px solid #e2e8f0;
  backdrop-filter: blur(8px);
}

/* 快捷键提示 */
.shortcuts-hint {
  position: absolute;
  bottom: 20px;
  left: 20px;
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(51, 65, 85, 0.95) 100%);
  color: white;
  padding: 16px;
  border-radius: 12px;
  font-size: 13px;
  z-index: 100;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* 手动添加模式提示 */
.manual-mode-hint {
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: linear-gradient(135deg, rgba(255, 51, 119, 0.95) 0%, rgba(255, 102, 153, 0.95) 100%);
  color: white;
  padding: 16px 20px;
  border-radius: 12px;
  font-size: 14px;
  z-index: 200;
  box-shadow: 0 8px 24px rgba(255, 51, 119, 0.3);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  animation: slideInDown 0.3s ease-out;
}

.hint-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.hint-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.hint-text {
  flex: 1;
  line-height: 1.4;
}

.hint-text strong {
  font-size: 16px;
  margin-bottom: 4px;
  display: block;
}

.hint-actions {
  flex-shrink: 0;
}

.hint-actions .el-button {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
  color: white;
}

.hint-actions .el-button:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
}

.shortcut-item {
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.shortcut-item:last-child {
  margin-bottom: 0;
}

kbd {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.2) 0%, rgba(255, 255, 255, 0.1) 100%);
  padding: 4px 8px;
  border-radius: 6px;
  font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
  font-size: 11px;
  font-weight: 600;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

/* 状态栏 */
.status-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0.85));
  border-top: 1px solid rgba(196, 30, 58, 0.15);
  font-size: 13px;
  color: #64748b;
  box-shadow: 0 -4px 16px rgba(196, 30, 58, 0.1);
  backdrop-filter: blur(10px);
}

.status-left, .status-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
}

.status-item svg {
  width: 16px;
  height: 16px;
  color: #94a3b8;
}

/* 动画 */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes slideInDown {
  0% {
    opacity: 0;
    transform: translateX(-50%) translateY(-20px);
  }
  100% {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

/* 按钮样式优化 */
:deep(.el-button) {
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.2s ease;
}

:deep(.el-button:hover) {
  transform: translateY(-1px);
}

:deep(.el-button--primary) {
  background: linear-gradient(135deg, #C41E3A 0%, #E63462 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(196, 30, 58, 0.3);
}

:deep(.el-button--primary:hover) {
  background: linear-gradient(135deg, #E63462 0%, #FF3377 100%);
  box-shadow: 0 6px 16px rgba(196, 30, 58, 0.4);
}

:deep(.el-button-group .el-button) {
  margin: 0;
}

:deep(.el-tag--info) {
  background: linear-gradient(135deg, rgba(196, 30, 58, 0.1) 0%, rgba(230, 52, 98, 0.1) 100%);
  border-color: rgba(196, 30, 58, 0.2);
  color: #C41E3A;
  font-weight: 600;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .center-tools {
    max-width: 500px;
  }

  .toolbar-section {
    gap: 12px;
  }
  
  .manual-face-controls {
    gap: 8px;
  }
}

@media (max-width: 768px) {
  .toolbar {
    flex-wrap: wrap;
    padding: 12px;
  }

  .center-tools {
    order: 3;
    width: 100%;
    justify-content: center;
    margin-top: 12px;
  }

  .shortcuts-hint {
    display: none;
  }

  .canvas-container {
    padding: 12px;
  }

  .toolbar-section {
    gap: 8px;
  }
  
  .manual-mode-hint {
    position: fixed;
    top: 60px;
    left: 12px;
    right: 12px;
    transform: none;
    font-size: 13px;
  }
  
  .hint-content {
    flex-direction: column;
    gap: 12px;
    text-align: center;
  }
  
  .hint-text {
    text-align: center;
  }
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .editor-layout {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  }

  .toolbar, .status-bar {
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    border-color: #475569;
    color: #e2e8f0;
  }

  .title {
    color: #f1f5f9;
  }

  .canvas-container {
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  }

  .stage-wrapper {
    border-color: #475569;
    background: #0f172a;
  }

  .canvas-toolbar {
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    border-color: #475569;
  }

  .loading-content {
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    color: #e2e8f0;
    border-color: #475569;
  }

  .zoom-display {
    background: rgba(71, 85, 105, 0.3);
    color: #cbd5e1;
  }
}
</style>