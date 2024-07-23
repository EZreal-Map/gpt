<template>
  <div class="APPIDConfiguration">
    <div class="left-block">
      <!-- 左侧内容 -->
      <div class="database-box">
        <DataBaseBox
          :key="appset.id"
          :appID="appset.id"
          v-model:name="appset.name"
          v-model:description="appset.description"
          v-model:privacy="appset.privacy"
          :fetchDataSet="fetchAppSet"
          :putDatasetAxios="putAppsetAxios"
          :deleteDatasetAxios="deleteAppsetAxios"
          :created_at="appset.created_at"
        ></DataBaseBox>
      </div>
      <div class="left-block-setting">
        <div class="left-block-setting-title">
          <p>应用配置</p>
          <el-button type="primary" @click="updateDataSet">保存</el-button>
        </div>

        <div class="left-block-setting-content">
          <div class="ai-setting">
            <div class="title">AI 配置</div>
            <button
              class="ai-setting-button"
              @click="isShowAISettingsModal = true"
            >
              {{ selectModelName }}
            </button>
            <!-- 设置模型参数弹窗 -->
            <div
              class="document-modal-background"
              v-show="isShowAISettingsModal"
            >
              <div class="document-modal">
                <!-- 弹窗 title -->
                <div class="document-modal-header">
                  <span class="document-modal-title">大语言模型配置</span>
                  <span
                    class="document-model-close"
                    @click="isShowAISettingsModal = false"
                    >&times;</span
                  >
                </div>
                <!-- 弹窗 content -->
                <div class="ai-setting-model-content">
                  <!-- 模型的选择 -->
                  <div>
                    <div class="left">AI 模型</div>
                    <div class="right">
                      <el-select v-model="selectModelName" placeholder="请选择">
                        <el-option
                          v-for="model in modelList"
                          :key="model.name"
                          :label="model.name"
                          :value="model.name"
                        ></el-option>
                      </el-select>
                    </div>
                  </div>
                  <!-- 模型的温度设置 -->
                  <div>
                    <div class="left">温度</div>
                    <div class="right">
                      <el-slider
                        v-model="selectModelTemperature"
                        :min="0"
                        :max="200"
                        :format-tooltip="formatTooltip"
                      />
                    </div>
                  </div>
                  <!-- 模型的上限回复（max_token)设置 -->
                  <div>
                    <div class="left">最大上限回复</div>
                    <div class="right">
                      <el-slider
                        v-model="selectModelMaxTokenResponse"
                        :min="1"
                        :max="4096"
                      />
                    </div>
                  </div>
                  <!-- 模型上下文记录聊天记录数量（history_window_length） -->
                  <div>
                    <div class="left">聊天记录数量</div>
                    <div class="right">
                      <el-slider
                        v-model="selectModelHistoryWindowLength"
                        :min="0"
                        :max="30"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="template-prompt">
            <div class="title">提示词</div>
            <el-input
              class="template-prompt-input"
              style="width: 240px"
              :autosize="{ minRows: 6, maxRows: 10 }"
              type="textarea"
              :placeholder="templatePromptInputPlaceHolder"
              v-model="templatePromptInput"
            />
          </div>
          <div class="connect-datasets">
            <div class="title">关联知识库</div>
            <div class="connect-datasets-button-set">
              <button @click="showSelectDataSetsModal">选择</button>
              <button @click="showRetrievalSettingModel = true">参数</button>
            </div>
          </div>
          <div class="grid-container-small">
            <div
              class="grid-item-small"
              v-for="(dataset, index) in selectDataSets"
              :key="index"
            >
              <el-tooltip
                class="box-item"
                effect="light"
                :content="dataset.name"
                placement="top"
              >
                <div class="name">{{ dataset.name }}</div>
              </el-tooltip>
            </div>
          </div>
        </div>

        <!-- 设置检索参数的弹出窗口 -->
        <RetrievalParameterModal
          v-model:showRetrievalSettingModel="showRetrievalSettingModel"
          v-model:searchMode="searchMode"
          v-model:citationLimit="citationLimit"
          :minRelevance="minRelevance"
          :questionOptimization="questionOptimization"
          :finishRetrievalParameterModalSelectionAndSubmit="
            finishRetrievalParameterModalSelectionAndSubmit
          "
        ></RetrievalParameterModal>

        <!-- 选择知识库弹窗 -->
        <div v-if="connectDataSetModalShow" class="modal">
          <div class="modal-content">
            <div class="modal-header">
              <span class="modal-title">选择知识库</span>
              <span class="close" @click="closeModal">&times;</span>
            </div>
            <div
              class="selected-datasets"
              v-show="tempSelectDataSets.length > 0"
            >
              已选的知识库
            </div>
            <div class="grid-container">
              <div
                class="grid-item"
                v-for="(dataset, index) in tempSelectDataSets"
                :key="index"
              >
                <span
                  class="close-icon"
                  @click="removeFromSelectedDatasets(dataset)"
                  >&times;</span
                >
                <el-tooltip
                  class="box-item"
                  effect="light"
                  :content="dataset.name"
                  placement="top"
                >
                  <div class="name">{{ dataset.name }}</div>
                </el-tooltip>

                <div class="created-at">
                  {{ dataset.created_at.split(' ')[0] }}
                </div>
              </div>
            </div>
            <div class="datasets">
              知识库集合
              <div class="grid-container">
                <div
                  class="grid-item cursor-pointer"
                  v-for="(dataset, index) in filteredDataSets"
                  :key="index"
                  @click="addToSelectedDatasets(dataset)"
                >
                  <el-tooltip
                    class="box-item"
                    effect="light"
                    :content="dataset.name"
                    placement="top"
                  >
                    <div class="name">{{ dataset.name }}</div>
                  </el-tooltip>
                  <div class="created-at">
                    {{ dataset.created_at.split(' ')[0] }}
                  </div>
                </div>
              </div>
            </div>
            <div class="button-group">
              <div></div>
              <button
                class="save-button"
                @click="finishDataSetSelectionAndSubmit"
              >
                完成
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="right-block">
      <!-- 右侧内容 -->
      <div class="right-block-title">
        <p>调试预览</p>
        <el-button type="primary" @click="cleanChatHistory">清除</el-button>
      </div>
      <div class="right-block-content" v-if="cleanRestart">
        <ChatComponent :isTestMode="true"></ChatComponent>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  getAppsetAxios,
  putAppsetAxios,
  deleteAppsetAxios,
  selectAppsetDatasetsAxios,
  getAppsetDatasetsAxios
} from '@/api/appset'
import { getDatasetsAxios } from '@/api/dataset.js'
import { cleanChatHistoryAxios } from '@/api/chatset.js'
import DataBaseBox from '@/components/DataBaseBox.vue'
import RetrievalParameterModal from '@/components/RetrievalParameterModal.vue'
import ChatComponent from '@/components/ChatComponent.vue'
import { ElMessage } from 'element-plus'

