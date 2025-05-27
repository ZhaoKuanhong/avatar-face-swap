<template>
  <el-container>
    <el-main>
      <!-- 顶部操作区域 -->
      <div class="top-section">
        <div class="page-header">
          <h1 class="page-title">活动管理</h1>
          <p class="page-subtitle">管理所有活动和图片处理</p>
        </div>

        <div class="action-buttons">
          <el-button
              type="primary"
              :icon="Plus"
              @click="dialogFormVisible = true"
              class="add-button"
          >
            <span class="button-text">添加活动</span>
          </el-button>
        </div>
      </div>

      <!-- 添加活动表单对话框 -->
      <el-dialog
          v-model="dialogFormVisible"
          :title="isEditMode ? '编辑活动' : '添加活动'"
          :width="dialogWidth"
          :fullscreen="isMobile"
          class="add-dialog"
      >
        <el-form @submit.prevent label-position="top" class="dialog-form">
          <el-form-item label="event_id">
            <el-input v-model="form.event_id" placeholder="请输入活动 ID" />
          </el-form-item>
          <el-form-item label="活动名称">
            <el-input v-model="form.description" placeholder="请输入活动名称" />
          </el-form-item>
          <el-form-item label="活动日期">
            <el-date-picker
                v-model="form.event_date"
                type="date"
                placeholder="选择日期"
                style="width: 100%"
            />
          </el-form-item>
          <el-form-item label="token">
            <el-input v-model="form.token" placeholder="请输入访问令牌" >
              <template #append>
                <el-button :icon="Refresh" @click="autoGeneratePwd"/>
              </template>
            </el-input>
          </el-form-item>
        </el-form>

        <template #footer>
          <div class="dialog-footer">
            <el-button @click="dialogFormVisible = false" class="cancel-btn">取消</el-button>
            <el-button
                type="primary"
                @click="addEvent"
                :loading="addLoading"
                class="confirm-btn"
            >
                {{ addLoading ? (isEditMode ? '更新中...' : '创建中...') : (isEditMode ? '更新' : '创建') }}
            </el-button>
          </div>
        </template>
      </el-dialog>

      <!-- 二维码对话框 -->
      <el-dialog
          v-model="qrCodeDialogVisible"
          title="收集二维码"
          :width="dialogWidth"
          :fullscreen="isMobile"
          class="add-dialog"
          >
          <QrCodeDisplay :eventId="currentEventId" :description="currentDescription" />
      </el-dialog>


      <!-- 上传图片对话框 -->
      <el-dialog
          v-model="uploadDialogVisible"
          title="上传活动图片"
          :width="dialogWidth"
          :fullscreen="isMobile"
          class="upload-dialog"
      >
        <div class="upload-container">
          <el-upload
              class="upload-dragger"
              drag
              action="#"
              :auto-upload="false"
              :on-change="handleFileChange"
              :file-list="fileList"
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              拖拽图片到此处，或 <em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                请上传JPEG/PNG格式图片，图片应包含多个人脸，系统将自动识别并裁剪
              </div>
            </template>
          </el-upload>

          <div v-if="uploadStatus" class="upload-status">
            <el-alert
                :title="uploadStatus.message"
                :type="uploadStatus.type"
                :description="uploadStatus.description"
                show-icon
            />
          </div>
        </div>

        <template #footer>
          <div class="dialog-footer">
            <el-button @click="uploadDialogVisible = false" class="cancel-btn">取消</el-button>
            <el-button
                type="primary"
                @click="submitUpload"
                :loading="uploadLoading"
                class="confirm-btn"
            >
              {{ uploadLoading ? '上传中...' : '上传并处理' }}
            </el-button>
          </div>
        </template>
      </el-dialog>

      <!-- 活动列表 -->
      <div class="table-section">
        <!-- 桌面端表格 -->
        <el-table
            :data="eventList"
            style="width: 100%"
            stripe
            v-loading="loading"
            class="desktop-table"
            :class="{ 'mobile-hidden': isMobile }"
        >
          <el-table-column prop="event_id" label="event_id" width="150" />
          <el-table-column prop="description" label="description" width="200" />
          <el-table-column prop="event_date" label="event_date" width="150" />

          <el-table-column prop="isOpen" label="开启采集" width="100">
            <template #default="scope">
              <el-switch
                  v-model="scope.row.is_open"
                  @change="(val) => updateEventStatus(scope.row.event_id, val)"
              />
            </template>
          </el-table-column>

          <el-table-column label="操作" min-width="400" fixed="right">
            <template #default="scope">
              <div class="table-actions">
                <el-button type="primary" @click="handleQrCodeShow(scope.row.event_id, scope.row.description)" size="small">
                  <el-icon style="cursor: pointer;">
                    <svg viewBox="0 0 1024 1024" width="20" height="20" fill="currentColor">
                      <path d="M128 128h320v320H128V128zm64 64v192h192V192H192zm384-64h320v320H576V128zm64 64v192h192V192H640zM128 576h320v320H128V576zm64 64v192h192V640H192zM704 576h64v64h-64v-64z m-128 0h64v64h-64v-64z m0 128h192v192H576V704z m64 64v64h64v-64h-64z m128-64h64v64h-64v-64z"/>
                    </svg>
                  </el-icon>
                </el-button>
                <el-button type="primary" @click="handleEventView(scope.row.event_id)" size="small">
                  查看活动
                </el-button>
                <el-button type="primary" @click="editEvent(scope.row)" size="small">
                  编辑活动
                </el-button>
                <el-button type="primary" @click="handleEditPic(scope.row.event_id)" size="small">
                  生成图片
                </el-button>
                <el-button type="success" @click="showUploadDialog(scope.row.event_id)" size="small">
                  上传活动图片
                </el-button>
                <el-popconfirm
                    title="确定要删除这一项吗？"
                    @confirm="deleteEvent(scope.row.event_id)"
                >
                  <template #reference>
                    <el-button type="danger" size="small">删除</el-button>
                  </template>
                </el-popconfirm>
              </div>
            </template>
          </el-table-column>
        </el-table>

        <!-- 移动端卡片列表 -->
        <div class="mobile-cards" :class="{ 'mobile-visible': isMobile }" v-loading="loading">
          <el-card
              v-for="event in eventList"
              :key="event.event_id"
              class="event-card"
              shadow="hover"
          >
            <template #header>
              <div class="card-header">
                <div class="event-info">
                  <h3 class="event-title">{{ event.description }}</h3>
                  <div class="event-meta">
                    <el-tag size="small" type="info">ID: {{ event.event_id }}</el-tag>
                    <span class="event-date">{{ event.event_date }}</span>
                  </div>
                </div>
            <div class="event-actions"> <div class="event-status">
                    <el-switch
                        v-model="event.is_open"
                        @change="(val) => updateEventStatus(event.event_id, val)"
                        :active-text="event.is_open ? '开放' : '关闭'"
                    />
                  </div>
                  <el-button type="primary" @click="handleQrCodeShow(event.event_id, event.description)" size="small" class="qr-code-button"> <el-icon style="cursor: pointer;"> <svg viewBox="0 0 1024 1024" width="20" height="20" fill="currentColor">
                        <path d="M128 128h320v320H128V128zm64 64v192h192V192H192zm384-64h320v320H576V128zm64 64v192h192V192H640zM128 576h320v320H128V576zm64 64v192h192V640H192zM704 576h64v64h-64v-64z m-128 0h64v64h-64v-64z m0 128h192v192H576V704z m64 64v64h64v-64h-64z m128-64h64v64h-64v-64z"/>
                      </svg>
                    </el-icon>
                  </el-button>
                </div>
              </div>
            </template>

            <div class="card-actions">
              <div class="action-row">
                <el-button
                    type="primary"
                    @click="handleEventView(event.event_id)"
                    :icon="View"
                    class="action-button"
                >
                  查看活动
                </el-button>
                <el-button
                    type="primary"
                    @click="handleEditPic(event.event_id)"
                    :icon="Edit"
                    class="action-button"
                >
                  生成图片
                </el-button>
              </div>
              <div class="action-row">
                <el-button
                    type="success"
                    @click="showUploadDialog(event.event_id)"
                    :icon="UploadFilled"
                    class="action-button"
                >
                  上传活动图片
                </el-button>
                <el-popconfirm
                    title="确定要删除这一项吗？"
                    @confirm="deleteEvent(event.event_id)"
                >
                  <template #reference>
                    <el-button
                        type="danger"
                        :icon="Delete"
                        class="action-button"
                    >
                      删除
                    </el-button>
                  </template>
                </el-popconfirm>
              </div>
            </div>
          </el-card>

          <!-- 空状态 -->
          <div v-if="!loading && eventList.length === 0" class="empty-state">
            <el-empty description="暂无活动数据">
              <el-button type="primary" @click="dialogFormVisible = true">创建第一个活动</el-button>
            </el-empty>
          </div>
        </div>
      </div>
    </el-main>
  </el-container>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { ElNotification, ElMessage } from 'element-plus';
