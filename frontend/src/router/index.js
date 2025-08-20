import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import PainelAdminView from '../views/PainelAdminView.vue'
import GerenciarUsuariosView from '../views/GerenciarUsuariosView.vue'
import AdicionarUsuarioView from '../views/AdicionarUsuarioView.vue'
import EditarUsuarioView from '../views/EditarUsuarioView.vue'
import RedefinirSenhaView from '../views/RedefinirSenhaView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'login',
      component: LoginView
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: PainelAdminView,
      meta: { requiresAuth: true }
    },
    {
      path: '/gerenciar-usuarios',
      name: 'gerenciar-usuarios',
      component: GerenciarUsuariosView,
      meta: { requiresAuth: true }
    },
    {
      path: '/adicionar-usuario',
      name: 'adicionar-usuario',
      component: AdicionarUsuarioView,
      meta: { requiresAuth: true }
    },
    {
      path: '/editar-usuario/:username',
      name: 'editar-usuario',
      component: EditarUsuarioView,
      meta: { requiresAuth: true }
    },
    {
      path: '/redefinir-senha',
      name: 'redefinir-senha',
      component: RedefinirSenhaView
    }
  ]
})

router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  const isAuthenticated = localStorage.getItem('token');

  if (requiresAuth && !isAuthenticated) {
    next({ name: 'login' });
  } else {
    next();
  }
});

export default router