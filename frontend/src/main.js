import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { authStore, useAuthActions } from './stores/auth';

const app = createApp(App)

app.use(router)

app.provide('authStore', authStore);
app.provide('authActions', useAuthActions());

app.mount('#app')