import { createRouter, createWebHistory } from 'vue-router'

import AppView from '@/views/AppView.vue'
import DataBaseFolderView from '@/views/DataBaseFolderView.vue'
import AccountView from '@/views/AccountView.vue'
import IDDataBaseRouterView from '@/views/IDDataBaseRouterView.vue'
import IDDataBaseDocumentView from '@/views/IDDataBaseDocumentView.vue'
import IDDataBaseHitTestingView from '@/views/IDDataBaseHitTestingView.vue'
import IDDataBaseDocumentChunkView from '@/views/IDDataBaseDocumentChunkView.vue'
import IDDataBaseUpdateDocumentView from '@/views/IDDataBaseUpdateDocumentView.vue'

import APPIDRouterView from '@/views/APPIDRouterView.vue'
import APPIDConfiguration from '@/views/APPIDConfiguration.vue'
import APPIDChat from '@/views/APPIDChat.vue'
import APPIDPublish from '@/views/APPIDPublish.vue'

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
        },
        {
          path: 'chat-test',
          name: 'id-app-chat',
          component: APPIDChat
        },
        {
          path: 'publish',
          name: 'id-app-publish',
          component: APPIDPublish
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
    { path: '/account', name: 'account', component: AccountView }
  ]
})

export default router
