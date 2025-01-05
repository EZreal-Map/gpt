<template>
  <NormalUserAfterLogin
    v-if="role === 'user'"
    :logout="logout"
  ></NormalUserAfterLogin>
  <div class="login-center-container" v-else>
    <div class="login-box">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <div v-if="!isLogin">
          <h1 class="login-title">登录窗口</h1>
          <el-form-item label="用户名" prop="username">
            <el-input
              v-model="form.username"
              placeholder="请输入用户名"
              @keydown.enter="onSubmit(formRef)"
              :style="{ width: formInputWidth }"
            />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input
              v-model="form.password"
              placeholder="请输入密码"
              type="password"
              @keydown.enter="onSubmit(formRef)"
              :style="{ width: formInputWidth }"
            />
          </el-form-item>
          <div class="button-group">
            <el-button type="primary" @click="onSubmit(formRef)"
              >确定</el-button
            >
            <el-button class="right-btn" @click="logout()">退出</el-button>
          </div>
        </div>
        <div v-if="role === 'admin'">
          <h1 class="login-title">欢迎, {{ tokenStore.name }}</h1>
          <p class="login-content">您已成功登录</p>
          <div class="button-group">
            <el-button type="primary" @click="goToAppView">进入</el-button>
            <el-button class="right-btn" @click="logout()">退出</el-button>
          </div>
        </div>
      </el-form>
    </div>
  </div>
</template>
<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { postFormLoginAxios, isNormalUserAccessApp } from '@/api/admin_user.js'
import NormalUserAfterLogin from '@/components/NormalUserAfterLogin.vue'
import { useTokenStore } from '@/stores/token.js'
import { useRouter } from 'vue-router'

// 判断是否登录
const tokenStore = useTokenStore()
const isLogin = ref(tokenStore.access_token ? true : false)

// role 为 admin 还是 user
const role = ref(tokenStore.role)
console.log('role:', role.value)
console.log(role.value === 'admin')

// 匿名箭头函数并直接调用
;(async () => {
  const result = await isNormalUserAccessApp()
  isLogin.value = result // 更新响应式变量
  if (!isLogin.value) {
    // 清空持久保存的用户数据
    tokenStore.token_type = ''
    tokenStore.access_token = ''
    tokenStore.username = ''
    tokenStore.name = ''
    tokenStore.role = ''
    // 更新响应式变量（控制界面响应）
    // isLogin.value = false
    role.value = ''
  }
})()

// 提供给admin_user"进入"按钮跳转函数
const router = useRouter()
const goToAppView = () => {
  router.push({
    name: 'app'
  })
}

const formRef = ref()
const form = reactive({
  username: '',
  password: ''
})

const formInputWidth = '240px'

const rules = reactive({
  username: [{ required: true, message: '请输入用户名字', trigger: 'blur' }],
  password: [
    { required: true, message: '请选择密码', trigger: 'blur' },
    {
      pattern: /^[A-Za-z0-9]+$/, // 只允许数字和字母
      message: '密码只能包含数字和字母',
      trigger: 'blur'
    }
  ]
})
const onSubmit = async (formRef) => {
  // 如果 formRef 不存在，直接返回，防止下面代码报错
  if (!formRef) return
  // 校验表单
  formRef.validate(async (valid) => {
    if (valid) {
      const response = await postFormLoginAxios({
        username: form.username,
        password: form.password
      })
      if (response.data.code === 0) {
        // 持久保存登录的用户信息
        tokenStore.token_type = response.data.data.token_type
        tokenStore.access_token = response.data.data.access_token
        tokenStore.username = form.username // 保存用户名, 登录表单的的第一行（不用后端返回）
        tokenStore.name = response.data.data.name // 保存姓名，用于显示欢迎信息
        tokenStore.role = response.data.data.role
        // 更新响应式变量（控制界面响应）
        isLogin.value = true
        role.value = tokenStore.role
        ElMessage.success('登录成功')
      } else {
        // response.data.code === 1
        ElMessage.error(response.data.message)
      }
    } else {
      ElMessage.error('登录失败')
    }
    // router.push({
    //   name: 'app'
    // })
  })
}

const logout = (message) => {
  if (isLogin.value) {
    // 清空持久保存的用户数据
    tokenStore.token_type = ''
    tokenStore.access_token = ''
    tokenStore.username = ''
    tokenStore.name = ''
    tokenStore.role = ''
    // 更新响应式变量（控制界面响应）
    isLogin.value = false
    role.value = ''
    // 如果没有传入 message 参数，显示默认提示信息
    if (message === undefined) {
      ElMessage.success('退出成功')
    } else {
      ElMessage.success(message)
    }
  } else {
    ElMessage.info('您还未登录')
  }
}
</script>
<style scoped>
.login-center-container {
  display: flex;
  justify-content: center; /* 水平居中 */
  align-items: center; /* 垂直居中 */
  height: 100%; /* 让容器占满整个视口高度 */
  width: 100%; /* 让容器占满整个视口宽度 */
  background-color: #f5f5f5; /* 可选，设置背景色以美化页面 */
  margin: 0; /* 清除默认的外边距 */
}

.login-box {
  background-color: #ffffff; /* 登录框背景颜色 */
  padding: 10px 30px 20px 30px; /* 增加填充 */
  border-radius: 10px; /* 圆角边框 */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* 增加阴影 */
  text-align: center; /* 文本居中 */
  width: 350px;
}

.login-title {
  font-size: 24px; /* 标题字体大小 */
  margin-bottom: 20px; /* 标题下方间距 */
}

/* 既是 <p> 元素又具有 login-content 类的元素 */
p.login-content {
  margin-bottom: 20px;
}

.el-form-item {
  margin-bottom: 20px; /* 表单项之间的间距 */
}

.el-button {
  padding: 0 25px;
}

.position-right {
  position: absolute;
  right: 0%;
}

.right-btn {
  background-color: #ff4d4f; /* 退出登录按钮颜色 */
  color: white; /* 按钮文字颜色 */
  border-color: #ff4d4f; /* 按钮边框颜色 */
}

.right-btn:hover {
  background-color: #ff7875; /* 按钮悬停颜色 */
  border-color: #ff7875; /* 按钮悬停边框颜色 */
}

.button-group {
  display: flex;
  justify-content: space-between;
  margin: 0 30px;
}
</style>
