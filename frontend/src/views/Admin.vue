<template>
  <div class="admin-layout">
    <el-container>
      <!-- 移动端汉堡菜单按钮 -->
      <div class="mobile-menu-btn" @click="toggleMobileMenu">
        <el-icon><Menu /></el-icon>
      </div>

      <!-- 移动端遮罩层 -->
      <div
          v-show="showMobileMenu"
          class="mobile-overlay"
          @click="closeMobileMenu"
      ></div>

      <!-- 侧边栏 -->
      <el-aside
          width="200px"
          class="sidebar"
          :class="{ 'mobile-sidebar-open': showMobileMenu }"
      >
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
          <el-menu-item index="/event/admin/list" @click="closeMobileMenu">
            <el-icon><Grid /></el-icon>
            <span>活动管理</span>
          </el-menu-item>
          <el-menu-item index="/event/admin/logs" @click="closeMobileMenu">
            <el-icon><Document /></el-icon>
            <span>系统日志</span>
          </el-menu-item>
        </el-menu>

        <div class="sidebar-footer">
          <el-button type="text" @click="logout" class="logout-btn">
            <el-icon><SwitchButton /></el-icon>
            <span>退出登录</span>
          </el-button>
        </div>
      </el-aside>

      <!-- 主内容区域 -->
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
import { inject, computed, ref, onMounted, onUnmounted } from 'vue';
import { Menu, Grid, Document, SwitchButton } from '@element-plus/icons-vue';

const router = useRouter();
const route = useRoute();
const eventName = inject('eventName', null);
const showMobileMenu = ref(false);

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

// 移动端菜单控制
const toggleMobileMenu = () => {
  showMobileMenu.value = !showMobileMenu.value;
};

const closeMobileMenu = () => {
  showMobileMenu.value = false;
};

// 监听窗口大小变化
const handleResize = () => {
  if (window.innerWidth > 768) {
    showMobileMenu.value = false;
  }
};

onMounted(() => {
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
});
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
  width: 100vw;
  background-color: #f9f9f9;
  display: flex;
  position: relative;
}

.el-main {
  background-color: #f5f7f9;
  height: calc(100vh - 8rem);
}

/* 移动端汉堡菜单按钮 */
.mobile-menu-btn {
  display: none;
  position: fixed;
  top: 15px;
  left: 15px;
  z-index: 1002;
  background: #FF3377;
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 8px;
  cursor: pointer;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(255, 51, 119, 0.3);
  transition: all 0.3s ease;
}

.mobile-menu-btn:hover {
  background: #FF1166;
  transform: scale(1.05);
}

.mobile-menu-btn:active {
  transform: scale(0.95);
}

/* 移动端遮罩层 */
.mobile-overlay {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.mobile-overlay[style*="block"] {
  opacity: 1;
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
  min-height: 48px;
  transition: all 0.3s ease;
}

.el-menu-item:hover, .el-menu-item.is-active {
  background-color: rgba(255, 221, 238, 0.3) !important;
  color: #FFDDEE !important;
}

.el-menu-item .el-icon {
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
  width: 100%;
  min-height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
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

/* 平板设备适配 */
@media (max-width: 1024px) {
  .admin-header {
    padding: 0 15px;
  }

  .admin-main {
    padding: 15px;
  }
}

/* 移动端适配 */
@media (max-width: 768px) {
  .mobile-menu-btn {
    display: flex;
  }

  .mobile-overlay {
    display: block;
  }

  .sidebar {
    position: fixed;
    top: 0;
    left: -200px;
    height: 100vh;
    z-index: 1000;
    transition: left 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    width: 200px !important;
  }

  .sidebar.mobile-sidebar-open {
    left: 0;
  }

  .main-container {
    width: 100%;
    margin-left: 0;
  }

  .admin-header {
    padding: 0 60px 0 65px;
  }

  .welcome-text {
    display: none;
  }

  .breadcrumb-container {
    font-size: 14px;
  }

  .admin-main {
    padding: 15px;
  }

  .admin-footer {
    font-size: 10px;
    height: 50px !important;
  }

  .logo {
    width: 60px;
    height: 60px;
  }

  .logo-container {
    padding: 15px 0;
  }

  .el-menu-item {
    font-size: 15px;
    margin-right: 12px;
  }
}

/* 超小屏幕适配 */
@media (max-width: 480px) {
  .mobile-menu-btn {
    top: 12px;
    left: 12px;
    width: 36px;
    height: 36px;
  }

  .admin-header {
    padding: 0 50px 0 65px;
    height: 50px !important;
  }

  .admin-main {
    padding: 10px;
    min-height: calc(100vh - 100px);
  }

  .breadcrumb-container {
    font-size: 12px;
  }

  .sidebar {
    width: 180px !important;
    left: -180px;
  }

  .sidebar.mobile-sidebar-open {
    left: 0;
  }

  .copyright, .disclaimer {
    font-size: 9px;
  }

  .admin-footer {
    height: 45px !important;
    padding: 8px 0 !important;
  }

  .logo {
    width: 50px;
    height: 50px;
  }

  .logo-container {
    padding: 12px 0;
  }

  .el-menu-item {
    font-size: 14px;
    min-height: 42px;
  }
}

/* 横屏模式适配 */
@media (max-width: 768px) and (orientation: landscape) {
  .sidebar {
    width: 160px !important;
    left: -160px;
  }

  .sidebar.mobile-sidebar-open {
    left: 0;
  }

  .logo {
    width: 50px;
    height: 50px;
  }

  .logo-container {
    padding: 10px 0;
  }

  .admin-main {
    padding: 10px;
  }
}

/* 深色模式支持
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

  .mobile-overlay {
    background: rgba(0, 0, 0, 0.7);
  }

  .mobile-menu-btn {
    background: #CC1155;
  }

  .mobile-menu-btn:hover {
    background: #BB1144;
  }
}
*/
/* 高分辨率屏幕优化 */
@media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
  .logo {
    image-rendering: crisp-edges;
  }

  .mobile-menu-btn {
    box-shadow: 0 2px 8px rgba(255, 51, 119, 0.4);
  }
}

/* 无障碍支持 */
@media (prefers-reduced-motion: reduce) {
  .sidebar,
  .mobile-overlay,
  .mobile-menu-btn,
  .el-menu-item {
    transition: none;
  }
}

/* 触摸设备优化 */
@media (hover: none) and (pointer: coarse) {
  .el-menu-item {
    min-height: 52px;
  }

  .logout-btn {
    min-height: 48px;
  }

  .mobile-menu-btn {
    width: 44px;
    height: 44px;
  }
}
</style>