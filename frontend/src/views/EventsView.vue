<script setup>
import { computed, onMounted, onUnmounted, reactive, ref, watch } from "vue";
import {
  createEvent,
  EVENTS_PAGE_SIZE,
  exportEventsXlsx,
  fetchEvents,
  fetchPlaces,
  importEventsXlsx,
  resolveMediaUrl,
} from "../api";
import { getAuthState } from "../auth";

const auth = getAuthState();
const canExportXlsx = computed(() => Boolean(auth.token));
const loading = ref(false);
const error = ref("");
const events = ref([]);
const total = ref(0);
const places = ref([]);

const filters = reactive({
  search: "",
  ordering: "starts_at",
  starts_at_from: "",
  starts_at_to: "",
  page: 1,
});

const eventForm = reactive({
  name: "",
  description: "",
  publish_at: "",
  starts_at: "",
  ends_at: "",
  place: "",
  rating: 0,
  status: "draft",
});

const previewImageFile = ref(null);
const galleryImageFiles = ref([]);
const previewInputRef = ref(null);
const galleryInputRef = ref(null);
const xlsxInputRef = ref(null);
const xlsxNotice = ref("");

function normalizeDate(dateValue) {
  if (!dateValue) return "";
  return new Date(dateValue).toISOString();
}

function onPreviewChange(e) {
  const f = e.target.files?.[0];
  previewImageFile.value = f || null;
}

function onGalleryChange(e) {
  galleryImageFiles.value = Array.from(e.target.files || []);
}

const totalPages = computed(() => {
  const n = total.value;
  if (n <= 0) return 1;
  return Math.ceil(n / EVENTS_PAGE_SIZE);
});

let filterReloadTimer = null;

function listQueryParams() {
  return {
    search: filters.search || undefined,
    ordering: filters.ordering || undefined,
    starts_at_from: normalizeDate(filters.starts_at_from),
    starts_at_to: normalizeDate(filters.starts_at_to),
  };
}

async function loadEvents() {
  loading.value = true;
  error.value = "";
  try {
    const params = { ...listQueryParams(), page: filters.page };
    const data = await fetchEvents(params);
    events.value = data.results || [];
    total.value = data.count || 0;
    const count = total.value;
    const pages = Math.max(1, Math.ceil(count / EVENTS_PAGE_SIZE));
    if (count === 0) {
      filters.page = 1;
    } else if (filters.page > pages) {
      filters.page = pages;
      return loadEvents();
    }
  } catch (e) {
    error.value = "Не удалось загрузить мероприятия.";
  } finally {
    loading.value = false;
  }
}

watch(
  () => [filters.search, filters.ordering, filters.starts_at_from, filters.starts_at_to],
  () => {
    filters.page = 1;
    if (filterReloadTimer) clearTimeout(filterReloadTimer);
    filterReloadTimer = setTimeout(() => {
      filterReloadTimer = null;
      loadEvents();
    }, 400);
  }
);

onUnmounted(() => {
  if (filterReloadTimer) clearTimeout(filterReloadTimer);
});

function goToPage(p) {
  const next = Math.min(Math.max(1, p), totalPages.value);
  if (next === filters.page) return;
  filters.page = next;
  loadEvents();
}

async function downloadEventsXlsx() {
  xlsxNotice.value = "";
  try {
    const blob = await exportEventsXlsx(listQueryParams());
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `events-${new Date().toISOString().slice(0, 10)}.xlsx`;
    a.click();
    URL.revokeObjectURL(url);
  } catch (e) {
    error.value = "Не удалось выгрузить XLSX.";
  }
}

function openImportPicker() {
  xlsxInputRef.value?.click();
}

async function onImportXlsxChange(e) {
  const file = e.target.files?.[0];
  if (!file) return;
  xlsxNotice.value = "";
  try {
    const data = await importEventsXlsx(file);
    xlsxNotice.value = `Импортировано записей: ${data.imported}`;
    await loadEvents();
  } catch (e) {
    error.value = "Импорт XLSX не удался (нужны права администратора сайта).";
  }
  e.target.value = "";
}

async function loadPlacesForForm() {
  try {
    places.value = await fetchPlaces();
  } catch {
    places.value = [];
  }
}

