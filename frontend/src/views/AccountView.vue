<template>
  <div class="account-view">
    <div class="login-box">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="60px">
        <div v-if="!isLogin">
          <h1 class="login-title">登录窗口</h1>
          <el-form-item label="用户名" prop="username">
            <el-input
              v-model="form.username"
              placeholder="请输入用户名"
              @keydown.enter="onSubmit(formRef)"
            />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input
              v-model="form.password"
              placeholder="请输入密码"
              type="password"
              @keydown.enter="onSubmit(formRef)"
            />
          </el-form-item>
          <div class="button-group">
            <el-button type="primary" @click="onSubmit(formRef)"
              >确定</el-button
            >
            <el-button class="right-btn" @click="logout">登出</el-button>
          </div>
        </div>
        <div v-else>
          <h1 class="login-title">欢迎, {{ tokenStore.username }}</h1>
          <p class="login-content">您已成功登录</p>
          <div class="button-group">
            <el-button type="primary" @click="onSubmit(formRef)"
              >确定</el-button
            >
            <el-button class="right-btn" @click="logout">登出</el-button>
          </div>
        </div>
      </el-form>
    </div>
  </div>
</template>
<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { postFormLoginAxios, checkIsLogin } from '@/api/user.js'
import { useTokenStore } from '@/stores/token.js'
import { useRouter } from 'vue-router'

const router = useRouter()
const tokenStore = useTokenStore()

const isLogin = ref(tokenStore.token_type ? true : false)

// 匿名箭头函数并直接调用
;(async () => {
  const result = await checkIsLogin()
  isLogin.value = result // 更新响应式变量
})()

const validateUsername = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请输入用户名'))
  }
  callback()
}

const validatePassword = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请输入密码'))
  }
  callback()
}

const formRef = ref()
// do not use same name with ref
const form = reactive({
  username: '',
  password: ''
})

const rules = reactive({
  username: [{ validator: validateUsername, trigger: 'blur' }],
  password: [{ validator: validatePassword, trigger: 'blur' }]
})

const onSubmit = async (formRef) => {
  if (!formRef) return
  if (!isLogin.value) {
    formRef.validate(async (valid) => {
      if (valid) {
        const response = await postFormLoginAxios({
          username: form.username,
          password: form.password
        })
        ElMessage.success('登录成功')
        tokenStore.token_type = response.data.token_type
        tokenStore.access_token = response.data.access_token
        tokenStore.username = form.username
        isLogin.value = true
      } else {
        ElMessage.error('登录失败')
      }
    })
  } else {
    router.push({
      name: 'app'
    })
  }
}

const logout = () => {
  tokenStore.token_type = ''
  tokenStore.access_token = ''
  ElMessage.success('登出成功')
  isLogin.value = false
}
</script>
<style scoped>
.account-view {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
}

.login-box {
  background-color: #ffffff; /* 登录框背景颜色 */
  padding: 10px 30px 20px 30px; /* 增加填充 */
  border-radius: 10px; /* 圆角边框 */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* 增加阴影 */
  text-align: center; /* 文本居中 */
  width: 300px;
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
  background-color: #ff4d4f; /* 登出按钮颜色 */
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