import { apiClient } from '@/api/axios';
import {Plus, UploadFilled, View, Edit, Delete, Refresh} from '@element-plus/icons-vue';
import QrCodeDisplay from "@/components/QrCodeDisplay.vue";

// 状态变量定义
const dialogFormVisible = ref(false);
const qrCodeDialogVisible = ref(false)
const loading = ref(true);
const addLoading = ref(false);
const eventList = ref([]);
const router = useRouter();

const isEditMode = ref(false); // false: 新建, true: 编辑

// 图片上传相关状态
const uploadDialogVisible = ref(false);
const uploadLoading = ref(false);
const fileList = ref([]);
const currentEventId = ref(null);
const currentDescription = ref(null);
const uploadStatus = ref(null);
const statusCheckInterval = ref(null);

// 响应式相关
const windowWidth = ref(window.innerWidth);
const isMobile = computed(() => windowWidth.value < 768);
const dialogWidth = computed(() => isMobile.value ? '95%' : '500px');

// 表单数据
const form = reactive({
  event_id: '',
  description: '',
  event_date: '',
  token: '',
});

// 监听窗口大小变化
const handleResize = () => {
  windowWidth.value = window.innerWidth;
};

onMounted(() => {
  window.addEventListener('resize', handleResize);
  fetchEvent();
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  clearInterval(statusCheckInterval.value);
});

