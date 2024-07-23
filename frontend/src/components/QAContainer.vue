<template>
  <div class="qa-container">
    <div class="question">
      <span>{{ question }}</span>
    </div>
    <div
      class="loading-box"
      v-if="isloading && isConnecting"
      v-loading="isloading"
    ></div>
    <div class="answer" v-else>
      <MdPreview
        editorId="preview-only"
        :modelValue="answer"
        previewTheme="github"
      />
      <div class="citation" v-if="!isConnecting">
        <div class="citation-text">引用</div>
        <a
          href="#"
          class="citation-filename"
          v-for="filename in uniqueFilenames"
          :key="filename"
        >
          {{ filename }}
        </a>
        <div class="citation-buttons">
          <span class="citation-document" @click="showDocumentModalFunction"
            >{{ documentCount }}条引用</span
          >
          <span class="citation-context" @click="isShowChatHistoryModel = true"
            >{{ contextCount }}条上下文</span
          >
          <span class="citation-execute-time">{{ parentExecuteTime }}s</span>
          <span class="citation-more"
            ><el-dropdown>
              <span class="el-dropdown-link">
                <el-icon size="20"><MoreFilled /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="copyToClipboard(answer)"
                    ><el-icon><CopyDocument /></el-icon
                  ></el-dropdown-item>
                  <el-dropdown-item @click="deleteChatHistory"
                    ><el-icon><Delete /></el-icon
                  ></el-dropdown-item>
                  <el-dropdown-item @click="retryAnswer"
                    ><el-icon><Refresh /></el-icon
                  ></el-dropdown-item>
                </el-dropdown-menu>
              </template> </el-dropdown
          ></span>
        </div>
        <!-- <div>{{ citeDocument }}</div> -->
      </div>
    </div>
  </div>

  <!-- 引用有关的弹窗 -->
  <div class="document-modal-background" v-show="isShowDocumentModal">
    <!-- 弹窗内容待定 -->
    <div class="document-modal">
      <div class="document-modal-header">
        <span class="document-modal-title">引用文档详情</span>
        <span class="document-model-close" @click="isShowDocumentModal = false"
          >&times;</span
        >
      </div>
      <!-- 具体的文档内容 -->
      <div class="document-modal-content">
        <el-scrollbar height="500px">
          <RetrievalList
            v-for="(result, index) in citeDocument"
            :key="index"
            :result="result"
            :editBox="editBox"
            :index="index"
          ></RetrievalList>
        </el-scrollbar>
      </div>
    </div>
  </div>

  <!-- 编辑文档的窗口 -->
  <EditChunkModal
    v-if="showEditModal"
    v-model:showEditModal="showEditModal"
    v-model:currentItem="currentItem"
    v-model:documentChunks="documentChunks"
  ></EditChunkModal>

  <!-- 历史上下文有关的弹窗 -->
  <div class="document-modal-background" v-show="isShowChatHistoryModel">
    <!-- 弹窗内容待定 -->
    <div class="document-modal">
      <div class="document-modal-header">
        <span class="document-modal-title">历史上下文详情</span>
        <span
          class="document-model-close"
          @click="isShowChatHistoryModel = false"
          >&times;</span
        >
      </div>
      <!-- 具体的文档内容 -->
      <div class="document-modal-content">
        <el-scrollbar height="500px">
          <div v-for="(chat, index) in contextHistory" :key="index">
            <div class="question-chunk-modal">
              <div class="label">Human</div>
              <div class="content">{{ chat.question }}</div>
            </div>
            <div class="answer-chunk-modal">
              <div class="label">AI</div>
              <div class="content">{{ chat.answer }}</div>
            </div>
          </div>
        </el-scrollbar>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { MdPreview } from 'md-editor-v3'
import 'md-editor-v3/lib/preview.css'
import RetrievalList from '@/components/RetrievalList.vue'
import { addChatHistoryAxios, deleteChatHistoryAxios } from '@/api/chatset.js'
import { useRoute, useRouter } from 'vue-router'
import {
  MoreFilled,
  CopyDocument,
  Delete,
  Refresh
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 跳转路由
const router = useRouter()
// 使用 useRoute 获取路由信息
const appID = useRoute().params.appID
const chatID = useRoute().query.chatID
// defineProps 接收父组件传递的数据
const props = defineProps({
  id: String,
  question: String,
  answer: String,
  citeDocument: Array,
  isConnecting: Boolean,
  contextHistory: Array,
  parentExecuteTime: {
    type: Number,
    default: 0
  },
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
  },
  messages: Object,
  sendMessage: Function
})

