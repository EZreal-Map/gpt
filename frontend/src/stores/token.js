import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useTokenStore = defineStore(
  'token',
  () => {
    // 直接赋值，没有返回函数的方式修改
    const token_type = ref('')
    const access_token = ref('')
    const username = ref('')
    const name = ref('')
    const role = ref('')

    return {
      token_type,
      access_token,
      username, // 用户名(admin的username和name是一样的，而普通用户的username是登录编号（id），name是姓名)
      name, // 姓名, 用于显示欢迎信息
      role
    }
  },
  {
    persist: {
      paths: ['username', 'token_type', 'access_token', 'role', 'name']
    }
  }
)
