<template>
  <div class="add-user-container">
    <h1>Adicionar Novo Usuário</h1>
    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label for="username">Nome de Usuário:</label>
        <input type="text" id="username" v-model="username" required />
      </div>
      <div class="form-group">
        <label for="email">E-mail:</label>
        <input type="email" id="email" v-model="email" required />
      </div>
      <div class="form-group">
        <label for="password">Senha:</label>
        <input type="password" id="password" v-model="password" required />
      </div>
      <div class="form-group">
        <label for="role">Função:</label>
        <select id="role" v-model="role" required>
          <option value="admin">Admin</option>
          <option value="editor">Editor</option>
          <option value="reader">Leitor</option>
        </select>
      </div>
      <button type="submit" class="submit-button">Adicionar Usuário</button>
    </form>
    <div v-if="message" :class="messageClass">{{ message }}</div>
  </div>
</template>

<script setup>
import { ref, inject } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();
const authStore = inject('authStore');

const username = ref('');
const email = ref('');
const password = ref('');
const role = ref('reader');
const message = ref('');
const messageClass = ref('');

const handleSubmit = async () => {
  message.value = '';
  const token = localStorage.getItem('token');

  if (!token) {
    message.value = 'Você não está autenticado.';
    messageClass.value = 'error-message';
    return;
  }

  try {
    const response = await axios.post('http://localhost:5000/api/users', {
      username: username.value,
      email: email.value,
      password: password.value,
      role: role.value,
    }, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });

    message.value = response.data.message;
    messageClass.value = 'success-message';
    // Redireciona de volta para a lista de usuários após o sucesso
    setTimeout(() => {
      router.push('/gerenciar-usuarios');
    }, 1500);

  } catch (error) {
    message.value = error.response?.data?.error || 'Erro ao criar usuário. Tente novamente.';
    messageClass.value = 'error-message';
  }
};
</script>

<style scoped>
.add-user-container {
  max-width: 500px;
  margin: 2em auto;
  padding: 2em;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  background-color: #f9f9f9;
  font-family: Arial, sans-serif;
  text-align: left;
}
h1 {
  text-align: center;
  color: #333;
}
.form-group {
  margin-bottom: 1em;
}
label {
  display: block;
  margin-bottom: 0.5em;
  color: #555;
}
input, select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
}
.submit-button {
  width: 100%;
  padding: 12px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1em;
}
.submit-button:hover {
  background-color: #0056b3;
}
.success-message {
  color: green;
  text-align: center;
  margin-top: 1em;
}
.error-message {
  color: red;
  text-align: center;
  margin-top: 1em;
}
</style>