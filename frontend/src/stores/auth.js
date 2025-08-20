import { reactive, readonly } from 'vue';

const state = reactive({
  user: null,
  isAuthenticated: false,
});

const setUser = (user) => {
  state.user = user;
  state.isAuthenticated = !!user;
};

const clearUser = () => {
  state.user = null;
  state.isAuthenticated = false;
};

export const authStore = readonly(state);
export const useAuthActions = () => ({
  setUser,
  clearUser,
});