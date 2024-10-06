import { createApp } from 'vue'
import App from './App.vue'
import axios from 'axios';
import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';

const app = createApp(App);

// Устанавливаем axios как глобальное свойство
app.config.globalProperties.$axios = axios;

// Устанавливаем базовый URL для axios
axios.defaults.baseURL = '/';

// Используем Element Plus
app.use(ElementPlus);

app.mount('#app')
