<template>
  <div class="chat-view">
    <div
      class="sidebar-container"
      :class="{ hidden: !settingStore.isSidebarVisible }"
    >
      <div class="button-group">
        <el-tooltip
          content="关闭侧边栏"
          placement="bottom"
          :visible="tooltipVisible_sidebar && tooltipVisible_sidebar_ready"
        >
          <div
            class="button"
            @mouseenter="tooltipVisible_sidebar = true"
            @mouseleave="sidebarMouseLeaveHandler"
            @click="sidebarClickHandler"
          >
            <el-icon size="24"><Open /></el-icon>
          </div>
        </el-tooltip>
        <el-tooltip
          content="新建聊天"
          placement="bottom"
          :visible="
            tooltipVisible_sidebar_newchat &&
            tooltipVisible_sidebar_newchat_ready
          "
        >
          <div
            class="button"
            @mouseenter="tooltipVisible_sidebar_newchat = true"
            @mouseleave="tooltipVisible_sidebar_newchat = false"
            @click="newChat"
          >
            <el-icon size="24"><ChatLineSquare /></el-icon>
          </div>
        </el-tooltip>
      </div>
      <div class="chatset-list" ref="chatsetListDOM">
        <ChatSetBox
          v-for="chatset in chatsets"
          :key="chatset.id"
          v-model:name="chatset.name"
          :chatset="chatset"
          :routeToChat="routeToChat"
          :fetchChatSetsData="fetchChatSetsData"
          :newChat="newChat"
        ></ChatSetBox>
      </div>
    </div>
    <div class="chat-container">
      <div class="chat-container-title">
        <div
          :class="{ hidden: !settingStore.isSidebarVisible }"
          class="button-group"
        >
          <el-tooltip
            content="打开侧边栏"
            placement="bottom"
            :visible="tooltipVisible_chat && tooltipVisible_chat_ready"
          >
            <div
              class="button"
              @mouseenter="tooltipVisible_chat = true"
              @mouseleave="chatMouseLeaveHandler"
              @click="chatClickHandler"
            >
              <el-icon size="24"><TurnOff /></el-icon>
            </div>
          </el-tooltip>
          <el-tooltip
            content="新建聊天"
            placement="bottom"
            :visible="tooltipVisible_chat_newchat"
          >
            <div
              class="button"
              @mouseenter="tooltipVisible_chat_newchat = true"
              @mouseleave="tooltipVisible_chat_newchat = false"
              @click="newChat"
            >
              <el-icon size="24"><ChatLineSquare /></el-icon>
            </div>
          </el-tooltip>
        </div>
        <el-tooltip content="回到管理界面" placement="bottom"
          ><img
            src="/avatar.png"
            alt=""
            class="avater-img"
            @click="goBackAdminRouter"
        /></el-tooltip>
      </div>
      <div class="chat-container-content">
        <ChatComponent
          :fetchChatSetsData="fetchChatSetsData"
          :updateNewChatSetName="updateNewChatSetName"
          ref="ChatComponentDOM"
        ></ChatComponent>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { TurnOff, Open, ChatLineSquare } from '@element-plus/icons-vue'
import { getChatSetsAxios } from '@/api/chatset.js'
import { updateNewChatTitleAxios } from '@/api/chat.js'
import { useSettingStore } from '@/stores/setting.js'
import ChatSetBox from '@/components/ChatSetBox.vue'
import ChatComponent from '@/components/ChatComponent.vue'
import { getAppsetAxios } from '@/api/appset.js'
import { checkIsLogin } from '@/api/user.js'
import { ElMessage, ElMessageBox } from 'element-plus'

// 跳转路由
const router = useRouter()
// 使用 useRoute 获取路由信息
const appID = useRoute().params.appID
// 侧边栏显示与隐藏逻辑
const settingStore = useSettingStore() // 持久化存储 侧边栏状态

const checkAppPrivacyStatus = async () => {
  const response = await getAppsetAxios(appID)
  console.log(response.data.privacy)
  // 如果是私有的，需要判断是否登录
  if (response.data.privacy === '私有') {
    // 判断是否登录
    const isLogin = await checkIsLogin()
    if (isLogin) return
    // 未登录，弹出提示登录框
    // 关闭侧边栏显示
    settingStore.isSidebarVisible = false
    // 弹出提示登录框
    ElMessageBox.confirm('你访问的应用已被设置为私有访问', {
      confirmButtonText: '登录',
      cancelButtonText: '取消访问'
    })
      .then(async () => {
        // 跳转到登录界面
        router.push({ name: 'account' })
        ElMessage.info('请登录后再访问')
      })
      .catch(() => {
        // 跳转到403页面
        router.push({ name: 'forbidden' })
      })
  }
}
checkAppPrivacyStatus()

const chatsets = ref('')
const fetchChatSetsData = async () => {
  const { data } = await getChatSetsAxios({ appset_id: appID })
  chatsets.value = data
  console.log('chatsets', data)
}
fetchChatSetsData()

