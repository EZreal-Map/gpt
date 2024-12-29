import { createApp } from 'vue'
import App from './App.vue'
import { createPinia } from 'pinia'
import persist from 'pinia-plugin-persistedstate'
import router from './router'
import 'default-passive-events' // 解再移动端滚动性能问题
// 参考：https://juejin.cn/post/7230806990452588581

const pinia = createPinia().use(persist)
const app = createApp(App)

app.use(pinia) // pinia持久化后的封装
app.use(router)
app.mount('#app')
