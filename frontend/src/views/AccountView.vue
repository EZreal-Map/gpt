<template>
  <div class="account-view">
    <div class="table-content">
      <div class="table-bar">
        <div class="table-bar-left">
          <label style="margin-right: 10px">查询姓名：</label>
          <el-input
            v-model="QueryNameString"
            placeholder="请输入查询姓名"
            style="width: 15%"
            clearable
            @clear="initTable"
            @keyup.enter="initTable"
          />
          <label style="margin-right: 5px; margin-left: 20px">查询分组：</label>
          <el-select
            v-model="QueryGroupString"
            placeholder="请选择查询分组"
            clearable
            style="width: 15%"
            @clear="initTable"
          >
            <el-option
              v-for="group in groupList"
              :key="group"
              :label="group"
              :value="group"
            />
          </el-select>
          <el-button type="primary" style="margin-left: 20px" @click="initTable"
            >查询</el-button
          >
        </div>
        <div class="table-bar-right">
          <el-button type="primary" @click="dialogCreateFormVisible = true">
            + 新增用户
          </el-button>
          <el-upload
            :action="postUploadFileURL()"
            :headers="{
              Authorization: `${tokenStore.token_type} ${tokenStore.access_token}`
            }"
            :before-upload="beforeUpload"
            :on-success="successUpload"
            :show-file-list="false"
          >
            <el-button type="primary" style="margin-left: 20px">
              + 批量添加</el-button
            >
          </el-upload>
        </div>
      </div>

      <el-table :data="userList" @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="50" />
        <el-table-column property="user_id" label="学号" width="200" sortable />
        <el-table-column property="name" label="姓名" width="200" sortable />
        <el-table-column property="groups" label="分组" sortable />
        <el-table-column property="updated_at" label="更新时间" sortable />
        <el-table-column fixed="right" label="操作" width="100">
          <template #default="scope">
            <el-button
              link
              type="primary"
              size="small"
              @click="deleteNormalUserHandle(scope.row.user_id)"
            >
              删除
            </el-button>
            <el-button
              link
              type="primary"
              size="small"
              @click="updateNormalUserHandle(scope.row)"
              >更新</el-button
            >
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 分页操作组件 -->
    <div class="table-footer">
      <el-pagination
        layout="prev, pager, next"
        :page-count="total_page_num"
        :page-size="pageSize"
        :hide-on-single-page="true"
        @change="changeHandle"
      />
    </div>
  </div>

  <!-- 新增用户弹窗 -->
  <el-dialog v-model="dialogCreateFormVisible" title="新增用户" width="500">
    <el-form :model="form" :rules="rules" ref="formRef">
      <el-form-item
        label="用户编号"
        :label-width="formLabelWidth"
        prop="user_id"
      >
        <el-input
          v-model="form.user_id"
          autocomplete="on"
          placeholder="请输入用户编号（必填）"
          :style="{ width: formInputWidth }"
        />
      </el-form-item>
      <el-form-item label="用户名字" :label-width="formLabelWidth" prop="name">
        <el-input
          v-model="form.name"
          autocomplete="on"
          placeholder="请输入用户名字（必填）"
          :style="{ width: formInputWidth }"
        />
      </el-form-item>
      <el-form-item
        label="用户密码"
        :label-width="formLabelWidth"
        prop="password"
      >
        <el-input
          v-model="form.password"
          autocomplete="on"
          placeholder="请输入用户密码（不输入会使用默认密码123456）"
          :style="{ width: formInputWidth }"
        />
      </el-form-item>
      <el-form-item label="分组" :label-width="formLabelWidth" prop="groups">
        <el-select
          v-model="form.groups"
          multiple
          filterable
          allow-create
          default-first-option
          :reserve-keyword="false"
          placeholder="选择分组"
          :style="{ width: formInputWidth }"
        >
          <el-option
            v-for="group in groupList"
            :key="group"
            :label="group"
            :value="group"
          />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="dialogCreateFormVisible = false">取消</el-button>
        <el-button type="primary" @click="createNormalUserHandle">
          确定
        </el-button>
      </div>
    </template>
  </el-dialog>

  <!-- 更新用户弹窗 -->
  <el-dialog v-model="dialogUpdateFormVisible" title="更新用户" width="500">
    <el-form :model="formUpdate" :rules="rules" ref="formUpdateRef">
      <el-form-item
        label="用户编号"
        :label-width="formLabelWidth"
        prop="new_user_id"
      >
        <el-input
          v-model="formUpdate.new_user_id"
          autocomplete="on"
          placeholder="请输入用户编号（必填）"
          :style="{ width: formInputWidth }"
        />
      </el-form-item>
      <el-form-item label="用户名字" :label-width="formLabelWidth" prop="name">
        <el-input
          v-model="formUpdate.name"
          autocomplete="on"
          placeholder="请输入用户名字（必填）"
          :style="{ width: formInputWidth }"
        />
      </el-form-item>
      <el-form-item label="重置用户密码" :label-width="formLabelWidth">
        <el-switch v-model="formUpdate.isResetPassword" />
      </el-form-item>
      <el-form-item label="分组" :label-width="formLabelWidth" prop="groups">
        <el-select
          v-model="formUpdate.groups"
          multiple
          filterable
          allow-create
          default-first-option
          :reserve-keyword="false"
          placeholder="选择分组"
          :style="{ width: formInputWidth }"
        >
          <el-option
            v-for="group in groupList"
            :key="group"
            :label="group"
            :value="group"
          />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="dialogUpdateFormVisible = false">取消</el-button>
        <el-button type="primary" @click="updateNormalUserAxios">
          确定
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>
<script setup>
import { ref } from 'vue'
import {
  getNormalUsers,
  createNormalUser,
  deleteNormalUser,
  updateNormalUser,
  postUploadFileURL,
  getGroups
} from '@/api/normal_user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useTokenStore } from '@/stores/token.js'
const tokenStore = useTokenStore()

