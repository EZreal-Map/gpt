import request from '@/utils/request'

// ChatView.vue
// 根据问题 和 答案 更新 chatset 的标题 (原来打算也使用流式接口，但是后来发现不需要)
export const updateNewChatTitleAxios = ({ chat_id, question, answer }) => {
  return request.post('/chat/title', {
    chat_id,
    question,
    answer
  })
}