async function submitEvent() {
  error.value = "";
  try {
    await createEvent({
      name: eventForm.name,
      description: eventForm.description,
      publish_at: normalizeDate(eventForm.publish_at),
      starts_at: normalizeDate(eventForm.starts_at),
      ends_at: normalizeDate(eventForm.ends_at),
      place: eventForm.place,
      rating: Number(eventForm.rating),
      status: eventForm.status,
      previewImage: previewImageFile.value,
      uploadedImages: galleryImageFiles.value,
    });
    Object.assign(eventForm, {
      name: "",
      description: "",
      publish_at: "",
      starts_at: "",
      ends_at: "",
      place: "",
      rating: 0,
      status: "draft",
    });
    previewImageFile.value = null;
    galleryImageFiles.value = [];
    if (previewInputRef.value) previewInputRef.value.value = "";
    if (galleryInputRef.value) galleryInputRef.value.value = "";
    await loadEvents();
  } catch (e) {
    error.value = "Создание мероприятия не удалось.";
  }
}

onMounted(() => {
  loadEvents();
  loadPlacesForForm();
});
</script>

<template>
  <main class="container">
    <h1>Мероприятия</h1>

    <section class="card">
      <h2>Фильтры</h2>
      <div class="grid">
        <div class="form-field">
          <label for="filter-search">Поиск по названию события или места</label>
          <input id="filter-search" v-model="filters.search" type="search" />
        </div>
        <div class="form-field">
          <label for="filter-ordering">Сортировка</label>
          <select id="filter-ordering" v-model="filters.ordering">
            <option value="name">По названию (A–Z)</option>
            <option value="starts_at">По дате начала</option>
            <option value="ends_at">По дате завершения</option>
            <option value="-starts_at">По дате начала (убыв.)</option>
            <option value="-ends_at">По дате завершения (убыв.)</option>
          </select>
        </div>
        <div class="form-field">
          <label for="filter-starts-from">Начало проведения не раньше</label>
          <input id="filter-starts-from" v-model="filters.starts_at_from" type="datetime-local" />
        </div>
        <div class="form-field">
          <label for="filter-starts-to">Начало проведения не позже</label>
          <input id="filter-starts-to" v-model="filters.starts_at_to" type="datetime-local" />
        </div>
      </div>
      <div class="row">
        <button type="button" @click="loadEvents">Обновить</button>
        <span>Всего: {{ total }}</span>
      </div>
    </section>

    <section class="card">
      <h2>Создать мероприятие</h2>
      <p class="muted">Список мест доступен только суперпользователю (страница «Места»).</p>
      <div class="grid">
        <div class="form-field">
          <label for="event-name">Название</label>
          <input id="event-name" v-model="eventForm.name" type="text" autocomplete="off" />
        </div>
        <div class="form-field form-field-span">
          <label for="event-description">Описание</label>
          <textarea id="event-description" v-model="eventForm.description" rows="3" />
        </div>
        <div class="form-field">
          <label for="event-publish-at">Дата и время публикации</label>
          <input id="event-publish-at" v-model="eventForm.publish_at" type="datetime-local" />
        </div>
        <div class="form-field">
          <label for="event-starts-at">Дата и время начала</label>
          <input id="event-starts-at" v-model="eventForm.starts_at" type="datetime-local" />
        </div>
        <div class="form-field">
          <label for="event-ends-at">Дата и время окончания</label>
          <input id="event-ends-at" v-model="eventForm.ends_at" type="datetime-local" />
        </div>
        <div class="form-field">
          <label for="event-place">Место проведения</label>
          <select id="event-place" v-model="eventForm.place">
            <option disabled value="">Выберите место</option>
            <option v-for="p in places" :key="p.id" :value="p.id">{{ p.name }}</option>
          </select>
        </div>
        <div class="form-field">
          <label for="event-rating">Рейтинг (0–25)</label>
          <input id="event-rating" v-model.number="eventForm.rating" type="number" min="0" max="25" />
        </div>
        <div class="form-field">
          <label for="event-status">Статус</label>
          <select id="event-status" v-model="eventForm.status">
            <option value="draft">Черновик</option>
            <option value="published">Опубликовано</option>
          </select>
        </div>
        <div class="form-field">
          <label for="event-preview-image">Обложка (необязательно)</label>
          <input
            id="event-preview-image"
            ref="previewInputRef"
            type="file"
            accept="image/*"
            @change="onPreviewChange"
          />
        </div>
        <div class="form-field form-field-span">
          <label for="event-gallery-images">Фотографии мероприятия (необязательно, можно несколько)</label>
          <input
            id="event-gallery-images"
            ref="galleryInputRef"
            type="file"
            accept="image/*"
            multiple
            @change="onGalleryChange"
          />
        </div>
      </div>
      <button type="button" @click="submitEvent">Создать</button>
    </section>

    <section class="card">
      <div class="list-head">
        <h2>Список</h2>
        <div v-if="canExportXlsx" class="row xlsx-actions">
          <button type="button" class="btn-secondary" @click="downloadEventsXlsx">
            Экспорт в XLSX
          </button>
          <template v-if="auth.isSuperuser">
            <input
              id="import-xlsx"
              ref="xlsxInputRef"
              type="file"
              accept=".xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
              class="visually-hidden"
              @change="onImportXlsxChange"
            />
            <button type="button" class="btn-secondary" @click="openImportPicker">
              Импорт из XLSX
            </button>
          </template>
        </div>
      </div>
      <p v-if="xlsxNotice" class="notice">{{ xlsxNotice }}</p>
      <p v-if="loading">Загрузка…</p>
      <p v-if="error" class="error">{{ error }}</p>
      <ul class="event-list">
        <li v-for="item in events" :key="item.id">
          <h3>{{ item.name }} <span class="status">({{ item.status }})</span></h3>
          <p>{{ item.description }}</p>
          <div v-if="item.preview_image" class="thumb-row">
            <img
              class="thumb"
              :src="resolveMediaUrl(item.preview_image)"
              alt=""
              loading="lazy"
            />
          </div>
          <div v-if="item.images?.length" class="thumb-row">
            <img
              v-for="img in item.images"
              :key="img.id"
              class="thumb"
              :src="resolveMediaUrl(img.image)"
              alt=""
              loading="lazy"
            />
          </div>
          <p><strong>Место:</strong> {{ item.place_data?.name }}</p>
          <p><strong>Рейтинг:</strong> {{ item.rating }}</p>
          <p>
            <strong>Проведение:</strong>
            {{ new Date(item.starts_at).toLocaleString() }} —
            {{ new Date(item.ends_at).toLocaleString() }}
          </p>
          <p v-if="item.weather">
            <strong>Погода:</strong> {{ item.weather.temperature }}°C, ветер
            {{ item.weather.wind_speed }} м/с {{ item.weather.wind_direction }}
          </p>
        </li>
      </ul>
      <div v-if="total > 0" class="pagination row pagination-bottom">
        <button type="button" :disabled="filters.page <= 1" @click="goToPage(filters.page - 1)">
          Назад
        </button>
        <span class="page-info">
          Страница {{ filters.page }} из {{ totalPages }} · всего {{ total }}
        </span>
        <button
          type="button"
          :disabled="filters.page >= totalPages"
          @click="goToPage(filters.page + 1)"
        >
          Вперёд
        </button>
      </div>
    </section>
  </main>
</template>

<style scoped>
.muted {
  color: #6b7280;
  font-size: 14px;
  margin-top: 0;
}

.status {
  font-weight: normal;
  color: #6b7280;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-field label {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.form-field-span {
  grid-column: 1 / -1;
}

.thumb-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 8px 0;
}

.thumb {
  max-width: 160px;
  max-height: 120px;
  object-fit: cover;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
}

.list-head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 8px;
}

.list-head h2 {
  margin: 0;
}

.xlsx-actions {
  flex-wrap: wrap;
}

.btn-secondary {
  background: #fff;
  color: #1f2937;
  border: 1px solid #d1d5db;
}

.btn-secondary:hover:not(:disabled) {
  background: #f9fafb;
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.notice {
  color: #059669;
  font-size: 14px;
  margin: 0 0 8px;
}

.pagination {
  margin: 12px 0;
  align-items: center;
}

.pagination-bottom {
  margin-top: 16px;
  margin-bottom: 0;
}

.page-info {
  font-size: 14px;
  color: #4b5563;
}

.pagination button:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
</style>
