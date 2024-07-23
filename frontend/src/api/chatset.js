import request from '@/utils/request'

// APPIDConfiguration.vue
// 获取指定 appset_id 的 APPSet 的测试界面(chatset)的对话历史
export const getChatHistoryAxios = ({ appset_id, chat_id = null }) => {
  return request.get(`/chatset/${appset_id}/chat_history`, {
    params: { chat_id }
  })
}

// 删除指定 appset_id 的 APPSet 的测试界面(chatset)的所有对话历史 （清空对话历史）
export const cleanChatHistoryAxios = ({ appset_id, chat_id = null }) => {
  return request.delete(`/chatset/${appset_id}/chat_history`, {
    params: { chat_id }
  })
}

// 发送 POST 请求到后端的 chat_history 路由
export const addChatHistoryAxios = async ({
  appset_id,
  chat_id = null,
  question,
  answer,
  cite_documents,
  context_histories,
  execute_time,
  is_test_mode
}) => {
  return await request.post(`/chatset/${appset_id}/chat_history`, {
    appset_id,
    chat_id,
    question,
    answer,
    cite_documents,
    context_histories,
    execute_time,
    is_test_mode
  })
}

// ChatView.vue
// 根据 appset_id 返回所有与 appset_id 关联的 chatset
export const getChatSetsAxios = async ({ appset_id }) => {
  return await request.get(`/chatset/${appset_id}/chatset`)
}

// 更新一个 ChatSet 的名称
export const updateChatSetNameAxios = async ({ chatset_id, chat_name }) => {
  // 传递的参数是 chat_name 是一个字符串 Body 而不是常见的对象 Body {chat_name: 'xxx'}
  return await request.put(`/chatset/${chatset_id}`, chat_name)
}

// 删除一个 ChatSet
export const deleteChatSetAxios = async ({ chatset_id }) => {
  return await request.delete(`/chatset/${chatset_id}`)
}

// 删除一个 ChatHistory
export const deleteChatHistoryAxios = async ({ chat_history_id }) => {
  return await request.delete(`/chat_history/${chat_history_id}`)
}
