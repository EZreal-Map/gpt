import qs from 'qs' // 引入 qs 库，用于序列化表单数据
import request from '@/utils/request'

//  Account.vue
// 用户登录
export const postFormLoginAxios = ({ username, password }) => {
  return request.post('/login', qs.stringify({ username, password }), {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  })
}

// 判断用户是否登录，比直接判断是否保存userStore.username为空要更加准确，因为后端可以多判断token是否过期
export const checkIsLogin = async () => {
  // 响应拦截器自动添加
  // headers.Authorization = `${tokenStore.token_type} ${tokenStore.access_token}`
  const response = await request.get('/login')
  return response.data.is_login
}
