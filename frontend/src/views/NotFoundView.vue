<template>
  <div class="not-found-container">
    <h1>404 - Not Found</h1>
    <p>Sorry, the page you are looking for does not exist.</p>
    <button @click="redirectToHome">Go to Login</button>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()

const redirectToHome = () => {
  // 进行页面导航
  router.push({ name: 'account' })
}
</script>

<style scoped>
/* 添加样式以美化界面 */
.not-found-container {
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
