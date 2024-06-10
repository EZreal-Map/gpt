<template>
  <div class="main-container" ref="tableContainer">
    <el-steps style="max-width: 100%" :active="activeStep" align-center>
      <el-step title="选择文件" />
      <el-step title="数据处理" />
      <el-step title="上传数据" />
    </el-steps>

    <div class="prevStepButton" v-show="activeStep !== 1">
      <el-button @click="prev">上一步</el-button>
    </div>
    <div class="nextStepButton">
      <el-button @click="next" ref="nextStepButton">{{
        nextButtonText
      }}</el-button>
    </div>

    <!-- activeStep 等于 1 时显示上传文件按钮 -->
    <el-upload
      v-show="activeStep === 1"
      v-model:file-list="fileList"
      action="http://127.0.0.1:7979/retrieval/uploadfiles/"
      multiple
      :before-remove="beforeRemove"
    >
      <el-button type="primary">点击上传</el-button>
      <template #tip>
        <div class="el-upload__tip">
          支持 .txt .docx .csv .pdf .html 类型文件
        </div>
      </template>
    </el-upload>

    <el-button type="primary" v-show="activeStep === 2" @click="SplitDocument"
      >重新分割</el-button
    >
    <!-- activeStep 等于 2 时显示数据处理 -->
    <div class="activeStep2" v-show="activeStep === 2">
      <div class="activeStep2-left">
        <div class="activeStep2-title">数据处理参数</div>
        <div class="activeStep2-left-radio1">
          <span>训练模式</span>
          <el-radio-group v-model="radio1">
            <el-radio value="1" size="large" border>直接拆分</el-radio>
            <el-radio value="2" size="large" border disabled>问答拆分</el-radio>
          </el-radio-group>
        </div>
        <div class="activeStep2-left-radio2">
          <span>处理方式</span>
          <el-radio-group v-model="radio2">
            <el-radio value="1" size="large" border>自动 </el-radio>
            <el-radio value="2" size="large" border>自定义规则</el-radio>
          </el-radio-group>
          <div v-show="radio2 === '2'" class="custom-rule-show">
            <el-form
              label-position="left"
              label-width="120x"
              style="max-width: 300px"
              :model="radio2Form"
            >
              <el-form-item label="理想分块长度" prop="chunkLength">
                <el-input-number
                  v-model="radio2Form.chunkLength"
                  controls-position="right"
                  :min="radio2Form.overlapLength"
                  :step="100"
                />
              </el-form-item>
              <el-form-item label="上下文重叠长度" prop="overlapLength">
                <el-input-number
                  v-model="radio2Form.overlapLength"
                  controls-position="right"
                  :min="0"
                  :max="radio2Form.chunkLength"
                  :step="100"
                />
              </el-form-item>
              <el-form-item label="自定义分隔符" prop="separatorCharacter">
                <el-input
                  v-model="radio2Form.separatorCharacter"
                  placeholder="如无特殊需求，可不填写"
                  clearable
                />
              </el-form-item>
            </el-form>
          </div>
        </div>
      </div>
      <div class="activeStep2-right">
        <el-tabs type="border-card">
          <el-tab-pane label="分段预览">
            <div class="segment-preview" ref="maxHeightSegmentPreview">
              <div
                class="block"
                v-for="(document, index) in step2DocumentData"
                :key="document.index"
              >
                <div class="title">
                  <span class="title-index">#{{ index + 1 }} </span
                  ><span class="title-filename">{{
                    document.metadata.filename
                  }}</span>
                </div>
                <div class="content">{{ document.page_content }}</div>
              </div>
            </div>
          </el-tab-pane>
          <el-tab-pane label="来源列表">
            <div class="source-list" ref="maxHeightSourceList">
              <div
                class="block"
                v-for="(chunkNUm, index) in step2ChunkNumData"
                :key="chunkNUm.filename"
              >
                <span class="filename"
                  ><span class="title-index">#{{ index + 1 }} </span
                  >{{ chunkNUm.filename }}</span
                >
                <span class="chunk-length"
                  >分段：{{ chunkNUm.chunk_sum_num }}</span
                >
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>

    <!-- activeStep 等于 3 时显示上传数据 -->
    <div class="activeStep3" v-show="activeStep === 3">
      <el-table
        :data="step2ChunkNumData"
        style="width: 100%"
        table-layout="fixed"
        :header-row-style="{
          color: '#000',
          fontWeight: 'bold'
        }"
        :height="tableContainerMaxHeight - 140"
      >
        <el-table-column prop="filename" label="文件名" />
        <el-table-column prop="total_word_count" label="字符数" width="180" />
        <el-table-column prop="chunkLength" label="理想分块长度" width="180" />
        <el-table-column
          prop="overlapLength"
          label="上下文重叠长度"
          width="180"
        />
        <el-table-column
          prop="separatorCharacter"
          label="自定义分隔符"
          width="180"
        />
        <el-table-column prop="chunk_sum_num" label="分段数" width="180" />
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import 'element-plus/es/components/message/style/css'
import 'element-plus/es/components/message-box/style/css'
import { useRoute, useRouter } from 'vue-router'
const route = useRoute()
// 从路由对象中提取 databaseID 参数
const databaseID = route.params.databaseID

