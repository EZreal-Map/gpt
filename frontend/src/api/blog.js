import request from '@/utils/request'
// 文章：获取文章列表
export const getBlogListService = (limit, tag) => {
  // 构建请求参数对象
  const params = {}
  if (limit) {
    params.limit = limit
  }
  if (tag) {
    params.tag = tag
  }
  // 发送请求
  return request.get('/blog', { params })
}
// 文章：根据ID获取文章详情
export const getBlogIDService = (id) => request.get(`/blog/${id}`)
// 文章：根据ID修改文章 title-content
export const putBlogIDService = (id, title, content, tag) =>
  request.put(`/blog/${id}`, { title, content, tag })
// 文章：新建文章
export const postBlogService = (title, content, tag) =>
  request.post('/blog', { title, content, tag })
// 文章：根据ID删除文章
export const deleteBlogIDService = (id) => request.delete(`/blog/${id}`)
