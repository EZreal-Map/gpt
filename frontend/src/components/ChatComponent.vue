<template>
  <div class="chat-componet">
    <div class="messages-container" ref="messagesDiv">
      <!-- 历史消息 (history_messages) -->
      <QAContainer
        v-for="message in history_messages"
        :key="message.id"
        :id="message.id"
        :question="message.question"
        :answer="message.answer"
        v-model:citeDocument="message.cite_documents"
        :isConnecting="false"
        :parentExecuteTime="message.execute_time"
        :contextHistory="message.context_histories"
        :isTestMode="props.isTestMode"
        :fetchChatSetsData="props.fetchChatSetsData"
        :updateNewChatSetName="props.updateNewChatSetName"
        v-model:messages="history_messages"
        :sendMessage="sendMessage"
      ></QAContainer>
      <!-- 当前消息 (messages) -->
      <QAContainer
        v-for="message in messages"
        :key="message.id"
        v-model:id="message.id"
        :question="message.question"
        :answer="message.answer"
        v-model:citeDocument="message.citeDocument"
        :isConnecting="message.isConnecting"
        v-model:parentExecuteTime="message.execute_time"
        :contextHistory="message.contextHistory"
        :isTestMode="props.isTestMode"
        :fetchChatSetsData="props.fetchChatSetsData"
        :updateNewChatSetName="props.updateNewChatSetName"
        v-model:messages="messages"
        :sendMessage="sendMessage"
      ></QAContainer>
    </div>
    <!-- 初始封面 -->
    <div class="init-cover" v-if="isShowInitCover">
      <h1>
        <div
          :class="{ 'typing-animation': !isTypingDone }"
          @animationend="handleFirstLineAnimationEnd"
        >
          {{ initCoverText.firstLine }}
        </div>
      </h1>
      <div>
        <div
          class="second-line"
          v-if="isSecondLineVisible"
          :class="{ 'typing-animation': !isSecondLineTypingDone }"
          @animationend="isSecondLineTypingDone = true"
        >
          {{ initCoverText.secondLine }}
        </div>
      </div>
    </div>

    <div class="input-container">
      <el-input
        v-model="newQuery"
        :autosize="{ minRows: 1, maxRows: 8 }"
        type="textarea"
        resize="none"
        placeholder="Type a message..."
        class="input-field"
        @keydown.enter="handleEnterKeyDown"
        @input="checkInput"
      />

      <el-icon
        size="20"
        class="input-icon enabled-icon"
        color="red"
        v-if="isConnecting"
        @click="stopSendMessage"
        ><CircleClose
      /></el-icon>
      <el-icon
        v-else
        size="20"
        :class="{
          'enabled-icon': canSendMessage,
          'disabled-icon': !canSendMessage
        }"
        class="input-icon"
        @click="sendMessage(newQuery)"
        :disabled="!canSendMessage"
        ><Top
      /></el-icon>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { fetchEventSource } from '@microsoft/fetch-event-source'
import { baseURL } from '@/utils/request.js'
import QAContainer from '@/components/QAContainer.vue'
import { Top, CircleClose } from '@element-plus/icons-vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getChatHistoryAxios } from '@/api/chatset.js'

// 使用 useRoute 获取路由信息
const route = useRoute()
let appID = route.params.appID
let chatID = route.query.chatID
console.log('chatID', chatID)
// defineProps 接收父组件传递的数据
// isTestMode 除了在本组件 (ChatComponent) 内部使用，还会主动传递给子组件使用 (QAContainer)
const props = defineProps({
  isTestMode: { type: Boolean, default: false },
  fetchChatSetsData: {
    type: Function,
    default: () => {
      console.log('Function fetchChatSetsData is null')
    }
  },
  updateNewChatSetName: {
    type: Function,
    default: () => {
      console.log('Function updateNewChatSetName is null')
    }
  }
})

