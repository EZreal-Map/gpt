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

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/app'
    },
    { path: '/app', name: 'app', component: AppView },
    {
      path: '/app/:appID',
      name: 'id-app',
      component: APPIDRouterView,
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
      component: DataBaseFolderView
    },
    {
      path: '/database/:databaseID',
      name: 'id-database',
      component: IDDataBaseRouterView,
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
    }
  ]
})

export default router
