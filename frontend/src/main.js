import './assets/main.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'


import { createApp } from 'vue'
import App from './App.vue'
import Auth from "@/views/Auth.vue";
import Event from "@/views/Event.vue";
import EventList from "@/views/EventList.vue"
import NotFound from "@/views/NotFound.vue";

import { createRouter, createWebHistory } from 'vue-router';

import axios from 'axios';
import { ElMessage } from "element-plus";
import { apiClient } from "@/api/axios.js";
import VueKonva from "vue-konva";

axios.defaults.baseURL = `${import.meta.env.VITE_API_BASE_URL}`;

const PublicRoutes = [
    { path: '/', redirect: '/event' },
    { path: '/about', component: () => import('@/views/About.vue'), name: 'About' },
    {
        path: '/event/admin',
        component:  () => import('@/views/Admin.vue'),
        name: 'admin',
        meta:{
            title: '管理',
            requiresAdmin: true
        },
        children: [
            {
                path: 'list',
                name: 'EventList',
                component:  EventList,
                meta: {
                    title: '活动一览',
                },
            },
            {
                path: 'list/:event_id/export',
                name: 'EventPicExport',
                component: () => import('@/components/PicEdit.vue')
            },
            {
                path: 'list/:event_id/view',
                name: 'EventView',
                component: () => import('@/components/EventView.vue')
            },
            {
                path: 'logs',
                name: 'SystemLogs',
                component: () => import('@/views/LogView.vue'),
                meta: {
                    title: '系统日志',
                    requiresAdmin: true
                }
            }
        ]
    },
    { path: '/event', component: Auth},
    {
        path: '/event/:event_id(\\d+)',
        component: Event,
        props: true,
        meta: { requiresAuth: true }
    },

    { path: '/:pathMatch(.*)*', name: 'NotFound', component: NotFound },

    // { path: '/event/admin/edit/:event_id', component:  () => import('@/views/PicEdit.vue'), name: 'pic', props: true},
]

const router = createRouter({
  history: createWebHistory(),
  routes: PublicRoutes
})

//Global Route Guard
router.beforeEach(async (to, from, next) => {
    const token = localStorage.getItem('token');

    const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
    const requiresAdmin = to.matched.some(record => record.meta.requiresAdmin);

    if (!requiresAuth && !requiresAdmin) {
        return next();
    }

    if (!token) {
        ElMessage.error('请先登录');
        return next('/event');
    }

    try {
        const response = await apiClient.get('/verify-token');
        const userData = response.data;

        if (requiresAdmin && userData.role !== 'admin') {
            ElMessage.error('需要管理员权限');
            return next('/event');
        }

        return next();

    } catch (error) {
        console.error('Token验证失败:', error);
        ElMessage.error('登录状态异常，请重新登录');
        localStorage.removeItem('token');
        localStorage.removeItem('description');
        return next('/event');
    }
});

const app = createApp(App)
app.use(VueKonva)

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
}
app.use(router).mount('#app')