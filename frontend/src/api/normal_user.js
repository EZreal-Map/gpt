import request from '@/utils/request'
import { baseURL } from '@/utils/request'

// 获取所有普通用户
// 接收查询参数 name 和 group
export const getNormalUsers = (name, group, page_num, page_size) => {
  // 构建查询参数对象
  const params = {}

  if (name) {
    params.name = name
  }
  if (group) {
    params.group = group
  }
  if (page_num) {
    params.page_num = page_num
  }
  if (page_size) {
    params.page_size = page_size
  }

  // 发送 GET 请求，params 会自动被转换为查询字符串
  return request.get('/normal_user/', { params })
}

// 新增普通用户
export const createNormalUser = ({ user_id, name, password, groups }) =>
  request.post('/normal_user/', { user_id, name, password, groups })

// 删除普通用户
export const deleteNormalUser = (user_id_list) =>
  request.delete(`/normal_user/`, {
    data: user_id_list
  })

// 修改普通用户
export const updateNormalUser = async (userData) => {
  return request.put(`/normal_user/${userData.original_user_id}`, {
    new_user_id: userData.new_user_id,
    name: userData.name,
    is_reset_password: userData.isResetPassword,
    groups: userData.groups
  })
}

// 修改普通用户密码
export const updateNormalUserPassword = (password) =>
  request.put(`/normal_user/password/update`, password)

// 上传chatid对应的文件路径
export const postUploadFileURL = () => `${baseURL}/normal_user/uploadfile/`

// 获取所有分组名列表
export const getGroups = () => request.get('/group/')

// 获取所有分组名+用户计数列表
export const getGroupsUserCount = () => request.get('/group/usercount/')

// 更新分组名
export const updateGroupName = ({ group_id, newname }) =>
  request.put(`/group/${group_id}`, newname)

// 删除分组
export const deleteGroup = (group_id) => request.delete(`/group/${group_id}`)

// 绑定分组和应用
export const postGroupsAPPBind = ({ groups, appid }) =>
  request.post('/group/appset/', { groups, appid })

// 通过应用id获取已绑定的分组
export const getGroupsByAppid = (appid) =>
  request.get(`/group/appset/`, { params: { appid } })

// 通过user_id获取用户所有可以访问的应用
export const getAppsByUserId = (user_id) =>
  request.get(`/normal_user/appset/`, { params: { user_id } })
