<script setup>
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { login as apiLogin } from "../api";
import { setSession } from "../auth";

const router = useRouter();
const route = useRoute();

const username = ref("");
const password = ref("");
const error = ref("");
const loading = ref(false);

async function submit() {
  error.value = "";
  loading.value = true;
  try {
    const data = await apiLogin(username.value, password.value);
    setSession({
      token: data.token,
      username: data.username,
      is_superuser: data.is_superuser,
    });
    const redirect = route.query.redirect;
    router.push(typeof redirect === "string" ? redirect : "/events");
  } catch (e) {
    error.value =
      e.response?.data?.detail || "Не удалось войти. Проверьте логин и пароль.";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <main class="container narrow">
    <div class="card login-card">
      <h1>Вход</h1>
      <p class="hint">Используйте учётную запись Django (логин и пароль).</p>
      <form @submit.prevent="submit">
        <label>
          <span>Логин</span>
          <input v-model="username" type="text" autocomplete="username" required />
        </label>
        <label>
          <span>Пароль</span>
          <input v-model="password" type="password" autocomplete="current-password" required />
        </label>
        <p v-if="error" class="error">{{ error }}</p>
        <button type="submit" :disabled="loading">{{ loading ? "Вход…" : "Войти" }}</button>
      </form>
    </div>
  </main>
</template>

<style scoped>
.narrow {
  max-width: 420px;
  margin-top: 48px;
}

.login-card h1 {
  margin-top: 0;
}

.hint {
  color: #6b7280;
  font-size: 14px;
  margin-bottom: 20px;
}

form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

label {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

label span {
  font-size: 13px;
  font-weight: 500;
  color: #374151;
}

button[type="submit"] {
  margin-top: 8px;
}
</style>
