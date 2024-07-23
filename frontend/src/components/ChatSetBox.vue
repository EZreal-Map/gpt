<template>
  <div
    @click="routeToChat(chatset.app_id_id, chatset.id)"
    :class="{
      'chatset-item': true,
      chatsetItemActive: chatset.id === chatID
    }"
  >
    <div class="chatset-item-content">
      <!-- 可以根据实际需求显示更多信息，例如 chatset.name 等 -->
      <!-- 不可以删除下面多余的div，控制动画效果的长度为文字的长度 -->
      <div v-if="!isEditingName" @dblclick="enableEditingName">
        <div class="chatset-item-name" @animationend="handleAnimationEnd">
          {{ name }}
        </div>
      </div>
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

    <div class="title-right-more" @click.stop="" v-if="!isEditingName">
      <el-dropdown>
        <span class="el-dropdown-link">
          <el-icon size="20"><MoreFilled /></el-icon>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="handleClickRename"
              >重命名</el-dropdown-item
            >
            <el-dropdown-item @click="handleClickDelete">删除</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>
<script setup>
import { ref, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { MoreFilled } from '@element-plus/icons-vue'
import { updateChatSetNameAxios, deleteChatSetAxios } from '@/api/chatset'
import { ElMessage, ElMessageBox } from 'element-plus'

const props = defineProps({
  name: String, // 唯一name需要更改的，所有单独定义，其他的包括在chatset中
  chatset: Object,
  routeToChat: Function,
  fetchChatSetsData: Function,
  newChat: Function
})

// defineEmits 定义组件的事件
const emits = defineEmits(['update:name'])

// 使用 useRoute 获取路由信息
const chatID = ref(null)
const route = useRoute()
// 使用 watch 来监听 useRoute().query.chatID 的变化
watch(
  () => route.query.chatID,
  (newChatID) => {
    chatID.value = newChatID
  },
  { immediate: true }
)

// 动画结束时调用的函数
const handleAnimationEnd = (event) => {
  const targetElement = event.target // 获取触发事件的元素
  if (targetElement) {
    targetElement.classList.remove('typing-animation') // 移除打字动画类
  }
}

// name 修改相关变量
const isEditingName = ref(false)
const editableName = ref(props.name)
const nameInput = ref(null)
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
    const response = await updateChatSetNameAxios({
      chatset_id: props.chatset.id,
      chat_name: editableName.value
    })
    console.log('保存名字', response)
  } else {
    editableName.value = props.name
  }
}

// 下拉菜单相关
// 重命名
const handleClickRename = () => {
  isEditingName.value = true
}

// 删除
const handleClickDelete = async () => {
  ElMessageBox.confirm('确认删除聊天集合吗？', {
    confirmButtonText: '确定',
    cancelButtonText: '取消'
  })
    .then(async () => {
      // 后端删除数据
      await deleteChatSetAxios({ chatset_id: props.chatset.id })
      // 如果删除的是当前聊天集合，就跳转到新建聊天集合
      if (chatID.value === props.chatset.id) {
        props.newChat()
      }
      // 删除成功后重新获取数据，前端更新数据
      props.fetchChatSetsData()
      ElMessage.success('删除成功')
    })
    .catch(() => {
      ElMessage.info('已取消删除')
    })
}
</script>
<style scoped>
.chatset-item {
  cursor: pointer;
  padding: 8px;
  transition: background-color 0.2s ease;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chatset-item:hover {
  background-color: #ececec;
}

.chatset-item .title-right-more {
  opacity: 0;
}

.chatset-item:hover .title-right-more {
  opacity: 1;
}

.chatsetItemActive {
  background-color: #ececec;
}

.chatset-item-content {
  display: flex;
  align-items: center;
}

.chatset-item-name {
  color: #0d0d0d;
  font-size: 14px;
  margin-right: 10px;
}

.typing-animation {
  white-space: nowrap;
  overflow: hidden;
  border-right: 2px solid;
  animation:
    typing 1s steps(30, end),
    blink-caret 0.5s step-end infinite;
}

@keyframes typing {
  from {
    width: 0;
  }
  to {
    width: 100%;
  }
}

@keyframes blink-caret {
  from,
  to {
    border-color: transparent;
  }
  50% {
    border-color: black;
  }
}

.el-dropdown-link:focus-visible {
  outline: unset; /* 去除默认的轮廓线 */
}

.name-input {
  border: 1px solid #c0c4cc; /* 更浅的边框颜色 */
  border-radius: 4px;
  padding: 5px;
  font-size: 16px;
  outline: none; /* 去除输入框默认的轮廓线 */
}

.name-input:focus {
  border-color: #007bff; /* 输入框获得焦点时的边框颜色 */
  box-shadow: 0 0 3px rgba(0, 123, 255, 0.5); /* 输入框获得焦点时的浅色阴影 */
}
</style>