// 使用 useRoute 获取路由信息
const route = useRoute()
const appID = route.params.appID

const appset = ref('')

const fetchAppSet = async () => {
  const response = await getAppsetAxios(appID)
  console.log(response)
  appset.value = response.data
  selectModelName.value = appset.value.model_name
  selectModelMaxTokenResponse.value = appset.value.model_max_tokens
  selectModelTemperature.value = appset.value.model_temperature * 100
  selectModelHistoryWindowLength.value =
    appset.value.model_history_window_length
  templatePromptInput.value = appset.value.prompt_template
  // searchMode.value = appset.value.search_mode
  citationLimit.value = appset.value.citation_limit
  minRelevance.value = appset.value.min_relevance * 100
  // questionOptimization.value = appset.value.question_optimization
}

// 更新数据集操作
const updateDataSet = async () => {
  const data = {
    name: appset.value.name,
    description: appset.value.description,
    privacy: appset.value.privacy,
    model_name: selectModelName.value,
    model_max_tokens: selectModelMaxTokenResponse.value,
    model_temperature: selectModelTemperature.value / 100,
    model_history_window_length: selectModelHistoryWindowLength.value,
    prompt_template: templatePromptInput.value,
    citation_limit: citationLimit.value,
    min_relevance: minRelevance.value / 100
  }

  const response = await putAppsetAxios(appID, data)
  ElMessage.success('参数保存成功')
  console.log('保存描述', response)
}

// 模型参数相关数据
const modelList = [
  { name: 'gpt-3.5-turbo', max_tokens: 4096, context_length: 16000 },
  { name: 'gpt-4o', max_tokens: 4096, context_length: 128000 },
  { name: 'gpt-4-turbo', max_tokens: 4096, context_length: 128000 }
]
const isShowAISettingsModal = ref(false)
const selectModelName = ref('')
const selectModelTemperature = ref(100)
const formatTooltip = (value) => {
  return (value / 100).toFixed(2)
}
const selectModelMaxTokenResponse = ref(4096)
const selectModelHistoryWindowLength = ref(4)

