<template>
  <el-table :data="groupList">
    <el-table-column property="group_name" label="分组名称" sortable />
    <el-table-column property="user_count" label="分组人数" sortable />
    <el-table-column fixed="right" label="操作" width="100">
      <template #default="scope">
        <el-button
          link
          type="primary"
          size="small"
          @click="deleteGroupHandle(scope.row.id)"
        >
          删除
        </el-button>
        <el-button
          link
          type="primary"
          size="small"
          @click="updateGroupHandle(scope.row.id)"
        >
          修改</el-button
        >
      </template>
    </el-table-column>
  </el-table>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getGroupsUserCount,
  updateGroupName,
  deleteGroup
} from '@/api/normal_user'

const groupList = ref([])

const initGroupCountList = async () => {
  const res = await getGroupsUserCount()
  groupList.value = res.data.data
}
initGroupCountList()

const updateGroupHandle = async (group_id) => {
  try {
    // 弹出框输入新的分组名
    const { value } = await ElMessageBox.prompt('请输入新的分组名', '修改', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPattern: /^(?!\s*$).+/,
      inputErrorMessage: '不能为空'
    })
    // 调用 API 更新分组名
    const response = await updateGroupName({
      group_id: group_id,
      newname: value
    })
    // 更新分组列表
    initGroupCountList()
    // 根据返回的结果显示不同的提示信息
    if (response.data.code === 0) {
      ElMessage.success(response.data.message)
    } else {
      ElMessage.error(response.data.message)
    }
  } catch (error) {
    // 如果发生错误或用户取消了输入
    ElMessage({
      type: 'info',
      message: '取消修改'
    })
  }
}

const deleteGroupHandle = async (group_id) => {
  // 弹出确认框
  ElMessageBox.confirm(
    '此操作将永久删除该分组及仅与该分组唯一关联的全部用户，删除后无法恢复，是否继续？',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )
    .then(async () => {
      // 调用 API 删除分组
      const response = await deleteGroup(group_id)
      // 更新分组列表
      initGroupCountList()
      // 根据返回的结果显示不同的提示信息
      if (response.data.code === 0) {
        ElMessage.success(response.data.message)
      } else {
        ElMessage.error(response.data.message)
      }
    })
    .catch(() => {
      // 用户取消删除操作
      ElMessage({
        type: 'info',
        message: '已取消删除'
      })
    })
}
</script>
<style scoped></style>
