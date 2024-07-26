<template>
  <div class="layout">
    <!-- 使用 router-view 插槽 -->
    <router-view v-slot="{ Component, route }">
      <!-- 如果当前路由没有 noLayout 元数据，则渲染公共布局 -->
      <el-container v-if="!route.meta.noLayout">
        <el-aside> <LeftAside></LeftAside> </el-aside>
        <el-main>
          <div class="app-main-container">
            <!-- 动态渲染当前路由对应的组件 -->
            <component :is="Component" />
          </div>
        </el-main>
      </el-container>
      <!-- 如果当前路由有 noLayout 元数据，则直接渲染当前路由对应的组件（为 /chat 独立布局） -->
      <component v-else :is="Component" />
    </router-view>
  </div>
</template>

<script setup>
import LeftAside from '@/components/LeftAside.vue'
</script>

<style scoped>
.layout {
  height: 100vh;
}
.el-aside {
  background-color: #f4f4f7;
  text-align: center;
  height: 100vh;
  width: 80px;
  padding: 20px 8px;
}

.el-main {
  display: flex;
  flex-direction: column;
  background-color: #f4f4f7;
  text-align: center;
  height: 100vh;
  padding: 0;
}

.app-main-container {
  border-radius: 20px; /* 设置边框圆角 */
  padding: 20px; /* 内边距 */
  margin: 20px; /* 外边距 */
  margin-left: 4px;
  background-color: #ffffff; /* 背景颜色 */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* 阴影效果 */
  flex: 1; /* 使子容器填充父容器的剩余空间 */
  box-sizing: border-box; /* 包含内边距和边框 */
  overflow: auto;
}
</style>