// 初始封面与动画有关变量
const isShowInitCover = ref(true) // 初始封面显示状态
const isTypingDone = ref(false) // 是否打字动画完成
const isSecondLineVisible = ref(false) // 第二行是否显示
const isSecondLineTypingDone = ref(false) // 第二行打字动画完成

// defineExpose 用于暴露组件内部的方法给父组件使用
defineExpose({
  // 重置初始封面参数，为了重新显示typing动画
  initParams: () => {
    isTypingDone.value = false
    isSecondLineVisible.value = false
    isSecondLineTypingDone.value = false
    console.log('initParams')
  }
})

const initCoverText = {
  firstLine: '我是你的AI助手',
  secondLine: '请你试着开始和我对话吧'
}

const handleFirstLineAnimationEnd = () => {
  isTypingDone.value = true
  // 开始显示第二行
  isSecondLineVisible.value = true
}

const history_messages = ref('') // 历史对话存储 （关键）
const fetchChatHistory = async () => {
  isShowInitCover.value = false
  const { data } = await getChatHistoryAxios({
    appset_id: appID,
    chat_id: chatID
  })
  history_messages.value = data
  if (history_messages.value.length > 0) {
    isShowInitCover.value = false
  }
  console.log('fetchChatHistory', history_messages.value)
}

// 如果是测试模式或者有chatID，就获取聊天记录
// 既不是测试模式，也没有chatID，就不获取聊天记录 (这个是新建聊天的情况，不需要获取聊天记录)
if (props.isTestMode || chatID) {
  fetchChatHistory()
} else {
  // initCoverText.value = ''
  isShowInitCover.value = true
  // initCoverText.value = text
}

// messages -> 问答对话集合
// newQuery -> 存放input的问题
const messages = ref([])
const newQuery = ref('')

// 处理input输入框的回车事件，shift+回车换行, 回车发送消息
const handleEnterKeyDown = (event) => {
  if (!event.shiftKey) {
    event.preventDefault()
    sendMessage(newQuery.value)
  }
}

// 检查输入框是否为空,不为空的时候，发送按钮可用
const canSendMessage = ref(false)
const checkInput = () => {
  canSendMessage.value = newQuery.value.trim() !== ''
}

// 是否正在连接，获取最后一个消息的连接状态
const isConnecting = computed(() => {
  if (messages.value.length > 0) {
    return messages.value[messages.value.length - 1].isConnecting
  }
  return false
})

// 用于控制连接的终止
const ctrl = ref(null) // 使用 ref 来定义 AbortController

const sendMessage = (query) => {
  // const query = newQuery.value.trim()

  // 如果input没有内容，直接返回
  // 如果有问题正在回答（正在连接），直接返回
  if (!query || isConnecting.value) return
  isShowInitCover.value = false // 隐藏初始封面
  // 在这里重新创建 AbortController 实例
  ctrl.value = new AbortController()
  messages.value.push({
    id: null,
    question: query,
    answer: '',
    citeDocument: [],
    isConnecting: true,
    contextHistory: [],
    execute_time: 0
  })
  // 还是把输入框重置
  newQuery.value = ''
  const streamUrl = baseURL + '/chat'
  fetchEventSource(streamUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      query: query,
      appset_id: appID,
      chat_id: chatID
    }),
    signal: ctrl.value.signal,
    openWhenHidden: true, // 在调用失败时禁止重复调用
    onmessage(event) {
      // 接收到消息回调 （多次）
      // console.log(event)
      const data = JSON.parse(event.data)
      // console.log(data)
      if (event.event === 'message') {
        messages.value[messages.value.length - 1].answer += data.content
      } else if (event.event === 'quotation') {
        messages.value[messages.value.length - 1].citeDocument = data
      } else if (event.event === 'context_history') {
        messages.value[messages.value.length - 1].contextHistory = data
      }
    },
    onclose() {
      // 正常连接关闭回调
      messages.value[messages.value.length - 1].isConnecting = false
      console.log('Connection closed')
    },
    onerror(err) {
      //连接出现异常回调
      // 必须抛出错误才会停止
      ElMessage.error('回答出现问题，请重试')
      if (messages.value[messages.value.length - 1]?.isConnecting) {
        messages.value[messages.value.length - 1].isConnecting = false
      }
      ctrl.value.abort() // 终止连接
      throw err
    }
  })
}

