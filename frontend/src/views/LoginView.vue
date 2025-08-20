<template>
  <div class="login-container">
    <h1>Login</h1>
    <form @submit.prevent="login">
      <div class="form-group">
        <label for="username">Usuário</label>
        <input type="text" id="username" v-model="username" required>
      </div>
      <div class="form-group">
        <label for="password">Senha</label>
        <input type="password" id="password" v-model="password" required>
      </div>
      <button type="submit">Entrar</button>
    </form>
    <div v-if="error" class="error-message">{{ error }}</div>
    <div class="forgot-password">
      <router-link to="/redefinir-senha">Esqueceu a senha?</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, inject } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const username = ref('');
const password = ref('');
const error = ref('');
const router = useRouter();
const { setUser } = inject('authActions');

const login = async () => {
  try {
    const response = await axios.post('http://localhost:5000/api/login', {
      username: username.value,
      password: password.value,
    });
    const token = response.data.token;
    localStorage.setItem('token', token);

    const userResponse = await axios.get('http://localhost:5000/api/user', {
        headers: {
            Authorization: `Bearer ${token}`
        }
    });
    
    setUser(userResponse.data);

    router.push('/dashboard');
} catch (err) {
    console.error(err); // <-- Adicione esta linha
    if (err.response && err.response.data && err.response.data.error) {
      error.value = err.response.data.error;
    } else {
      error.value = 'Ocorreu um erro. Tente novamente.';
    }
  }
};
</script>

<style scoped>
.login-container {
  max-width: 400px;
  margin: 100px auto;
  padding: 2em;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  background-color: #f9f9f9;
}
.form-group {
  margin-bottom: 1em;
}
label {
  display: block;
  margin-bottom: 0.5em;
  color: #555;
}
input[type="text"], input[type="password"] {
  width: 95%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
}
button {
  width: 100%;
  padding: 10px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1em;
}
button:hover {
  background-color: #0056b3;
}
.error-message {
  color: red;
  margin-top: 1em;
  text-align: center;
}
.forgot-password {
  margin-top: 1em;
  text-align: center;
}
.forgot-password a {
  color: #007bff;
  text-decoration: none;
}
.forgot-password a:hover {
  text-decoration: underline;
}
</style>