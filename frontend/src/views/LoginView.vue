<template>
  <div class="center-container">
    <LoginComponent />
  </div>
</template>

<script setup>
import LoginComponent from '@/components/LoginComponent.vue'
</script>

<style scoped>
.center-container {
  display: flex;
  justify-content: center; /* 水平居中 */
  align-items: center; /* 垂直居中 */
  height: 100vh; /* 让容器占满整个视口高度 */
  background-color: #f5f5f5; /* 可选，设置背景色以美化页面 */
  margin: 0; /* 清除默认的外边距 */
}
</style>
