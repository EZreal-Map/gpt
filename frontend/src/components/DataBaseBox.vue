<template>
  <div class="box" @click="routeToIDDataBaseView(databaseID)">
    <div class="title-container">
      <div class="title-left-name">
        <el-icon size="30"><DocumentCopy /></el-icon>
        <span
          @dblclick="enableEditingTitle"
          @click.stop=""
          v-if="!isEditingTitle"
          >{{ title }}</span
        >
        <input
          v-else
          v-model="editableTitle"
          @blur="saveTitle"
          @keyup.enter="saveTitle"
          @click.stop=""
          class="title-input"
          ref="titleInput"
        />
      </div>
      <div class="title-right-more">
        <el-icon size="20"><MoreFilled /></el-icon>
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
    <div class="bottom-container" @click="changePrive">
      <el-icon size="18" v-if="privacy === '私有'"><Lock /> </el-icon>
      <el-icon size="18" v-else><Unlock /></el-icon>
      <span>{{ privacy }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { DocumentCopy, MoreFilled, Lock, Unlock } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'

// defineProps 接收父组件传递的数据
const props = defineProps({
  databaseID: String,
  title: String,
  description: String,
  privacy: String
})

// defineEmits 定义组件的事件
const emits = defineEmits([
  'update:title',
  'update:description',
  'update:privacy'
])

// title 修改相关
const isEditingTitle = ref(false)
const editableTitle = ref(props.title)
const titleInput = ref(null)

const enableEditingTitle = () => {
  isEditingTitle.value = true
  nextTick(() => {
    titleInput.value.focus()
  })
}

const saveTitle = () => {
  isEditingTitle.value = false
  // 更新父组件或服务器上的数据
  console.log('保存描述', editableTitle.value)
  emits('update:title', editableTitle.value)
}

// description 修改相关
const isEditingDesctiption = ref(false)
const editableDescription = ref(props.description)
const descriptionInput = ref(null)

const enableEditingDescription = () => {
  isEditingDesctiption.value = true
  nextTick(() => {
    descriptionInput.value.focus()
  })
}

const saveDescription = () => {
  isEditingDesctiption.value = false
  // 更新父组件或服务器上的数据
  console.log('保存描述', editableDescription.value)
  emits('update:description', editableDescription.value)
}

const changePrive = (event) => {
  event.stopPropagation() // 阻止事件冒泡
  console.log('修改隐私')
  emits('update:privacy', props.privacy === '私有' ? '公开' : '私有')
}

// 路由跳转相关 跳转到文档详情页
const router = useRouter()
const routeToIDDataBaseView = (databaseID) => {
  console.log('跳转到文档', databaseID)
  // router.push(`/database/${databaseID}`)
  router.push({ name: 'id-database', params: { databaseID } })
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
  display: flex;
  align-items: center;
  cursor: pointer;
}

.bottom-container .el-icon {
  margin-right: 2px;
}

.title-input,
.description-input {
  border: 1px solid #c0c4cc; /* 更浅的边框颜色 */
  border-radius: 4px;
  padding: 5px;
  font-size: 16px;
  outline: none; /* 去除输入框默认的轮廓线 */
}

.title-input:focus,
.description-input:focus {
  border-color: #007bff; /* 输入框获得焦点时的边框颜色 */
  box-shadow: 0 0 3px rgba(0, 123, 255, 0.5); /* 输入框获得焦点时的浅色阴影 */
}
</style>