const updateNewChatSetName = async (chat_id, question, answer) => {
  console.log('第一个QA：', question, answer)
  const firstChatsetItemName =
    chatsetListDOM.value.querySelector('.chatset-item-name')
  console.log('第一个firstChatsetItemName', firstChatsetItemName)
  console.log('更新名字之前', chatsets.value[0].name)
  const response = await updateNewChatTitleAxios({ chat_id, question, answer })
  chatsets.value[0].name = response.data.title_name
  firstChatsetItemName.classList.add('typing-animation') // 添加打字动画类
  console.log('更新名字之后', chatsets.value[0].name)
}

// const isSidebarVisible = ref(false)
// const toggleSidebar = () => {
//   isSidebarVisible.value = !isSidebarVisible.value
// }

// 有关 tooltip 的显示逻辑 (与侧边栏显示与隐藏的联动 )
// 有ready命名的变量 代表是否具备显示的条件
// 无ready命名的变量 是配合MouseEnter和MouseLeave事件的显示逻辑
const tooltipVisible_sidebar = ref(false)
const tooltipVisible_sidebar_ready = ref(true)
const tooltipVisible_sidebar_newchat = ref(false)
const tooltipVisible_sidebar_newchat_ready = ref(true)
const tooltipVisible_chat = ref(false)
const tooltipVisible_chat_ready = ref(true)
const tooltipVisible_chat_newchat = ref(false) // 最后一个按钮(chat界面下的new_chat)，始终具备显示条件，所有无ready变量

const sidebarMouseLeaveHandler = () => {
  tooltipVisible_sidebar.value = false
  tooltipVisible_sidebar_ready.value = true
}
const chatMouseLeaveHandler = () => {
  tooltipVisible_chat.value = false
  tooltipVisible_chat_ready.value = true
}

// 侧边栏 隐藏侧边栏按钮点击事件
const sidebarClickHandler = () => {
  // 点击按钮时，调用toggleSidebar方法，切换侧边栏的显示状态
  settingStore.toggleSidebar()
  // 一些防止联动tooltip显示混乱的逻辑
  tooltipVisible_chat_ready.value = false
  tooltipVisible_sidebar_newchat_ready.value = false
  setTimeout(() => {
    tooltipVisible_sidebar_newchat_ready.value = true
  }, 100) // 设置一个定时器，在 0.1 秒后将值改为 true
}
// 聊天界面 显示侧边栏按钮点击事件
const chatClickHandler = () => {
  // 点击按钮时，调用toggleSidebar方法，切换侧边栏的显示状态
  settingStore.toggleSidebar()
  // 一些防止联动tooltip显示混乱的逻辑
  tooltipVisible_sidebar_ready.value = false
  tooltipVisible_sidebar_newchat_ready.value = false
  setTimeout(() => {
    tooltipVisible_sidebar_newchat_ready.value = true
  }, 100) // 设置一个定时器，在 0.1 秒后将值改为 true
}

const chatsetListDOM = ref('') // 侧边栏列表dom
const ChatComponentDOM = ref('') // 聊天组件dom

// 路由跳转 切换不同的chatset
const routeToChat = (appID, chatID = null) => {
  if (chatID) {
    router.push({
      name: 'chat',
      params: { appID: appID },
      query: { chatID: chatID }
    })
  } else {
    router.push({
      name: 'chat',
      params: { appID: appID }
    })
  }
}

const newChat = () => {
  // 新建聊天的逻辑
  routeToChat(appID)
  ChatComponentDOM.value.initParams()
}

const goBackAdminRouter = () => {
  router.push({
    name: 'id-app-configuration',
    params: { appID: appID }
  })
}
</script>

<style scoped>
.chat-view {
  display: flex;
  height: 100%;
}

.sidebar-container {
  width: 250px;
  background-color: #f9f9f9;
  padding: 8px; /* 看起来padding-right多了8px 因为滚动条设置有8px */
  box-sizing: border-box;
  transition: margin-left 0.1s ease;
  overflow-y: scroll; /* 增加滚动条 */
  height: 100%; /* 确保侧边栏容器高度占满父容器 */
}

.sidebar-container.hidden {
  margin-left: -250px;
}

.chat-container {
  flex: 1;
  padding: 8px 12px;
  overflow-y: auto;
  background-color: #ffffff;
  transition: margin-left 0.1s ease;
  display: flex;
  flex-direction: column;
}

.button-group {
  display: flex;
  margin-bottom: 10px;
}

.sidebar-container .button-group {
  justify-content: space-between;
}

.chat-container .button-group {
  opacity: 0;
}

.chat-container .button-group.hidden {
  opacity: 1;
}

.button-group .button {
  color: #7d7d7d;
  width: 40px;
  height: 40px;
  display: flex;
  justify-content: center; /* 水平居中 */
  align-items: center; /* 垂直居中 */
  border-radius: 10px;
}

.button-group .button:hover {
  color: #333;
  background-color: #ececec;
}

.chat-container-title {
  display: flex;
  justify-content: space-between;
}

.avater-img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
}

.chat-container-content {
  flex: 1;
  height: 0; /* 设置height后,确保了它不会因内容撑开自己,如果子元素有滚动条，优先产生滚动条 */
}

.chatset-list {
  list-style-type: none;
  padding: 0;
}
</style>
