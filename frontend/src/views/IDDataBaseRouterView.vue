<template>
  <div class="IDDataBaseRouterView">
    <div class="title-container">
      <div class="title-container-left">
        <h1 class="gradient-text">我的知识库</h1>
        <h1 class="dataset-dir" @click="backToDataBaseView">/dataset</h1>
        <h1 class="document-dir" @click="backToIDDataBaseDocumentView">
          /document
        </h1>
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
      <button class="update-document-button" @click="goToUpdateDocumentView">
        <el-icon><Plus /></el-icon>
        <span>上传文档</span>
      </button>
    </div>

    <div class="main-container">
      <router-view></router-view>
    </div>
  </div>
</template>

<script setup>
import { Plus } from '@element-plus/icons-vue'
import { useRoute, useRouter } from 'vue-router'
import { Document, Aim } from '@element-plus/icons-vue'
import { ref, computed, watch } from 'vue'

// 使用 useRoute 获取路由信息
const route = useRoute()
const databaseID = route.params.databaseID

// 使用 useRouter 获取 router 实例
const router = useRouter()

const backToDataBaseView = () => {
  router.push({ name: 'database' }) // 使用路由名称
}

// 回到上一级
const backToIDDataBaseDocumentView = () => {
  router.push({
    name: 'id-database-document',
    params: { databaseID: databaseID.value }
  }) // 使用路由名称
}

const goToUpdateDocumentView = () => {
  router.push({
    name: 'id-database-document-update',
    params: { databaseID: databaseID.value }
  }) // 使用路由名称
}

const menuItems = [
  {
    text: '文档集合',
    route: { name: 'id-database-document', params: { databaseID } },
    icon: Document
  },
  {
    text: '召回测试',
    route: { name: 'id-database-hit-testing', params: { databaseID } },
    icon: Aim
  }
]

const currentRoute = ref(route.path)

const isSelected = (itemRoute) => {
  const itemRouteUrl = router.resolve(itemRoute).href
  // 检查当前路由是否以指定路径开头
  return computed(() => route.path.startsWith(itemRouteUrl)).value
}
const getIconColor = (itemRoute) => {
  return computed(() => (isSelected(itemRoute) ? '#007bff' : '#808080')).value
}

// 监听路由变化
watch(
  () => route.path,
  (newPath) => {
    currentRoute.value = newPath
  }
)
</script>

<style scoped>
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

.title-container-left .dataset-dir {
  margin: 0 10px 0 50px; /* 设置图标与文字之间的间距 */
  cursor: pointer;
}

.title-container-left .document-dir {
  cursor: pointer;
}

.title-container-left .dataset-dir:hover,
.title-container-left .document-dir:hover {
  background-color: #f0f0f0; /* 添加悬停时的背景色 */
  transition: background-color 0.3s ease; /* 添加过渡效果 */
}

.title-container-center {
  display: flex; /* 设置为 flex 布局 */
  align-items: center; /* 垂直居中 */
}
/* 按钮样式 */
.update-document-button {
  padding: 10px 20px;
  font-size: 14px;
  background-color: #ffffff;
  color: #007bff;
  border: 1px solid #007bff;
  border-radius: 8px;
  cursor: pointer;
  margin-right: 30px;
  display: flex; /* 将按钮设置为 flex 布局 */
  align-items: center; /* 垂直居中 */
  transition: background-color 0.3s ease; /* 添加过渡效果 */
}

.update-document-button:hover {
  background-color: #e6ecfc;
  border-color: #0056b3; /* 修改边框颜色 */
}

/* 渐变文字效果 */
.gradient-text {
  background: linear-gradient(to right, #007bff, #0056b3); /* 设置背景渐变 */
  background-clip: text; /* 使用背景裁剪文字 */
  color: transparent; /* 使文字颜色透明 */
}

/* 图标样式  '+' 与 '新增' 的间隔*/
.update-document-button .el-icon {
  margin-right: 4px;
}

h1 {
  display: inline-block; /* 将元素呈现为行内块元素 */
}

.IDDataBaseRouterView {
  display: flex;
  flex-direction: column; /* 垂直方向排列子元素 */
  height: 100%; /* 确保容器占据整个可视区域 */
}

.main-container {
  flex: 1; /* 占据父元素的剩余空间 */
}
</style>