// 跳转到图片编辑页面
const handleEditPic = (event_id) => {
  router.push(`/event/admin/list/${event_id}/export`);
};

const handleEventView = (event_id) => {
  router.push(`/event/admin/list/${event_id}/view`)
}

// 获取活动列表数据
const fetchEvent = async () => {
  try {
    loading.value = true;
    const response = await apiClient.get('/events');
    if (response.data && response.data.events) {
      if (Array.isArray(response.data.events)) {
        eventList.value = response.data.events;
      } else {
        eventList.value = Object.entries(response.data.events).map(([id, data]) => ({
          event_id: id,
          description: data.description,
          event_date: data.event_date || '',
          token: data.token,
          is_open: data.is_open,
        }));
      }
    } else {
      eventList.value = [];
    }
  } catch (error) {
    ElNotification({
      title: '错误',
      message: '后端API无响应',
      type: 'error',
    });
  } finally {
    loading.value = false;
  }
};

// 添加新活动
const addEvent = async () => {
  try {
    addLoading.value = true;
    await apiClient.post(`/events/${form.event_id}`, {
      event_id: form.event_id,
      description: form.description,
      event_date: form.event_date,
      token: form.token,
    });

    await fetchEvent();

    ElNotification({
      title: '成功',
      message: '添加成功',
      type: 'success',
    });

    dialogFormVisible.value = false;
    form.event_id = '';
    form.description = '';
    form.event_date = '';
    form.token = '';
  } catch (error) {
    ElNotification({
      title: '错误',
      message: '后端API无响应',
      type: 'error',
    });
  } finally {
    addLoading.value = false;
  }
};

// 编辑活动
const editEvent = (event) => {
  isEditMode.value = true;
  dialogFormVisible.value = true;
  form.event_id = event.event_id;
  form.description = event.description;
  form.event_date = event.event_date;
  form.token = event.token;
};

// 删除活动
const deleteEvent = async (event_id) => {
  try {
    await apiClient.delete(`/events/${event_id}`, {
      data: { event_id }
    });
    await fetchEvent();
    ElNotification({
      title: '成功',
      message: '删除成功',
      type: 'success',
    });
  } catch (error) {
    ElNotification({
      title: '错误',
      message: '删除失败',
      type: 'error',
    });
  }
};

// 更新活动开关状态
const updateEventStatus = async (eventId, newVal) => {
  try {
    await apiClient.post(`/events/${eventId}`, {
      is_open: newVal
    })
    ElMessage.success('状态已更新')
  } catch (error) {
    ElMessage.error('更新失败，已回滚')
    // 回滚状态
    const event = eventList.value.find(e => e.event_id === eventId)
    if (event) event.is_open = !newVal
  }
}

const handleQrCodeShow = (eventId,description) => {
  currentEventId.value = eventId;
  currentDescription.value = description;
  qrCodeDialogVisible.value = true;
}

// 显示上传图片对话框
const showUploadDialog = (eventId) => {
  currentEventId.value = eventId;
  fileList.value = [];
  uploadStatus.value = null;
  uploadDialogVisible.value = true;
  clearInterval(statusCheckInterval.value);
};

// 文件选择处理
const handleFileChange = (file) => {
  fileList.value = [file];
};

