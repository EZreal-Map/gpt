<template>
  <div class="table-container" ref="tableContainer">
    <table class="table">
      <thead>
        <tr>
          <th class="column-number">#</th>
          <th class="column-filename">文件名</th>
          <th class="column-charcount">字符数</th>
          <th class="column-recallcount">召回次数</th>
          <th class="column-uploadtime">上传时间</th>
          <th class="column-status">状态</th>
          <th class="column-action">操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(item, index) in tableData" :key="index">
          <td>{{ index + 1 }}</td>
          <td @click="editFile(item.documentID)" class="tdEditPointer">
            {{ item.fileName }}
          </td>
          <td @click="editFile(item.documentID)" class="tdEditPointer">
            {{ item.charCount }}
          </td>
          <td @click="editFile(item.documentID)" class="tdEditPointer">
            {{ item.recallCount }}
          </td>
          <td @click="editFile(item.documentID)" class="tdEditPointer">
            {{ item.uploadTime }}
          </td>
          <td>{{ item.status }}</td>
          <td>
            <button @click="downloadFile(index)" class="download-button">
              下载
            </button>
            <button @click="editFile(item.documentID)" class="edit-button">
              编辑
            </button>
            <button @click="deleteFile(index)" class="delete-button">
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
import { useRouter } from 'vue-router'

