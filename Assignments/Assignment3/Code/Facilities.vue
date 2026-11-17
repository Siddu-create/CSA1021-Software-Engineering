<template>
  <section>
    <div class="page-heading"><div><p class="eyebrow">DISCOVER</p><h1>Campus Facilities</h1></div><button class="secondary" @click="load">Refresh</button></div>
    <p v-if="loading" class="muted">Loading facilities…</p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <div v-else class="grid">
      <article v-for="facility in facilities" :key="facility.id" class="panel">
        <div class="tag" :class="facility.is_available ? 'good' : 'bad'">{{ facility.is_available ? "Available" : "Unavailable" }}</div>
        <h2>{{ facility.name }}</h2><p class="muted">{{ facility.location }}</p>
        <p>{{ facility.description || "No description provided." }}</p>
        <div class="meta">Capacity: {{ facility.capacity }}</div>
        <div class="meta">{{ facility.restricted ? "Restricted facility" : "General access" }}</div>
      </article>
      <p v-if="!facilities.length" class="muted">No facilities have been added yet. Add them through Django admin.</p>
    </div>
  </section>
</template>
<script setup>
import { ref, onMounted } from "vue";
import api from "../services/api";
const facilities = ref([]), loading = ref(true), error = ref("");
async function load() {
  loading.value = true; error.value = "";
  try { const { data } = await api.get("facilities/"); facilities.value = data.results ?? data; }
  catch { error.value = "Could not load facilities. Check that the backend is running and the API is reachable."; }
  finally { loading.value = false; }
}
onMounted(load);
</script>