<template>
  <div>
    <header class="topbar">
      <router-link class="brand" to="/">Smart Campus</router-link>
      <nav>
        <router-link to="/">Dashboard</router-link>
        <router-link to="/facilities">Facilities</router-link>
        <router-link to="/bookings">Bookings</router-link>
        <router-link to="/maintenance">Maintenance</router-link>
        <router-link to="/login">Login</router-link>
      </nav>
    </header>
    <main class="container"><router-view /></main>
    <footer>Smart Campus Facility Booking and Maintenance Platform</footer>
  </div>
</template>