<template>
  <div class="aside-top-avater" @click="navigateToAccount">
    <el-avatar :size="50" :src="userImageUrl" />
  </div>
  <div class="aside-middle-menu">
    <IconTextButton
      v-for="item in menuItems"
      :key="item.route"
      :text="item.text"
      :route="item.route"
      :isSelected="isSelected(item.route)"
    >
      <template #icon>
        <el-icon :size="24" :color="getIconColor(item.route)">
          <component :is="item.icon" />
        </el-icon>
      </template>
    </IconTextButton>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import IconTextButton from '@/components/IconTextButton.vue'
import { Promotion, Coin, UserFilled } from '@element-plus/icons-vue'
import { useRoute, useRouter } from 'vue-router'

const userImageUrl = ref(
  'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
)
const route = useRoute()
const router = useRouter()
const currentRoute = ref()

const navigateToAccount = () => {
  router.push('/account')
}

const menuItems = [
  { text: '应用', route: '/app', icon: Promotion },
  { text: '知识库', route: '/database', icon: Coin },
  { text: '账号', route: '/account', icon: UserFilled }
]

const isSelected = (itemRoute) =>
  computed(() => currentRoute.value === itemRoute).value
const getIconColor = (route) =>
  computed(() => (currentRoute.value === route ? '#007bff' : '#808080')).value

// 监听路由变化
watch(
  () => route.path,
  (newPath) => {
    currentRoute.value = newPath
  }
)
</script>

<style scoped>
.aside-top-avater {
  cursor: pointer;
  margin: 10px 0px 40px;
}
</style>
