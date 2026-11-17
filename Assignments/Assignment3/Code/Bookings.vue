<template>
  <section>
    <p class="eyebrow">RESERVATIONS</p><h1>Facility Bookings</h1>
    <div class="two-col">
      <form class="panel form" @submit.prevent="createBooking">
        <h2>Request a booking</h2>
        <label>Facility
          <select v-model.number="form.facility" required>
            <option disabled value="">Select a facility</option>
            <option v-for="f in facilities" :key="f.id" :value="f.id">{{ f.name }} (ID {{ f.id }})</option>
          </select>
        </label>
        <label>Start time<input v-model="form.start_time" type="datetime-local" required /></label>
        <label>End time<input v-model="form.end_time" type="datetime-local" required /></label>
        <label>Purpose<input v-model="form.purpose" required maxlength="250" /></label>
        <button :disabled="busy">{{ busy ? "Submitting…" : "Submit booking" }}</button>
        <p v-if="message" :class="messageType">{{ message }}</p>
      </form>
      <div>
        <h2>My booking requests</h2>
        <button class="secondary" @click="loadBookings">Refresh list</button>
        <p v-if="!bookings.length" class="muted">No bookings to display, or sign in to view your requests.</p>
        <article v-for="b in bookings" :key="b.id" class="panel compact">
          <strong>Booking #{{ b.id }}</strong><span class="tag">{{ b.status }}</span>
          <p>Facility ID: {{ b.facility }}</p><p>{{ b.start_time }} – {{ b.end_time }}</p><p>{{ b.purpose }}</p>
        </article>
      </div>
    </div>
  </section>
</template>
<script setup>
import { ref, reactive, onMounted } from "vue";
import api from "../services/api";
const facilities = ref([]), bookings = ref([]), message = ref(""), messageType = ref("muted"), busy = ref(false);
const form = reactive({ facility: "", start_time: "", end_time: "", purpose: "" });
async function loadFacilities() {
  try { const { data } = await api.get("facilities/"); facilities.value = data.results ?? data; } catch {}
}
async function loadBookings() {
  try { const { data } = await api.get("bookings/"); bookings.value = data.results ?? data; }
  catch { message.value = "Sign in before viewing your bookings."; messageType.value = "error"; }
}
async function createBooking() {
  busy.value = true; message.value = "";
  try {
    await api.post("bookings/", { ...form, start_time: new Date(form.start_time).toISOString(), end_time: new Date(form.end_time).toISOString() });
    message.value = "Booking request submitted."; messageType.value = "success";
    Object.assign(form, { facility: "", start_time: "", end_time: "", purpose: "" });
    await loadBookings();
  } catch (e) {
    message.value = e.response?.data ? JSON.stringify(e.response.data) : "Booking failed. Sign in and check the backend.";
    messageType.value = "error";
  } finally { busy.value = false; }
}
onMounted(async () => { await loadFacilities(); await loadBookings(); });
</script>