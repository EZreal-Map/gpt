import request from '@/utils/request'

// APPView.vue
// 获取所有 “条” 应用集合数据
export const getAppsetsAxios = () => request.get('/appset/')

// 创建一条应用集合数据
export const postAppsetAxios = ({ name, description, privacy }) =>
  request.post('/appset/', { name, description, privacy })

// DataBaseBox.vue
// 更新一条应用集合数据
export const putAppsetAxios = (appID, { name, description, privacy }) =>
  request.put(`/appset/${appID}`, { name, description, privacy })

// 删除一条应用集合数据
export const deleteAppsetAxios = (appID) => request.delete(`/appset/${appID}`)

// APPIDConfiguration.vue
// 获取一条应用集合数据
export const getAppsetAxios = (appID) => request.get(`/appset/${appID}`)

// 添加 APPSet 的 datasets 集合
export const selectAppsetDatasetsAxios = async (appsetId, datasetIds) =>
  request.put(`/appset/${appsetId}/datasets`, datasetIds)

// 获取指定 APPSet 关联的所有 DataSet 数据
export const getAppsetDatasetsAxios = async (appsetId) =>
  await request.get(`/appset/${appsetId}/datasets`)
