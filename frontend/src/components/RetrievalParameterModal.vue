<template>
  <!-- 设置模型参数弹窗 -->
  <div class="document-modal-background" v-if="showRetrievalSettingModel">
    <div class="document-modal">
      <!-- 弹窗 title -->
      <div class="document-modal-header">
        <span class="document-modal-title">设置参数</span>
        <span class="document-model-close" @click="cancelSelectionAndSubmit"
          >&times;</span
        >
      </div>
      <!-- 弹窗 content -->
      <div class="ai-setting-model-content">
        <!-- 1、搜索模式的选择 -->
        <div>
          <div class="left">搜索模式</div>
          <div class="right">
            <el-select v-model="localSearchMode" placeholder="请选择">
              <el-option label="语义检索" value="语义检索"></el-option>
              <el-option label="关键词检索" value="关键词检索"></el-option>
            </el-select>
          </div>
        </div>
        <!-- 2、引用个数的设置 -->
        <div>
          <div class="left">引用个数</div>
          <div class="right">
            <el-slider
              v-model="localCitationLimit"
              :min="0"
              :max="20"
            ></el-slider>
          </div>
        </div>
        <!-- 3、最低相关度的设置 -->
        <div>
          <div class="left">最低相关度</div>
          <div class="right">
            <el-slider
              v-model="localMinRelevance"
              :min="0"
              :max="100"
              :format-tooltip="formatTooltip"
            ></el-slider>
          </div>
        </div>
        <!-- 4、模型上下文记录聊天记录数量（history_window_length） -->
        <div>
          <div class="left">问题优化</div>
          <div class="right">
            <el-select
              v-model="localQuestionOptimization"
              placeholder="请选择"
              style="width: 100%"
            >
              <el-option label="是" value="✓"></el-option>
              <el-option label="否" value="×"></el-option>
            </el-select>
          </div>
        </div>
      </div>
      <!-- 弹窗 footer -->
      <div class="button-group">
        <div></div>
        <button
          class="save-button"
          @click="
            finishRetrievalParameterModalSelectionAndSubmit(
              localSearchMode,
              localCitationLimit,
              localMinRelevance,
              localQuestionOptimization
            )
          "
        >
          完成
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

// defineProps 接收父组件传递的数据并设置默认值
const props = defineProps({
  showRetrievalSettingModel: {
    type: Boolean,
    default: false
  },
  searchMode: {
    type: String,
    default: '语义检索'
  },
  citationLimit: {
    type: Number,
    default: 4
  },
  minRelevance: {
    type: Number,
    default: 50
  },
  questionOptimization: {
    type: String,
    default: '×'
  },
  finishRetrievalParameterModalSelectionAndSubmit: Function
})

// defineEmits 定义组件的事件
const emits = defineEmits(['update:showRetrievalSettingModel'])

// 设置检索参数弹出框有关参数
const localSearchMode = ref(props.searchMode)
const localCitationLimit = ref(props.citationLimit)
const localMinRelevance = ref(props.minRelevance)
const localQuestionOptimization = ref(props.questionOptimization)

const formatTooltip = (value) => {
  return (value / 100).toFixed(2)
}

// 当点击取消更改按钮的时候，关闭弹窗（modal），初始化还原
const cancelSelectionAndSubmit = () => {
  // 关闭弹窗（modal）
  emits('update:showRetrievalSettingModel', false)
  // 初始化还原
  localSearchMode.value = props.searchMode
  localCitationLimit.value = props.citationLimit
  localMinRelevance.value = props.minRelevance
  localQuestionOptimization.value = props.questionOptimization
}

// 因为使用了local变量，无法响应式接收props
// 如果弹窗（modal）显示，需要再重新初始化弹窗（modal）参数
watch(
  () => props.showRetrievalSettingModel,
  (newVal) => {
    if (newVal) {
      // 初始化弹窗（modal）参数
      localSearchMode.value = props.searchMode
      localCitationLimit.value = props.citationLimit
      localMinRelevance.value = props.minRelevance
      localQuestionOptimization.value = props.questionOptimization
    }
  }
)
</script>

<style scoped>
/* 全屏模态弹窗 */
.document-modal-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5); /* 半透明黑色背景 */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1;
}

.document-modal {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  width: 100%;
  position: relative;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  width: 400px; /* 调整弹窗宽度 */
  max-width: 90%; /* 限制最大宽度 */
  max-height: 90%; /* 限制最大高度 */
}

.document-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e5e5e5;
  padding-bottom: 10px;
  margin-bottom: 10px;
}

.document-modal-title {
  font-size: 18px;
  font-weight: bold;
}

.document-modal-content {
  width: 100%;
  margin-top: 10px;
  text-align: left;
}

.document-model-close {
  font-size: 24px;
  cursor: pointer;
}

.ai-setting-model-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ai-setting-model-content > div {
  display: flex;
  align-items: center;
}

.ai-setting-model-content .left {
  flex: 0 0 120px; /* 调整标签的宽度 */
  color: #1f212a;
  text-align: center;
  padding-right: 10px;
}

.ai-setting-model-content .right {
  flex: 1;
  margin-right: 20px;
}

.button-group {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.save-button {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 10px 20px;
  margin-top: 20px;
  cursor: pointer;
  border-radius: 4px;
}

.save-button:hover {
  background-color: #0056b3;
}
</style>
