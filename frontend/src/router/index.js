import { createRouter, createWebHistory } from 'vue-router'
// 3个一级路由 应用/知识库/账户
import AppView from '@/views/AppView.vue'
import DataBaseFolderView from '@/views/DataBaseFolderView.vue'
import AccountView from '@/views/AccountView.vue'

// 二级路由：知识库的子路由
import IDDataBaseRouterView from '@/views/IDDataBaseRouterView.vue'
import IDDataBaseDocumentView from '@/views/IDDataBaseDocumentView.vue'
import IDDataBaseHitTestingView from '@/views/IDDataBaseHitTestingView.vue'
import IDDataBaseDocumentChunkView from '@/views/IDDataBaseDocumentChunkView.vue'
import IDDataBaseUpdateDocumentView from '@/views/IDDataBaseUpdateDocumentView.vue'

// 二级路由：应用的子路由
import APPIDRouterView from '@/views/APPIDRouterView.vue'
import APPIDConfiguration from '@/views/APPIDConfiguration.vue'

// 一级路由：聊天
import ChatView from '@/views/ChatView.vue'

// 其他路由：403禁止访问、404未找到
import ForbiddenView from '@/views/ForbiddenView.vue'
import NotFoundView from '@/views/NotFoundView.vue'

import { ElMessage } from 'element-plus'
import { checkIsLogin } from '@/api/user.js'
// 定义登录判断路由守卫
const isLogin = async (to, from, next) => {
  const isLogin = await checkIsLogin()
  if (isLogin) {
    next() // 已经登录，允许访问
  } else {
    ElMessage.warning('您没有权限访问此页面，请登录') // 显示警告消息
    next({ name: 'account' }) // 未登录，重定向到首页或其他页面
  }
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/account'
    },
    { path: '/app', name: 'app', component: AppView, beforeEnter: isLogin },
    {
      path: '/app/:appID',
      name: 'id-app',
      component: APPIDRouterView,
      beforeEnter: isLogin,
      redirect: (to) => {
        return {
          name: 'id-app-configuration',
          params: { appID: to.params.appID }
        }
      },
      children: [
        {
          path: 'configuration',
          name: 'id-app-configuration',
          component: APPIDConfiguration
        }
      ]
    },
    {
      path: '/database',
      name: 'database',
      component: DataBaseFolderView,
      beforeEnter: isLogin
    },
    {
      path: '/database/:databaseID',
      name: 'id-database',
      component: IDDataBaseRouterView,
      beforeEnter: isLogin,
      // 重定向其子路径 /database/:databaseID/document
      redirect: (to) => {
        return {
          name: 'id-database-document',
          params: { databaseID: to.params.databaseID }
        }
      },
      children: [
        {
          path: 'document',
          name: 'id-database-document',
          component: IDDataBaseDocumentView
        },
        {
          path: 'hitTesting',
          name: 'id-database-hit-testing',
          component: IDDataBaseHitTestingView
        },
        {
          path: 'document/:documentID',
          name: 'id-database-document-chunk',
          component: IDDataBaseDocumentChunkView
        },
        {
          path: 'document/update',
          name: 'id-database-document-update',
          component: IDDataBaseUpdateDocumentView
        }
      ]
    },
    { path: '/account', name: 'account', component: AccountView },
    {
      path: '/chat/:appID',
      name: 'chat',
      component: ChatView,
      meta: { noLayout: true }
    },
    {
      path: '/403',
      name: 'forbidden',
      component: ForbiddenView,
      meta: { noLayout: true }
    },
    {
      path: '/404',
      name: 'not-found',
      component: NotFoundView,
      meta: { noLayout: true }
    }
  ]
})

export default router
