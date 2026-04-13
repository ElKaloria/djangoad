<script setup>
import { onMounted, reactive, ref } from "vue";
import { createPlace, fetchPlaces } from "../api";

const loading = ref(false);
const error = ref("");
const places = ref([]);

const form = reactive({
  name: "",
  latitude: "",
  longitude: "",
});

async function load() {
  loading.value = true;
  error.value = "";
  try {
    places.value = await fetchPlaces();
  } catch (e) {
    error.value = "Нет доступа к местам или ошибка API.";
  } finally {
    loading.value = false;
  }
}

async function submit() {
  error.value = "";
  try {
    await createPlace({
      name: form.name,
      latitude: Number(form.latitude),
      longitude: Number(form.longitude),
    });
    form.name = "";
    form.latitude = "";
    form.longitude = "";
    await load();
  } catch (e) {
    error.value = "Не удалось создать место.";
  }
}

onMounted(load);
</script>

<template>
  <main class="container">
    <h1>Места проведения</h1>
    <p class="lead">Раздел только для суперпользователя.</p>

    <section class="card">
      <h2>Новое место</h2>
      <div class="grid">
        <input v-model="form.name" placeholder="Название" />
        <input v-model="form.latitude" placeholder="Широта" type="number" step="0.000001" />
        <input v-model="form.longitude" placeholder="Долгота" type="number" step="0.000001" />
      </div>
      <button type="button" @click="submit">Добавить</button>
    </section>

    <section class="card">
      <h2>Список</h2>
      <div class="row">
        <button type="button" class="secondary" @click="load">Обновить</button>
      </div>
      <p v-if="loading">Загрузка…</p>
      <p v-if="error" class="error">{{ error }}</p>
      <ul class="place-list">
        <li v-for="p in places" :key="p.id">
          <strong>{{ p.name }}</strong>
          <span v-if="p.geo_location" class="coords">
            {{ Number(p.geo_location.latitude).toFixed(4) }},
            {{ Number(p.geo_location.longitude).toFixed(4) }}
          </span>
        </li>
      </ul>
    </section>
  </main>
</template>

<style scoped>
.lead {
  color: #6b7280;
  margin-bottom: 20px;
}

.place-list {
  list-style: none;
  margin: 12px 0 0;
  padding: 0;
}

.place-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid #f3f4f6;
}

.coords {
  font-size: 13px;
  color: #6b7280;
  font-variant-numeric: tabular-nums;
}
</style>
