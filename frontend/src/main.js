import { createApp } from 'vue'
import App from './App.vue'
import { createPinia } from 'pinia'
import persist from 'pinia-plugin-persistedstate'
import router from './router'

const pinia = createPinia().use(persist)
const app = createApp(App)

app.use(pinia) // pinia持久化后的封装
app.use(router)
app.mount('#app')
