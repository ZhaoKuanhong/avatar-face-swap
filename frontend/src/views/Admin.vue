<template>
  <div class="admin-layout">
    <!-- background layers to echo Auth.vue aesthetics -->
    <div class="bg-layer" aria-hidden="true"></div>
    <div class="gradient-overlay" aria-hidden="true"></div>

    <el-container>
      <!-- 移动端汉堡菜单按钮 -->
      <button class="mobile-menu-btn" @click="toggleMobileMenu" :aria-expanded="showMobileMenu.toString()" aria-label="打开侧边栏">
        <el-icon><Menu /></el-icon>
      </button>

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
          <img src="../assets/img/fc-logo.png" alt="GDUT BanGDream Fan Club" class="logo" />
          <div class="brand">
            <span class="brand-title">管理中心</span>
            <span class="brand-sub">Admin Console</span>
          </div>
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
          <el-button type="text" @click="logout" class="logout-btn" aria-label="退出登录">
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
          <div class="copyright">Copyright (C) 2025 Faspand & Mio for 広東工業大学アイドル研究部 </div>
          <div class="disclaimer">広東工業大学アイドル研究部は非営利団体であり、本プロジェクトの不適切な使用によって生じたあらゆる問題について、広東工業大学アイドル研究部および本サイトの作者は一切の責任を負いません。</div>
        </el-footer>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { Document, Grid, Menu, SwitchButton } from '@element-plus/icons-vue';
