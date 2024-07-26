import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useSettingStore = defineStore(
  'setting',
  () => {
    // 变量 通过返回函数修改
    const isSidebarVisible = ref(false) // 侧边栏显示与隐藏逻辑

    // 通过返回函数的方式修改
    const toggleSidebar = () => {
      isSidebarVisible.value = !isSidebarVisible.value
    }
    return {
      isSidebarVisible,
      toggleSidebar
    }
  },
  {
    persist: {
      paths: ['isSidebarVisible']
    }
  }
)
