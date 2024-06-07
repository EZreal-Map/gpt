<template>
  <div class="title-container">
    <div class="title-container-left">
      <h1 class="gradient-text">我的知识库</h1>
      <el-icon size="35" @click="backToIDDataBaseDocumentView(databaseID)"
        ><Back
      /></el-icon>
      <h1>/</h1>
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
    <button class="new-button">
      <el-icon><Plus /></el-icon>
      <span>新建</span>
    </button>
  </div>

  <div class="main-container">
    <router-view></router-view>
  </div>
</template>

<script setup>
import { Plus, Back } from '@element-plus/icons-vue'
import { useRoute, useRouter } from 'vue-router'
import { Document, Aim, Setting } from '@element-plus/icons-vue'
import { ref, computed, watch } from 'vue'

// 使用 useRoute 获取路由信息
const route = useRoute()

// 使用 useRouter 获取 router 实例
const router = useRouter()

// 回到上一级
const backToIDDataBaseDocumentView = (databaseID) => {
  router.push({
    name: 'id-database-document',
    params: { databaseID: databaseID }
  }) // 使用路由名称
}

// 获取路由参数 id
const databaseID = route.params.databaseID

const menuItems = [
  {
    text: '文档',
    route: { name: 'id-database-document', params: { databaseID } },
    icon: Document
  },
  {
    text: '召回测试',
    route: { name: 'id-database-hit-testing', params: { databaseID } },
    icon: Aim
  },
  {
    text: '设置',
    route: { name: 'id-database-setting', params: { databaseID } },
    icon: Setting
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

.title-container-left .el-icon {
  margin: 0 10px 0 50px; /* 设置图标与文字之间的间距 */
  cursor: pointer;
}

.title-container-center {
  display: flex; /* 设置为 flex 布局 */
  align-items: center; /* 垂直居中 */
}
/* 按钮样式 */
.new-button {
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

.new-button:hover {
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
.new-button .el-icon {
  margin-right: 4px;
}

h1 {
  display: inline-block; /* 将元素呈现为行内块元素 */
}
</style>
