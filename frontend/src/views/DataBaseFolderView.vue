<template>
  <div class="title-container">
    <h1 class="gradient-text">我的知识库</h1>
    <button class="new-button">
      <el-icon><Plus /></el-icon>
      <span>新建</span>
    </button>
  </div>

  <div class="main-container" ref="tableContainer">
    <DataBaseBox
      v-for="item in data"
      :key="item.databaseID"
      :databaseID="item.databaseID"
      v-model:title="item.title"
      v-model:description="item.description"
      v-model:privacy="item.privacy"
    ></DataBaseBox>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import DataBaseBox from '@/components/DataBaseBox.vue'
const data = ref([
  {
    databaseID: 'fewaiojifaowhouo1',
    title: '我的知识库1',
    description: '这是一个描述1',
    privacy: '私有1'
  },
  {
    databaseID: 'fewaiojifaowhouo2',
    title: '我的知识库2',
    description: '这是一个描述2',
    privacy: '私有'
  },
  {
    databaseID: 'fewaiojifaowhouo3',
    title: '我的知识库',
    description: '这是一个描述3',
    privacy: '私有'
  },
  {
    databaseID: 'fewaiojifaowhouo4',
    title: '我的知识库',
    description: '这是一个描述4',
    privacy: '私有'
  },
  {
    databaseID: 'fewaiojifaowhouo5',
    title: '我的知识库',
    description: '这是一个描述',
    privacy: '私有'
  },
  {
    databaseID: 'fewaiojifaowhouo6',
    title: '我的知识库',
    description: '这是一个描述',
    privacy: '私有'
  },
  {
    databaseID: 'fewaiojifaowhouo7',
    title: '我的知识库',
    description: '这是一个描述',
    privacy: '私有'
  },
  {
    databaseID: 'fewaiojifaowhouo8',
    title: '我的知识库',
    description: '这是一个描述',
    privacy: '私有'
  },
  {
    databaseID: 'fewaiojifaowhouo5',
    title: '我的知识库',
    description: '这是一个描述',
    privacy: '私有'
  },
  {
    databaseID: 'fewaiojifaowhouo6',
    title: '我的知识库',
    description: '这是一个描述',
    privacy: '私有'
  },
  {
    databaseID: 'fewaiojifaowhouo7',
    title: '我的知识库',
    description: '这是一个描述',
    privacy: '私有'
  },
  {
    databaseID: 'fewaiojifaowhouo8',
    title: '我的知识库',
    description: '这是一个描述',
    privacy: '私有'
  },
  {
    databaseID: 'fewaiojifaowhouo5',
    title: '我的知识库',
    description: '这是一个描述',
    privacy: '私有'
  },
  {
    databaseID: 'fewaiojifaowhouo6',
    title: '我的知识库',
    description: '这是一个描述',
    privacy: '私有'
  },
  {
    databaseID: 'fewaiojifaowhouo7',
    title: '我的知识库',
    description: '这是一个描述',
    privacy: '私有'
  },
  {
    databaseID: 'fewaiojifaowhouo8',
    title: '我的知识库',
    description: '这是一个描述',
    privacy: '私有'
  },
  {
    databaseID: 'fewaiojifaowhouo5',
    title: '我的知识库',
    description: '这是一个描述',
    privacy: '私有'
  },
  {
    databaseID: 'fewaiojifaowhouo6',
    title: '我的知识库',
    description: '这是一个描述',
    privacy: '私有'
  },
  {
    databaseID: 'fewaiojifaowhouo7',
    title: '我的知识库',
    description: '这是一个描述',
    privacy: '私有'
  },
  {
    databaseID: 'fewaiojifaowhouo8',
    title: '我的知识库',
    description: '这是一个描述',
    privacy: '私有'
  },
  {
    databaseID: 'fewaiojifaowhouo5',
    title: '我的知识库',
    description: '这是一个描述',
    privacy: '私有'
  },
  {
    databaseID: 'fewaiojifaowhouo6',
    title: '我的知识库',
    description: '这是一个描述',
    privacy: '私有'
  },
  {
    databaseID: 'fewaiojifaowhouo7',
    title: '我的知识库',
    description: '这是一个描述',
    privacy: '私有'
  },
  {
    databaseID: 'fewaiojifaowhouo8',
    title: '我的知识库',
    description: '这是一个描述',
    privacy: '私有'
  }
])

// 滚动条位置设置
const tableContainer = ref(null)

onMounted(() => {
  calculateMaxHeight()
  window.addEventListener('resize', calculateMaxHeight)
})

const calculateMaxHeight = () => {
  const windowHeight = window.innerHeight
  const tableContainerOffsetTop = tableContainer.value.offsetTop
  const tableContainerMaxHeight = windowHeight - tableContainerOffsetTop - 70 // 70为额外留白，可根据实际情况调整
  tableContainer.value.style.maxHeight = `${tableContainerMaxHeight}px`
}
</script>
<style scoped>
/* Flex容器 */
.title-container {
  display: flex;
  justify-content: space-between; /* 左右布局，元素之间的空间 */
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
.el-icon {
  margin-right: 4px;
}

.main-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  grid-gap: 20px;
  overflow: auto; /* 当内容溢出时显示滚动条 */
}
</style>
