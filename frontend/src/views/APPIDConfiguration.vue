<template>
  <div class="APPIDConfiguration">
    <div class="left-block">
      <!-- 左侧内容 -->
      <DataBaseBox
        v-for="item in appset"
        :key="item.id"
        :appID="item.id"
        v-model:name="item.name"
        v-model:description="item.description"
        v-model:privacy="item.privacy"
        :fetchDataSet="fetchAppSet"
        :putDatasetAxios="putAppsetAxios"
        :deleteDatasetAxios="deleteAppsetAxios"
        :created_at="item.created_at"
      ></DataBaseBox>
      <div class="content-title">
        <p>应用配置</p>
        <el-button type="primary">保存并预览</el-button>
      </div>

      <div class="content">
        <div class="ai-setting">
          <div class="title">AI 配置</div>
          <button class="ai-setting-button">
            <!-- <img src="gpt-icon.png" alt="GPT Icon" class="icon" /> -->
            gpt-3.5-turbo
          </button>
        </div>
        <div class="template-prompt">
          <div class="title">提示词</div>
          <el-input
            class="template-prompt-input"
            v-model="templatePromptInput"
            style="width: 240px"
            :autosize="{ minRows: 6, maxRows: 10 }"
            type="textarea"
            placeholder="Please input"
          />
        </div>
        <div class="connect-datasets">
          <div class="title">关联知识库</div>
          <div class="connect-datasets-button-set">
            <button @click="showSelectDataSetsModal">选择</button>
            <button>参数</button>
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
    </div>

    <!-- 选择知识库弹窗 -->
    <div v-if="connectDataSetModalShow" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <span class="modal-title">选择知识库</span>
          <span class="close" @click="closeModal">&times;</span>
        </div>
        <div class="selected-datasets" v-show="tempSelectDataSets.length > 0">
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

            <div class="created-at">{{ dataset.created_at.split(' ')[0] }}</div>
          </div>
        </div>
        <div class="datasets">
          知识库集合
          <div class="grid-container">
            <div
              class="grid-item cursor-pointer"
              v-for="(dataset, index) in dataSets"
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
          <button class="save-button" @click="finishSelectionAndSubmit">
            完成
          </button>
        </div>
      </div>
    </div>

    <div class="right-block">
      <!-- 右侧内容 -->
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import {
  getAppsetAxios,
  putAppsetAxios,
  deleteAppsetAxios,
  selectAppsetDatasetsAxios,
  getAppsetDatasetsAxios
} from '@/api/appset'
import { getDatasetsAxios } from '@/api/dataset.js'

// 使用 useRoute 获取路由信息
const route = useRoute()
const appID = route.params.appID

const appset = ref('')

const fetchAppSet = async () => {
  const response = await getAppsetAxios(appID)
  console.log(response)
  appset.value = [response.data]
}

fetchAppSet()

const templatePromptInput = ref('')

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

// 点击选择按钮时调用的方法
const showSelectDataSetsModal = () => {
  connectDataSetModalShow.value = true
  // 拷贝已选知识库数组（不可直接赋值，否则会直接影响原数组）
  tempSelectDataSets.value = selectDataSets.value.map((item) => ({
    ...item
  }))
}

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
const finishSelectionAndSubmit = async () => {
  console.log('已选择的知识库：', tempSelectDataSets.value)
  const datasetIds = tempSelectDataSets.value.map((item) => item.id)
  const response = await selectAppsetDatasetsAxios(appID, datasetIds)
  console.log(response)
  // selectDataSets.value = [] // 清空已选知识库数组
  fetchSelectDataSets()
  connectDataSetModalShow.value = false
}
</script>

<style scoped>
.APPIDConfiguration {
  display: flex;
}

.left-block {
  flex: 0 0 30%; /* 左侧占30% */
  padding: 10px;
  border: 1px solid #111;
}

.right-block {
  flex: 1; /* 使左右两块均分容器 */
  padding: 10px;
}

.right-block {
  background-color: #e0e0e0; /* 可根据需要调整背景色 */
}

.left-block .content-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 20px 20px;
}

.left-block .content-title p {
  font-size: 20px;
  font-weight: bold;
  margin: 0; /* 移除段落的默认外边距 */
}

.left-block .content {
  margin: 5px;
  border: 1px solid #ccc;
  padding: 20px 10px;
}

.left-block .content .ai-setting {
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

.left-block .content .template-prompt {
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
  margin: 20px;
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
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 10px;
  margin-top: 10px;
}

.grid-item {
  position: relative;
  background-color: #fefefe;
  border: 2px solid #ddd;
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
  font-weight: bold;
  overflow: hidden;
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
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 10px;
  margin-top: 10px;
}

.grid-item-small {
  background-color: #fefefe;
  border: 2px solid #ddd;
  border-radius: 5px;
  padding: 10px;
  text-align: left;
  font-size: 12px;
  height: 20px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
