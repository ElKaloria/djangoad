import axios from "axios";
import { clearSession, getAuthState } from "./auth";

const rawBase = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api";
const api = axios.create({
  baseURL: rawBase.replace(/\/$/, ""),
});

api.interceptors.request.use((config) => {
  const { token } = getAuthState();
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      const url = err.config?.url || "";
      if (!url.includes("/auth/login/")) {
        clearSession();
      }
    }
    return Promise.reject(err);
  }
);

export async function login(username, password) {
  const { data } = await api.post("/auth/login/", { username, password });
  return data;
}

/** Совпадает с PAGE_SIZE в backend/core/settings.py (REST_FRAMEWORK). */
export const EVENTS_PAGE_SIZE = 20;

export async function fetchEvents(params = {}) {
  const { data } = await api.get("/events/", { params });
  return data;
}

export async function exportEventsXlsx(params = {}) {
  const { data } = await api.get("/events/export-xlsx/", {
    params,
    responseType: "blob",
  });
  return data;
}

export async function importEventsXlsx(file) {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await api.post("/events/import-xlsx/", formData);
  return data;
}

export async function fetchPlaces() {
  const { data } = await api.get("/places/");
  return Array.isArray(data) ? data : data.results || [];
}

export async function createPlace(payload) {
  const { data } = await api.post("/places/", payload);
  return data;
}

/**
 * Преобразует относительный URL медиа из API в URL, пригодный для <img src>.
 */
export function resolveMediaUrl(path) {
  if (!path) return "";
  if (typeof path === "string" && path.startsWith("http")) return path;
  const rawBase = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api";
  const origin = String(rawBase).replace(/\/api\/?$/, "");
  const p = String(path).startsWith("/") ? path : `/${path}`;
  if (origin) return `${origin}${p}`;
  return p;
}

export async function createEvent(payload) {
  const {
    uploadedImages = [],
    previewImage,
    name,
    description,
    publish_at,
    starts_at,
    ends_at,
    place,
    rating,
    status,
  } = payload;

  const hasFiles =
    previewImage instanceof File ||
    (Array.isArray(uploadedImages) && uploadedImages.length > 0);

  if (!hasFiles) {
    const { data } = await api.post("/events/", {
      name,
      description,
      publish_at,
      starts_at,
      ends_at,
      place,
      rating,
      status,
    });
    return data;
  }

  const formData = new FormData();
  formData.append("name", name);
  formData.append("description", description ?? "");
  formData.append("publish_at", publish_at);
  formData.append("starts_at", starts_at);
  formData.append("ends_at", ends_at);
  formData.append("place", String(place));
  formData.append("rating", String(rating));
  formData.append("status", status);
  if (previewImage instanceof File) {
    formData.append("preview_image", previewImage);
  }
  for (const file of uploadedImages) {
    formData.append("uploaded_images", file);
  }

  const { data } = await api.post("/events/", formData);
  return data;
}

export { api };
