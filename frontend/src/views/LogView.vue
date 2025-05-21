<template>
  <div class="log-container">
    <el-card class="filter-card">
      <div class="filter-header">
        <h2>系统日志</h2>
        <el-button type="primary" @click="fetchLogs">刷新</el-button>
      </div>

      <el-form :model="filters" inline>
        <el-form-item label="日志级别">
          <el-select v-model="filters.level" placeholder="全部级别" clearable :teleported="false" style="min-width: 130px;">
            <el-option label="信息" value="INFO" />
            <el-option label="警告" value="WARNING" />
            <el-option label="错误" value="ERROR" />
          </el-select>
        </el-form-item>

        <el-form-item label="模块">
          <el-select v-model="filters.module" placeholder="全部模块" clearable :teleported="false"  style="min-width: 150px;">
            <el-option label="活动管理" value="活动管理" />
            <el-option label="用户认证" value="用户认证" />
            <el-option label="图片处理" value="图片处理" />
            <el-option label="系统" value="系统" />
          </el-select>
        </el-form-item>

        <el-form-item label="时间范围">
          <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
              :teleported="false"
              :popper-options="{
              modifiers: [
                {
                  name: 'preventOverflow',
                  options: {
                    padding: 20,
                    boundary: 'viewport'
                  }
                }
              ],
              strategy: 'fixed'
            }"
              popper-class="date-picker-popper"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="applyFilters">筛选</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="log-table-card">
      <el-table
          :data="logs"
          style="width: 100%"
          border
          stripe
          v-loading="loading"
      >
        <el-table-column prop="timestamp" label="时间" width="180" sortable>
          <template #default="scope">
            {{ formatDate(scope.row.timestamp) }}
          </template>
        </el-table-column>

        <el-table-column prop="level" label="级别" width="100">
          <template #default="scope">
            <el-tag :type="getLogLevelType(scope.row.level)">
              {{ scope.row.level }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="module" label="模块" width="120" />

        <el-table-column prop="action" label="操作" width="150" />

        <el-table-column prop="event_id" label="活动ID" width="100" />

        <el-table-column prop="user_id" label="用户" width="120" />

        <el-table-column prop="ip_address" label="IP地址" width="140" />

        <el-table-column prop="details" label="详情">
          <template #default="scope">
            <el-popover
                placement="top"
                trigger="hover"
                v-if="scope.row.details"
            >
              <pre>{{ formatJSON(scope.row.details) }}</pre>
              <template #reference>
                <el-button type="text">查看详情</el-button>
              </template>
            </el-popover>
            <span v-else>-</span>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="totalLogs"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { apiClient } from '@/api/axios';
import { ElMessage } from 'element-plus';

// 状态
const logs = ref([]);
const loading = ref(false);
const currentPage = ref(1);
const pageSize = ref(20);
const totalLogs = ref(0);
const dateRange = ref([]);

// 筛选条件
const filters = ref({
  level: null,
  module: null,
  start_date: null,
  end_date: null
});

// 获取日志数据
const fetchLogs = async () => {
  loading.value = true;
  try {
    const params = {
      page: currentPage.value,
      per_page: pageSize.value
    };

    // 添加筛选条件
    if (filters.value.level) params.level = filters.value.level;
    if (filters.value.module) params.module = filters.value.module;
    if (filters.value.start_date) params.start_date = filters.value.start_date;
    if (filters.value.end_date) params.end_date = filters.value.end_date;

    const response = await apiClient.get('/logs', { params });
    logs.value = response.data.logs;
    totalLogs.value = response.data.total;
  } catch (error) {
    ElMessage.error('获取日志数据失败');
    console.error('获取日志失败:', error);
  } finally {
    loading.value = false;
  }
};

// 应用筛选
const applyFilters = () => {
  // 处理日期范围
  if (dateRange.value && dateRange.value.length === 2) {
    filters.value.start_date = dateRange.value[0];
    filters.value.end_date = dateRange.value[1];
  } else {
    filters.value.start_date = null;
    filters.value.end_date = null;
  }

  currentPage.value = 1; // 重置到第一页
  fetchLogs();
};

// 重置筛选
const resetFilters = () => {
  filters.value = {
    level: null,
    module: null,
    start_date: null,
    end_date: null
  };
  dateRange.value = [];
  currentPage.value = 1;
  fetchLogs();
};

// 分页处理
const handleSizeChange = (val) => {
  pageSize.value = val;
  fetchLogs();
};

const handleCurrentChange = (val) => {
  currentPage.value = val;
  fetchLogs();
};

// 工具函数
const formatDate = (timestamp) => {
  if (!timestamp) return '-';
  const date = new Date(timestamp);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
};

const formatJSON = (jsonString) => {
  try {
    return JSON.stringify(JSON.parse(jsonString), null, 2);
  } catch (e) {
    return jsonString;
  }
};

const getLogLevelType = (level) => {
  switch (level) {
    case 'ERROR': return 'danger';
    case 'WARNING': return 'warning';
    case 'INFO': return 'info';
    default: return '';
  }
};

// 初始化
onMounted(() => {
  fetchLogs();
});
</script>

<style scoped>
.log-container {
  padding: 20px;
}

.filter-card, .log-table-card {
  margin-bottom: 20px;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.filter-header h2 {
  margin: 0;
  color: #333;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}

:deep(.el-button--primary) {
  background-color: #FF3377;
  border-color: #FF3377;
}

:deep(.el-button--primary:hover) {
  background-color: #FF1166;
  border-color: #FF1166;
}

:deep(.el-pagination .el-pager .is-active) {
  color: #FF3377;
}

pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  max-width: 400px;
  max-height: 300px;
  overflow: auto;
}

.filter-card {
  margin-bottom: 20px;
  overflow: visible;
  position: relative;
  z-index: 2;
}

.log-table-card {
  margin-bottom: 20px;
  position: relative;
  z-index: 1;
}

:deep(.date-picker-popper) {
  z-index: 3000 !important;
}
</style>