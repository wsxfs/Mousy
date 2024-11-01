import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import axios from "axios"; // 引入 axios

axios.defaults.withCredentials = true; // 允许携带 cookie
axios.defaults.baseURL = 'http://127.0.0.1:8000'; // 设置默认的 baseURL

createApp(App).mount('#app').$nextTick(() => {
  // Use contextBridge
  window.ipcRenderer.on('main-process-message', (_event, message) => {
    console.log(message)
  })
})