// 分页相关
const currentPage = ref(1)
const pageSize = ref(15)
const total_page_num = ref(1)

const changeHandle = (newCurrentPage, newPageSize) => {
  console.log(newCurrentPage, newPageSize)
  currentPage.value = newCurrentPage
  pageSize.value = newPageSize
  initTable()
}

// 2个查询字段 一个是姓名 一个是分组
const QueryNameString = ref('')
const QueryGroupString = ref('')

// 表格选择行
const multipleSelection = ref([])

const handleSelectionChange = (seletValues) => {
  multipleSelection.value = seletValues
}

// 表格数据（初始化）
const userList = ref([])

const initTable = async () => {
  const data = (
    await getNormalUsers(
      QueryNameString.value,
      QueryGroupString.value,
      currentPage.value,
      pageSize.value
    )
  ).data.data
  userList.value = data.users
  total_page_num.value = data.total_page_num
  initGroup()
}
initTable()
// 分组数据（初始化）
const groupList = ref([])
const initGroup = async () => {
  groupList.value = (await getGroups()).data.data
}
// 表格操作
const deleteNormalUserHandle = (user_id) => {
  let message = `确认删除学号为 ${user_id} 的用户吗？`
  let confirmButtonText = '确定'
  let cancelButtonText = '取消'
  let user_id_list = [user_id]
  if (multipleSelection.value.length > 1) {
    message = `确认删除选中的 ${multipleSelection.value.length} 个用户吗？`
    confirmButtonText = '批量删除'
    cancelButtonText = '取消'
    user_id_list = multipleSelection.value.map((item) => item.user_id)
  }
  ElMessageBox.confirm(message, {
    confirmButtonText,
    cancelButtonText
  })
    .then(async () => {
      const message = await (await deleteNormalUser(user_id_list)).data
      ElMessage.success(message)
      initTable()
    })
    .catch(() => {
      ElMessage.info('已取消删除')
    })
}

// 新增一个用户 弹窗相关
const dialogCreateFormVisible = ref(false)
const formLabelWidth = '100px'
const formInputWidth = '350px'

