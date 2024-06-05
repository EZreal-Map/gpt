<template>
  <div class="layout">
    <el-container>
      <el-aside> <LeftAside></LeftAside> </el-aside>
      <el-main>
        Main hhh
        <router-view></router-view>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import LeftAside from '@/components/LeftAside.vue'
</script>

<style scoped>
.el-aside {
  background-color: #f4f4f7;
  text-align: center;
  height: 100vh;
  width: 80px;
  padding: 8px;
}

.el-main {
  background-color: #e9eaec;
  color: #333;
  text-align: center;
  height: 100vh;
  padding: 0;
}
</style>
