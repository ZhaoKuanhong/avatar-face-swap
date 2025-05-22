<template>
  <div class="admin-layout">
    <el-container>
      <el-aside width="200px" class="sidebar">
        <div class="logo-container">
          <img src="../assets/img/fc-logo.png" alt="GDUT BanGDream Fan Club" class="logo">
        </div>

        <el-menu
            class="admin-menu"
            :default-active="route.path"
            @select="handleSelect"
            :uniqueOpened="true"
            :router="true"
        >
          <el-menu-item index="/event/admin/list">
            <el-icon><i class="el-icon-s-grid"></i></el-icon>
            <span>活动管理</span>
          </el-menu-item>
          <!--Todo-->
          <el-menu-item index="/event/admin/logs">
            <el-icon><i class="el-icon-document"></i></el-icon>
            <span>系统日志</span>
          </el-menu-item>
<!--          <el-menu-item index="/event/admin/settings">-->
<!--            <el-icon><i class="el-icon-setting"></i></el-icon>-->
<!--            <span>系统设置</span>-->
<!--          </el-menu-item>-->
        </el-menu>

        <div class="sidebar-footer">
          <el-button type="text" @click="logout" class="logout-btn">
            <i class="el-icon-switch-button"></i> 退出登录
          </el-button>
        </div>
      </el-aside>

      <el-container class="main-container">
        <el-header class="admin-header">
          <div class="breadcrumb-container">
            <el-breadcrumb separator="/">
              <el-breadcrumb-item :to="{ path: '/event/admin/list' }">
                管理中心
              </el-breadcrumb-item>
              <el-breadcrumb-item v-if="route.params.event_id">
                {{ breadcrumbTitle }}
              </el-breadcrumb-item>
            </el-breadcrumb>
          </div>

          <div class="header-actions">
            <span class="welcome-text">欢迎，管理员</span>
          </div>
        </el-header>

        <el-main class="admin-main">
          <router-view />
        </el-main>

        <el-footer class="admin-footer">
          <div class="copyright">Copyright (C) 2025 Faspand & Mio for GDUT BanGDream Fan Club</div>
          <div class="disclaimer">「BanGDream!」は株式会社ブシロードの登録商標です。</div>
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

const handleSelect = (key) => {
  router.push(key);
};

const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('description');
  router.push('/event');
};
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
  width: 100vw;
  background-color: #f9f9f9;
  display: flex;
}

.el-main {
    background-color: #f5f7f9;
    height: calc(100vh - 8rem);
}

.sidebar {
  background: linear-gradient(180deg, #FF3377 0%, #FF3366 100%);
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  position: relative;
  width: 200px !important;
  transition: all 0.3s ease;
}

.logo-container {
  padding: 20px 0;
  text-align: center;
  background-color: rgba(255, 255, 255, 0.1);
  margin-bottom: 10px;
}

.logo {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  border: 3px solid #FFDDEE;
}

.admin-menu {
  flex: 1;
  border-right: none !important;
  background: transparent !important;
}

.el-menu-item {
  color: white !important;
  font-size: 16px;
  display: flex;
  align-items: center;
  margin: 8px 0;
  border-radius: 0 24px 24px 0;
  margin-right: 16px;
}

.el-menu-item:hover, .el-menu-item.is-active {
  background-color: rgba(255, 221, 238, 0.3) !important;
  color: #FFDDEE !important;
}

.el-menu-item i {
  color: white;
  margin-right: 8px;
  font-size: 18px;
}

.sidebar-footer {
  padding: 15px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  text-align: center;
}

.logout-btn {
  color: white !important;
  opacity: 0.8;
  transition: opacity 0.3s;
}

.logout-btn:hover {
  opacity: 1;
}

.main-container {
  flex: 1;
  position: relative;
}

.admin-header {
  background-color: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 0 20px;
  height: 60px !important;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.breadcrumb-container {
  font-size: 16px;
}

.header-actions {
  display: flex;
  align-items: center;
}

.welcome-text {
  color: #666;
  margin-right: 15px;
}

.admin-main {
  padding: 20px;
  background-color: #f9f9f9;
  min-height: calc(100vh - 120px);
}

.admin-footer {
  height: 60px !important;
  background-color: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #999;
  font-size: 12px;
  padding: 10px 0 !important;
  border-top: 1px solid #eee;
}

.copyright {
  margin-bottom: 5px;
}

@media (max-width: 768px) {
  .sidebar {
    width: 64px !important;
    overflow: hidden;
  }

  .logo {
    width: 40px;
    height: 40px;
  }

  .el-menu-item span {
    display: none;
  }

  .admin-header {
    padding: 0 10px;
  }

  .welcome-text {
    display: none;
  }
}

/* dark mode */
@media (prefers-color-scheme: dark) {
  .admin-layout {
    background-color: #121212;
  }

  .sidebar {
    background: linear-gradient(180deg, #CC1155 0%, #BB1144 100%);
  }

  .admin-header {
    background-color: #1e1e1e;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  }

  .welcome-text {
    color: #ccc;
  }

  .admin-main {
    background-color: #121212;
  }

  .admin-footer {
    background-color: #1e1e1e;
    color: #777;
    border-top: 1px solid #333;
  }
}
</style>