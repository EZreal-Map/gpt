<template>
  <div class="table-container" ref="tableContainer">
    <table class="table">
      <thead>
        <tr>
          <th class="column-number">#</th>
          <th class="column-filename">文件名</th>
          <th class="column-charcount">字符数</th>
          <th class="column-recallcount">分段数</th>
          <th class="column-recallcount">召回次数</th>
          <th class="column-uploadtime">上传时间</th>
          <th class="column-status">状态</th>
          <th class="column-action">操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(document, index) in documentData" :key="document.id">
          <td>{{ index + 1 }}</td>
          <td @click="editFile(document.id)" class="tdEditPointer">
            {{ document.name }}
          </td>
          <td @click="editFile(document.id)" class="tdEditPointer">
            {{ document.character_count }}
          </td>
          <td @click="editFile(document.id)" class="tdEditPointer">
            {{ document.chunk_sum_num }}
          </td>
          <td @click="editFile(document.id)" class="tdEditPointer">
            {{ document.recall_count }}
          </td>
          <td @click="editFile(document.id)" class="tdEditPointer">
            {{ document.created_at }}
          </td>
          <td>
            <el-icon><SuccessFilled color="green" /></el-icon>
          </td>
          <td>
            <button @click="downloadFile(document.id)" class="download-button">
              下载
            </button>
            <button @click="editFile(document.id)" class="edit-button">
              编辑
            </button>
            <button @click="deleteFile(document.id)" class="delete-button">
              删除
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { SuccessFilled } from '@element-plus/icons-vue'
import {
  getDocumentsAxios,
  getDownloadDocumentAxios,
  deleteDocumentAxios
} from '@/api/dataset.js'

// 从路由对象中提取 databaseID 参数
const route = useRoute()
const databaseID = route.params.databaseID

// 模拟表格数据
const documentData = ref([])

// 获取对应数据库databaseID的document数据集
const fetchDataSet = async () => {
  try {
    const response = await getDocumentsAxios(databaseID)
    documentData.value = response.data
  } catch (error) {
    console.error('请求失败:', error)
  }
}
fetchDataSet()

// 计算表格容器的最大高度
const tableContainer = ref(null)
onMounted(() => {
  calculateMaxHeight()
  // 监听窗口大小变化，动态更新最大高度
  window.addEventListener('resize', calculateMaxHeight)
})

const calculateMaxHeight = () => {
  const windowHeight = window.innerHeight
  const tableContainerOffsetTop = tableContainer.value.offsetTop
  const tableContainerMaxHeight = windowHeight - tableContainerOffsetTop - 20 // 20为额外留白，可根据实际情况调整
  tableContainer.value.style.maxHeight = `${tableContainerMaxHeight}px`
}

// 下载文件操作
const downloadFile = (doucmentID) => {
  try {
    getDownloadDocumentAxios(doucmentID)
  } catch (error) {
    console.error('下载文件时出错：', error)
  }
}

// 路由跳转相关 跳转到文档详情页
const router = useRouter()
// 编辑文件操作
const editFile = (documentID) => {
  console.log('编辑文件：', documentID)
  router.push({ name: 'id-database-document-chunk', params: { documentID } })
}

// 删除文件操作
const deleteFile = async (documentID) => {
  try {
    const response = await deleteDocumentAxios(documentID)
    console.log('删除文件成功：', response)

    // 删除成功后重新获取数据
    fetchDataSet()
  } catch (error) {
    console.error('请求失败:', error)
  }
}
</script>

<style scoped>
.table-container {
  overflow: auto; /* 当内容溢出时显示滚动条 */
}

.table {
  width: 100%;
  border-collapse: separate;
}

thead {
  position: sticky;
  top: 0px;
  z-index: 1;
}

.table th,
.table td {
  padding: 5px; /* 调整表格元素内边距 */
  border: 1px solid #ddd;
  text-align: center;
}

.table th {
  background-color: #f2f2f2;
  padding: 16px;
}

/* 中间部分列可以点击触发编辑 */
.tdEditPointer {
  cursor: pointer;
}
/* 调整列宽 */
.column-number {
  width: 2%;
}

.column-filename {
  width: 40%;
}

.column-charcount {
  width: 5%;
}

.column-recallcount {
  width: 5%;
}

.column-uploadtime {
  width: 10%;
}

.column-status {
  width: 4%;
}

.column-action {
  width: 20%;
}

/* 按钮样式 */
.download-button,
.edit-button,
.delete-button {
  padding: 8px 12px;
  font-size: 14px;
  background-color: #007bff;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  margin: 0 8px;
}

.download-button:hover,
.edit-button:hover,
.delete-button:hover {
  background-color: #0056b3;
}
</style>