const stopSendMessage = () => {
  ctrl.value.abort() // 终止连接
  console.log('stopSendMessage')
  messages.value[messages.value.length - 1].isConnecting = false
}
const messagesDiv = ref(null)
const observer = ref(null)

onMounted(() => {
  observeScrollHeight()
})

const observeScrollHeight = () => {
  if (messagesDiv.value) {
    // MutationObserver 接受一个回调函数作为参数 (callback)，
    // 这个回调函数会在监听到指定 DOM 节点（messagesDiv.value）的变化时被调用。
    observer.value = new MutationObserver(() => {
      scrollToBottom()
    })
    // childList: true 表示监听子节点的变化，即节点的子节点（即消息列表中的消息条目）发生变化时触发回调。
    // subtree: true 表示监听目标节点的所有后代节点，即包括子节点、子节点的子节点等，以确保深度监听
    observer.value.observe(messagesDiv.value, {
      childList: true,
      subtree: true
    })
  }
}

const scrollToBottom = () => {
  if (messagesDiv.value) {
    if (
      messagesDiv.value.scrollHeight -
        messagesDiv.value.scrollTop -
        messagesDiv.value.clientHeight <
      200
    ) {
      messagesDiv.value.scrollTop = messagesDiv.value.scrollHeight
    }
  }
}

// 监听路由变化，重新加载组件
watch(
  () => route.query.chatID,
  (newChatID, oldChatID) => {
    if (newChatID !== oldChatID) {
      // 触发组件重新加载逻辑
      console.log('Chat ID changed from', oldChatID, 'to', newChatID)
      // 清空本轮（未刷新界面）对话产生的记录
      messages.value = []
      appID = route.params.appID
      chatID = route.query.chatID
      if (props.isTestMode || chatID) {
        // 获取历史聊天记录 (测试模式或者有chatID)
        fetchChatHistory() // 获取聊天记录
      } else {
        // 清空历史记录 (新建聊天)
        history_messages.value = [] // 清空聊天记录
        isShowInitCover.value = true
      }
    }
  }
)

// 当组件销毁时停止观察
onUnmounted(() => {
  if (observer.value) {
    observer.value.disconnect()
  }
})
</script>

<style scoped>
.chat-componet {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  text-align: left;
  max-height: 100%; /* 确保子组件不超过父组件 */
}

.init-cover {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
}

.init-cover second-line {
  font-size: 16px;
  font-weight: 400;
}

.typing-animation {
  white-space: nowrap;
  overflow: hidden;
  border-right: 2px solid;
  animation:
    typing 1s steps(30, end),
    blink-caret 0.5s step-end infinite;
}

@keyframes typing {
  from {
    width: 0;
  }
  to {
    width: 100%;
  }
}

@keyframes blink-caret {
  from,
  to {
    border-color: transparent;
  }
  50% {
    border-color: black;
  }
}

.input-container {
  display: flex;
  align-items: center;
  margin: 10px auto; /* 居中对齐 */
  margin-top: auto; /* 将输入框放置在底部 */
  width: 70%;
}

.input-container button {
  margin-left: 10px;
  padding: 8px 15px;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 3px;
  cursor: pointer;
}

.input-icon {
  margin-left: 10px;
  margin-bottom: 2px;
  border-radius: 8px;
  padding: 6px;
  transition:
    background-color 0.3s,
    color 0.3s;
}

.input-icon.enabled-icon {
  background-color: #409eff;
  color: white;
  cursor: pointer;
}

.input-icon.disabled-icon {
  background-color: #f1f1f1;
  color: black;
}
</style>
