import './assets/main.css'
import 'element-plus/theme-chalk/dark/css-vars.css'


import { createApp } from 'vue'
import App from './App.vue'
import Auth from "@/views/Auth.vue";
import Event from "@/views/Event.vue";
import EventList from "@/views/EventList.vue"

import { createRouter, createWebHistory } from 'vue-router';

import axios from 'axios';

axios.defaults.baseURL = `${import.meta.env.VITE_API_BASE_URL}`;

const PublicRoutes = [
    { path: '/event', component: Auth},
    { path: '/event/:event_id', component: Event, props: true },
    {
        path: '/event/admin',
        component:  () => import('@/views/Admin.vue'),
        name: 'admin',
        meta:{
            title: '管理'
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

    // { path: '/event/admin/edit/:event_id', component:  () => import('@/views/PicEdit.vue'), name: 'pic', props: true},
]

const router = createRouter({
  history: createWebHistory(),
  routes: PublicRoutes
})

const app = createApp(App)
app.use(router).mount('#app')