// 用于向父组件发出事件
const emits = defineEmits([
  'update:citeDocument',
  'update:messages',
  'update:id',
  'update:parentExecuteTime'
])

// 创建一个本地的 <引用列表> 中间媒介，实现爷孙组件通信
const documentChunks = ref([])

// 监视 documentChunks 的变化
watch(
  documentChunks,
  (newChunks) => {
    console.log('更新 citeDocument:', newChunks)
    console.log('citeDocument:', props.citeDocument)
    emits('update:citeDocument', newChunks)
  },
  { deep: true }
)

// 使用 computed 属性提取并确保唯一的 filename 列表
const uniqueFilenames = computed(() => {
  // 提取 filename 字段
  const filenames = props.citeDocument.map((doc) => doc.metadata.filename)
  // 使用 Set 去重
  return Array.from(new Set(filenames))
})

// 使用 computed 属性计算 引用的document数量
const documentCount = computed(() => props.citeDocument.length)
// 使用 computed 属性计算 上下文数量
const contextCount = computed(() => props.contextHistory.length)

// 计算连接时间
const startTime = ref(0)

// 是否有第一个文字加载完成
const isloading = ref(true)

const addChatHistory = async (execute_time) => {
  console.log('处理时间props.parentExecuteTime', props.parentExecuteTime)
  const response = await addChatHistoryAxios({
    appset_id: appID,
    chat_id: chatID,
    question: props.question,
    answer: props.answer,
    cite_documents: props.citeDocument,
    context_histories: props.contextHistory,
    execute_time: execute_time,
    is_test_mode: props.isTestMode
  })
  console.log('已经添加一条历史记录')

  // 保存 messages 里面的 id，用于后面的删除操作
  emits('update:id', response.data.chat_history_id)

  if (response.data.chat_set_mode === 'new_chat_set') {
    console.log('进入new-chat-set')
    // 聊天列表添加新填的聊天记录，使用默认的名字 (new chat)
    await props.fetchChatSetsData() // 调用父亲的父亲的方法，刷新聊天列表

    // 传入第一个历史对话记录，为对话取一个名字
    // 调用父亲的父亲的方法，更新名字
    await props.updateNewChatSetName(
      response.data.chat_set_id,
      props.question,
      props.answer
    )

    // 路由跳转到新建的chatID去
    router.replace({
      name: 'chat',
      params: { appID: appID },
      query: { chatID: response.data.chat_set_id }
    })
  }
}

watch(
  () => props.isConnecting,
  (newValue) => {
    if (newValue) {
      console.log('开始计时')
      startTime.value = Date.now()
      isloading.value = true // 应对重新生成回答
    } else {
      if (startTime.value !== 0) {
        const elapsedTime = Date.now() - startTime.value
        const execute_time = parseFloat((elapsedTime / 1000).toFixed(2))
        emits('update:parentExecuteTime', execute_time)
        startTime.value = 0

        // 回答完毕，添加一条问答历史记录
        addChatHistory(execute_time)
      }
    }
  },
  { immediate: true }
)

watch(
  () => props.answer,
  (newValue) => {
    if (newValue) {
      // console.log('开始加载文字')
      isloading.value = false
    }
  }
)

// 引用有关弹窗 documentModal
const isShowDocumentModal = ref(false)
// const citeDocuments = ref('')
const showDocumentModalFunction = () => {
  isShowDocumentModal.value = true
  // citeDocuments
}

// 编辑文档的窗口
const showEditModal = ref(false)
const currentItem = ref(null)

const editBox = (item) => {
  // 复制 props.citeDocument 的值
  documentChunks.value = [...props.citeDocument]
  console.log(`编辑文档:`, item)
  currentItem.value = item
  showEditModal.value = true
}

// 历史上下文的弹窗 chatHistoryModal
const isShowChatHistoryModel = ref(false)

// 更多按钮
// 复制功能
const copyToClipboard = async (textToCopy) => {
  try {
    // navigator clipboard 需要https等安全上下文
    if (navigator.clipboard && window.isSecureContext) {
      // navigator clipboard 向剪贴板写文本
      navigator.clipboard.writeText(textToCopy)
    } else {
      // 保证在非https下，复制功能也可以正常使用（使用弃用的execCommand接口
      // 创建textarea
      let textArea = document.createElement('textarea')
      textArea.value = textToCopy
      // 使text area不在viewport，同时设置不可见
      textArea.style.position = 'absolute'
      textArea.style.opacity = 0
      textArea.style.left = '-999999px'
      textArea.style.top = '-999999px'
      document.body.appendChild(textArea)
      textArea.focus()
      textArea.select()
      new Promise((res, rej) => {
        // 执行复制命令并移除文本框
        document.execCommand('copy') ? res() : rej()
        textArea.remove()
      })
    }
    ElMessage.success('复制成功')
  } catch (err) {
    console.error('复制失败:', err)
  }
}

