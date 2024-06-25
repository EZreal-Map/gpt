<template>
  <div class="container">
    <div class="left-panel">
      <div class="text-input">
        <h3>文本输入</h3>
        <el-input
          v-model="inputText"
          type="textarea"
          :autosize="{ minRows: 6, maxRows: 10 }"
          placeholder="请输入要测试文本"
          class="textarea-with-button"
        >
        </el-input>
        <button @click="createNewHistoryQuery" class="test-button">测试</button>
      </div>
      <h3>测试历史</h3>
      <div class="test-history" ref="testHistoryDom">
        <div
          v-for="history in testHistory"
          :key="history.id"
          class="history-item"
        >
          <div
            class="history-content"
            @click="
              getHistoryQueryResult({
                query: history.query,
                k: history.k,
                min_relevance: history.min_relevance
              })
            "
          >
            <span class="history-query">{{ history.query }}</span>
          </div>
          <div class="history-actions">
            <div class="history-info">
              <span class="history-time">{{ history.created_at }}</span>
              <span class="history-k-mr">引用个数：{{ history.k }}</span>
              <span class="history-k-mr"
                >最低相关度：{{ history.min_relevance }}</span
              >
            </div>
            <button class="delete-icon" @click="deleteHistoryQuery(history.id)">
              <el-icon><CircleClose /></el-icon>
            </button>
          </div>
        </div>
      </div>
    </div>
    <div class="right-panel">
      <h3>测试参数</h3>
      <div class="parameters" @click="showSettings = true">
        <div class="parameter-item">
          <span class="parameter-title">搜索模式:</span>
          <span class="parameter-value">{{ searchMode }}</span>
        </div>
        <div class="parameter-item">
          <span class="parameter-title">引用个数:</span>
          <span class="parameter-value">{{ citationLimit }}</span>
        </div>
        <div class="parameter-item">
          <span class="parameter-title">最低相关度:</span>
          <span class="parameter-value">{{ formattedMinRelevance }}</span>
        </div>
        <div class="parameter-item">
          <span class="parameter-title">问题优化:</span>
          <span class="parameter-value">{{ questionOptimization }}</span>
        </div>
      </div>
      <h3>测试结果</h3>
      <div
        class="test-results"
        ref="testResultDom"
        v-loading="vloadingBoolean"
        element-loading-background="rgba(248, 248, 248, 0.8)"
      >
        <div
          v-for="(result, index) in testResults"
          :key="index"
          class="test-result-container"
        >
          <div class="test-result-header">
            <el-tooltip
              content="通过计算向量之间的距离获取得分，范围为 0~1"
              placement="top"
              effect="light"
            >
              #{{ index + 1 }} | 语义检索 {{ result.score.toFixed(4) }}
            </el-tooltip>
          </div>
          <div class="test-result-body">
            {{ result.document.page_content }}
          </div>
          <div class="test-result-footer">
            <div class="test-result-footer-left">
              <el-tooltip
                content="点击下载源文件"
                placement="bottom"
                effect="light"
              >
                <span>{{ result.document.metadata.filename }}</span>
              </el-tooltip>
              <el-tooltip
                content="文件内文段编号/总文段数"
                placement="bottom"
                effect="light"
              >
                <span
                  >{{ result.document.metadata.chunk_count }}/{{
                    result.document.metadata.chunk_sum_num
                  }}</span
                >
              </el-tooltip>
              <el-tooltip
                content="引用内容长度"
                placement="bottom"
                effect="light"
              >
                <span>{{ result.document.metadata.chunk_word_count }}</span>
              </el-tooltip>
            </div>
            <span class="edit-icon" @click="editBox(result.document)"
              >编辑</span
            >
          </div>
        </div>
      </div>
    </div>

    <!-- 设置参数的弹出窗口 -->
    <el-dialog title="设置参数" v-model="showSettings" width="600px">
      <div class="dialog-content">
        <el-row :gutter="10" align="middle">
          <el-col :span="4">
            <label for="searchMode" class="center-label">搜索模式:</label>
          </el-col>
          <el-col :span="20">
            <el-select v-model="searchMode" placeholder="请选择">
              <el-option label="语义检索" value="语义检索"></el-option>
              <el-option label="关键词检索" value="关键词检索"></el-option>
            </el-select>
          </el-col>
        </el-row>
        <el-row :gutter="10" class="mt-10" align="middle">
          <el-col :span="4">
            <label for="citationLimit" class="center-label">引用个数:</label>
          </el-col>
          <el-col :span="20">
            <el-slider v-model="citationLimit" :min="1" :max="20"></el-slider>
          </el-col>
        </el-row>
        <el-row :gutter="10" class="mt-10" align="middle">
          <el-col :span="4">
            <label for="minRelevance" class="center-label">最低相关度:</label>
          </el-col>
          <el-col :span="20">
            <el-slider
              v-model="minRelevance"
              :min="0"
              :max="100"
              :format-tooltip="formatTooltip"
            ></el-slider>
          </el-col>
        </el-row>
        <el-row :gutter="10" class="mt-10" align="middle">
          <el-col :span="4">
            <label for="questionOptimization" class="center-label"
              >问题优化:</label
            >
          </el-col>
          <el-col :span="20">
            <el-select
              v-model="questionOptimization"
              placeholder="请选择"
              style="width: 100%"
            >
              <el-option label="是" value="✓"></el-option>
              <el-option label="否" value="×"></el-option>
            </el-select>
          </el-col>
        </el-row>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showSettings = false">取消</el-button>
          <el-button type="primary" @click="applySettings">应用</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 编辑文档的弹出窗口 -->
    <div v-if="showEditModal" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <span class="modal-title">编辑文档 </span>
          <span class="close" @click="showEditModal = false">&times;</span>
        </div>
        <div class="modal-title-filename">
          {{ currentItem?.metadata.filename }}
        </div>
        <div class="modal-info">
          <div class="info-item">
            <span>编号: </span
            ><span
              >{{ currentItem?.metadata.chunk_count }} /
              {{ currentItem?.metadata.chunk_sum_num }}</span
            >
          </div>
          <div class="info-item">
            <span>ID: </span
            ><span>{{ currentItem?.metadata.document_metadata_id }}</span>
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
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getHitTestingAxios,
  putEditChunkByMetadataIDAxios,
  deleteChunkByMetadataIDAxios,
  getTestHistoryAxios,
  deleteHistoryQueryAxios,
  postTestHistoryAxios
} from '@/api/dataset.js'
import { CircleClose } from '@element-plus/icons-vue'
import { useRoute } from 'vue-router'
const route = useRoute()
const databaseID = route.params.databaseID

