<template>
  <div class="title-container">
    <h1 class="gradient-text">我的知识库</h1>
    <button class="new-button" @click="dialogFormVisible = true">
      <el-icon><Plus /></el-icon>
      <span>新建</span>
    </button>
  </div>

  <div class="main-container" ref="tableContainer">
    <DataBaseBox
      v-for="item in dataSet"
      :key="item.id"
      :databaseID="item.id"
      v-model:name="item.name"
      v-model:description="item.description"
      v-model:privacy="item.privacy"
      :fetchDataSet="fetchDataSet"
      :putDatasetAxios="putDatasetAxios"
      :deleteDatasetAxios="deleteDatasetAxios"
      :created_at="item.created_at"
    ></DataBaseBox>
  </div>

  <el-dialog v-model="dialogFormVisible" title="新建知识库" width="500">
    <el-form :model="form" :rules="rules" ref="formRef">
      <el-form-item
        label="知识库名字"
        :label-width="formLabelWidth"
        prop="name"
      >
        <el-input
          v-model="form.name"
          autocomplete="on"
          placeholder="请输入知识库名字"
          :style="{ width: formInputWidth }"
        />
      </el-form-item>
      <el-form-item
        label="知识库描述"
        :label-width="formLabelWidth"
        prop="description"
      >
        <el-input
          type="textarea"
          v-model="form.description"
          autocomplete="on"
          :rows="4"
          placeholder="请输入知识库描述"
          :label-width="formLabelWidth"
          :style="{ width: formInputWidth }"
        />
      </el-form-item>
      <el-form-item
        label="私有 / 公开"
        :label-width="formLabelWidth"
        prop="privacy"
      >
        <el-select
          v-model="form.privacy"
          placeholder="请选择隐私设置"
          :style="{ width: formInputWidth }"
        >
          <el-option label="私有" value="私有" />
          <el-option label="公开" value="公开" />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="dialogFormVisible = false">取消</el-button>
        <el-button type="primary" @click="createNewDataBaseHandle()">
          确定
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import DataBaseBox from '@/components/DataBaseBox.vue'
import {
  getDatasetsAxios,
  postDatasetAxios,
  putDatasetAxios,
  deleteDatasetAxios
} from '@/api/dataset.js'
const dataSet = ref([])
// 获取知识库列表
async function fetchDataSet() {
  try {
    const response = await getDatasetsAxios()
    console.log(response)
    dataSet.value = response.data
  } catch (error) {
    console.error('请求失败:', error)
  }
}
fetchDataSet()

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
    const tableContainerMaxHeight = windowHeight - tableContainerOffsetTop - 70 // 70为额外留白，可根据实际情况调整
    tableContainer.value.style.maxHeight = `${tableContainerMaxHeight}px`
  }
}

// 新建弹框
const dialogFormVisible = ref(false)
const formLabelWidth = '100px'
const formInputWidth = '350px'

const formRef = ref()
const form = ref({
  name: '',
  privacy: '',
  description: ''
})

// 表单验证规则
const rules = {
  name: [{ required: true, message: '请输入知识库名字', trigger: 'blur' }],
  description: [
    { required: false, message: '请输入知识库描述', trigger: 'blur' }
  ],
  privacy: [{ required: true, message: '请选择隐私设置', trigger: 'blur' }]
}

// 创建新知识库的处理函数
const createNewDataBaseHandle = () => {
  formRef.value.validate(async (valid) => {
    if (valid) {
      // 如果表单通过验证，则继续执行提交操作
      await postDatasetAxios({
        name: form.value.name,
        description: form.value.description,
        privacy: form.value.privacy
      })

      fetchDataSet() // 重新获取知识库列表
      formRef.value.resetFields() // 重置表单
      dialogFormVisible.value = false // 关闭弹框
    } else {
      // 如果表单验证失败，则不执行提交操作
      console.log(valid)
      console.log('表单验证失败')
    }
  })
}
</script>
<style scoped>
/* Flex容器 */
.title-container {
  display: flex;
  justify-content: space-between; /* 左右布局，元素之间的空间 */
  align-items: center; /* 垂直居中 */
}

/* 按钮样式 */
.new-button {
  padding: 10px 20px;
  font-size: 14px;
  background-color: #ffffff;
  color: #007bff;
  border: 1px solid #007bff;
  border-radius: 8px;
  cursor: pointer;
  margin-right: 30px;
  display: flex; /* 将按钮设置为 flex 布局 */
  align-items: center; /* 垂直居中 */
  transition: background-color 0.3s ease; /* 添加过渡效果 */
}

.new-button:hover {
  background-color: #e6ecfc;
  border-color: #0056b3; /* 修改边框颜色 */
}

/* 渐变文字效果 */
.gradient-text {
  background: linear-gradient(to right, #007bff, #0056b3); /* 设置背景渐变 */
  background-clip: text; /* 使用背景裁剪文字 */
  color: transparent; /* 使文字颜色透明 */
}

/* 图标样式  '+' 与 '新增' 的间隔*/
.el-icon {
  margin-right: 4px;
}

.main-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  grid-gap: 20px;
  overflow: auto; /* 当内容溢出时显示滚动条 */
}

.el-dialog {
  text-align: left;
}
</style>
