<template>
  <div class="main-container" ref="tableContainer">
    <div
      v-for="item in documentChunks"
      :key="item.ids"
      class="box"
      @click="editBox(item)"
    >
      <div class="box-title">
        <span>编号: {{ item.metadatas.chunk_count }}</span>
        <span>ID: {{ item.ids.substring(0, 18) }}</span>
      </div>
      <div class="box-content">
        <span>{{ item.documents }}</span>
      </div>
      <div class="box-hover">
        <span>字数: {{ item.metadatas.chunk_word_count }}</span>
        <button>编辑</button>
      </div>
    </div>

    <!-- 编辑弹窗 -->
    <div v-if="showEditModal" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <span class="modal-title">编辑文档</span>
          <span class="close" @click="closeEditModal">&times;</span>
        </div>
        <div class="modal-info">
          <div class="info-item">
            <span>编号: </span
            ><span>{{ currentItem?.metadatas.chunk_count }}</span>
          </div>
          <div class="info-item">
            <span>ID: </span><span>{{ currentItem?.ids }}</span>
          </div>
        </div>
        <el-input
          v-model="editContent"
          class="modal-input"
          :autosize="{ minRows: 4, maxRows: 20 }"
          type="textarea"
          placeholder="请输入内容"
        />
        <div class="button-group">
          <button class="delete-button" @click="deleteEdit">删除</button>
          <button class="save-button" @click="saveEdit">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getDocumentChunksAxios } from '@/api/dataset.js'

// 从路由对象中提取 documentID 参数
const route = useRoute()
const databaseID = route.params.databaseID
const documentID = route.params.documentID

// 模拟表格数据
const documentChunks = ref([])

// 获取对应数据库documentID的chunk数据集
async function fetchDocumentChunks() {
  try {
    const response = await getDocumentChunksAxios(documentID)
    documentChunks.value = response.data
  } catch (error) {
    console.error('请求失败:', error)
  }
}
fetchDocumentChunks()

const showEditModal = ref(false)
const editContent = ref('')
const currentItem = ref(null)

const editBox = (item) => {
  currentItem.value = item
  editContent.value = item.documents
  showEditModal.value = true
}

const closeEditModal = () => {
  showEditModal.value = false
}

const saveEdit = async () => {
  if (currentItem.value) {
    const chunkId = currentItem.value.ids // 替换为你的 chunk ID
    try {
      currentItem.value.documents = editContent
      closeEditModal()
      const response = await axios.put(
        `http://127.0.0.1:7979/dataset/${databaseID}/edit-chunk`,
        {
          page_content: editContent.value
        },
        {
          params: {
            chunk_id: chunkId
          }
        }
      )
      if (response.status === 200) {
        ElMessage.success('保存成功')
      } else {
        ElMessage.error('保存失败')
      }
    } catch (error) {
      console.error('Error updating chunk:', error)
      ElMessage.error('保存失败')
    }
  }
}

const deleteChunkFunction = async (databaseID, documentID, chunkID) => {
  try {
    // 构造 DELETE 请求的 URL
    const url = `http://127.0.0.1:7979/dataset/${databaseID}/delete-chunk`
    // 设置查询参数
    const params = {
      article_id: documentID,
      chunk_id: chunkID
    }
    // 发送 DELETE 请求，并传递查询参数
    const response = await axios.delete(url, { params })
    // 处理成功响应
    console.log('删除成功:', response.data)
  } catch (error) {
    // 处理错误响应
    console.error('删除失败:', error)
    throw error
  }
}

const deleteEdit = () => {
  ElMessageBox.confirm('确认要删除文档吗？', {
    confirmButtonText: '确定',
    cancelButtonText: '取消'
  }).then(() => {
    if (currentItem.value) {
      // 数据库删除数据
      deleteChunkFunction(databaseID, documentID, currentItem.value.ids)

      // 前端删除视图数据
      documentChunks.value = documentChunks.value.filter(
        (item) => item.ids !== currentItem.value.ids
      )
    }
    closeEditModal()
    ElMessage.success('删除成功')
  })
}

// 滚动条位置设置
const tableContainer = ref(null)

onMounted(() => {
  calculateMaxHeight()
  window.addEventListener('resize', calculateMaxHeight)
})

const calculateMaxHeight = () => {
  const windowHeight = window.innerHeight
  const tableContainerOffsetTop = tableContainer.value.offsetTop
  const tableContainerMaxHeight = windowHeight - tableContainerOffsetTop - 50 // 50为额外留白，可根据实际情况调整
  tableContainer.value.style.maxHeight = `${tableContainerMaxHeight}px`
}
</script>

<style scoped>
/* 主容器样式 */
.main-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
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

/* 弹窗样式 */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  width: 600px;
  position: relative;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e5e5e5;
  padding-bottom: 10px;
}

.modal-title {
  font-size: 18px;
  font-weight: bold;
}

.modal-info {
  display: flex;
  justify-content: space-between;
  margin: 20px 0;
}

.info-item {
  font-size: 14px;
}

.modal-input {
  width: 100%;
  margin-top: 10px;
}

.close {
  font-size: 24px;
  cursor: pointer;
}

.button-group {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.save-button {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 10px 20px;
  margin-top: 20px;
  cursor: pointer;
  border-radius: 4px;
  float: right;
}

.save-button:hover {
  background-color: #0056b3;
}

.delete-button {
  background-color: #dc3545;
  color: white;
  border: none;
  padding: 10px 20px;
  margin-top: 20px;
  cursor: pointer;
  border-radius: 4px;
}

.delete-button:hover {
  background-color: #c82333;
}
</style>
