<template>
  <div class="common-layout">
    <el-container>
      <el-aside width="150px">
        <el-menu
          class="el-menu"
          active-text-color="#ffd04b"
          background-color="#545c64"
          text-color="#fff"
          mode="vertical"
          :default-active="route.path"
          @select="handleSelect"
        >
          <el-menu-item >
            <img
              style="width: 50px"
              src="../assets/img/img_sd_hski_cmmn-00-thumb-circle.png"
            />
          </el-menu-item>
          <el-menu-item index="/event/admin/list">活动管理</el-menu-item>
          <el-menu-item >日志</el-menu-item>
        </el-menu>
      </el-aside>

      <el-container>
        <el-header>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/event/admin/list' }">活动一览</el-breadcrumb-item>
            <el-breadcrumb-item v-if="route.params.event_id">
              {{ breadcrumbTitle }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </el-header>

        <el-main>
          <router-view />
        </el-main>

        <el-footer>
          Copyright (C) 2025 Faspand for GDUT BangDream Fan Club
        </el-footer>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router';
import { inject, computed } from 'vue';

const router = useRouter();
const route = useRoute();
// 如果有 inject 到 eventName 就使用它
const eventName = inject('eventName', null);

// 面包屑标题：优先使用活动名
const breadcrumbTitle = computed(() => {
  if (route.params.event_id && eventName?.value) {
    return `活动设置（${eventName.value}）`;
  } else if (route.params.event_id) {
    return `活动设置（ID: ${route.params.event_id}）`;
  }
  return '';
});

// 点击菜单跳转
const handleSelect = (key) => {
  router.push(key);
};

</script>

<style scoped>
.common-layout {
  height: 100vh;
  width: 100vw;
}
.common-layout .el-header {
  background-color: var(--el-color-primary-light-7);
  color: var(--el-text-color-primary);
  padding: 20px;
}
.common-layout .el-aside {
  color: var(--el-text-color-primary);
  background: var(--el-color-primary-light-8);
}
.common-layout .el-menu {
  border-right: none;
  height: 100vh;
}
.common-layout .el-main {
  padding: 0;
}
.common-layout .toolbar {
  height: 100%;
  right: 20px;
}
</style>