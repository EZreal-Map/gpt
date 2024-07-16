<template>
  <div class="chat-container">
    <div class="messages-container" ref="messagesDiv">
      <QAContainer
        v-for="message in messages"
        :key="message"
        :question="message.question"
        :answer="message.answer"
        v-model:citeDocument="message.citeDocument"
        :isConnecting="message.isConnecting"
      ></QAContainer>
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
        @click="sendMessage"
        :disabled="!canSendMessage"
        ><Top
      /></el-icon>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { fetchEventSource } from '@microsoft/fetch-event-source'
import { baseURL } from '@/utils/request.js'
import QAContainer from '@/components/QAContainer.vue'
import { Top, CircleClose } from '@element-plus/icons-vue'
import { useRoute } from 'vue-router'

// 使用 useRoute 获取路由信息
const appID = useRoute().params.appID

// messages -> 问答对话集合
// newQuery -> 存放input的问题
const messages = ref([])
const newQuery = ref('')

// 处理input输入框的回车事件，shift+回车换行, 回车发送消息
const handleEnterKeyDown = (event) => {
  if (!event.shiftKey) {
    event.preventDefault()
    sendMessage()
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

const sendMessage = () => {
  const query = newQuery.value.trim()

  // 如果input没有内容，直接返回
  // 如果有问题正在回答（正在连接），直接返回
  if (!query || isConnecting.value) return
  // 在这里重新创建 AbortController 实例
  ctrl.value = new AbortController()
  messages.value.push({
    question: newQuery.value,
    answer: '',
    citeDocument: [],
    isConnecting: true
  })
  newQuery.value = ''
  const streamUrl = baseURL + '/chat'
  fetchEventSource(streamUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      query: query,
      appset_id: appID
    }),
    signal: ctrl.value.signal,
    onmessage(event) {
      // 接收到消息回调 （多次）
      // console.log(event)
      const data = JSON.parse(event.data)
      // console.log(data)
      if (event.event === 'quotation') {
        // console.log(data)
        messages.value[messages.value.length - 1].citeDocument = data
      } else {
        messages.value[messages.value.length - 1].answer += data.content
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

// 当组件销毁时停止观察
onUnmounted(() => {
  if (observer.value) {
    observer.value.disconnect()
  }
})
</script>

<style scoped>
.chat-container {
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

/* 自定义滚动条样式 */
/* .messages-container::-webkit-scrollbar {
  width: 8px;
}

.messages-container::-webkit-scrollbar-thumb {
  background-color: #ccc;
  border-radius: 10px;
}

.messages-container::-webkit-scrollbar-track {
  background-color: transparent;
  border-radius: 10px;
}

.messages-container::-webkit-scrollbar-corner {
  background-color: transparent;
} */

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
