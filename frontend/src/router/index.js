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
import IDDataBaseUpdateDocumentView from '@/views/IDDataBaseUploadDocumentView.vue'

// 二级路由：应用的子路由
import APPIDRouterView from '@/views/APPIDRouterView.vue'
import APPIDConfiguration from '@/views/APPIDConfiguration.vue'
import APPUserManagement from '@/views/APPUserManagement.vue'

// 一级路由：聊天
import ChatView from '@/views/ChatView.vue'

// 其他路由：403禁止访问、404未找到
import ForbiddenView from '@/views/ForbiddenView.vue'
import NotFoundView from '@/views/NotFoundView.vue'
// 其他路由：登录
import LoginView from '@/views/LoginView.vue'

import { ElMessage } from 'element-plus'
import {
  checkIsAdminLogin,
  checkIsNormalLogin,
  isNormalUserAccessApp
} from '@/api/admin_user.js'
// 定义登录判断路由守卫
const isAdminLogin = async (to, from, next) => {
  const result = await checkIsAdminLogin()
  if (result) {
    next() // 已经登录，允许访问
  } else {
    ElMessage.warning('抱歉，您没有权限访问此页面') // 显示警告消息
    next({ name: 'login' }) // 未登录，重定向到首页或其他页面
  }
}

const isNormalLogin = async (to, from, next) => {
  let result
  console.log(to.name === 'chat')
  if (to.name === 'chat') {
    console.log('to.params.appID', to.params.appID)
    // 如果访问的是聊天页面，就要判断是否有权限访问
    result = await isNormalUserAccessApp(to.params.appID)
  } else {
    // 如果访问的是其他页面，就要判断是否登录就行
    result = await checkIsNormalLogin()
  }
  if (result) {
    next() // 已经登录，允许访问
  } else {
    ElMessage.warning('抱歉，您没有权限访问此页面') // 显示警告消息
    next({ name: 'login' }) // 未登录，重定向到首页或其他页面
  }
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/app',
      name: 'app',
      component: AppView,
      beforeEnter: isAdminLogin
    },
    {
      path: '/app/:appID',
      name: 'id-app',
      component: APPIDRouterView,
      beforeEnter: isAdminLogin,
      redirect: (to) => {
        return {
          name: 'app-configuration',
          params: { appID: to.params.appID }
        }
      },
      children: [
        {
          path: 'configuration',
          name: 'app-configuration',
          component: APPIDConfiguration
        },
        {
          path: 'userManagement',
          name: 'app-user-management',
          component: APPUserManagement
        }
      ]
    },
    {
      path: '/database',
      name: 'database',
      component: DataBaseFolderView,
      beforeEnter: isAdminLogin
    },
    {
      path: '/database/:databaseID',
      name: 'id-database',
      component: IDDataBaseRouterView,
      beforeEnter: isAdminLogin,
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
    {
      path: '/account',
      name: 'account',
      component: AccountView,
      beforeEnter: isAdminLogin
    },
    {
      path: '/chat/:appID',
      name: 'chat',
      component: ChatView,
      beforeEnter: isNormalLogin,
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
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { noLayout: true }
    },
    // 捕获未匹配的路由
    {
      path: '/:pathMatch(.*)*', // Vue Router 4 推荐用法
      redirect: '/404' // 未匹配路由跳转到登录页面
    }
  ]
})

export default router
