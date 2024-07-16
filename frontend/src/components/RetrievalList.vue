<template>
  <div class="test-result-container">
    <div class="test-result-header">
      <el-tooltip
        content="通过计算向量之间的距离获取得分，范围为 0~1"
        placement="top"
        effect="light"
      >
        #{{ index + 1 }} | 语义检索 - {{ result.score.toFixed(4) }}
      </el-tooltip>
    </div>
    <div class="test-result-body">
      {{ result.page_content }}
    </div>
    <div class="test-result-footer">
      <div class="test-result-footer-left">
        <el-tooltip content="点击下载源文件" placement="bottom" effect="light">
          <span>{{ result.metadata.filename }}</span>
        </el-tooltip>
        <el-tooltip
          content="文件内文段编号/总文段数"
          placement="bottom"
          effect="light"
        >
          <span
            >{{ result.metadata.chunk_count }}/{{
              result.metadata.chunk_sum_num
            }}</span
          >
        </el-tooltip>
        <el-tooltip content="引用内容长度" placement="bottom" effect="light">
          <span>{{ result.metadata.chunk_word_count }}</span>
        </el-tooltip>
      </div>
      <span class="edit-icon" @click="editBox(result)">编辑</span>
    </div>
  </div>
</template>

<script setup>
// import { ref } from 'vue'

// 从父组件接收的props
const props = defineProps({
  result: Object,
  editBox: Function,
  index: Number
})

console.log(props)
</script>

<style scoped>
/* 测试结果容器样式 */
.test-result-container {
  background-color: #ffffff; /* 白色背景 */
  border: 1px solid #ddd; /* 细边框 */
  border-radius: 8px; /* 圆角边框 */
  padding: 15px; /* 内边距 */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* 浅阴影 */
  margin-bottom: 20px; /* 底部间距 */
}

/* 测试结果头部样式 */
.test-result-header {
  background-color: #f0f0f0; /* 淡灰色背景 */
  color: #333; /* 深灰色文字 */
  font-weight: bold;
  font-size: 16px;
  padding: 10px;
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
}

/* 测试结果主体样式 */
.test-result-body {
  font-size: 14px;
  line-height: 1.6;
  color: #666; /* 灰色文字 */
  margin-top: 10px;
}

/* 测试结果底部样式 */
.test-result-footer {
  position: relative; /* 相对定位，为绝对定位的参考点 */
  font-size: 12px;
  color: #999; /* 浅灰色文字 */
  padding-top: 10px;
  border-top: 1px solid #ddd; /* 顶部边框分隔线 */
  margin-top: 10px;
}

/* 测试结果底部内部元素样式 */
.test-result-footer span {
  margin-right: 10px; /* 右侧间距 */
}

.test-result-footer span:hover {
  color: #007bff; /* 蓝色文字 */
  cursor: pointer; /* 鼠标指针 */
}

/* 测试结果底部左侧文字部分，加一个margin-right防止与编辑 button 文字重叠 */
.test-result-footer-left {
  margin-right: 50px;
}

.edit-icon {
  display: none; /* 默认隐藏 */
}

.test-result-container:hover .edit-icon {
  display: inline-block; /* 悬停时显示 */
}

.edit-icon {
  position: absolute; /* 绝对定位 */
  top: 50%; /* 垂直居中 */
  right: 10px; /* 距离右侧的位置 */
  color: #999; /* 蓝色文字 */
  cursor: pointer; /* 鼠标指针 */
}
</style>
