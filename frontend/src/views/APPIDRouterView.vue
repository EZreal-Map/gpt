<template>
  <div class="APPIDRouterView">
    <div class="title-container">
      <div class="title-container-left">
        <h1 class="gradient-text" @click="backToDataBaseView">我的应用</h1>
      </div>

      <div class="title-container-center">
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
      <div></div>
    </div>

    <div class="main-container">
      <router-view></router-view>
    </div>
  </div>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import IconTextButton from '@/components/IconTextButton.vue'
import { Document, Link } from '@element-plus/icons-vue'
import { computed } from 'vue'

// 使用 useRoute 获取路由信息
const route = useRoute()
const appID = route.params.appID

// 使用 useRouter 获取 router 实例
const router = useRouter()

const backToDataBaseView = () => {
  router.push({ name: 'app' }) // 使用路由名称
}

const menuItems = [
  {
    text: '简易配置',
    route: { name: 'id-app-configuration', params: { appID } },
    icon: Document
  },
  {
    text: '发布链接',
    route: { name: 'chat', params: { appID } },
    icon: Link
  }
  // {
  //   text: '发布应用',
  //   route: { name: 'id-app-publish', params: { appID } },
  //   icon: Link
  // }
]

// const currentRoute = ref(route.path)

const isSelected = (itemRoute) => {
  console.log(itemRoute)
  const itemRouteUrl = router.resolve(itemRoute).href
  console.log(itemRouteUrl)
  // 检查当前路由是否以指定路径开头
  return computed(() => route.path.startsWith(itemRouteUrl)).value
}
const getIconColor = (itemRoute) => {
  return computed(() => (isSelected(itemRoute) ? '#007bff' : '#808080')).value
}

// 监听路由变化
// watch(
//   () => route.path,
//   (newPath) => {
//     currentRoute.value = newPath
//   }
// )
</script>

<style scoped>
.APPIDRouterView {
  display: flex;
  flex-direction: column; /* 垂直方向排列子元素 */
  height: 100%; /* 确保容器占据整个可视区域 */
}

.main-container {
  flex: 1; /* 占据父元素的剩余空间 */
}
/* Flex容器 */
.title-container {
  display: flex;
  justify-content: space-between; /* 左右布局，元素之间的空间 */
  align-items: center; /* 垂直居中 */
}

.title-container-left {
  display: flex; /* 设置为 flex 布局 */
  align-items: center; /* 垂直居中 */
}

.title-container-center {
  display: flex; /* 设置为 flex 布局 */
  align-items: center; /* 垂直居中 */
}

/* 渐变文字效果 */
.gradient-text {
  background: linear-gradient(to right, #007bff, #0056b3); /* 设置背景渐变 */
  background-clip: text; /* 使用背景裁剪文字 */
  color: transparent; /* 使文字颜色透明 */
  cursor: pointer;
}
</style>
