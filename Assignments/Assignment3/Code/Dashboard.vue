<template>
  <section>
    <p class="eyebrow">CAMPUS OPERATIONS</p>
    <h1>Smart Campus Dashboard</h1>
    <p class="muted">A central place to discover facilities, request bookings and report maintenance issues.</p>
    <div class="grid">
      <router-link class="panel link-panel" to="/facilities">
        <div class="panel-icon">▦</div><h2>Facilities</h2>
        <p>Browse rooms, labs and shared campus spaces.</p><span>View facilities →</span>
      </router-link>
      <router-link class="panel link-panel" to="/bookings">
        <div class="panel-icon">▣</div><h2>Bookings</h2>
        <p>Submit and review facility booking requests.</p><span>Manage bookings →</span>
      </router-link>
      <router-link class="panel link-panel" to="/maintenance">
        <div class="panel-icon">⚙</div><h2>Maintenance</h2>
        <p>Raise and track campus maintenance tickets.</p><span>Open maintenance →</span>
      </router-link>
    </div>
    <div class="notice">Sign in through the Login page before submitting bookings or maintenance tickets.</div>
  </section>
</template>