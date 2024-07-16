<template>
  <div class="main-container" ref="tableContainer">
    <div
      v-for="item in documentChunks"
      :key="item.id"
      class="box"
      @click="editBox(item)"
    >
      <div class="box-title">
        <span
          >编号: {{ item.metadata.chunk_count }} /
          {{ item.metadata.chunk_sum_num }}</span
        >
        <span>ID: {{ item.metadata.document_metadata_id }}</span>
      </div>
      <div class="box-content">
        <span>{{ item.page_content }}</span>
      </div>
      <div class="box-hover">
        <span>字数: {{ item.metadata.chunk_word_count }}</span>
        <button>编辑</button>
      </div>
    </div>

    <EditChunkModal
      v-if="showEditModal"
      v-model:showEditModal="showEditModal"
      v-model:currentItem="currentItem"
      v-model:documentChunks="documentChunks"
    ></EditChunkModal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
// import { ElMessage, ElMessageBox } from 'element-plus'
import { getDocumentChunksAxios } from '@/api/dataset.js'
import EditChunkModal from '@/components/EditChunkModal.vue'

// 从路由对象中提取 documentID 参数
const route = useRoute()
// const databaseID = route.params.databaseID
const documentID = route.params.documentID

// chunks 数据集 -> Dict (id, page_content, metadata) 数据集
const documentChunks = ref([])

// 获取对应数据库documentID的chunk数据集
async function fetchDocumentChunks() {
  try {
    const response = await getDocumentChunksAxios(documentID)
    documentChunks.value = response.data
    console.log('请求成功:', response.data)
  } catch (error) {
    console.error('请求失败:', error)
  }
}
fetchDocumentChunks()

const showEditModal = ref(false)
// const editContent = ref('')
const currentItem = ref(null)

const editBox = (item) => {
  currentItem.value = item
  // editContent.value = item.documents
  showEditModal.value = true
}

// 滚动条位置设置
const tableContainer = ref(null)

onMounted(() => {
  calculateMaxHeight()
  window.addEventListener('resize', calculateMaxHeight)
})

const calculateMaxHeight = () => {
  if (tableContainer.value?.offsetTop) {
    const windowHeight = window.innerHeight
    const tableContainerOffsetTop = tableContainer.value.offsetTop
    const tableContainerMaxHeight = windowHeight - tableContainerOffsetTop - 50 // 50为额外留白，可根据实际情况调整
    tableContainer.value.style.maxHeight = `${tableContainerMaxHeight}px`
  }
}
</script>

<style scoped>
/* 主容器样式 */
.main-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  grid-gap: 20px;
  overflow: auto; /* 当内容溢出时显示滚动条 */
}

/* 盒子样式 */
.box {
  border: 1px solid #ccc;
  padding: 15px;
  border-radius: 8px;
  position: relative;
  background-color: #f9f9f9;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  height: 200px;
  overflow: hidden; /* 防止悬停内容溢出 */
  text-align: left;
  color: #787878;
  cursor: pointer;
}

.box:hover {
  border-color: #007bff;
  background-color: #fff;
  color: #000;
}

.box-title {
  display: flex;
  justify-content: space-between;
  align-items: flex-start; /* 向上对齐 */
  margin-bottom: 10px;
  font-size: 12px;
}

.box-title {
  font-size: 12px;
}

.box-content {
  flex-grow: 1;
  margin-bottom: 10px;
  overflow: hidden;
}

.box-content span {
  margin: 0;
  padding: 0;
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  height: 90%;
  line-height: 1.5;
}

.box:hover .box-hover {
  display: flex;
  justify-content: space-between;
  position: absolute;
  bottom: 10px; /* 固定在底部 */
  left: 15px;
  right: 10px;
  border-radius: 4px;
}

.box-hover {
  display: none;
}

.box-hover span {
  margin: 0;
}

.box-hover button {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 5px 10px;
  cursor: pointer;
  border-radius: 4px;
}

.box-hover button:hover {
  background-color: #0056b3;
}
</style>
