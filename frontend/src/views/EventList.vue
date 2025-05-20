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

            <el-table-column label="操作" width="200">
              <template #default="scope">
                <el-button type="primary" @click="handleEditPic(scope.row.event_id)">
                  生成图片
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
import { ref, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElNotification } from 'element-plus';
import { apiClient } from '@/api/axios';

// 状态
const dialogFormVisible = ref(false);
const loading = ref(true);
const addLoading = ref(false);
const eventList = ref([]);
const router = useRouter();

// 表单
const form = reactive({
  event_id: '',
  description: '',
  event_date: '',
  token: '',
});

// 跳转编辑页
const handleEditPic = (event_id) => {
  router.push(`/event/admin/list/${event_id}`);
};

// 获取事件列表
const fetchEvent = async () => {
  try {
    loading.value = true;
    const response = await apiClient.get('/events');
    if (response.data && response.data.events) {
      eventList.value = Object.entries(response.data.events).map(([id, data]) => ({
        event_id: id,
        description: data.description,
        event_date: data.event_date || '', // 你原代码没设置
        token: data.token,
        is_open: data.is_open,
      }));
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

// 添加事件
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

// 删除事件
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

// 更新事件开关状态
const updateEventStatus = async (eventId, newVal) => {
  try {
    await apiClient.post(`/events/${eventId}`, {
      is_open: newVal
    })
    ElMessage.success('状态已更新')
  } catch (error) {
    ElMessage.error('更新失败，已回滚')
    // 回滚状态
    const event = tableData.value.find(e => e.event_id === eventId)
    if (event) event.is_open = !newVal
  }
}

// 初始化加载
onMounted(() => {
  fetchEvent();
});
</script>

<style scoped lang="scss">
.el-row {
  margin-bottom: 20px;
}
.el-row:last-child {
  margin-bottom: 0;
}
</style>