// 删除功能
const deleteChatHistory = async () => {
  ElMessageBox.confirm('确认删除这条历史记录吗？', {
    confirmButtonText: '确定',
    cancelButtonText: '取消'
  })
    .then(async () => {
      await deleteChatHistoryAxios({ chat_history_id: props.id })
      const newMessages = props.messages.filter(
        (message) => message.id !== props.id
      )
      emits('update:messages', newMessages)
      ElMessage.success('删除成功')
    })
    .catch(() => {
      ElMessage.info('已取消删除')
    })
}

// 重新回答功能
const retryAnswer = async () => {
  // 先删除这条对话
  await deleteChatHistoryAxios({ chat_history_id: props.id })
  const newMessages = props.messages.filter(
    (message) => message.id !== props.id
  )
  emits('update:messages', newMessages)
  // 再使用同样的问题重新回答
  props.sendMessage(props.question)
}
</script>

<style scoped>
.qa-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  margin: 10px 0;
}

.question {
  text-align: left;
  max-width: 70%;
  align-self: flex-end;
  border: 1px solid #ccc;
  background-color: #e1f5fe;
  padding: 10px;
  border-radius: 5px;
  margin-bottom: 20px;
  margin-right: 20px;
  white-space: pre-line; /* 保留换行符，显示多行文本*/
}

.answer {
  text-align: left;
  align-self: flex-start;
  max-width: 70%;
  border: 1px solid #ccc;
  background-color: #fdfdfd;
  padding: 4px;
  border-radius: 5px;
  margin-bottom: 20px;
  margin-left: 20px;
}

.loading-box {
  text-align: left;
  align-self: flex-start;
  margin-left: 20px;
  background-color: #fdfdfd;
  border-radius: 5px;
  margin-bottom: 20px;
}

.citation {
  border-radius: 5px;
}

.citation-text {
  display: flex;
  gap: 10px;
  font-size: 0.9em;
  color: #666;
  position: relative;
}

.citation-text::after {
  content: '';
  flex: 1;
  border-bottom: 2px solid #ddd;
  margin: auto 0;
}

.citation-filename {
  display: block;
  font-size: 12px;
  color: #111824;
  text-decoration: none;
  margin-bottom: 8px;
  margin-left: 40px;
}

.citation-buttons {
  display: flex;
  margin: 0px 0px 10px 40px;
}

.citation-buttons .citation-document,
.citation-buttons .citation-context,
.citation-buttons .citation-execute-time {
  padding: 5px 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  background-color: #f6f8fa;
  font-size: 10px;
  color: #666;
  text-decoration: none;
  cursor: pointer;
  margin-right: 10px;
  transition:
    background-color 0.1s ease,
    border-color 0.1s ease,
    color 0.1s ease; /* 添加过渡效果 */
}

.citation-buttons .citation-document:hover,
.citation-buttons .citation-context:hover,
.citation-buttons .citation-execute-time:hover {
  background-color: #4e8cff; /* 浅蓝色 */
  border-color: #4e8cff; /* 浅蓝色边框 */
  color: #fff; /* 白色文字 */
}

.citation-more {
  display: flex;
  justify-content: center; /* 将Flex容器内的项目水平居中。 */
  align-items: center; /* 将Flex容器内的项目垂直居中。 */
}

.el-dropdown-link:focus-visible {
  outline: unset; /* 去除默认的轮廓线 */
}

/* 全屏模态弹窗 */
.document-modal-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5); /* 半透明黑色背景 */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1;
}

.document-modal {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  width: 100%;
  position: relative;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  width: 600px; /* 调整弹窗宽度 */
  max-width: 90%; /* 限制最大宽度 */
  max-height: 90%; /* 限制最大高度 */
}

.document-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e5e5e5;
  padding-bottom: 10px;
}

.document-modal-title {
  font-size: 18px;
  font-weight: bold;
}

.document-modal-content {
  width: 100%;
  margin-top: 10px;
  text-align: left;
}

.document-model-close {
  font-size: 24px;
  cursor: pointer;
}

.document-modal-content {
  padding: 10px;
  background-color: #fff;
  font-family: Arial, sans-serif;
}

.question-chunk-modal,
.answer-chunk-modal {
  margin-bottom: 10px;
  margin-right: 20px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
}

.document-modal-content .label {
  font-weight: bold;
  margin-bottom: 5px;
}

.document-modal-content .content {
  font-size: 14px;
  line-height: 1.5;
}
</style>