const inputText = ref('')
const testHistory = ref([])
const testResults = ref([])
const searchMode = ref('语义检索')
const citationLimit = ref(4)
const minRelevance = ref(50)
const formatTooltip = (value) => {
  return (value / 100).toFixed(2)
}

// 控制加载显示 boolean
const vloadingBoolean = ref(false)

const fetchTestHistory = async () => {
  try {
    const response = await getTestHistoryAxios(databaseID)
    testHistory.value = response.data
  } catch (error) {
    console.error('请求失败:', error)
  }
}
fetchTestHistory()

const formattedMinRelevance = computed(() => {
  return (minRelevance.value / 100).toFixed(2)
})
const questionOptimization = ref('×')
const showSettings = ref(false)

const getHistoryQueryResult = async ({ query, k, min_relevance }) => {
  // 开始加载动画
  vloadingBoolean.value = true

  const response = await getHitTestingAxios(databaseID, {
    query,
    k,
    min_relevance
  })
  testResults.value = response.data
  console.log(response)

  // 停止加载动画
  vloadingBoolean.value = false
}

// 创建新的历史查询
const createNewHistoryQuery = async () => {
  if (!inputText.value) {
    ElMessage.warning('请输入要测试的文本')
    return
  }

  // 发送请求 - 提交一个新的查询
  await postTestHistoryAxios({
    dataset_id: databaseID,
    query: inputText.value,
    k: citationLimit.value,
    min_relevance: formattedMinRelevance.value
  })

  // 获取历史查询 - 并且更新历史查询列表 testHistory
  fetchTestHistory()

  // 获取测试结果列表 - 并且更新 testResults
  await getHistoryQueryResult({
    query: inputText.value,
    k: citationLimit.value,
    min_relevance: formattedMinRelevance.value
  })
}

const applySettings = () => {
  showSettings.value = false
  ElMessage.success('参数设置已应用')
}

