import { createRouter, createWebHistory } from 'vue-router'

import AppView from '@/views/AppView.vue'
import DataBaseView from '@/views/DataBaseView.vue'
import AccountView from '@/views/AccountView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/app'
    },
    { path: '/app', component: AppView },
    { path: '/database', component: DataBaseView },
    { path: '/account', component: AccountView }
  ]
})

export default router
