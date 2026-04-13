<script setup>
import { computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import { getAuthState, clearSession } from "./auth";

const router = useRouter();
const route = useRoute();
const auth = getAuthState();

const showNav = computed(() => route.name !== "login");

function logout() {
  clearSession();
  router.push({ name: "login" });
}
</script>

<template>
  <div class="app-root">
    <header v-if="showNav" class="top-bar">
      <nav class="nav">
        <RouterLink class="nav-link" to="/events">Мероприятия</RouterLink>
        <RouterLink v-if="auth.isSuperuser" class="nav-link" to="/places">Места</RouterLink>
      </nav>
      <div class="user-block" v-if="auth.token">
        <span class="username">{{ auth.username }}</span>
        <span v-if="auth.isSuperuser" class="badge">superuser</span>
        <button type="button" class="btn-secondary" @click="logout">Выйти</button>
      </div>
    </header>
    <RouterView />
  </div>
</template>

<style scoped>
.app-root {
  min-height: 100vh;
}

.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  padding: 12px 20px;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
}

.nav {
  display: flex;
  gap: 8px;
}

.nav-link {
  padding: 8px 14px;
  border-radius: 8px;
  text-decoration: none;
  color: #374151;
  font-weight: 500;
}

.nav-link.router-link-active {
  background: #eff6ff;
  color: #2563eb;
}

.user-block {
  display: flex;
  align-items: center;
  gap: 10px;
}

.username {
  color: #6b7280;
  font-size: 14px;
}

.badge {
  font-size: 11px;
  text-transform: uppercase;
  background: #dbeafe;
  color: #1d4ed8;
  padding: 2px 8px;
  border-radius: 999px;
}

.btn-secondary {
  padding: 6px 12px;
  border-radius: 8px;
  border: 1px solid #d1d1db;
  background: rgb(0, 0, 255);
  cursor: pointer;
  font-size: 14px;
}

.btn-secondary:hover {
  background: rgb(0, 0, 255);
}
</style>
