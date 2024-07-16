import request from '@/utils/request'
import { baseURL } from '@/utils/request'

// DataBaseFolderView.vue
// 获取所有 “条” 知识库数据
export const getDatasetsAxios = () => request.get('/dataset/')

// 创建一条知识库数据
export const postDatasetAxios = ({ name, description, privacy }) =>
  request.post('/dataset/', { name, description, privacy })

// DataBaseBox.vue
// 更新一条知识库数据
export const putDatasetAxios = (databaseID, { name, description, privacy }) =>
  request.put(`/dataset/${databaseID}`, { name, description, privacy })

// 删除一条知识库数据
export const deleteDatasetAxios = (databaseID) =>
  request.delete(`/dataset/${databaseID}`)

// IDDataBaseUpdateDocumentView.vue
// 上传文件url
export const postUploadFileURLAxios = () => `${baseURL}/retrieval/uploadfiles/`

// 清空临时文件夹
export const postClearTempDirectoryAxios = () =>
  request.post('/retrieval/clear-temp-dir/')

// 删除临时文件夹里的一个临时文件
export const deleteTempFileAxios = (filename) =>
  request.delete(`/retrieval/deletetempfile/${encodeURIComponent(filename)}`)

// 预览拆分效果 把临时文件夹里面的文件拆分chunks
export const getTempPDFChunksAxios = ({
  chunk_size,
  chunk_overlap,
  separator
}) =>
  request.get(`/retrieval/temp-pdf-files-chunks/`, {
    params: { chunk_size, chunk_overlap, separator }
  })

// 确认上传文件，保存到目录/数据库中
export const postMoveTempFileToDatabaseAxios = (
  databaseID,
  { chunk_size, chunk_overlap, separator }
) =>
  request.post(`/dataset/move-temp-files/${databaseID}`, {
    params: { chunk_size, chunk_overlap, separator }
  })

// IDDataBaseDocumentView.vue
// 获取所有 “条” 文档数据
export const getDocumentsAxios = (databaseID) =>
  request.get(`/dataset/${databaseID}/articles/`)

const parseFilenameFromContentDisposition = (contentDisposition) => {
  // 匹配 filename*=
  const matches = contentDisposition.match(/filename\*=(utf-8'')(.*?)$/i)
  if (matches && matches.length === 3) {
    // 解码文件名部分
    const encodedFilename = matches[2]
    const decodedFilename = decodeURIComponent(encodedFilename)
    return decodedFilename
  }
  return 'download.pdf' // 如果未找到合适的匹配，返回 null 或者适当的默认值
}

// 下载指定一条文档
export const getDownloadDocumentAxios = async (documentID) => {
  const response = await request.get(`/dataset/download-file/${documentID}`, {
    responseType: 'blob' // 设置响应类型为 blob
  })

  // 从响应头中尝试获取文件名
  const contentDisposition = response.headers['content-disposition']
  console.log('contentDisposition:', contentDisposition)
  const filename = parseFilenameFromContentDisposition(contentDisposition)

  // 创建一个虚拟的下载链接
  const url = window.URL.createObjectURL(new Blob([response.data]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', filename)

  // 将虚拟链接添加到页面中并点击
  document.body.appendChild(link)
  link.click()

  // 下载完成后移除虚拟链接
  document.body.removeChild(link)
}

// 删除指定一条文档
export const deleteDocumentAxios = (documentID) =>
  request.delete(`/dataset/${documentID}/delete-documents`)

// IDDataBaseDocumentChunkView.vue
// 获取指定一条文档的所有chunks
export const getDocumentChunksAxios = (documentID) =>
  request.get(`/dataset/${documentID}/chunks`)

// 通过 ID 更新chunk
// export const putEditChunkByIDAxios = (databaseID, { page_content, chunk_id }) =>
//   request.put(
//     `/dataset/${databaseID}/edit-chunk`,
//     { page_content },
//     { params: { chunk_id } }
//   )

// export const deleteChunkAxios = (databaseID, { article_id, chunk_id }) =>
//   request.delete(`/retrieval/${databaseID}/delete-chunk`, {
//     params: {
//       article_id,
//       chunk_id
//     }
//   })

// IDDataBaseHitTestingView.vue
// 获取指定一条文档的所有chunks
// export const getHitTestingAxios = (databaseID, { query, k, min_relevance }) =>
//   request.get(`/retrieval/${databaseID}/similarity-search`, {
//     params: { query, k, min_relevance }
//   })

export const postSimilaritySearchAxios = ({
  dataset_ids,
  query,
  k,
  min_relevance
}) =>
  request.post('/retrieval/similarity-search', {
    dataset_ids,
    query,
    k,
    min_relevance
  })

// 通过 metadata ID 新chunk
export const putEditChunkByMetadataIDAxios = (
  databaseID,
  { page_content, metadata_id }
) =>
  request.put(
    `/retrieval/${databaseID}/edit-chunk`,
    { page_content },
    { params: { metadata_id } }
  )

// 删除指定 metadata ID 的 chunk
export const deleteChunkByMetadataIDAxios = (
  databaseID,
  { article_id, metadata_id }
) =>
  request.delete(`/retrieval/${databaseID}/delete-chunk`, {
    params: {
      article_id,
      metadata_id
    }
  })

// 获取测试历史记录
export const getTestHistoryAxios = (databaseID) =>
  request.get(`/dataset/${databaseID}/query-test-history/`)

// 删除测试历史记录
export const deleteHistoryQueryAxios = (query_test_history_id) =>
  request.delete(`/dataset/query-test-history/${query_test_history_id}`)

// 新添加测试历史记录
export const postTestHistoryAxios = ({ dataset_id, query, k, min_relevance }) =>
  request.post(`/dataset/query-test-history`, {
    dataset_id,
    query,
    k,
    min_relevance
  })
