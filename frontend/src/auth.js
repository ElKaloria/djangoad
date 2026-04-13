import { reactive, readonly } from "vue";

const STORAGE_TOKEN = "api_token";
const STORAGE_USERNAME = "auth_username";
const STORAGE_SUPERUSER = "auth_is_superuser";

const state = reactive({
  token: "",
  username: "",
  isSuperuser: false,
});

function loadFromStorage() {
  state.token = localStorage.getItem(STORAGE_TOKEN) || "";
  state.username = localStorage.getItem(STORAGE_USERNAME) || "";
  state.isSuperuser = localStorage.getItem(STORAGE_SUPERUSER) === "true";
}

export function initAuth() {
  loadFromStorage();
}

export function getAuthState() {
  return readonly(state);
}

export function isAuthenticated() {
  return Boolean(state.token);
}

export function isSuperuser() {
  return state.isSuperuser === true;
}

export function setSession({ token, username, is_superuser }) {
  state.token = token || "";
  state.username = username || "";
  state.isSuperuser = Boolean(is_superuser);
  if (state.token) {
    localStorage.setItem(STORAGE_TOKEN, state.token);
    localStorage.setItem(STORAGE_USERNAME, state.username);
    localStorage.setItem(STORAGE_SUPERUSER, state.isSuperuser ? "true" : "false");
  } else {
    clearSession();
  }
}

export function clearSession() {
  state.token = "";
  state.username = "";
  state.isSuperuser = false;
  localStorage.removeItem(STORAGE_TOKEN);
  localStorage.removeItem(STORAGE_USERNAME);
  localStorage.removeItem(STORAGE_SUPERUSER);
}