// 检索参数弹出框有关参数
const showRetrievalSettingModel = ref(false)
const searchMode = ref('语义检索')
const citationLimit = ref(4)
const minRelevance = ref(50)
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
  updateDataSet()
}
// 数据定义完成，可以开始获取数据
fetchAppSet()

// 提示词模板相关数据
const templatePromptInputPlaceHolder = `你是一个用于回答问题的助手。请认真参考检索到的上下文片段和历史对话来回答问题。
只用生成回答是什么，不用重复生成问题。
问题: {question}
检索到的上下文: {context}
回答:`
const templatePromptInput = ref(templatePromptInputPlaceHolder)

// 控制关联知识库 弹窗相关数据
const connectDataSetModalShow = ref(false)
const dataSets = ref([])
const selectDataSets = ref([])
const tempSelectDataSets = ref([])
// 获取知识库列表
const fetchDataSets = async () => {
  try {
    const response = await getDatasetsAxios()
    console.log(response)
    dataSets.value = response.data
  } catch (error) {
    console.error('请求失败:', error)
  }
}
fetchDataSets()

const fetchSelectDataSets = async () => {
  const response = await getAppsetDatasetsAxios(appID)
  console.log(response)
  selectDataSets.value = response.data
}
fetchSelectDataSets()

// 点击选择(知识库)按钮时调用的方法
const showSelectDataSetsModal = () => {
  connectDataSetModalShow.value = true
  // 拷贝已选知识库数组（不可直接赋值，否则会直接影响原数组）
  tempSelectDataSets.value = selectDataSets.value.map((item) => ({
    ...item
  }))
}

// 计算属性：过滤掉已选知识库的数据集
const filteredDataSets = computed(() => {
  return dataSets.value.filter(
    (dataSet) =>
      !tempSelectDataSets.value.some(
        (selectedSet) => selectedSet.id === dataSet.id
      )
  )
})

// 关闭模态框并清空已选知识库
const closeModal = () => {
  connectDataSetModalShow.value = false
}

// 点击已有的dataset时调用的添加select的方法
const addToSelectedDatasets = (dataset) => {
  // 检查 selectDataSets 中是否已经包含相同的 dataset
  if (!tempSelectDataSets.value.some((d) => d.id === dataset.id)) {
    // 如果不包含，才将 dataset 添加到 selectDataSets 中
    tempSelectDataSets.value.push(dataset)
  }
}

// 点击关闭图标时调用的方法
const removeFromSelectedDatasets = (datasetToRemove) => {
  // 使用 filter 方法来筛选掉要移除的 dataset
  tempSelectDataSets.value = tempSelectDataSets.value.filter(
    (dataset) => dataset !== datasetToRemove
  )
}

// 选择结束并提交的函数，打印已选知识库并清空数组
const finishDataSetSelectionAndSubmit = async () => {
  console.log('已选择的知识库：', tempSelectDataSets.value)
  const datasetIds = tempSelectDataSets.value.map((item) => item.id)
  const response = await selectAppsetDatasetsAxios(appID, datasetIds)
  console.log(response)
  // selectDataSets.value = [] // 清空已选知识库数组
  fetchSelectDataSets()
  connectDataSetModalShow.value = false
  ElMessage.success('知识库关联成功')
}

const cleanRestart = ref(true)
const cleanChatHistory = async () => {
  cleanRestart.value = false
  await cleanChatHistoryAxios({ appset_id: appID })
  ElMessage.success('聊天记录清除成功')
  cleanRestart.value = true
}
</script>

<style scoped>
.APPIDConfiguration {
  display: flex;
  height: calc(100vh - 140px);
  align-items: stretch;
}

.left-block {
  flex: 0 0 30%; /* 左侧占30% */
  padding: 10px;
  display: flex;
  flex-direction: column;
}

.left-block-setting {
  margin-top: 20px;
  border: 1px solid #808080;
  border-radius: 8px;
  overflow-y: auto;
  height: 100%;
}

.right-block .right-block-title,
.left-block .left-block-setting-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 20px 20px 0;
}

.right-block .right-block-title,
.left-block .left-block-setting-title p {
  font-size: 20px;
  font-weight: bold;
  margin: 0; /*移除段落的默认外边距 */
}
.left-block .left-block-setting-content {
  margin: 5px;
  padding: 10px;
}

