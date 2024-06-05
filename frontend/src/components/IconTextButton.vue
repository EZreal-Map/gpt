<template>
  <div
    :class="['icon-text-button', { selected: isSelected }]"
    @click="navigate"
  >
    <div class="icon">
      <slot name="icon"></slot>
    </div>
    <div class="text">{{ text }}</div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  text: {
    type: String,
    required: true
  },
  route: {
    type: String,
    required: true
  },
  isSelected: {
    type: Boolean,
    default: false
  }
})

const router = useRouter()
const navigate = () => {
  router.push(props.route)
}
</script>

<style scoped>
.icon-text-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  padding: 8px;
  margin: 5px 5px 10px;
  border-radius: 10px;
  border: 1px solid transparent; /* 添加一个边框，避免边框样式在选中状态下的抖动 */
  transition: box-shadow 0.3s ease; /* 添加过渡效果 */
}

.icon-text-button.selected {
  background-color: #ffffff; /* 可以根据需要调整选中后的背景颜色 */
  border-color: #9fbacb; /* 可以根据需要调整选中后的边框颜色 */
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1); /* 调整阴影效果 */
}

.icon-text-button:hover {
  background-color: #ffffff; /* 悬停时的背景颜色 */
}

.icon {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 24px;
  height: 24px;
}

.icon-text-button.selected .text {
  color: #007bff; /* 可以根据需要调整选中后的文字颜色 */
}

.text {
  margin-top: 2px;
  font-size: 10px;
  font-weight: 700;
  color: #808080; /* 文字静止颜色 */
}
</style>
