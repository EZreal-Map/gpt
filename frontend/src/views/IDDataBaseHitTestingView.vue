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
      <div class="parameters" @click="showRetrievalSettingModel = true">
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
        <RetrievalList
          v-for="(result, index) in testResults"
          :key="index"
          :result="result"
          :editBox="editBox"
          :index="index"
        ></RetrievalList>
      </div>
    </div>

    <!-- 设置检索参数的弹出窗口 -->
    <RetrievalParameterModal
      v-model:showRetrievalSettingModel="showRetrievalSettingModel"
      :searchMode="searchMode"
      :citationLimit="citationLimit"
      :minRelevance="minRelevance"
      :questionOptimization="questionOptimization"
      :finishRetrievalParameterModalSelectionAndSubmit="
        finishRetrievalParameterModalSelectionAndSubmit
      "
    ></RetrievalParameterModal>

    <!-- 编辑文档的窗口 -->
    <EditChunkModal
      v-if="showEditModal"
      v-model:showEditModal="showEditModal"
      v-model:currentItem="currentItem"
      v-model:documentChunks="testResults"
    ></EditChunkModal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  postSimilaritySearchAxios,
  getTestHistoryAxios,
  postTestHistoryAxios,
  deleteHistoryQueryAxios
} from '@/api/dataset.js'
import { CircleClose } from '@element-plus/icons-vue'
import { useRoute } from 'vue-router'
import EditChunkModal from '@/components/EditChunkModal.vue'
import RetrievalList from '@/components/RetrievalList.vue'
import RetrievalParameterModal from '@/components/RetrievalParameterModal.vue'

const route = useRoute()
const databaseID = route.params.databaseID

const inputText = ref('')
const testHistory = ref([])
const testResults = ref([])

// 检索参数弹出框有关参数
const showRetrievalSettingModel = ref(false)
const searchMode = ref('语义检索')
const citationLimit = ref(4)
const minRelevance = ref(50)
const formattedMinRelevance = computed(() => {
  return (minRelevance.value / 100).toFixed(2)
})
const questionOptimization = ref('×')
const finishRetrievalParameterModalSelectionAndSubmit = (
  loaclSearchMode,
  loaclCitationLimit,
  loaclMinRelevance,
  localQuestionOptimization
) => {
  showRetrievalSettingModel.value = false
  // 更新前端数据
  searchMode.value = loaclSearchMode
  citationLimit.value = loaclCitationLimit
  minRelevance.value = loaclMinRelevance
  questionOptimization.value = localQuestionOptimization
  // 更新后端数据库数据
}

// 滚动条位置设置  dom ref
const testResultDom = ref(null)

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

// 静止滚动函数 (解决v-loading时滚动条问题, 先上移动到顶部, 然后禁止滚动)
function disableScroll() {
  testResultDom.value.scrollTop = 0
}

const getHistoryQueryResult = async ({ query, k, min_relevance }) => {
  // 开始加载动画
  vloadingBoolean.value = true
  if (testResultDom.value) {
    // 检查是否有垂直滚动条
    console.log('没有滚动条')
    const hasVerticalScrollbar =
      testResultDom.value.scrollHeight > testResultDom.value.clientHeight

    if (hasVerticalScrollbar) {
      console.log('有滚动条')
      console.log(testResultDom.value.scrollTop)
      // 移动滚动条到最上面
      testResultDom.value.scrollTop = 0

      // 禁止滚动
      testResultDom.value.addEventListener('scroll', disableScroll)
    }
  }
  const response = await postSimilaritySearchAxios({
    dataset_ids: [databaseID],
    query,
    k,
    min_relevance
  })
  testResults.value = response.data
  console.log(testResults.value)

  // 停止加载动画
  vloadingBoolean.value = false
  // 当不再需要禁止滚动时，记得移除事件监听器
  testResultDom.value?.removeEventListener('scroll', disableScroll)
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

// 删除一个历史查询
const deleteHistoryQuery = async (id) => {
  await deleteHistoryQueryAxios(id)
  fetchTestHistory()
}

// 编辑文档的窗口
const showEditModal = ref(false)
const currentItem = ref(null)

const editBox = (item) => {
  console.log(`编辑文档:`, item)
  currentItem.value = item
  showEditModal.value = true
}

// 滚动条位置设置
// 计算表格容器的最大高度
// const testResultDom = ref(null) 放在上面了
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
  display: flex;
  flex-direction: column;
  height: cal(100% - 20px);
}

.test-results {
  flex: 1; /* 占据父元素的剩余空间 */
  overflow: auto; /* 如果内容超过高度，可添加滚动条 */
}
</style>
