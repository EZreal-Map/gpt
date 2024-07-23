import request from '@/utils/request'

// ChatView.vue
// 根据问题 和 答案 更新 chatset 的标题
export const updateNewChatTitleAxios = ({ chat_id, question, answer }) => {
  return request.post('/chat/title', {
    chat_id,
    question,
    answer
  })
}

// import { fetchEventSource } from '@microsoft/fetch-event-source'
// import { baseURL } from '@/utils/request'

// export const updateNewChatTitleSSERequest = (question, answer, object) => {
//   console.log('updateNewChatTitleSSERequest', question, answer, object)
//   const streamUrl = baseURL + '/chat/title'
//   const ctrl = new AbortController()

//   fetchEventSource(streamUrl, {
//     method: 'POST',
//     headers: {
//       'Content-Type': 'application/json'
//     },
//     body: JSON.stringify({
//       question,
//       answer
//     }),
//     signal: ctrl.signal,
//     openWhenHidden: true, // 在调用失败时禁止重复调用
//     onmessage(event) {
//       // 接收到消息回调 （多次）
//       // console.log(event)
//       const data = JSON.parse(event.data)
//       console.log('event', event)
//       if (event.id === '0') {
//         object.name = '' // 开始的时候，清空一次
//       }
//       if (event.event === 'message' && data.content) {
//         object.name += data.content
//       }
//     },
//     onclose() {
//       // 正常连接关闭回调
//       console.log('Connection closed')
//     },
//     onerror(err) {
//       //连接出现异常回调
//       // 必须抛出错误才会停止
//       console.log('Connection error')
//       ctrl.value.abort() // 终止连接
//       throw err
//     }
//   })
// }