// 提交图片上传
const submitUpload = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请先选择图片');
    return;
  }

  uploadLoading.value = true;
  uploadStatus.value = {
    type: 'info',
    message: '上传中...',
    description: '正在上传图片，请稍候'
  };

  try {
    const formData = new FormData();
    formData.append('file', fileList.value[0].raw);

    const response = await apiClient.post(
        `/events/${currentEventId.value}/upload-pic`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
    );

    uploadStatus.value = {
      type: 'success',
      message: '上传成功',
      description: '图片已上传，正在处理人脸识别...'
    };

    // 开始轮询处理状态
    checkProcessStatus();

  } catch (error) {
    uploadStatus.value = {
      type: 'error',
      message: '上传失败',
      description: error.response?.data?.error || '服务器处理请求时出错'
    };
    uploadLoading.value = false;
  }
};

// 检查处理状态
const checkProcessStatus = () => {
  clearInterval(statusCheckInterval.value);

  statusCheckInterval.value = setInterval(async () => {
    try {
      const response = await apiClient.get(`/events/${currentEventId.value}/process-status`);

      if (response.data.status === 'completed') {
        uploadStatus.value = {
          type: 'success',
          message: '处理完成',
          description: response.data.message
        };
        uploadLoading.value = false;
        clearInterval(statusCheckInterval.value);
      } else if (response.data.status === 'processing') {
        uploadStatus.value = {
          type: 'info',
          message: '处理中',
          description: '正在识别和裁剪人脸，请稍候...'
        };
      }
    } catch (error) {
      console.error('检查处理状态失败:', error);
      clearInterval(statusCheckInterval.value);
      uploadStatus.value = {
        type: 'warning',
        message: '状态查询失败',
        description: '无法获取处理状态，请刷新页面查看结果'
      };
      uploadLoading.value = false;
    }
  }, 2000); // 每2秒检查一次
};


// 自动生产随机密码
const autoGeneratePwd = () => {
    form.token = generateRandomPassword()
}
const generateRandomPassword = () => {
  const length = Math.floor(Math.random() * 9) + 8 // 随机生成8-16之间的密码长度
  const lowerCaseChars = 'abcdefghijklmnopqrstuvwxyz'
  const upperCaseChars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
  const numberChars = '0123456789'

  let password = ''

  while (password.length < length) {
    const randomCharType = Math.floor(Math.random() * 3) // 随机选择字符类型：0代表小写字母，1代表大写字母，2代表数字

    if (randomCharType === 0) {
      password += lowerCaseChars[Math.floor(Math.random() * lowerCaseChars.length)]
    } else if (randomCharType === 1) {
      password += upperCaseChars[Math.floor(Math.random() * upperCaseChars.length)]
    } else {
      password += numberChars[Math.floor(Math.random() * numberChars.length)]
    }
  }

  return password;
}
</script>

<style scoped>
/* 基础布局 */
.el-main {
  padding: 20px;
  background-color: #f5f7f9;
  min-height: calc(100vh - 140px);
}

