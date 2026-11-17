import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/",
  withCredentials: true,
  headers: { "Content-Type": "application/json" }
});

// Django session authentication: send the CSRF cookie on unsafe requests.
api.interceptors.request.use((config) => {
  const csrf = document.cookie
    .split("; ")
    .find((item) => item.startsWith("csrftoken="))
    ?.split("=")[1];
  if (csrf && !["get", "head", "options"].includes((config.method || "get").toLowerCase())) {
    config.headers["X-CSRFToken"] = decodeURIComponent(csrf);
  }
  return config;
});

export default api;