import axios from 'axios'

const clearTempDirectory = async () => {
  await axios.post('http://127.0.0.1:7979/retrieval/clear-temp-dir/')
  console.log('IDDataBaseUpdateDocumentView.vue -- 清空temp')
}
clearTempDirectory()

// activeStep 等于 1 时 上传文件操作
const fileList = ref([])

const beforeRemove = (uploadFile) => {
  return ElMessageBox.confirm(`取消上传 ${uploadFile.name} ?`, {
    confirmButtonText: '确定',
    cancelButtonText: '取消'
  }).then(
    () => {
      axios
        .delete(
          `http://127.0.0.1:7979/retrieval/deletefile/${encodeURIComponent(uploadFile.name)}`
        )
        .then((response) => {
          ElMessage.success(response.data.message) // 提示删除成功
          return true
        })
        .catch((error) => {
          console.error('Error:', error) // 打印错误信息
          return false
        })
    },
    () => {
      return false
    }
  )
}

// activeStep 等于 2 时数据处理操作
const radio1 = ref('1')
const radio2 = ref('1')

const radio2Form = ref({
  chunkLength: 500,
  overlapLength: 100,
  separatorCharacter: ''
})

const step2DocumentData = ref([])

const step2ChunkNumData = ref([])

const SplitDocument = async () => {
  try {
    const response = await axios.get(
      'http://127.0.0.1:7979/retrieval/pdf-files/',
      {
        params: {
          chunk_size: radio2Form.value.chunkLength,
          chunk_overlap: radio2Form.value.overlapLength,
          separator: radio2Form.value.separatorCharacter
        }
      }
    )
    console.log(response.data) // 返回获取的数据
    step2DocumentData.value = response.data

    // 提取 filename 和 chunk_sum_num，并存储为对象
    const extractedData = {}
    response.data.forEach((item) => {
      extractedData[item.metadata.filename] = [
        item.metadata.chunk_sum_num,
        item.metadata.total_word_count
      ]
    })

    console.log(extractedData) // 打印提取的数据

    // 转换为数组
    const dataArray = Object.keys(extractedData).map((filename) => ({
      filename,
      chunk_sum_num: extractedData[filename][0],
      total_word_count: extractedData[filename][1],
      chunkLength: radio2Form.value.chunkLength,
      overlapLength: radio2Form.value.overlapLength,
      separatorCharacter: radio2Form.value.separatorCharacter || '无'
    }))

    step2ChunkNumData.value = dataArray
  } catch (error) {
    console.error('Error fetching PDF files:', error)
    throw error // 抛出错误，供调用者处理
  }
}

// 滚动条位置设置
const tableContainer = ref(null)
const tableContainerMaxHeight = ref(null) // 记录main-container容器的最大高度
// step2 中的分段预览和来源列表的最大高度
const maxHeightSegmentPreview = ref(null)
const maxHeightSourceList = ref(null)

onMounted(() => {
  calculateMaxHeight()
  window.addEventListener('resize', calculateMaxHeight)
})

const calculateMaxHeight = () => {
  // 计算main-container容器的最大高度
  const windowHeight = window.innerHeight
  const tableContainerOffsetTop = tableContainer.value.offsetTop
  tableContainerMaxHeight.value = windowHeight - tableContainerOffsetTop - 50 // 50为额外留白，可根据实际情况调整
  tableContainer.value.style.maxHeight = `${tableContainerMaxHeight.value}px`

  // 计算segment-preview容器的最大高度
  const maxHeightSegmentPreviewOffsetTop =
    maxHeightSegmentPreview.value.offsetTop
  const maxHeightSegmentPreviewMaxHeight =
    windowHeight - maxHeightSegmentPreviewOffsetTop - 400 // 50为额外留白，可根据实际情况调整
  maxHeightSegmentPreview.value.style.maxHeight = `${maxHeightSegmentPreviewMaxHeight}px`

  // 计算source-list容器的最大高度
  const maxHeightSourceListOffsetTop = maxHeightSourceList.value.offsetTop
  const maxHeightSourceListMaxHeight =
    windowHeight - maxHeightSourceListOffsetTop - 400 // 50为额外留白，可根据实际情况调整
  maxHeightSourceList.value.style.maxHeight = `${maxHeightSourceListMaxHeight}px`
}

