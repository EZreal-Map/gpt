import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useTokenStore = defineStore(
  'token',
  () => {
    // 直接赋值，没有返回函数的方式修改
    const token_type = ref('')
    const access_token = ref('')
    const username = ref('')

    return {
      token_type,
      access_token,
      username
    }
  },
  {
    persist: {
      paths: ['username', 'token_type', 'access_token']
    }
  }
)
