import { baseURL } from '@/utils/request.js'

// WebSocket 地址拼接函数
export const getWebSocketURL = (path) => {
  let wsURL

  // 如果 baseURL 是 http:// 或 https:// 开头，使用完整的 WebSocket 地址
  if (baseURL.startsWith('http://') || baseURL.startsWith('https://')) {
    const wsProtocol = baseURL.startsWith('https://') ? 'wss://' : 'ws://'
    const wsDomain = baseURL.replace(/^http(s)?:\/\//, '') // 去掉 http:// 或 https://

    // 拼接 WebSocket URL
    wsURL = `${wsProtocol}${wsDomain}${path}`
  } else {
    // 如果 baseURL 是相对路径，拼接成完整的 WebSocket URL
    const wsProtocol = window.location.protocol.startsWith('https')
      ? 'wss://'
      : 'ws://'
    wsURL = `${wsProtocol}${window.location.host}${baseURL}${path}`
  }

  return wsURL
}

export const sttWSURL = getWebSocketURL('/ws/stt')

export const ttsWSURL = getWebSocketURL('/ws/tts')
