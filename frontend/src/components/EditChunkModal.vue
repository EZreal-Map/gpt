<template>
  <!-- 编辑弹窗 -->
  <div class="modal">
    <div class="modal-content">
      <div class="modal-header">
        <span class="modal-title">编辑文档</span>
        <span class="close" @click="closeEditModal">&times;</span>
      </div>
      <div class="modal-title-filename">
        {{ currentItem.metadata.filename }}
      </div>
      <div class="modal-info">
        <div class="info-item">
          <span>编号: </span
          ><span
            >{{ currentItem.metadata.chunk_count }} /
            {{ currentItem.metadata.chunk_sum_num }}</span
          >
        </div>
        <div class="info-item">
          <span>ID: </span
          ><span>{{ currentItem.metadata.document_metadata_id }}</span>
        </div>
      </div>
      <div v-loading="isloading" element-loading-text="正在保存...">
        <el-input
          v-model="editContent"
          class="modal-input"
          :autosize="{ minRows: 4, maxRows: 20 }"
          type="textarea"
          placeholder="请输入内容"
        />
      </div>

      <div class="button-group">
        <button class="delete-button" @click="deleteEdit">删除</button>
        <button class="save-button" @click="saveEdit">保存</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  putEditChunkByMetadataIDAxios,
  deleteChunkByMetadataIDAxios
} from '@/api/dataset.js'

const props = defineProps({
  showEditModal: Boolean,
  currentItem: Object,
  documentChunks: Array
})

const emits = defineEmits(['update:showEditModal', 'update:documentChunks'])

const closeEditModal = () => {
  emits('update:showEditModal', false)
}

// 这里的 databaseID 不从路由获取，而是从 document.metadata.database_id 获取
const deleteChunkFunction = async (databaseID, article_id, metadata_id) => {
  try {
    // 设置查询参数
    const params = {
      article_id: article_id,
      metadata_id: metadata_id
    }
    // 发送 DELETE 请求，并传递查询参数
    const response = await deleteChunkByMetadataIDAxios(databaseID, params)
    // 处理成功响应
    console.log('删除成功:', response.data)
  } catch (error) {
    // 处理错误响应
    console.error('删除失败:', error)
    throw error
  }
}

const deleteEdit = () => {
  ElMessageBox.confirm('确认删除分段吗？', {
    confirmButtonText: '确定',
    cancelButtonText: '取消'
  })
    .then(async () => {
      if (props.currentItem) {
        // 数据库删除数据
        await deleteChunkFunction(
          props.currentItem.metadata.dataset_id,
          props.currentItem.metadata.article_id,
          props.currentItem.metadata.document_metadata_id
        )

        // 前端删除视图数据
        emits(
          'update:documentChunks',
          props.documentChunks.filter(
            (item) =>
              item.metadata.document_metadata_id !==
              props.currentItem.metadata.document_metadata_id
          )
        )
      }
      closeEditModal()
      ElMessage.success('删除成功')
    })
    .catch(() => {
      ElMessage.info('已取消删除')
    })
}

// 存储编辑文档内容，以便确定修改后，进行保存，而不是直接修改
const editContent = ref(props.currentItem.page_content)
const isloading = ref(false)

const saveEdit = async () => {
  if (props.currentItem) {
    isloading.value = true
    console.log('metadata_id:', props.currentItem.metadata.document_metadata_id)
    try {
      const response = await putEditChunkByMetadataIDAxios(
        props.currentItem.metadata.dataset_id,
        {
          page_content: editContent.value,
          metadata_id: props.currentItem.metadata.document_metadata_id
        }
      )
      console.log(response)
      if (response.status === 200) {
        ElMessage.success('保存成功')
        isloading.value = false
        closeEditModal()
        // 前端edit视图数据
        emits(
          'update:documentChunks',
          props.documentChunks.map((item) => {
            if (
              item.metadata.document_metadata_id ===
              props.currentItem.metadata.document_metadata_id
            ) {
              item.page_content = editContent.value
              item.metadata.chunk_word_count = editContent.value.length
              console.log(item.page_content)
            }
            return item
          })
        )
      } else {
        ElMessage.error('保存失败')
      }
    } catch (error) {
      console.error('Error updating chunk:', error)
      ElMessage.error('保存失败')
    }
  }
}
</script>

<style scoped>
/* 弹窗样式 */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  width: 600px;
  position: relative;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e5e5e5;
  padding-bottom: 10px;
}

.modal-title {
  font-size: 18px;
  font-weight: bold;
}

.modal-title-filename {
  font-size: 14px;
  color: #666;
}

.modal-info {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
}

.info-item {
  font-size: 14px;
}

.modal-input {
  width: 100%;
  margin-top: 10px;
}

.close {
  font-size: 24px;
  cursor: pointer;
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
  float: right;
}

.save-button:hover {
  background-color: #0056b3;
}

.delete-button {
  background-color: #dc3545;
  color: white;
  border: none;
  padding: 10px 20px;
  margin-top: 20px;
  cursor: pointer;
  border-radius: 4px;
}

.delete-button:hover {
  background-color: #c82333;
}
</style>
