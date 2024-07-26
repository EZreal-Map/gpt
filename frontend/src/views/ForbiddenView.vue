<template>
  <div class="forbidden-container">
    <h1>403 - Forbidden</h1>
    <p>Access denied. You are not authorized to access this resource.</p>
    <button @click="goToLogin">Go to Login</button>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
// 使用 Vue Router 的 useRouter 进行页面跳转
const router = useRouter()

const goToLogin = () => {
  router.push({ name: 'account' }) // 跳转到登录页面，'account' 是你路由中登录页面的名称
}
</script>

<style scoped>
.forbidden-container {
  text-align: center;
  margin-top: 50px;
}

h1 {
  font-size: 2em;
  color: #333;
}

p {
  color: #555;
  margin-bottom: 20px;
}

button {
  background-color: #007bff;
  color: #fff;
  padding: 10px 20px;
  font-size: 1em;
  border: none;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

button:hover {
  background-color: #0056b3;
}
</style>
