<template>
  <div class="log-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">系统日志</h1>
        <p class="page-subtitle">查看和筛选系统运行日志</p>
      </div>
      <div class="header-actions">
        <el-button
            type="primary"
            @click="fetchLogs"
            :loading="loading"
            :icon="Refresh"
            class="refresh-button"
        >
          <span class="button-text">刷新</span>
        </el-button>
      </div>
    </div>

    <!-- 筛选器区域 -->
    <el-card class="filter-card" shadow="hover">
      <template #header>
        <div class="filter-header">
          <div class="filter-title">
            <el-icon><Filter /></el-icon>
            <span>筛选条件</span>
          </div>
          <el-button
              v-if="isMobile"
              type="text"
              @click="toggleFilterCollapse"
              class="collapse-button"
          >
            <el-icon>
              <ArrowDown v-if="!filterCollapsed" />
              <ArrowRight v-else />
            </el-icon>
          </el-button>
        </div>
      </template>

      <div class="filter-content" :class="{ 'collapsed': isMobile && filterCollapsed }">
        <!-- 桌面端筛选器 -->
        <el-form
            :model="filters"
            :inline="!isMobile"
            class="filter-form"
            :class="{ 'mobile-form': isMobile }"
            label-position="left"
            :label-width="isMobile ? '80px' : '70px'"
        >
          <el-form-item label="日志级别" class="filter-item">
            <el-select
                v-model="filters.level"
                placeholder="全部级别"
                clearable
                :teleported="false"
                :style="{ minWidth: isMobile ? '100%' : '130px' }"
                class="filter-select"
            >
              <el-option label="信息" value="INFO" />
              <el-option label="警告" value="WARNING" />
              <el-option label="错误" value="ERROR" />
            </el-select>
          </el-form-item>

          <el-form-item label="模块" class="filter-item">
            <el-select
                v-model="filters.module"
                placeholder="全部模块"
                clearable
                :teleported="false"
                :style="{ minWidth: isMobile ? '100%' : '150px' }"
                class="filter-select"
            >
              <el-option label="活动管理" value="活动管理" />
              <el-option label="用户认证" value="用户认证" />
              <el-option label="图片处理" value="图片处理" />
              <el-option label="系统" value="系统" />
            </el-select>
          </el-form-item>

          <el-form-item label="时间范围" class="filter-item date-range-item">
            <el-date-picker
                v-model="dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                value-format="YYYY-MM-DD"
                :teleported="false"
                :style="{ width: isMobile ? '100%' : 'auto' }"
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
                class="date-picker"
            />
          </el-form-item>

          <el-form-item class="filter-actions">
            <div class="action-buttons">
              <el-button
                  type="primary"
                  @click="applyFilters"
                  :icon="Search"
                  class="action-button"
              >
                筛选
              </el-button>
              <el-button
                  @click="resetFilters"
                  :icon="RefreshLeft"
                  class="action-button"
              >
                重置
              </el-button>
            </div>
          </el-form-item>
        </el-form>
      </div>
    </el-card>

    <!-- 日志数据区域 -->
    <el-card class="log-table-card" shadow="hover">
      <template #header>
        <div class="table-header">
          <div class="table-info">
            <span class="log-count">共 {{ totalLogs }} 条日志</span>
            <el-tag v-if="hasActiveFilters" type="warning" size="small">已筛选</el-tag>
          </div>
        </div>
      </template>

      <!-- 桌面端表格 -->
      <el-table
          :data="logs"
          style="width: 100%"
          border
          stripe
          v-loading="loading"
          class="desktop-table"
          :class="{ 'mobile-hidden': isMobile }"
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

      <!-- 移动端卡片列表 -->
      <div
          class="mobile-cards"
          :class="{ 'mobile-visible': isMobile }"
          v-loading="loading"
      >
        <div
            v-for="(log, index) in logs"
            :key="`${log.timestamp}-${index}`"
            class="log-card"
        >
          <!-- 卡片头部 -->
          <div class="log-card-header">
            <div class="log-time">
              <el-icon><Clock /></el-icon>
              <span>{{ formatDate(log.timestamp) }}</span>
            </div>
            <el-tag :type="getLogLevelType(log.level)" size="small">
              {{ log.level }}
            </el-tag>
          </div>

          <!-- 卡片内容 -->
          <div class="log-card-content">
            <div class="log-main-info">
              <div class="log-module-action">
                <span class="log-module">{{ log.module }}</span>
                <span class="log-separator">•</span>
                <span class="log-action">{{ log.action }}</span>
              </div>

              <div class="log-meta" v-if="log.event_id || log.user_id || log.ip_address">
                <div class="meta-item" v-if="log.event_id">
                  <span class="meta-label">活动:</span>
                  <span class="meta-value">{{ log.event_id }}</span>
                </div>
                <div class="meta-item" v-if="log.user_id">
                  <span class="meta-label">用户:</span>
                  <span class="meta-value">{{ log.user_id }}</span>
                </div>
                <div class="meta-item" v-if="log.ip_address">
                  <span class="meta-label">IP:</span>
                  <span class="meta-value">{{ log.ip_address }}</span>
                </div>
              </div>
            </div>

            <!-- 详情按钮 -->
            <div class="log-details" v-if="log.details">
              <el-button
                  type="text"
                  @click="showLogDetails(log)"
                  :icon="Document"
                  class="details-button"
              >
                查看详情
              </el-button>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-if="!loading && logs.length === 0" class="empty-state">
          <el-empty description="暂无日志数据">
            <el-button type="primary" @click="resetFilters">清除筛选条件</el-button>
          </el-empty>
        </div>
      </div>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :layout="paginationLayout"
            :total="totalLogs"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
            :small="isMobile"
            class="pagination"
        />
      </div>
    </el-card>

    <!-- 日志详情对话框 -->
    <el-dialog
        v-model="detailsDialogVisible"
        title="日志详情"
        :width="dialogWidth"
        :fullscreen="isMobile"
        class="details-dialog"
    >
      <div v-if="selectedLog" class="log-details-content">
        <div class="detail-section">
          <h4>基本信息</h4>
          <div class="detail-grid">
            <div class="detail-item">
              <span class="detail-label">时间:</span>
              <span class="detail-value">{{ formatDate(selectedLog.timestamp) }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">级别:</span>
              <el-tag :type="getLogLevelType(selectedLog.level)" size="small">
                {{ selectedLog.level }}
              </el-tag>
            </div>
            <div class="detail-item">
              <span class="detail-label">模块:</span>
              <span class="detail-value">{{ selectedLog.module }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">操作:</span>
              <span class="detail-value">{{ selectedLog.action }}</span>
            </div>
            <div class="detail-item" v-if="selectedLog.event_id">
              <span class="detail-label">活动ID:</span>
              <span class="detail-value">{{ selectedLog.event_id }}</span>
            </div>
            <div class="detail-item" v-if="selectedLog.user_id">
              <span class="detail-label">用户:</span>
              <span class="detail-value">{{ selectedLog.user_id }}</span>
            </div>
            <div class="detail-item" v-if="selectedLog.ip_address">
              <span class="detail-label">IP地址:</span>
              <span class="detail-value">{{ selectedLog.ip_address }}</span>
            </div>
          </div>
        </div>

        <div class="detail-section" v-if="selectedLog.details">
          <h4>详细信息</h4>
          <pre class="details-json">{{ formatJSON(selectedLog.details) }}</pre>
        </div>
      </div>

      <template #footer>
        <el-button @click="detailsDialogVisible = false" class="dialog-button">
          关闭
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, onUnmounted } from 'vue';
import { apiClient } from '@/api/axios';
import { ElMessage } from 'element-plus';
import {
  Refresh, Filter, ArrowDown, ArrowRight, Search, RefreshLeft,
  Clock, Document
} from '@element-plus/icons-vue';

// 响应式相关
const windowWidth = ref(window.innerWidth);
const isMobile = computed(() => windowWidth.value < 768);
const dialogWidth = computed(() => isMobile.value ? '95%' : '600px');
const paginationLayout = computed(() =>
    isMobile.value ? 'prev, pager, next' : 'total, sizes, prev, pager, next, jumper'
);

// 状态
const logs = ref([]);
const loading = ref(false);
const currentPage = ref(1);
const pageSize = ref(20);
const totalLogs = ref(0);
const dateRange = ref([]);

// 移动端特有状态
const filterCollapsed = ref(true);
const detailsDialogVisible = ref(false);
const selectedLog = ref(null);

// 筛选条件
const filters = ref({
  level: null,
  module: null,
  start_date: null,
  end_date: null
});

// 是否有激活的筛选条件
const hasActiveFilters = computed(() => {
  return filters.value.level ||
      filters.value.module ||
      filters.value.start_date ||
      filters.value.end_date;
});

// 监听窗口大小变化
const handleResize = () => {
  windowWidth.value = window.innerWidth;
};

onMounted(() => {
  window.addEventListener('resize', handleResize);
  fetchLogs();
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
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

  // 移动端自动收起筛选器
  if (isMobile.value) {
    filterCollapsed.value = true;
  }
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

// 切换筛选器折叠状态
const toggleFilterCollapse = () => {
  filterCollapsed.value = !filterCollapsed.value;
};

// 显示日志详情
const showLogDetails = (log) => {
  selectedLog.value = log;
  detailsDialogVisible.value = true;
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
</script>

<style scoped>
/* 基础布局 */
.log-container {
  padding: 20px;
  background-color: #f5f7f9;
  min-height: calc(100vh - 140px);
}

/* 页面头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.header-content h1.page-title {
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

.header-actions {
  flex-shrink: 0;
}

.refresh-button {
  height: 44px;
  padding: 0 20px;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 筛选器 */
.filter-card {
  margin-bottom: 20px;
  border-radius: 12px;
  overflow: visible;
  position: relative;
  z-index: 2;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 0;
}

.filter-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #333;
}

.collapse-button {
  display: none;
}

.filter-content {
  transition: all 0.3s ease;
}

.filter-content.collapsed {
  display: none;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.filter-form.mobile-form {
  flex-direction: column;
  gap: 20px;
}

.filter-item {
  margin-bottom: 0;
}

.filter-actions {
  margin-left: auto;
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.action-button {
  height: 44px;
  padding: 0 16px;
}

/* 日志表格区域 */
.log-table-card {
  margin-bottom: 20px;
  border-radius: 12px;
  position: relative;
  z-index: 1;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.log-count {
  color: #666;
  font-size: 14px;
}

/* 桌面端表格 */
.desktop-table {
  width: 100%;
}

/* 移动端卡片 */
.mobile-cards {
  display: none;
  flex-direction: column;
  gap: 12px;
}

.mobile-cards.mobile-visible {
  display: flex;
}

.desktop-table.mobile-hidden {
  display: none;
}

.log-card {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  background: white;
  transition: all 0.3s ease;
}

.log-card:hover {
  box-shadow: 0 2px 8px rgba(255, 51, 119, 0.1);
  border-color: rgba(255, 51, 119, 0.2);
}

.log-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  background: rgba(255, 51, 119, 0.02);
}

.log-time {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #666;
  font-size: 13px;
}

.log-card-content {
  padding: 16px;
}

.log-main-info {
  margin-bottom: 12px;
}

.log-module-action {
  font-size: 15px;
  font-weight: 500;
  color: #333;
  margin-bottom: 8px;
}

.log-module {
  color: #FF3377;
}

.log-separator {
  margin: 0 8px;
  color: #ddd;
}

.log-action {
  color: #333;
}

.log-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
}

.meta-label {
  color: #999;
}

.meta-value {
  color: #666;
  font-family: monospace;
}

.log-details {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.details-button {
  height: 32px;
  font-size: 13px;
  padding: 0 12px;
}

/* 分页 */
.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.pagination {
  background: white;
  padding: 16px;
  border-radius: 8px;
}

/* 详情对话框 */
.details-dialog {
  border-radius: 12px;
}

.log-details-content {
  max-height: 70vh;
  overflow-y: auto;
}

.detail-section {
  margin-bottom: 24px;
}

.detail-section h4 {
  margin: 0 0 12px 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.detail-label {
  font-weight: 500;
  color: #666;
  min-width: 60px;
}

.detail-value {
  color: #333;
  font-family: monospace;
  word-break: break-all;
}

.details-json {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 16px;
  font-size: 12px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 300px;
  overflow: auto;
  font-family: 'Courier New', Courier, monospace;
}

.dialog-button {
  width: 100%;
  height: 44px;
  font-size: 16px;
}

/* 空状态 */
.empty-state {
  padding: 60px 20px;
  text-align: center;
}

/* Element Plus 样式覆盖 */
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

:deep(.date-picker-popper) {
  z-index: 3000 !important;
}

:deep(.el-card__header) {
  background: rgba(255, 51, 119, 0.02);
  border-bottom: 1px solid rgba(255, 51, 119, 0.1);
}

/* 平板适配 */
@media (max-width: 1024px) {
  .log-container {
    padding: 16px;
  }

  .page-header {
    padding: 16px;
  }

  .filter-form:not(.mobile-form) {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-actions {
    margin-left: 0;
    margin-top: 16px;
  }
}

/* 移动端适配 */
@media (max-width: 768px) {
  .log-container {
    padding: 12px;
  }

  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
    padding: 16px;
  }

  .header-actions {
    width: 100%;
  }

  .refresh-button {
    width: 100%;
    justify-content: center;
  }

  .button-text {
    display: inline;
  }

  .collapse-button {
    display: flex;
  }

  .filter-form.mobile-form .filter-item {
    width: 100%;
  }

  .filter-select,
  .date-picker {
    width: 100% !important;
  }

  .action-buttons {
    width: 100%;
  }

  .action-button {
    flex: 1;
  }

  .desktop-table {
    display: none;
  }

  .mobile-cards {
    display: flex;
  }

  .pagination {
    padding: 12px;
  }

  .page-header h1.page-title {
    font-size: 1.5rem;
  }

  .detail-grid {
    grid-template-columns: 1fr;
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
    margin-bottom: 8px;
  }

  :deep(.el-input__inner) {
    height: 44px;
    font-size: 16px;
  }

  :deep(.el-select .el-input__inner) {
    height: 44px;
  }

  :deep(.el-date-editor.el-input) {
    height: 44px;
  }
}

/* 超小屏幕适配 */
@media (max-width: 480px) {
  .log-container {
    padding: 8px;
  }

  .page-header {
    padding: 12px;
  }

  .page-header h1.page-title {
    font-size: 1.3rem;
  }

  .page-subtitle {
    font-size: 0.8rem;
  }

  .refresh-button {
    height: 40px;
    font-size: 14px;
  }

  .log-card {
    border-radius: 6px;
  }

  .log-card-header {
    padding: 10px 12px;
  }

  .log-card-content {
    padding: 12px;
  }

  .log-module-action {
    font-size: 14px;
  }

  .action-button {
    height: 40px;
    font-size: 14px;
  }

  .details-button {
    height: 28px;
    font-size: 12px;
  }

  .dialog-button {
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
  .page-header {
    flex-direction: row;
    align-items: center;
  }

  .header-actions {
    width: auto;
  }

  .refresh-button {
    width: auto;
  }

  .filter-content.collapsed {
    display: block;
  }

  .collapse-button {
    display: none;
  }
}

/* 触摸设备优化 */
@media (hover: none) and (pointer: coarse) {
  .refresh-button,
  .action-button,
  .details-button,
  .dialog-button {
    min-height: 48px;
  }

  .log-card {
    margin-bottom: 8px;
  }

  .log-card-header {
    padding: 14px 16px;
  }

  .log-card-content {
    padding: 16px;
  }
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .log-container {
    background-color: #121212;
  }

  .page-header,
  .filter-card,
  .log-table-card {
    background: #1e1e1e;
    color: #e4e7ed;
  }

  .page-header h1.page-title {
    color: #e4e7ed;
  }

  .page-subtitle {
    color: #909399;
  }

  .filter-title {
    color: #e4e7ed;
  }

  .log-count {
    color: #909399;
  }

  .log-card {
    background: #1e1e1e;
    border-color: #404040;
  }

  .log-card-header {
    background: rgba(255, 51, 119, 0.08);
    border-bottom-color: rgba(255, 51, 119, 0.2);
  }

  .log-module-action {
    color: #e4e7ed;
  }

  .log-action {
    color: #e4e7ed;
  }

  .meta-label {
    color: #909399;
  }

  .meta-value {
    color: #c9cdd4;
  }

  .detail-label {
    color: #909399;
  }

  .detail-value {
    color: #e4e7ed;
  }

  .details-json {
    background: #2d2d2d;
    border-color: #404040;
    color: #e4e7ed;
  }

  :deep(.el-card__header) {
    background: rgba(255, 51, 119, 0.08);
    border-bottom-color: rgba(255, 51, 119, 0.2);
  }
}

:deep(.el-form-item) {
  align-items: center;
}

:deep(.el-form-item__label) {
  line-height: 1 !important;
}

/* 减少动画偏好支持 */
@media (prefers-reduced-motion: reduce) {
  .log-card,
  .filter-content {
    transition: none;
  }

  .log-card:hover {
    transform: none;
  }
}
</style>