import { computed, inject, onMounted, onUnmounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const router = useRouter();
const route = useRoute();
const eventName = inject('eventName', null);
const showMobileMenu = ref(false);

const breadcrumbTitle = computed(() => {
  if (route.params.event_id && eventName?.value) {
    return `活动设置（${eventName.value}）`;
  } else if (route.params.event_id) {
    return `活动设置（ID: ${route.params.event_id}）`;
  }
  return '';
});

const handleSelect = (key) => {
  if (key === '/event/admin/list') {
    router.push('/event/admin/list');
  } else if (key === '/event/admin/logs') {
    router.push('/event/admin/logs');
  }
};

const logout = () => {
  localStorage.removeItem('admin_login');
  router.push('/');
};

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
/* ===== Theming (echoes Auth.vue without copying 1:1) ===== */
.admin-layout {
  /* tokens inspired by Auth.vue */
  --accent: #E63462;          /* 主色 */
  --accent-strong: #C41E3A;   /* 悬停/激活 */
  --surface: rgba(255, 255, 255, 0.72);
  --elev: rgba(255, 255, 255, 0.55);
  --outline: rgba(230, 52, 98, 0.35);
  --text: #1f1f1f;
  --text-muted: #6b7280;
  /* layout vars */
  --sidebar-w: 200px;
  --header-h: 64px;
  --header-h-sm: 56px;

  min-height: 100vh;
  width: 100%;
  max-width: 100vw; /* 🔥 防止被子元素撑开 */
  background: #f7f7fb;
  display: flex;
  position: relative;
  overflow-x: hidden;
  box-sizing: border-box;
}

/* subtle background layers (like Auth.vue) */
.bg-layer {
  position: fixed;
  inset: 0;
  background: radial-gradient(1200px 600px at 10% 10%, rgba(230, 52, 98, 0.08), transparent 60%),
  radial-gradient(900px 500px at 90% 80%, rgba(196, 30, 58, 0.07), transparent 60%);
  z-index: 0;
}
.gradient-overlay {
  position: fixed;
  inset: 0;
  background: linear-gradient(180deg, rgba(255,255,255,0.7) 0%, rgba(255,255,255,0.4) 100%);
  backdrop-filter: blur(12px);
  z-index: 0;
  pointer-events: none;
}

.el-container { 
  position: relative; 
  z-index: 1; 
  width: 100%;
  max-width: 100vw; /* 🔥 防止被子元素撑开 */
  overflow-x: hidden;
  box-sizing: border-box;
}

.el-main {
  background: transparent;
  min-height: calc(100vh - 8rem);
}

/* ===== Mobile menu button ===== */
.mobile-menu-btn {
  position: fixed;
  top: 16px;
  left: 16px;
  width: 42px;
  height: 42px;
  border-radius: 12px;
  display: none; /* hidden on desktop by default */
  place-items: center;
  z-index: 1100;
  border: 1px solid var(--outline);
  background: linear-gradient(180deg, var(--surface), var(--elev));
  box-shadow: 0 6px 20px rgba(230, 52, 98, 0.15);
  transition: transform .2s ease, box-shadow .2s ease, background .2s ease;
}
.mobile-menu-btn:hover { transform: translateY(-1px); box-shadow: 0 10px 26px rgba(196, 30, 58, 0.22); }
.mobile-menu-btn:active { transform: translateY(0); }
.mobile-menu-btn:hover { transform: translateY(-1px); box-shadow: 0 10px 26px rgba(196, 30, 58, 0.22); }
.mobile-menu-btn:active { transform: translateY(0); }

/* ===== Sidebar ===== */
.sidebar {
  background: linear-gradient(180deg, rgba(230, 52, 98, 0.95) 0%, rgba(196, 30, 58, 0.95) 100%);
  color: #fff;
  display: flex;
  flex-direction: column;
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  width: var(--sidebar-w) !important;
  padding-bottom: 12px;
  border-right: 1px solid rgba(255,255,255,0.18);
  box-shadow: 0 12px 40px rgba(230, 52, 98, 0.25);
  backdrop-filter: blur(8px);
  transform: translateX(0);
  transition: transform .28s cubic-bezier(.2,.8,.2,1), box-shadow .28s ease;
  z-index: 1000; /* This is the fix */
}

.logo-container {
  padding: 22px 14px 16px 14px;
  display: flex;
  align-items: center;
  gap: 12px;
  background: linear-gradient(180deg, rgba(255,255,255,0.12), transparent);
}
.logo {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  object-fit: cover;
  border: 2px solid rgba(255,255,255,0.35);
  box-shadow: 0 6px 18px rgba(0,0,0,0.18);
  background: #fff; /* white background behind logo */
}
.brand { display: flex; flex-direction: column; line-height: 1.1; }
.brand-title { font-weight: 700; letter-spacing: .2px; }
.brand-sub { opacity: .85; font-size: 12px; }

.admin-menu {
  flex: 1;
  padding: 8px 8px 0 8px;
  background: transparent !important;
  border-right: none !important;
}

.el-menu-item {
  color: rgba(255,255,255,0.95) !important;
  font-size: 15px;
  display: flex;
  align-items: center;
  margin: 6px 6px;
  border-radius: 12px;
  min-height: 44px;
  padding-inline: 12px;
  transition: background .2s ease, transform .2s ease, box-shadow .2s ease;
}
.el-menu-item:hover { background: rgba(255,255,255,0.16); transform: translateX(2px); }
.el-menu-item.is-active {
  background: linear-gradient(180deg, #fff, #f7f7f8);
  color: var(--accent) !important;
  box-shadow: 0 8px 24px rgba(0,0,0,.12);
}
.el-menu-item.is-active .el-icon { color: var(--accent) !important; }
.el-menu-item .el-icon { margin-right: 10px; }

.sidebar-footer {
  margin-top: auto;
  padding: 10px;
  border-top: 1px dashed rgba(255,255,255,0.25);
}
.logout-btn {
  width: 100%;
  color: #fff !important;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 10px;
  background: rgba(255,255,255,0.12);
  transition: background .2s ease, transform .2s ease;
}
.logout-btn:hover { background: rgba(255,255,255,0.2); transform: translateY(-1px); }
.logout-btn .el-icon { color: #fff; }

/* ===== Main header ===== */
.main-container {
  margin-left: var(--sidebar-w);
  width: calc(100% - var(--sidebar-w)); /* fill the rest to the right */
  max-width: calc(100vw - var(--sidebar-w)); /* 🔥 防止被子元素撑开 */
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  height: 100vh;
  overflow: hidden; /* prevent body scrollbars */
  box-sizing: border-box; /* 确保 padding 不会导致溢出 */
}
.admin-header {
  position: fixed;
  top: 0;
  left: var(--sidebar-w);
  right: 0;
  height: var(--header-h) !important;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-sizing: border-box; /* ensure full bleed and no overflow calc issues */
  background: linear-gradient(180deg, var(--surface), var(--elev));
  border-bottom: 1px solid var(--outline);
  backdrop-filter: blur(10px);
  z-index: 100;
  box-shadow: 0 8px 30px rgba(0,0,0,0.06);
}
.breadcrumb-container { font-size: 13px; color: var(--text-muted); }
.el-breadcrumb__separator { color: var(--text-muted); }
.el-breadcrumb__item:last-child .el-breadcrumb__inner { color: var(--text); font-weight: 600; }
.welcome-text { color: var(--text-muted); font-size: 13px; }

.admin-main {
  padding: calc(18px + var(--header-h)) 22px 24px 22px; /* add space for fixed header */
  flex: 1;
  overflow: auto; /* internal scroll only */
  overflow-x: hidden; /* no horizontal growth */
  -webkit-overflow-scrolling: touch;
  min-width: 0; /* 🔥 允许 flex 子元素缩小到内容以下 */
  box-sizing: border-box; /* 确保 padding 计入尺寸 */
}

.admin-footer {
  text-align: center;
  padding: 18px 12px 28px;
  color: var(--text-muted);
  font-size: 12px;
  border-top: 1px solid rgba(0,0,0,0.06);
  background: linear-gradient(180deg, rgba(255,255,255,0.6), rgba(255,255,255,0.4));
  backdrop-filter: blur(6px);
  min-width: 0; /* 🔥 允许 flex 子元素缩小 */
  box-sizing: border-box;
}

/* ===== Mobile & responsive ===== */
.mobile-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  z-index: 999;
  opacity: 0;
  transition: opacity .25s ease;
}
.mobile-overlay[style*="display: block"] { opacity: 1; }

@media (max-width: 1024px) {
  .admin-header { padding-left: 68px; }
}


@media (max-width: 768px) {
  .main-container { margin-left: 0; max-width: 100vw; display: flex; flex-direction: column; height: 100vh; }
  .sidebar { transform: translateX(-100%); left: 0; }
  .sidebar.mobile-sidebar-open { transform: translateX(0); box-shadow: 0 20px 60px rgba(0,0,0,.35); }
  .admin-header { left: 0; right: 0; height: var(--header-h-sm) !important; padding: 0 56px 0 72px; }
  .admin-main { padding: calc(18px + var(--header-h-sm)) 16px 20px 16px; }
  .mobile-menu-btn { display: grid; top: 14px; left: 14px; width: 40px; height: 40px; }
}

@media (max-width: 480px) {
  .admin-header { left: 0; max-width: 100vw; height: var(--header-h-sm) !important; padding: 0 48px 0 68px; }
  .admin-main { padding: calc(16px + var(--header-h-sm)) 12px 18px 12px; }
  .logo { width: 56px; height: 56px; border-radius: 14px; }
  .brand-title { font-size: 14px; }
}


/* ===== Dark mode (prefers-color-scheme) ===== */
@media (prefers-color-scheme: dark) {
  .admin-layout {
    --surface: rgba(80, 20, 40, 0.7);
    --elev: rgba(80, 20, 40, 0.55);
    --outline: rgba(230, 52, 98, 0.32);
    --text: #eee;
    --text-muted: #c0c0c0;
    background: #0f0f14;
  }
  .sidebar {
    background: linear-gradient(180deg, rgba(230, 52, 98, 0.92) 0%, rgba(196, 30, 58, 0.92) 100%);
    box-shadow: 0 18px 60px rgba(0,0,0,0.45);
  }
  .admin-header { box-shadow: 0 6px 24px rgba(0,0,0,0.45); }
  .admin-footer { border-top-color: rgba(255,255,255,0.08); background: linear-gradient(180deg, rgba(30,30,30,0.7), rgba(30,30,30,0.55)); }
}

/* ===== Touch-friendly targets ===== */
@media (hover: none) and (pointer: coarse) {
  .el-menu-item { min-height: 52px; }
  .logout-btn { min-height: 48px; }
  .mobile-menu-btn { width: 44px; height: 44px; }
}
/* ===== Global layout resets to prevent body scrollbars ===== */
:global(html, body, #app) {
  height: 100%;
  overflow: hidden;
}
:global(body) { overscroll-behavior: none; }
:global(*::-webkit-scrollbar) { width: 0; height: 0; }
:global(*) { scrollbar-width: none; -ms-overflow-style: none; }
:deep(.el-container) { width: 100%; }
:deep(.el-main) { width: 100%; max-width: 100%; }
</style>