/* 顶部区域 */
.top-section {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.page-header h1.page-title {
  font-size: 1.8rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px 0;
}

.page-subtitle {
  color: #666;
  font-size: 0.9rem;
  margin: 0;
}

.action-buttons {
  flex-shrink: 0;
}

.add-button {
  height: 44px;
  padding: 0 20px;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 表格区域 */
.table-section {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.desktop-table {
  width: 100%;
}

.table-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.event-actions {
  display: flex;
  flex-direction: column; /* Stack items vertically */
  align-items: flex-end; /* Align items (switch and button) to the right */
}

/* 移动端卡片 */
.mobile-cards {
  display: none;
  padding: 16px;
  gap: 16px;
  flex-direction: column;
}

.mobile-cards.mobile-visible {
  display: flex;
}

.desktop-table.mobile-hidden {
  display: none;
}

.event-card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.event-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(255, 51, 119, 0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.event-info {
  flex: 1;
}

.event-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px 0;
}

.event-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.event-date {
  font-size: 0.85rem;
  color: #666;
}

.event-status {
  flex-shrink: 0;
  margin-left: 16px;
}

.card-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-row {
  display: flex;
  gap: 8px;
}

.action-button {
  flex: 1;
  height: 44px;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

/* 对话框样式 */
.add-dialog, .upload-dialog {
  border-radius: 12px;
}

.dialog-form {
  padding: 0;
}

.dialog-form .el-form-item {
  margin-bottom: 20px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.cancel-btn, .confirm-btn {
  height: 44px;
  padding: 0 24px;
  font-size: 16px;
}

/* 上传组件 */
.upload-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.upload-dragger {
  width: 100%;
}

.upload-status {
  margin-top: 16px;
}

/* 空状态 */
.empty-state {
  padding: 60px 20px;
  text-align: center;
}

/* Element Plus 样式覆盖 */

:deep(.el-button--success) {
  background-color: #4CAF50;
  border-color: #4CAF50;
}

:deep(.el-button--success:hover) {
  background-color: #45a049;
  border-color: #45a049;
}

:deep(.el-card__header) {
  padding: 16px 20px;
  background: rgba(255, 51, 119, 0.02);
  border-bottom: 1px solid rgba(255, 51, 119, 0.1);
}

:deep(.el-card__body) {
  padding: 20px;
}

:deep(.el-switch__label) {
  font-size: 12px;
}

/* 平板适配 */
@media (max-width: 1024px) {
  .el-main {
    padding: 16px;
  }

  .top-section {
    padding: 16px;
  }

  .table-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .table-actions .el-button {
    margin-bottom: 4px;
  }
}

/* 移动端适配 */
@media (max-width: 768px) {
  .el-main {
    padding: 12px;
  }

  .top-section {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
    padding: 16px;
  }

  .action-buttons {
    width: 100%;
  }

  .add-button {
    width: 100%;
    justify-content: center;
  }

  .button-text {
    display: inline;
  }

  .desktop-table {
    display: none;
  }

  .mobile-cards {
    display: flex;
    padding: 0;
  }

  .page-header h1.page-title {
    font-size: 1.5rem;
  }

  .dialog-footer {
    flex-direction: column-reverse;
    gap: 8px;
  }

  .cancel-btn, .confirm-btn {
    width: 100%;
  }

  :deep(.el-dialog) {
    margin: 0;
    border-radius: 0;
  }

  :deep(.el-dialog__body) {
    padding: 16px 20px;
  }

  :deep(.el-form-item__label) {
    font-size: 14px;
    font-weight: 500;
  }

  :deep(.el-input__inner) {
    height: 44px;
    font-size: 16px;
  }

  :deep(.el-date-editor.el-input) {
    height: 44px;
  }

  :deep(.el-upload-dragger) {
    height: 140px;
  }
}

/* 超小屏幕适配 */
@media (max-width: 480px) {
  .el-main {
    padding: 8px;
  }

  .top-section {
    padding: 12px;
  }

  .page-header h1.page-title {
    font-size: 1.3rem;
  }

  .page-subtitle {
    font-size: 0.8rem;
  }

  .add-button {
    height: 40px;
    font-size: 14px;
  }

  .event-card {
    margin-bottom: 12px;
  }

  .event-title {
    font-size: 1.1rem;
  }

  .action-button {
    height: 40px;
    font-size: 13px;
  }

  .cancel-btn, .confirm-btn {
    height: 40px;
    font-size: 14px;
  }

  :deep(.el-card__header) {
    padding: 12px 16px;
  }

  :deep(.el-card__body) {
    padding: 16px;
  }
}

/* 横屏模式适配 */
@media (max-width: 768px) and (orientation: landscape) {
  .top-section {
    flex-direction: row;
    align-items: center;
  }

  .action-buttons {
    width: auto;
  }

  .add-button {
    width: auto;
  }

  .action-row {
    flex-direction: row;
  }
}

/* 触摸设备优化 */
@media (hover: none) and (pointer: coarse) {
  .add-button,
  .action-button,
  .cancel-btn,
  .confirm-btn {
    min-height: 48px;
  }

  :deep(.el-switch) {
    transform: scale(1.2);
  }

  :deep(.el-button) {
    min-height: 44px;
  }
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .el-main {
    background-color: #121212;
  }

  .top-section,
  .table-section {
    background: #1e1e1e;
    color: #e4e7ed;
  }

  .page-header h1.page-title {
    color: #e4e7ed;
  }

  .page-subtitle {
    color: #909399;
  }

  .event-title {
    color: #e4e7ed;
  }

  .event-date {
    color: #909399;
  }

  .event-card {
    background: #1e1e1e;
    border-color: #404040;
  }

  :deep(.el-card__header) {
    background: rgba(255, 51, 119, 0.05);
    border-bottom-color: rgba(255, 51, 119, 0.2);
  }
}

/* 减少动画偏好支持 */
@media (prefers-reduced-motion: reduce) {
  .event-card {
    transition: none;
  }

  .event-card:hover {
    transform: none;
  }
}
</style>