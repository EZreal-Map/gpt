<template>
  <div class="management">
    <el-transfer
      v-model="bindGroups"
      filterable
      :filter-method="filterMethod"
      filter-placeholder="查询"
      :titles="['未被添加的分组', '已被添加的分组']"
      :data="groupList"
      @change="rightDataChangeHandle"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import {
  getGroups,
  postGroupsAPPBind,
  getGroupsByAppid
} from '@/api/normal_user'
import { ElMessage } from 'element-plus'

// 使用 useRoute 获取路由信息
const route = useRoute()
const appID = route.params.appID

// 初始化分组列表
const groupList = ref([])
// 已绑定分组列表
const bindGroups = ref([])

const initGroup = async () => {
  // 获取已绑定分组列表
  bindGroups.value = (await getGroupsByAppid(appID)).data.data
  // 获取所有分组列表
  const data = (await getGroups()).data.data
  data.forEach((item) => {
    groupList.value.push({
      label: item,
      key: item
    })
  })
}
initGroup()

const filterMethod = (query, item) => {
  return item.label.includes(query)
}

const rightDataChangeHandle = async () => {
  // 已绑定分组会自动更新
  const response = await postGroupsAPPBind({
    groups: bindGroups.value,
    appid: appID
  })
  ElMessage.success(response.data.message)
}
</script>
<style scoped>
.management {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  background-color: #fefefe;
  border: 1px solid #d1d9e0;
  border-radius: 8px;
}

.el-transfer {
  --el-transfer-border-color: #d1d9e0;
  --el-transfer-panel-width: 400px;
  --el-transfer-panel-header-height: 60px;
  --el-transfer-panel-body-height: 600px;
  --el-transfer-item-height: 33px;
  --el-transfer-filter-height: 40px;
}
</style>
