<template>
  <div class="users-container">
    <h1>Gerenciar Usuários</h1>
    <router-link to="/adicionar-usuario" class="add-button" v-if="authStore.user?.role === 'admin'">
      Adicionar Novo Usuário
    </router-link>
    <table>
      <thead>
        <tr>
          <th>Nome de Usuário</th>
          <th>Função</th>
          <th>Ações</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.username">
          <td>{{ user.username }}</td>
          <td>{{ user.role }}</td>
          <td>
            <button
              @click="deleteUser(user.username)"
              class="delete-button"
              v-if="authStore.user?.role === 'admin' && authStore.user.username !== user.username">
              Deletar
            </button>
            <button
              @click="editUser(user)"
              class="edit-button"
              v-if="authStore.user?.role === 'admin' && authStore.user.username !== user.username">
              Editar
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted, inject } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();
const authStore = inject('authStore');
const users = ref([]);

const fetchUsers = async () => {
  const token = localStorage.getItem('token');
  if (!token) return;

  try {
    const response = await axios.get('http://localhost:5000/api/users', {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    users.value = response.data;
  } catch (error) {
    console.error('Erro ao buscar usuários:', error);
    alert('Erro ao buscar a lista de usuários.');
  }
};

const deleteUser = async (username) => {
  const token = localStorage.getItem('token');
  if (!token) return;

  if (confirm(`Tem certeza que deseja deletar o usuário ${username}?`)) {
    try {
      await axios.delete(`http://localhost:5000/api/users/${username}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      users.value = users.value.filter(user => user.username !== username);
      alert(`Usuário ${username} deletado com sucesso.`);
    } catch (error) {
      console.error('Erro ao deletar usuário:', error);
      alert('Erro ao deletar o usuário.');
    }
  }
};

const editUser = (user) => {
  router.push({
    name: 'editar-usuario',
    params: {
      username: user.username,
      role: user.role
    }
  });
};

onMounted(() => {
  fetchUsers();
});
</script>

<style scoped>
/* (O estilo pode permanecer o mesmo) */
.users-container {
  padding: 2em;
  text-align: center;
  font-family: Arial, sans-serif;
}
.add-button {
  display: inline-block;
  padding: 10px 20px;
  margin-bottom: 20px;
  background-color: #007bff;
  color: white;
  text-decoration: none;
  border-radius: 5px;
  font-weight: bold;
}
table {
  width: 80%;
  margin: 20px auto;
  border-collapse: collapse;
}
th, td {
  border: 1px solid #ddd;
  padding: 8px;
}
th {
  background-color: #f2f2f2;
  text-align: left;
}
.delete-button {
  background-color: #dc3545;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 5px;
  cursor: pointer;
  margin-right: 5px;
}
.edit-button {
  background-color: #ffc107;
  color: #333;
  border: none;
  padding: 5px 10px;
  border-radius: 5px;
  cursor: pointer;
}
</style>