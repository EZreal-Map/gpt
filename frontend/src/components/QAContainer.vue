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
          <span class="citation-document" @click="isShowDocumentModal = true"
            >{{ documentCount }}条引用</span
          >
          <span class="citation-context">{{ contextCount }}条上下文</span>
          <span class="citation-execute-time">{{ executeTime }}s</span>
          <span class="citation-more">查看详情</span>
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
      <!-- 此处替换为具体的文档引用内容 -->
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
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { MdPreview } from 'md-editor-v3'
import 'md-editor-v3/lib/preview.css'

// defineProps 接收父组件传递的数据
const props = defineProps({
  question: String,
  answer: String,
  citeDocument: Array,
  isConnecting: Boolean
})

// 用于向父组件发出事件
const emits = defineEmits(['update:citeDocument'])

// 创建一个本地的 <引用列表> 中间媒介，实现爷孙组件通信
const documentChunks = ref([])

// 监视 documentChunks 的变化
watch(
  documentChunks,
  (newChunks) => {
    console.log('更新 citeDocument:', newChunks)
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

// 计算连接时间
const startTime = ref(0)
const executeTime = ref('0.00')
// 是否有第一个文字加载完成
const isloading = ref(true)

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
        executeTime.value = (elapsedTime / 1000).toFixed(2)
        startTime.value = 0
        console.log('结束计时', executeTime.value)
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

// 计算上下文数量
const contextCount = 8
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
  margin: 0px 0px 10px 40px;
}

.citation-buttons span {
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

.citation-buttons span:hover {
  background-color: #4e8cff; /* 浅蓝色 */
  border-color: #4e8cff; /* 浅蓝色边框 */
  color: #fff; /* 白色文字 */
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
</style>
