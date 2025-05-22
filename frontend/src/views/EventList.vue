<template>
  <el-container>
    <el-main>
      <el-row justify="center">
        <el-col :span="4">
          <el-button plain @click="dialogFormVisible = true">
            添加活动
          </el-button>
        </el-col>
      </el-row>

      <!-- 添加活动表单对话框 -->
      <el-dialog v-model="dialogFormVisible" title="添加活动" width="30vh">
        <el-form @submit.prevent>
          <el-form-item label="event_id">
            <el-input v-model="form.event_id" />
          </el-form-item>
          <el-form-item label="活动名称">
            <el-input v-model="form.description" />
          </el-form-item>
          <el-form-item label="活动日期">
            <el-date-picker
                v-model="form.event_date"
                type="date"
                placeholder="选择日期"
            />
          </el-form-item>
          <el-form-item label="token">
            <el-input v-model="form.token" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="addEvent" :loading="addLoading">Create</el-button>
            <el-button @click="dialogFormVisible = false">Cancel</el-button>
          </el-form-item>
        </el-form>
      </el-dialog>

      <!-- 上传图片对话框 -->
      <el-dialog v-model="uploadDialogVisible" title="上传活动图片" width="500px">
        <div class="upload-container">
          <el-upload
              class="upload-dragger"
              drag
              action="#"
              :auto-upload="false"
              :on-change="handleFileChange"
              :file-list="fileList"
          >
            <el-icon class="el-icon--upload"><i class="el-icon-upload"></i></el-icon>
            <div class="el-upload__text">
              拖拽图片到此处，或 <em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                请上传JPEG/PNG格式图片，图片应包含多个人脸，系统将自动识别并裁剪
              </div>
            </template>
          </el-upload>

          <div class="upload-actions">
            <el-button type="primary" @click="submitUpload" :loading="uploadLoading">上传并处理</el-button>
            <el-button @click="uploadDialogVisible = false">取消</el-button>
          </div>

          <div v-if="uploadStatus" class="upload-status">
            <el-alert
                :title="uploadStatus.message"
                :type="uploadStatus.type"
                :description="uploadStatus.description"
                show-icon
            />
          </div>
        </div>
      </el-dialog>

      <el-row justify="center">
        <el-col :span="24">
          <el-table :data="eventList" style="width: 100%" stripe v-loading="loading">
            <el-table-column prop="event_id" label="event_id" width="150" />
            <el-table-column prop="description" label="description" width="200" />
            <el-table-column prop="event_date" label="event_date" width="150" />

            <el-table-column prop="isOpen" label="开启采集" width="100">
              <template #default="scope">
                <el-switch v-model="scope.row.is_open"
                           @change="(val) => updateEventStatus(scope.row.event_id, val)"
                />
              </template>
            </el-table-column>

            <el-table-column label="操作" min-width="400" fixed="right">
              <template #default="scope">
                <el-button type="primary" @click="handleEventView(scope.row.event_id)">
                  查看活动
                </el-button>
                <el-button type="primary" @click="handleEditPic(scope.row.event_id)">
                  生成图片
                </el-button>
                <el-button type="success" @click="showUploadDialog(scope.row.event_id)">
                  上传活动图片
                </el-button>
                <el-popconfirm title="确定要删除这一项吗？"
                               @confirm="deleteEvent(scope.row.event_id)">
                  <template #reference>
                    <el-button type="danger">删除</el-button>
                  </template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
        </el-col>
      </el-row>
    </el-main>
  </el-container>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElNotification, ElMessage } from 'element-plus';
import { apiClient } from '@/api/axios';

// 状态变量定义
const dialogFormVisible = ref(false);
const loading = ref(true);
const addLoading = ref(false);
const eventList = ref([]);
const router = useRouter();

// 图片上传相关状态
const uploadDialogVisible = ref(false);
const uploadLoading = ref(false);
const fileList = ref([]);
const currentEventId = ref(null);
const uploadStatus = ref(null);
const statusCheckInterval = ref(null);

// 表单数据
const form = reactive({
  event_id: '',
  description: '',
  event_date: '',
  token: '',
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

// 初始化加载
onMounted(() => {
  fetchEvent();
});

// 组件卸载时清理定时器
onUnmounted(() => {
  clearInterval(statusCheckInterval.value);
});
</script>

<style scoped>
.el-row {
  margin-bottom: 20px;
}
.el-row:last-child {
  margin-bottom: 0;
}

.upload-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.upload-dragger {
  width: 100%;
}

.upload-actions {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 20px;
}

.upload-status {
  margin-top: 15px;
}

/* 确保与现有主题一致 */
:deep(.el-button--primary) {
  background-color: #FF3377;
  border-color: #FF3377;
}

:deep(.el-button--primary:hover) {
  background-color: #FF1166;
  border-color: #FF1166;
}

:deep(.el-button--success) {
  background-color: #4CAF50;
  border-color: #4CAF50;
}

:deep(.el-button--success:hover) {
  background-color: #45a049;
  border-color: #45a049;
}
</style>