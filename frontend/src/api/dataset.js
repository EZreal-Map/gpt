import request from '@/utils/request'
import { baseURL } from '@/utils/request'

// // 文章：根据ID获取文章详情
// export const getBlogIDService = (id) => request.get(`/blog/${id}`)
// // 文章：根据ID修改文章 title-content
// export const putBlogIDService = (id, title, content, tag) =>
//   request.put(`/blog/${id}`, { title, content, tag })
// // 文章：新建文章
// export const postBlogService = (title, content, tag) =>
//   request.post('/blog', { title, content, tag })
// // 文章：根据ID删除文章
// export const deleteBlogIDService = (id) => request.delete(`/blog/${id}`)

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
export const getDocumentChunksAxios = (documentID) =>
  request.get(`/dataset/${documentID}/chunks`)