.left-block .left-block-setting-content .ai-setting {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ai-setting .title {
  font-weight: bold;
  margin-left: 20px;
}

.ai-setting-button {
  display: flex;
  align-items: center;
  justify-content: center; /* 使文本在水平方向上居中 */
  background-color: #fefefe;
  border: 1px solid #ccc;
  border-radius: 5px;
  padding: 8px 10px;
  font-size: 16px;
  color: #333;
  cursor: pointer;
  transition: background-color 0.3s;
  margin: 20px;
  flex: 1;
}

.ai-setting-button:hover {
  background-color: #e6ecfc;
  border-color: #0056b3; /* 修改边框颜色 */
}

/* ai-setting 模型弹窗有关 */
/* 全屏模态弹窗 */
.ai-setting .document-modal-background {
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

.ai-setting .document-modal {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  width: 100%;
  position: relative;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  width: 400px; /* 调整弹窗宽度 */
  max-width: 90%; /* 限制最大宽度 */
  max-height: 90%; /* 限制最大高度 */
}

.ai-setting .document-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e5e5e5;
  padding-bottom: 10px;
  margin-bottom: 10px;
}

.ai-setting .document-modal-title {
  font-size: 18px;
  font-weight: bold;
}

.ai-setting .document-modal-content {
  width: 100%;
  margin-top: 10px;
  text-align: left;
}

.ai-setting .document-model-close {
  font-size: 24px;
  cursor: pointer;
}

.ai-setting .ai-setting-model-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ai-setting .ai-setting-model-content > div {
  display: flex;
  align-items: center;
}

.ai-setting .ai-setting-model-content .left {
  flex: 0 0 120px; /* 调整标签的宽度 */
  color: #1f212a;
  text-align: center;
  padding-right: 10px;
}

.ai-setting .ai-setting-model-content .right {
  flex: 1;
}

.left-block .left-block-setting-content .template-prompt {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.template-prompt .title {
  font-weight: bold;
  margin-left: 23px;
  margin-right: 3px;
}

.template-prompt .template-prompt-input {
  margin: 10px 20px;
  flex: 1;
}

.connect-datasets {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.connect-datasets .title {
  font-weight: bold;
  margin-left: 20px;
}

.connect-datasets-button-set {
  display: flex;
  align-items: center;
  margin: 20px;
}

.connect-datasets-button-set button {
  background-color: transparent;
  border: none;
  border-radius: 5px;
  padding: 5px 15px;
  transition: background-color 0.3s ease;
  cursor: pointer;
}

.connect-datasets-button-set button:hover {
  background-color: #f0f1f6;
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
  width: 50%;
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
}

.save-button:hover {
  background-color: #0056b3;
}

/* 使用 Grid 布局展示知识库集合 */
.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 10px;
  margin-top: 10px;
}

.grid-item {
  position: relative;
  background-color: #fefefe;
  border: 1px solid #ddd;
  border-radius: 5px;
  padding: 10px;
  text-align: left;
  font-size: 12px;
  height: 50px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.grid-item-small .name,
.grid-item .name {
  overflow: hidden;
  color: #333;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.grid-item .created-at {
  position: absolute;
  bottom: 10px; /* 距离底部的距离 */
  right: 10px; /* 距离右侧的距离 */
  font-size: 10px; /* 可根据需要调整字体大小 */
  color: #666; /* 可根据需要调整颜色 */
}

.close-icon {
  position: absolute;
  top: 5px; /* 调整叉叉图标在垂直方向上的位置 */
  right: 5px; /* 调整叉叉图标在水平方向上的位置 */
  cursor: pointer;
  font-size: 16px; /* 调整叉叉图标的大小 */
  color: #999; /* 叉叉图标的颜色 */
}

.cursor-pointer {
  cursor: pointer;
}

.grid-container-small {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 10px;
  margin-top: 10px;
}

.grid-item-small {
  background-color: #fefefe;
  border: 1px solid #ddd;
  border-radius: 5px;
  padding: 20px 10px;
  text-align: left;
  font-size: 12px;
  height: 20px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.right-block {
  flex: 1; /* 使左右两块均分容器 */
  padding: 10px 20px;
  border: 1px solid #808080;
  border-radius: 8px;
  margin: 10px;
  display: flex;
  flex-direction: column;
}

.right-block .right-block-title {
  border-bottom: 1.5px solid #eee;
}

.right-block .right-block-content {
  flex-grow: 1;
  overflow: auto;
}
</style>
