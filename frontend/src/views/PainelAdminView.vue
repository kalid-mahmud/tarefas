<template>
  <div class="dashboard-container">
    <h1>Bem-vindo, {{ username }}!</h1>
    <p>Este é o conteúdo protegido do painel administrativo.</p>
    
    <button @click="navigateToUsers" class="nav-button">Gerenciar Usuários</button>
    <button @click="logout" class="logout-button">Sair</button>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();
const username = ref('');

const navigateToUsers = () => {
  router.push('/gerenciar-usuarios');
};

const logout = () => {
  localStorage.removeItem('token');
  router.push('/');
};

onMounted(async () => {
  const token = localStorage.getItem('token');
  if (token) {
    try {
      const response = await axios.get('http://localhost:5000/api/user', {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      username.value = response.data.username;
    } catch (error) {
      console.error('Erro ao buscar dados do usuário:', error);
      logout();
    }
  }
});
</script>

<style scoped>
.dashboard-container {
  padding: 2em;
  text-align: center;
  font-family: Arial, sans-serif;
}

h1 {
  color: #333;
}

p {
  color: #666;
}

.nav-button {
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1em;
  margin-right: 10px;
}

.logout-button {
  padding: 10px 20px;
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1em;
}

.nav-button:hover {
  background-color: #0056b3;
}

.logout-button:hover {
  background-color: #c82333;
}
</style>