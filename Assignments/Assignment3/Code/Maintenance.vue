<template>
  <section>
    <p class="eyebrow">CAMPUS UPKEEP</p><h1>Maintenance</h1>
    <div class="two-col">
      <form class="panel form" @submit.prevent="createTicket">
        <h2>Report an issue</h2>
        <label>Facility
          <select v-model.number="form.facility" required>
            <option disabled value="">Select a facility</option>
            <option v-for="f in facilities" :key="f.id" :value="f.id">{{ f.name }} (ID {{ f.id }})</option>
          </select>
        </label>
        <label>Issue title<input v-model="form.title" required maxlength="200" /></label>
        <label>Description<textarea v-model="form.description" rows="4" required /></label>
        <label>Priority<select v-model="form.priority"><option>LOW</option><option>MEDIUM</option><option>HIGH</option><option>CRITICAL</option></select></label>
        <button :disabled="busy">{{ busy ? "Submitting…" : "Submit ticket" }}</button>
        <p v-if="message" :class="messageType">{{ message }}</p>
      </form>
      <div>
        <h2>Maintenance tickets</h2><button class="secondary" @click="loadTickets">Refresh list</button>
        <p v-if="!tickets.length" class="muted">No tickets to display, or sign in to view tickets.</p>
        <article v-for="t in tickets" :key="t.id" class="panel compact">
          <strong>{{ t.title }}</strong><span class="tag">{{ t.status }}</span>
          <p>{{ t.description }}</p><p>Facility ID: {{ t.facility }} · Priority: {{ t.priority }}</p>
        </article>
      </div>
    </div>
  </section>
</template>
<script setup>
import { ref, reactive, onMounted } from "vue";
import api from "../services/api";
const facilities = ref([]), tickets = ref([]), message = ref(""), messageType = ref("muted"), busy = ref(false);
const form = reactive({ facility: "", title: "", description: "", priority: "MEDIUM" });
async function loadFacilities() {
  try { const { data } = await api.get("facilities/"); facilities.value = data.results ?? data; } catch {}
}
async function loadTickets() {
  try { const { data } = await api.get("tickets/"); tickets.value = data.results ?? data; }
  catch { message.value = "Sign in before viewing maintenance tickets."; messageType.value = "error"; }
}
async function createTicket() {
  busy.value = true; message.value = "";
  try {
    await api.post("tickets/", form);
    message.value = "Maintenance ticket submitted."; messageType.value = "success";
    Object.assign(form, { facility: "", title: "", description: "", priority: "MEDIUM" });
    await loadTickets();
  } catch (e) {
    message.value = e.response?.data ? JSON.stringify(e.response.data) : "Ticket submission failed. Sign in and check the backend.";
    messageType.value = "error";
  } finally { busy.value = false; }
}
onMounted(async () => { await loadFacilities(); await loadTickets(); });
</script>