<template>
  <div class="container">
    <header class="header">
      <div
        class="avatar-container"
        @mouseenter="handleHover"
        @mouseleave="handleLeave"
      >
        <img src="/avatar.png" alt="avatar" class="avatar-img" />
        <!-- 菜单容器 -->
        <div v-if="isHovered" class="menu">
          <ul>
            <li @click="props.logout()">退出登录</li>
            <li @click="dialogUpdateFormVisible = true">修改密码</li>
          </ul>
        </div>
      </div>
    </header>
    <div class="content">
      <div
        v-for="box in boxesData"
        :key="box.id"
        class="box"
        @click="goToChatView(box.id)"
      >
        <h3 class="box-title">{{ box.name }}</h3>
        <p class="box-description">{{ box.description }}</p>
      </div>
      <!-- 如果没有应用，则显示空文件夹图标和描述 -->
      <div class="boxesIsEmpty" v-if="boxesData.length === 0">
        <!-- 空文件夹图标 -->
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="1.5"
          stroke="currentColor"
          style="width: 48px; height: 48px; color: #999; margin-bottom: 10px"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M3.75 6.75h16.5M3.75 6.75v12a2.25 2.25 0 002.25 2.25h12a2.25 2.25 0 002.25-2.25v-12m-16.5 0L6 4.5h12l2.25 2.25"
          />
        </svg>
        <p style="font-size: 16px; font-weight: 500">暂无可用应用</p>
        <p style="font-size: 14px; color: #666">
          该账号暂无应用可使用，请联系管理员或添加新的应用。
        </p>
      </div>
    </div>
  </div>

  <!-- 修改密码弹窗 -->
  <el-dialog v-model="dialogUpdateFormVisible" title="修改密码" width="500">
    <el-form :model="formUpdate" :rules="rules" ref="formUpdateRef">
      <el-form-item
        label="用户编号"
        :label-width="formLabelWidth"
        prop="username"
      >
        <el-input
          v-model="formUpdate.username"
          disabled
          :style="{ width: formInputWidth }"
        />
      </el-form-item>
      <el-form-item label="用户名字" :label-width="formLabelWidth" prop="name">
        <el-input
          v-model="formUpdate.name"
          disabled
          :style="{ width: formInputWidth }"
        />
      </el-form-item>
      <el-form-item
        label="新密码"
        :label-width="formLabelWidth"
        prop="newPassword"
      >
        <el-input
          show-password
          v-model="formUpdate.newPassword"
          placeholder="请输入新密码"
          :style="{ width: formInputWidth }"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="dialogUpdateFormVisible = false">取消</el-button>
        <el-button type="primary" @click="updateNormalUserPasswordHandle">
          确定
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref } from 'vue'
import { getAppsByUserId } from '@/api/normal_user.js'
import { useRouter } from 'vue-router'
import { useTokenStore } from '@/stores/token.js'
import { ElMessage } from 'element-plus'
import { updateNormalUserPassword } from '@/api/normal_user.js'

const tokenStore = useTokenStore()
const user_id = tokenStore.username

const boxesData = ref([])

const initBoxesData = async () => {
  if (!user_id) return
  const response = await getAppsByUserId(user_id)
  boxesData.value = response.data.data
}
initBoxesData()

// 路由跳转，给每个盒子绑定，跳转到聊天页面
const router = useRouter()
const goToChatView = (appID) => {
  router.push({
    name: 'chat',
    params: { appID }
  })
}

// 控制头像的 hover 状态
const isHovered = ref(false)

// 父组件传递的 props 的退出登录函数
const props = defineProps({
  logout: {
    type: Function,
    required: true
  }
})

// 设置 hover 状态
const handleHover = () => {
  isHovered.value = true
}
const handleLeave = () => {
  isHovered.value = false
}

// 修改密码弹窗相关
const formLabelWidth = '100px'
const formInputWidth = '350px'
const dialogUpdateFormVisible = ref(false)
const formUpdateRef = ref()
const formUpdate = ref({
  username: tokenStore.username,
  name: tokenStore.name,
  newPassword: ''
})

// 表单验证规则
const rules = {
  newPassword: [
    { required: true, message: '不能为空', trigger: 'blur' },
    {
      pattern: /^[A-Za-z0-9]+$/, // 只允许数字和字母
      message: '密码只能包含数字和字母',
      trigger: 'blur'
    }
  ]
}

const updateNormalUserPasswordHandle = async () => {
  formUpdateRef.value.validate(async (valid) => {
    if (valid) {
      console.log(formUpdate.value.newPassword)
      const response = await updateNormalUserPassword(
        formUpdate.value.newPassword
      )
      if (response.data.code === 0) {
        dialogUpdateFormVisible.value = false
        props.logout(response.data.message)
      } else {
        ElMessage.error(response.data.message)
      }
    } else {
      // 如果表单验证失败，则不执行提交操作
      console.log('表单验证失败')
    }
  })
}
</script>

<style scoped>
.container {
  width: 100%;
  height: 100vh; /* 确保页面填满视窗高度 */

  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 12px;
  box-sizing: border-box;
  overflow: hidden;
}

.header {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  margin-bottom: 20px;
  box-sizing: border-box;
}

.avatar-container {
  position: relative;
  display: inline-block; /* 使头像和菜单并列显示 */
}

.avatar-img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
}

.menu {
  position: absolute;
  top: 40px; /* 位于头像下方 */
  right: 0;
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  width: 120px;
  z-index: 10;
}

.menu ul {
  list-style-type: none;
  padding: 0;
  margin: 0;
}

.menu li {
  padding: 10px;
  text-align: center;
  cursor: pointer;
  font-size: 14px;
  color: #555;
}

.menu li:hover {
  background-color: #f0f0f0;
}

.content {
  display: flex;
  flex-wrap: wrap;
  gap: 80px;
  justify-content: center;
  align-content: center;
  width: 100%;
  height: 100%;
  overflow-y: auto; /* 启用垂直滚动 */
  padding-bottom: 20px;
  box-sizing: border-box;
}

.box {
  flex: 0 1 calc(33.333% - 120px);
  height: calc(33.333% - 60px);
  background-color: #f9f9f9;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 15px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  box-sizing: border-box;
}

.box-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 10px;
}

.box-description {
  font-size: 14px;
  color: #555;
}

.boxesIsEmpty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: #f9f9f9;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  margin: 20px;
  text-align: center;
  color: #333;
}
</style>