// 编辑文档的窗口
const showEditModal = ref(false)
const editContent = ref('')
const currentItem = ref(null)

const editBox = (item) => {
  console.log(item)
  currentItem.value = item
  editContent.value = item.page_content
  showEditModal.value = true
}

const saveEdit = async () => {
  if (currentItem.value) {
    const metadata_id = currentItem.value.metadata.document_metadata_id // 替换为你的 metadata_id
    console.log(metadata_id)
    try {
      currentItem.value.page_content = editContent
      showEditModal.value = false
      const response = await putEditChunkByMetadataIDAxios(databaseID, {
        page_content: editContent.value,
        metadata_id: metadata_id
      })
      console.log(response)
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

const deleteEdit = () => {
  ElMessageBox.confirm('确认删除分段吗？', {
    confirmButtonText: '确定',
    cancelButtonText: '取消'
  })
    .then(async () => {
      if (currentItem.value) {
        const metadata_id = currentItem.value.metadata.document_metadata_id // 替换为你的 metadata_id
        const article_id = currentItem.value.metadata.article_id // 替换为你的 article_id
        // 数据库删除数据
        await deleteChunkByMetadataIDAxios(databaseID, {
          article_id,
          metadata_id
        })

        // 前端删除视图数据
        testResults.value = testResults.value.filter(
          (item) => item.document.metadata.document_metadata_id !== metadata_id
        )
      }
      showEditModal.value = false
      ElMessage.success('删除成功')
    })
    .catch(() => {
      ElMessage.info('已取消删除')
    })
}

// 测试历史 有关操作
const deleteHistoryQuery = async (id) => {
  try {
    const response = await deleteHistoryQueryAxios(id)
    console.log('删除历史查询成功：', response)
    fetchTestHistory()
  } catch (error) {
    console.error('请求失败:', error)
  }
}

// 滚动条位置设置
// 计算表格容器的最大高度
const testResultDom = ref(null)
const testHistoryDom = ref(null)
onMounted(() => {
  calculateMaxHeight()
  // 监听窗口大小变化，动态更新最大高度
  window.addEventListener('resize', calculateMaxHeight)
})

const calculateMaxHeight = () => {
  if (testResultDom.value?.offsetTop) {
    const windowHeight = window.innerHeight
    const testResultOffsetTop = testResultDom.value.offsetTop
    const testResultMaxHeight = windowHeight - testResultOffsetTop - 40 // 20为额外留白，可根据实际情况调整
    testResultDom.value.style.maxHeight = `${testResultMaxHeight}px`

    const testHistoryOffsetTop = testHistoryDom.value.offsetTop
    const testHistoryMaxHeight = windowHeight - testHistoryOffsetTop - 120
    console.log(testHistoryMaxHeight)
    testHistoryDom.value.style.maxHeight = `${testHistoryMaxHeight}px`
  }
}
</script>

<style scoped>
.container {
  display: flex;
  text-align: left;
  height: 100%;
}
.left-panel {
  width: 30%;
  padding: 10px;
  border: 1px solid #ccc;
}

.text-input {
  position: relative;
  margin-bottom: 20px;
}
.textarea-with-button {
  width: 100%;
}
.test-button {
  position: absolute;
  right: 10px;
  bottom: 10px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 5px 10px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}
.test-button:hover {
  background-color: #66b1ff;
}
.test-history {
  margin-top: 20px;
  overflow: auto;
}
.parameters {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  cursor: pointer;
}
.parameter-item {
  flex: 1 1 200px;
  display: flex;
  flex-direction: column;
  border: 1px solid #ccc;
  padding: 10px;
  border-radius: 4px;
}
.parameter-title {
  font-weight: bold;
  margin-bottom: 5px;
}
.parameter-value {
  color: #666;
}

.dialog-content {
  padding: 20px 20px 20px 40px;
}
.mt-10 {
  margin-top: 10px;
}
.dialog-footer {
  text-align: right;
}
.center-label {
  display: flex;
  align-items: center;
  height: 100%;
}

/* 测试结果容器样式 */
.test-result-container {
  background-color: #ffffff; /* 白色背景 */
  border: 1px solid #ddd; /* 细边框 */
  border-radius: 8px; /* 圆角边框 */
  padding: 15px; /* 内边距 */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* 浅阴影 */
  margin-bottom: 20px; /* 底部间距 */
}

/* 测试结果头部样式 */
.test-result-header {
  background-color: #f0f0f0; /* 淡灰色背景 */
  color: #333; /* 深灰色文字 */
  font-weight: bold;
  font-size: 16px;
  padding: 10px;
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
}

/* 测试结果主体样式 */
.test-result-body {
  font-size: 14px;
  line-height: 1.6;
  color: #666; /* 灰色文字 */
  margin-top: 10px;
}

/* 测试结果底部样式 */
.test-result-footer {
  position: relative; /* 相对定位，为绝对定位的参考点 */
  font-size: 12px;
  color: #999; /* 浅灰色文字 */
  padding-top: 10px;
  border-top: 1px solid #ddd; /* 顶部边框分隔线 */
  margin-top: 10px;
}

/* 测试结果底部内部元素样式 */
.test-result-footer span {
  margin-right: 10px; /* 右侧间距 */
}

.test-result-footer span:hover {
  color: #007bff; /* 蓝色文字 */
  cursor: pointer; /* 鼠标指针 */
}

/* 测试结果底部左侧文字部分，加一个margin-right防止与编辑 button 文字重叠 */
.test-result-footer-left {
  margin-right: 50px;
}

.edit-icon {
  display: none; /* 默认隐藏 */
}

.test-result-container:hover .edit-icon {
  display: inline-block; /* 悬停时显示 */
}

.edit-icon {
  position: absolute; /* 绝对定位 */
  top: 50%; /* 垂直居中 */
  right: 10px; /* 距离右侧的位置 */
  color: #999; /* 蓝色文字 */
  cursor: pointer; /* 鼠标指针 */
}

/* 编辑文档的弹出窗口样式 */
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

.modal-title-filename {
  font-size: 14px;
  text-align: center;
  color: #666;
}

.modal-info {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
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

.test-history {
  font-family: Arial, sans-serif;
}

.test-history h3 {
  font-size: 1.2em;
  margin-bottom: 10px;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 10px;
  border-bottom: 1px solid #eee;
  transition: background-color 0.3s; /* 添加背景色过渡效果 */
}

.history-item:hover {
  background-color: #f0f0f0; /* 鼠标悬停时的背景色 */
}

.history-content {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding-right: 10px; /* 添加右边距，以便与时间和删除按钮隔开 */
  transition: max-width 0.3s; /* 添加宽度过渡效果 */
  cursor: pointer; /* 鼠标指针 */
}

.history-item:hover .history-content {
  white-space: normal; /* 悬停时取消单行显示 */
  max-width: 250px; /* 根据实际需求设置最大宽度 */
}

.history-query {
  font-weight: bold;
}

.history-actions {
  display: flex;
  justify-content: space-between; /* 左右分布 */
  align-items: center; /* 垂直居中 */
}

.history-info {
  display: flex;
  flex-direction: column; /* 垂直布局 */
}

.history-time {
  margin-bottom: 5px; /* 间距 */
  color: #666;
}

.history-k-mr {
  margin-bottom: 5px; /* 间距 */
  font-size: 16px;
  color: #666;
  visibility: hidden; /* 初始隐藏 */
  height: 0; /* 高度为0 */
  overflow: hidden; /* 超出部分隐藏 */
  transition:
    visibility 0.3s,
    height 0.3s; /* 过渡效果 */
}

.history-item:hover .history-k-mr {
  visibility: visible; /* 鼠标悬停时显示 */
  height: auto; /* 自动撑开高度 */
}

.delete-icon {
  visibility: hidden; /* 初始隐藏 */
  border: none;
  cursor: pointer;
  color: #999;
  transition: color 0.3s; /* 添加颜色过渡效果 */
}

.history-item:hover .delete-icon {
  visibility: visible; /* 鼠标悬停时显示 */
}

.delete-icon:hover {
  color: #f00; /* 鼠标悬停时的颜色 */
}

.el-icon-close {
  font-size: 1.2em;
}

.right-panel {
  width: 70%;
  padding: 10px;
  border: 1px solid #ccc;
  border-left: none;
  display: flex;
  flex-direction: column;
  height: cal(100% - 20px);
}

.test-results {
  flex: 1; /* 占据父元素的剩余空间 */
  overflow: auto; /* 如果内容超过高度，可添加滚动条 */
}
</style>
