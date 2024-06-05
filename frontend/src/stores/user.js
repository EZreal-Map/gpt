import { ref } from 'vue'
import { defineStore } from 'pinia'
import { ElMessage } from 'element-plus'

export const useUserStore = defineStore(
  'user',
  () => {
    // 直接赋值，没有返回函数的方式修改
    const LoginVisibility = ref(false) // 登录框是否显示
    const Nickname = ref('')
    const Email = ref(null)
    const Edit = ref(false) // 是否是编辑状态
    const EditIconDisabled = ref(true) // 是否 Disabled 编辑图标
    const Role = ref('')
    const Token = ref('')

    const LogoutHandle = () => {
      Role.value = ''
      Nickname.value = ''
      Email.value = ''
      Token.value = ''
      LoginVisibility.value = false
      Edit.value = false
      EditIconDisabled.value = true
      LoginVisibility.value = false
      ElMessage.success('退出成功')
    }
    return {
      LoginVisibility,
      Nickname,
      Email,
      Edit,
      EditIconDisabled,
      Role,
      Token,
      LogoutHandle
    }
  },
  {
    persist: {
      paths: ['Nickname', 'Email', 'Role', 'Token']
    }
  }
)
