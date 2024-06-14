// import { useUserStore } from '@/stores/user'
import axios from 'axios'
import { ElMessage } from 'element-plus'
// import router from '@/router'

const baseURL = 'http://127.0.0.1:7979'
// const baseURL = '/api'

const instance = axios.create({
  baseURL, // TODO 1. 基础地址，超时时间
  timeout: 100000
})

// 请求拦截器
instance.interceptors.request.use(
  (config) => {
    // const userStore = useUserStore()
    // if (userStore.Token) {
    //   config.headers.Authorization = `${userStore.Token.token_type} ${userStore.Token.access_token}` // TODO 2. 携带token
    // }
    return config
  },
  (err) => Promise.reject(err)
)

// 响应拦截器
instance.interceptors.response.use(
  (response) => {
    return response
    // return Promise.reject(res.data)
  },
  (err) => {
    // 输出错误信息到控制台
    // const userStore = useUserStore()
    // 根据状态码进行特定处理
    if (err.response?.status === 400) {
      // 处理400错误，例如显示错误提示
      ElMessage({ message: '身份验证错误', type: 'error' })
    } else if (err.response?.status === 401) {
      // 处理401错误，例如跳转到登录页
      // userStore.LoginVisibility = true
      // router.push('/blog')
      ElMessage({ message: '无权限访问', type: 'error' })
    } else if (err.response?.status === 422) {
      // 处理403错误，例如提示用户无权限
      ElMessage({ message: '保存失败', type: 'error' })
    } else if (err.response?.status === 404) {
      // 处理404错误，例如显示页面不存在提示
      // router.push('/blog/not-found')
      ElMessage({ message: '文章不存在', type: 'error' })
    } else if (err.response?.status === 500) {
      // 处理500错误，例如显示服务端错误提示
      ElMessage({ message: '服务器错误', type: 'error' })
    }

    return Promise.reject(err)
  }
)

export default instance
export { baseURL }
