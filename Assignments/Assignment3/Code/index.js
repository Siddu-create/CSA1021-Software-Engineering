import { createRouter, createWebHistory } from "vue-router";
import Dashboard from "../views/Dashboard.vue";
import Facilities from "../views/Facilities.vue";
import Bookings from "../views/Bookings.vue";
import Maintenance from "../views/Maintenance.vue";
import Login from "../views/Login.vue";

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", component: Dashboard },
    { path: "/facilities", component: Facilities },
    { path: "/bookings", component: Bookings },
    { path: "/maintenance", component: Maintenance },
    { path: "/login", component: Login }
  ]
});