// 有关步骤条功能
const activeStep = ref(1)
const nextStepButton = ref(null)
const nextButtonText = ref('下一步')

// 回到上一级
const router = useRouter()
const backToIDDataBaseDocumentView = (databaseID) => {
  router.push({
    name: 'id-database-document',
    params: { databaseID: databaseID }
  }) // 使用路由名称
}

const next = async () => {
  try {
    if (activeStep.value++ >= 3) activeStep.value = 3
    if (activeStep.value === 3) {
      if (nextButtonText.value === '确认上传') {
        const response = await axios.post(
          `http://127.0.0.1:7979/dataset/move-temp-files/${databaseID}`,
          {
            chunk_size: radio2Form.value.chunkLength,
            chunk_overlap: radio2Form.value.overlapLength,
            separator: radio2Form.value.separatorCharacter
          }
        )
        console.log(response.data)
        backToIDDataBaseDocumentView(databaseID)
      }
      nextButtonText.value = '确认上传'
    } else {
      nextButtonText.value = '下一步'
    }
  } catch (error) {
    console.error('处理 next 事件时发生错误:', error)
  }
}

const prev = () => {
  if (activeStep.value-- <= 1) activeStep.value = 1
  if (activeStep.value === 3) {
    nextButtonText.value = '确认上传'
  } else {
    nextButtonText.value = '下一步'
  }
}
</script>

<style scoped>
/* 主容器样式 */
.main-container {
  position: relative;
  overflow: auto; /* 当内容溢出时显示滚动条 */
  padding-bottom: 50px; /* 为了给按钮留出空间 */
}

.prevStepButton {
  position: absolute;
  left: 100px;
}

.nextStepButton {
  position: absolute;
  right: 100px;
}

.activeStep2 {
  display: flex;
  justify-content: space-between;
  margin-top: 40px; /* 可根据需要调整间距 */
  text-align: left;
}

.activeStep2-left {
  width: 450px;
  flex-shrink: 0; /* 左侧不被压缩 */
  border: 1px solid #ccc;
  border-right: 0px solid #ccc;
  padding: 10px;
  margin-left: 50px;
}

.activeStep2-left span {
  margin-right: 20px; /* 可根据需要调整间距 */
}

.activeStep2-left-radio1 .el-radio {
  margin: 10px; /* 可根据需要调整间距 */
}

.activeStep2-left-radio2 .el-radio {
  margin: 10px; /* 可根据需要调整间距 */
}

.custom-rule-show {
  margin-top: 10px; /* 可根据需要调整间距 */
  margin-left: 100px;
}

.activeStep2-right {
  flex-grow: 1; /* 占据剩余的所有宽度 */
  border: 1px solid #ccc; /* 可选：添加边框以区分左右部分 */
  padding: 10px; /* 可选：添加内边距 */
}

.activeStep2-title {
  font-size: 20px; /* 可根据需要调整字体大小 */
  font-weight: bold; /* 可选：加粗字体 */
  margin-bottom: 10px; /* 可根据需要调整间距 */
}
.segment-preview,
.source-list {
  overflow: auto; /* 当内容溢出时显示滚动条 */
  height: 100%; /* 确保容器高度被限制 */
}
.segment-preview .block {
  border: 1px solid #ddd;
  margin-bottom: 10px;
  padding: 15px;
  background-color: #fff;
  border-radius: 5px; /* 圆角 */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* 轻微阴影 */
}

.segment-preview .title {
  font-weight: bold;
  display: flex;
  align-items: center;
  margin-bottom: 5px;
}

.segment-preview .content {
  margin-top: 10px;
  color: #999;
  font-size: 12px;
}

.source-list .block {
  border: 1px solid #ddd;
  margin-bottom: 10px;
  padding: 15px;
  background-color: #fff;
  border-radius: 5px; /* 圆角 */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* 轻微阴影 */
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.source-list .filename {
  font-weight: bold;
  display: flex;
  align-items: center;
}

.title-index {
  color: #007bff;
  margin-right: 10px;
}

.activeStep3 {
  margin-top: 40px;
}
</style>
