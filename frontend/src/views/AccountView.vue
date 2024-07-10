<template>
  <div class="chat-container">
    <div class="messages">
      <div
        v-for="(message, index) in messages"
        :key="index"
        class="message"
        :class="{
          'user-message': message.type === 'user',
          'bot-message': message.type === 'bot'
        }"
      >
        <MdPreview
          editorId="preview-only"
          :modelValue="message.text"
          previewTheme="github"
        />
      </div>
    </div>
    <div class="input-box">
      <input
        v-model="newQuery"
        @keyup.enter="sendMessage"
        placeholder="Type a message..."
        class="input-field"
      />
      <button @click="sendMessage">Send</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { fetchEventSource } from '@microsoft/fetch-event-source'
import { baseURL } from '@/utils/request.js'

import { MdPreview } from 'md-editor-v3'
// preview.css相比style.css少了编辑器那部分样式
import 'md-editor-v3/lib/preview.css'

console.log(baseURL)

const messages = ref([])
const newQuery = ref('')

function sendMessage() {
  const query = newQuery.value.trim()
  if (query === '') return
  messages.value.push({ text: newQuery.value, type: 'user' })

  const ctrl = new AbortController()
  const streamUrl = baseURL + '/chat'
  fetchEventSource(streamUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      query: query
    }),
    signal: ctrl.signal,
    onmessage(event) {
      const data = JSON.parse(event.data)
      console.log(data)
      if (messages.value[messages.value.length - 1].type === 'bot') {
        messages.value[messages.value.length - 1].text += data['content']
      } else {
        messages.value.push({ text: data['content'], type: 'bot' })
      }
      // console.log(messages.value[messages.value.length - 1].text)
    }
  })
  newQuery.value = ''
}

onMounted(() => {
  scrollToBottom()
})

function scrollToBottom() {
  const messagesDiv = document.querySelector('.messages')
  if (messagesDiv) {
    messagesDiv.scrollTop = messagesDiv.scrollHeight
  }
}
</script>

<style scoped>
.chat-container {
  border: 1px solid #ccc;
  padding: 10px;
  border-radius: 5px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  height: 95%; /* 占据父元素的高度 */
}

.messages {
  flex: 1;
  overflow-y: auto;
  text-align: left;
}

.message {
  margin: 5px;
  padding: 10px;
  border-radius: 5px;
}

.user-message {
  background-color: #e6f2ff;
  align-self: flex-end;
}

.bot-message {
  background-color: #f0f0f0;
  align-self: flex-start;
}

.input-box {
  margin-top: 10px;
  display: flex;
  align-items: center;
  margin-top: auto; /* 将输入框放置在底部 */
}

.input-box input {
  flex: 1;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 3px;
  margin-right: 10px;
}

.input-box button {
  padding: 8px 15px;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 3px;
  cursor: pointer;
}
</style>
