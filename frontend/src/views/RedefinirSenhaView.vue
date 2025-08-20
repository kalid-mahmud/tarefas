<template>
  <div class="reset-password-container">
    <h1>Redefinir Senha</h1>
    <div v-if="!tokenReceived">
      <p>Digite seu e-mail para receber um link de redefinição de senha.</p>
      <form @submit.prevent="handleRequest">
        <div class="form-group">
          <label for="email">E-mail:</label>
          <input type="email" id="email" v-model="email" required />
        </div>
        <button type="submit">Enviar Link</button>
      </form>
    </div>
    <div v-else>
      <p>Digite sua nova senha.</p>
      <form @submit.prevent="handleReset">
        <div class="form-group">
          <label for="newPassword">Nova Senha:</label>
          <input type="password" id="newPassword" v-model="newPassword" required />
        </div>
        <button type="submit">Redefinir Senha</button>
      </form>
    </div>
    <div v-if="message" :class="messageClass">{{ message }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';

const route = useRoute();
const router = useRouter();

const tokenReceived = ref(false);
const email = ref('');
const newPassword = ref('');
const token = ref('');
const message = ref('');
const messageClass = ref('');

onMounted(() => {
  if (route.query.token) {
    tokenReceived.value = true;
    token.value = route.query.token;
  }
});

const handleRequest = async () => {
  message.value = '';
  try {
    const response = await axios.post('http://localhost:5000/api/reset-password-request', { email: email.value });
    message.value = response.data.message;
    messageClass.value = 'success-message';
  } catch (error) {
    message.value = error.response?.data?.error || 'Erro ao enviar o link. Tente novamente.';
    messageClass.value = 'error-message';
  }
};

const handleReset = async () => {
  message.value = '';
  try {
    const response = await axios.post('http://localhost:5000/api/reset-password', {
      token: token.value,
      newPassword: newPassword.value
    });
    message.value = response.data.message;
    messageClass.value = 'success-message';
    setTimeout(() => {
      router.push('/'); // Redireciona para o login
    }, 2000);
  } catch (error) {
    message.value = error.response?.data?.error || 'Erro ao redefinir a senha. Tente novamente.';
    messageClass.value = 'error-message';
  }
};
</script>

<style scoped>
.reset-password-container {
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
input[type="email"], input[type="password"] {
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
.message-container {
  margin-top: 1em;
  text-align: center;
}
.success-message {
  color: green;
}
.error-message {
  color: red;
}
</style>