<template>
  <div class="box" @click="routeToIDDataBaseView()">
    <div class="title-container">
      <div class="title-left-name">
        <el-icon size="30" color="#0056b3"><DocumentCopy /></el-icon>
        <span
          @dblclick="enableEditingName"
          @click.stop=""
          v-if="!isEditingName"
          >{{ name }}</span
        >
        <input
          v-else
          v-model="editableName"
          @blur="saveName"
          @keyup.enter="saveName"
          @click.stop=""
          class="name-input"
          ref="nameInput"
        />
      </div>
      <div class="title-right-more" @click.stop="">
        <el-dropdown>
          <span class="el-dropdown-link">
            <el-icon size="20"><MoreFilled /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="handleClickRename"
                >重命名</el-dropdown-item
              >
              <el-dropdown-item @click="handleClickModifyDescription"
                >修改描述</el-dropdown-item
              >
              <el-dropdown-item @click="handleClickModifyPrivacy"
                >修改隐私</el-dropdown-item
              >
              <el-dropdown-item divided @click="handleClickDelete()"
                >删除</el-dropdown-item
              >
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
    <div class="middle-container" @dblclick="enableEditingDescription">
      <span v-if="!isEditingDesctiption" @click.stop="">{{ description }}</span>
      <input
        v-else
        v-model="editableDescription"
        @blur="saveDescription"
        @keyup.enter="saveDescription"
        @click.stop=""
        class="description-input"
        ref="descriptionInput"
      />
    </div>
    <div class="bottom-container">
      <div class="bottom-container-left" @click="changePrive">
        <el-icon size="18" v-if="privacy === '私有'"><Lock /> </el-icon>
        <el-icon size="18" v-else><Unlock /></el-icon>
        <span>{{ privacy }}</span>
      </div>
      <span class="bottom-container-right">{{ created_at }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { DocumentCopy, MoreFilled, Lock, Unlock } from '@element-plus/icons-vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

// 是否是应用配置页面
let appConfigurationView = false
// 使用 useRoute 获取路由信息
const route = useRoute()
if (route.params?.appID) {
  appConfigurationView = true
}

console.log('appConfigurationView', appConfigurationView)

// defineProps 接收父组件传递的数据
const props = defineProps({
  databaseID: String,
  name: String,
  description: String,
  privacy: String,
  fetchDataSet: Function,
  appID: String,
  putDatasetAxios: Function,
  deleteDatasetAxios: Function,
  created_at: String
})

// defineEmits 定义组件的事件
const emits = defineEmits([
  'update:name',
  'update:description',
  'update:privacy'
])

// name 修改相关变量
const isEditingName = ref(false)
const editableName = ref(props.name)
const nameInput = ref(null)

// description 修改相关变量
const isEditingDesctiption = ref(false)
const editableDescription = ref(props.description)
const descriptionInput = ref(null)
// privacy 修改相关变量
const editablePrivacy = ref(props.privacy)

// 更新数据集操作
const updateDataSet = async () => {
  const data = {
    name: editableName.value,
    description: editableDescription.value, // 可以根据需要添加描述
    privacy: editablePrivacy.value // 可以根据需要添加隐私
  }

  const ID = props.databaseID || props.appID
  const response = await props.putDatasetAxios(ID, data)
  console.log('保存描述', response)
}

// name 修改相关操作
const enableEditingName = () => {
  isEditingName.value = true
  nextTick(() => {
    nameInput.value.focus()
  })
}

const saveName = async () => {
  isEditingName.value = false
  if (editableName.value) {
    // 更新父组件或服务器上的数据
    emits('update:name', editableName.value)
    console.log('保存名字', editableName.value)
    updateDataSet()
  } else {
    editableName.value = props.name
  }
}

// description 修改相关操作
const enableEditingDescription = () => {
  isEditingDesctiption.value = true
  nextTick(() => {
    descriptionInput.value.focus()
  })
}

const saveDescription = () => {
  isEditingDesctiption.value = false
  // 更新父组件或服务器上的数据
  emits('update:description', editableDescription.value)
  updateDataSet()
}

// privacy 修改相关操作
const changePrive = (event) => {
  event.stopPropagation() // 阻止事件冒泡
  editablePrivacy.value = props.privacy === '私有' ? '公开' : '私有'
  console.log('修改隐私', editablePrivacy.value)
  emits('update:privacy', editablePrivacy.value)
  updateDataSet()
}

// 路由跳转相关 跳转到文档详情页
const router = useRouter()
const routeToIDDataBaseView = () => {
  const databaseID = props.databaseID
  if (databaseID) {
    console.log('跳转到文档', databaseID)
    // router.push(`/database/${databaseID}`)
    router.push({ name: 'id-database', params: { databaseID } })
  } else {
    const appID = props.appID
    console.log('跳转到应用', appID)
    router.push({ name: 'id-app', params: { appID } })
  }
}

// 下拉菜单相关
// 重命名
const handleClickRename = () => {
  isEditingName.value = true
}
// 修改描述
const handleClickModifyDescription = () => {
  isEditingDesctiption.value = true
}

// 修改隐私
const handleClickModifyPrivacy = () => {
  editablePrivacy.value = props.privacy === '私有' ? '公开' : '私有'
  emits('update:privacy', editablePrivacy.value)
  updateDataSet()
}

// 删除
const handleClickDelete = async () => {
  ElMessageBox.confirm('确认删除知识库吗？', {
    confirmButtonText: '确定',
    cancelButtonText: '取消'
  })
    .then(async () => {
      const ID = props.databaseID || props.appID
      const response = await props.deleteDatasetAxios(ID)
      if (appConfigurationView) {
        router.push({ name: 'app' })
      } else {
        props.fetchDataSet()
      }
      console.log('删除', response)
      ElMessage.success('删除成功')
    })
    .catch(() => {
      ElMessage.info('已取消删除')
    })
}
</script>
<style scoped>
.box {
  height: 140px;
  background-color: #fefefe;
  position: relative;
  padding: 10px;
  border: 1px solid #808080;
  border-radius: 8px;
  transition: background-color 0.3s ease; /* 添加过渡效果 */
  cursor: pointer;
}
.box:hover {
  background-color: #e6ecfc;
  border-color: #0056b3; /* 修改边框颜色 */
}

.title-container {
  display: flex;
  justify-content: space-between; /* 左右布局，元素之间的空间 */
  align-items: center; /* 垂直居中 */
  margin-top: 10px;
}

.title-left-name {
  display: flex;
  align-items: center;
  flex-grow: 1; /* 使标题占据剩余空间 */
}

.title-left-name .el-icon {
  margin: 0 5px 0 10px;
}

.title-left-name span {
  font-size: 16px;
  font-weight: 700;
  cursor: text;
  text-align: left; /* 将 span 文字左对齐 */
}

.title-right-more {
  cursor: pointer;
  margin: 0 10px;
}

.middle-container {
  display: flex;
  margin: 10px 20px;
}

.middle-container span {
  color: #667085;
  cursor: text;
}

.bottom-container {
  position: absolute;
  bottom: 10px;
  left: 10px; /* 调整左边距 */
  right: 10px; /* 调整右边距 */
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.bottom-container .bottom-container-left {
  display: flex;
  align-items: center;
}

.bottom-container .bottom-container-left .el-icon {
  margin-right: 2px;
}

.bottom-container .bottom-container-right {
  margin-left: auto; /* 将日期推到最右边 */
}

.name-input,
.description-input {
  border: 1px solid #c0c4cc; /* 更浅的边框颜色 */
  border-radius: 4px;
  padding: 5px;
  font-size: 16px;
  outline: none; /* 去除输入框默认的轮廓线 */
}

.name-input:focus,
.description-input:focus {
  border-color: #007bff; /* 输入框获得焦点时的边框颜色 */
  box-shadow: 0 0 3px rgba(0, 123, 255, 0.5); /* 输入框获得焦点时的浅色阴影 */
}

.el-dropdown-link {
  cursor: pointer;
  color: var(--el-color-primary);
  display: flex;
  align-items: center;
}

.el-dropdown-link:focus-visible {
  outline: unset; /* 去除默认的轮廓线 */
}
</style>
