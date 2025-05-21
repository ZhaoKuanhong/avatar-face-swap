import './assets/main.css'
import 'element-plus/theme-chalk/dark/css-vars.css'


import { createApp } from 'vue'
import App from './App.vue'
import Auth from "@/views/Auth.vue";
import Event from "@/views/Event.vue";
import EventList from "@/views/EventList.vue"
import NotFound from "@/views/NotFound.vue";

import { createRouter, createWebHistory } from 'vue-router';

import axios from 'axios';
import {ElMessage} from "element-plus";
import {apiClient} from "@/api/axios.js";

axios.defaults.baseURL = `${import.meta.env.VITE_API_BASE_URL}`;

const PublicRoutes = [
    { path: '/', redirect: '/event' },
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
                path: 'list/:event_id',
                name: 'EventSetting',
                component: () => import('@/components/PicEdit.vue')
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

    { path: '/:pathMatch(.*)*', name: 'NotFound', component: NotFound }
    // { path: '/event/admin/edit/:event_id', component:  () => import('@/views/PicEdit.vue'), name: 'pic', props: true},
]

const router = createRouter({
  history: createWebHistory(),
  routes: PublicRoutes
})

//Global Route Guard
router.beforeEach(async (to, from, next) => {
    const token = localStorage.getItem('token');

    // check
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
        // validate
        const response = await apiClient.get('/verify-token');
        const userData = response.data;

        // check if admin
        if (requiresAdmin && userData.role !== 'admin') {
            ElMessage.error('需要管理员权限');
            return next('/event');
        }

        // check user
        if (requiresAuth && to.params.event_id) {
            if (userData.role !== 'admin' && userData.event_id !== to.params.event_id) {
                ElMessage.error('您没有权限访问此活动');
                return next('/event');
            }
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
app.use(router).mount('#app')