// 模拟表格数据
const tableData = ref([
  {
    documentID: 'fawefwefwar1',
    fileName: '125国内水路运输管理条例(2023修订).csv',
    charCount: '8.2k',
    recallCount: 0,
    uploadTime: '2024-05-13 06:48',
    status: '排队中'
  },
  {
    documentID: 'fawefwefwar2',
    fileName: '186中华人民共和国外国籍船舶航行长江水域管理规定.csv',
    charCount: '2.6k',
    recallCount: 0,
    uploadTime: '2024-05-13 06:48',
    status: '排队中'
  },
  {
    documentID: 'fawefwefwar3',
    fileName: '186中华人民共和国外国籍船舶航行长江水域管理规定.csv',
    charCount: '2.6k',
    recallCount: 0,
    uploadTime: '2024-05-13 06:48',
    status: '排队中'
  },
  {
    documentID: 'fawefwefwar4',
    fileName: '186中华人民共和国外国籍船舶航行长江水域管理规定.csv',
    charCount: '2.6k',
    recallCount: 0,
    uploadTime: '2024-05-13 06:48',
    status: '排队中'
  },
  {
    documentID: 'fawefwefwar5',
    fileName: '186中华人民共和国外国籍船舶航行长江水域管理规定.csv',
    charCount: '2.6k',
    recallCount: 0,
    uploadTime: '2024-05-13 06:48',
    status: '排队中'
  },
  {
    documentID: 'fawefwefwar6',
    fileName: '186中华人民共和国外国籍船舶航行长江水域管理规定.csv',
    charCount: '2.6k',
    recallCount: 0,
    uploadTime: '2024-05-13 06:48',
    status: '排队中'
  },
  {
    documentID: 'fawefwefwar7',
    fileName: '125国内水路运输管理条例(2023修订).csv',
    charCount: '8.2k',
    recallCount: 0,
    uploadTime: '2024-05-13 06:48',
    status: '排队中'
  },
  {
    documentID: 'fawefwefwar8',
    fileName: '125国内水路运输管理条例(2023修订).csv',
    charCount: '8.2k',
    recallCount: 0,
    uploadTime: '2024-05-13 06:48',
    status: '排队中'
  },
  {
    documentID: 'fawefwefwar9',
    fileName: '125国内水路运输管理条例(2023修订).csv',
    charCount: '8.2k',
    recallCount: 0,
    uploadTime: '2024-05-13 06:48',
    status: '排队中'
  },
  {
    documentID: 'fawefwefwar10',
    fileName: '125国内水路运输管理条例(2023修订).csv',
    charCount: '8.2k',
    recallCount: 0,
    uploadTime: '2024-05-13 06:48',
    status: '排队中'
  },
  {
    documentID: 'fawefwefwar11',
    fileName: '125国内水路运输管理条例(2023修订).csv',
    charCount: '8.2k',
    recallCount: 0,
    uploadTime: '2024-05-13 06:48',
    status: '排队中'
  },
  {
    documentID: 'fawefwefwar12',
    fileName: '125国内水路运输管理条例(2023修订).csv',
    charCount: '8.2k',
    recallCount: 0,
    uploadTime: '2024-05-13 06:48',
    status: '排队中'
  },
  {
    documentID: 'fawefwefwar13',
    fileName: '125国内水路运输管理条例(2023修订).csv',
    charCount: '8.2k',
    recallCount: 0,
    uploadTime: '2024-05-13 06:48',
    status: '排队中'
  },
  {
    documentID: 'fawefwefwar14',
    fileName: '125国内水路运输管理条例(2023修订).csv',
    charCount: '8.2k',
    recallCount: 0,
    uploadTime: '2024-05-13 06:48',
    status: '排队中'
  },
  {
    documentID: 'fawefwefwar15',
    fileName: '125国内水路运输管理条例(2023修订).csv',
    charCount: '8.2k',
    recallCount: 0,
    uploadTime: '2024-05-13 06:48',
    status: '排队中'
  },
  {
    documentID: 'fawefwefwar16',
    fileName: '125国内水路运输管理条例(2023修订).csv',
    charCount: '8.2k',
    recallCount: 0,
    uploadTime: '2024-05-13 06:48',
    status: '排队中'
  },
  {
    documentID: 'fawefwefwar17',
    fileName: '125国内水路运输管理条例(2023修订).csv',
    charCount: '8.2k',
    recallCount: 0,
    uploadTime: '2024-05-13 06:48',
    status: '排队中'
  },
  {
    documentID: 'fawefwefwar18',
    fileName: '125国内水路运输管理条例(2023修订).csv',
    charCount: '8.2k',
    recallCount: 0,
    uploadTime: '2024-05-13 06:48',
    status: '排队中'
  },
  {
    documentID: 'fawefwefwar19',
    fileName: '125国内水路运输管理条例(2023修订).csv',
    charCount: '8.2k',
    recallCount: 0,
    uploadTime: '2024-05-13 06:48',
    status: '排队中'
  },
  {
    documentID: 'fawefwefwar20',
    fileName: '125国内水路运输管理条例(2023修订).csv',
    charCount: '8.2k',
    recallCount: 0,
    uploadTime: '2024-05-13 06:48',
    status: '排队中'
  },
  {
    documentID: 'fawefwefwar21',
    fileName: '125国内水路运输管理条例(2023修订).csv',
    charCount: '8.2k',
    recallCount: 0,
    uploadTime: '2024-05-13 06:48',
    status: '排队中'
  },
  {
    documentID: 'fawefwefwar22',
    fileName: '125国内水路运输管理条例(2023修订).csv',
    charCount: '8.2k',
    recallCount: 0,
    uploadTime: '2024-05-13 06:48',
    status: '排队中'
  },
  {
    documentID: 'fawefwefwar23',
    fileName: '125国内水路运输管理条例(2023修订).csv',
    charCount: '8.2k',
    recallCount: 0,
    uploadTime: '2024-05-13 06:48',
    status: '排队中'
  },
  {
    documentID: 'fawefwefwar24',
    fileName: '125国内水路运输管理条例(2023修订).csv',
    charCount: '8.2k',
    recallCount: 0,
    uploadTime: '2024-05-13 06:48',
    status: '排队中'
  },
  {
    documentID: 'fawefwefwar25',
    fileName: '125国内水路运输管理条例(2023修订).csv',
    charCount: '8.2k',
    recallCount: 0,
    uploadTime: '2024-05-13 06:48',
    status: '排队中'
  }
])

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
const downloadFile = (index) => {
  // 在这里执行下载文件的逻辑，可以根据 index 获取对应的文件信息进行下载
  console.log('下载文件：', tableData.value[index])
}

// 路由跳转相关 跳转到文档详情页
const router = useRouter()
// 编辑文件操作
const editFile = (documentID) => {
  console.log('编辑文件：', documentID)
  router.push({ name: 'id-database-document-detail', params: { documentID } })
}

// 删除文件操作
const deleteFile = (index) => {
  console.log('删除文件：', tableData.value[index])
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
  width: 6%;
}

.column-uploadtime {
  width: 10%;
}

.column-status {
  width: 5%;
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
