<template>
  <div class="layout">
    <el-container>
      <el-aside> <LeftAside></LeftAside> </el-aside>
      <el-main>
        <div class="main-container">
          <router-view></router-view>
        </div>
      </el-main>
    </el-container>
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

.main-container {
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