const formRef = ref()
const form = ref({
  user_id: '',
  name: '',
  password: '',
  groups: []
})

// 表单验证规则
const rules = {
  user_id: [{ required: true, message: '请输入用户编号', trigger: 'blur' }],
  new_user_id: [{ required: true, message: '请输入用户编号', trigger: 'blur' }], // 更新用户的id时候用到此字段
  name: [{ required: true, message: '请输入用户名字', trigger: 'blur' }],
  password: [
    { required: false, message: '请选择密码', trigger: 'blur' },
    {
      pattern: /^[A-Za-z0-9]+$/, // 只允许数字和字母
      message: '密码只能包含数字和字母',
      trigger: 'blur'
    }
  ],
  groups: [{ required: true, message: '请选择分组', trigger: 'blur' }]
}

// 创建用户的处理函数
const createNormalUserHandle = () => {
  formRef.value.validate(async (valid) => {
    if (valid) {
      // console.log(form.value)
      // 如果表单通过验证，则继续执行提交操作
      const response = await createNormalUser({
        user_id: form.value.user_id,
        name: form.value.name,
        password: form.value.password,
        groups: form.value.groups
      })
      if (response.data.code === 0) {
        formRef.value.resetFields() // 重置表单
        dialogCreateFormVisible.value = false // 关闭弹框
        initTable() // 重新获取数据
        ElMessage.success(response.data.message)
      } else {
        ElMessage.error(response.data.message)
      }
    } else {
      // 如果表单验证失败，则不执行提交操作
      console.log('表单验证失败')
    }
  })
}

// 更新用户 弹窗相关
const dialogUpdateFormVisible = ref(false)
const formUpdateRef = ref()
const formUpdate = ref({
  original_user_id: '',
  new_user_id: '',
  name: '',
  isResetPassword: false,
  groups: []
})

// 更新用户的处理函数
const updateNormalUserHandle = (row) => {
  dialogUpdateFormVisible.value = true
  formUpdate.value.original_user_id = row.user_id
  formUpdate.value.new_user_id = row.user_id
  formUpdate.value.name = row.name
  formUpdate.value.isResetPassword = false
  formUpdate.value.groups = row.groups
}

const updateNormalUserAxios = async () => {
  formUpdateRef.value.validate(async (valid) => {
    if (valid) {
      const response = await updateNormalUser(formUpdate.value)
      if (response.data.code === 0) {
        dialogUpdateFormVisible.value = false
        initTable()
        ElMessage.success(response.data.message)
      } else {
        ElMessage.error(response.data.message)
      }
    } else {
      // 如果表单验证失败，则不执行提交操作
      console.log('表单验证失败')
    }
  })
}

// 批量添加用户
// 上传文件前的处理
const beforeUpload = (file) => {
  console.log(file)
  const allowedTypes = [
    'text/csv',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  ]
  if (!allowedTypes.includes(file.type)) {
    ElMessage.error('仅支持上传 CSV、XLS、XLSX 文件')
    return false // 阻止上传
  }
  ElMessage.success('上传成功，正在处理文件')
  return true
}

// 上传文件成功的处理
const successUpload = async (response) => {
  console.log(response)
  if (response.code === 0) {
    ElMessage.success(response.message)
    initTable()
  } else {
    ElMessage.error(response.message)
  }
}
</script>
<style scoped>
.account-view {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  height: 100%;
}

.table-content {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 98%;
}

.table-bar {
  width: 100%;
  display: flex;
  justify-content: space-between; /* 两边子元素分布在左右 */
  align-items: center;
  margin: 20px 0;
}

.table-bar-left {
  flex: 1; /* 尽量撑开 */
  margin-left: 40px;
  text-align: left; /* 可选：左对齐内容 */
}

.table-bar-right {
  display: flex;
  margin-right: 40px;
  text-align: right; /* 可选：右对齐内容 */
}

.el-dialog {
  text-align: left;
}
</style>
