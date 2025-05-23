import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import axios from "axios"; // 引入 axios

// 导入element-plus
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './style.css'
import router from './router'
axios.defaults.withCredentials = true; // 允许携带 cookie
axios.defaults.baseURL = 'http://127.0.0.1:8000'; // 设置默认的 baseURL

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(ElementPlus)
app.use(router)
app.mount('#app').$nextTick(() => {
  // Use contextBridge
  window.ipcRenderer.on('main-process-message', (_event, message) => {
    console.log(message)
  })
})
