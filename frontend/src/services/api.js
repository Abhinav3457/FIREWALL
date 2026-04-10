import axios from "axios";

const envBaseUrl = (import.meta.env.VITE_API_URL || "").trim();
const normalizedEnvBaseUrl = envBaseUrl
  ? `${envBaseUrl.replace(/\/+$/, "")}${envBaseUrl.replace(/\/+$/, "").endsWith("/api") ? "" : "/api"}`
  : "";

const api = axios.create({
  baseURL: normalizedEnvBaseUrl || "http://localhost:8000/api",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("cafw_token");
  if (token && token !== "undefined" && token !== "null") {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error?.response?.status === 401) {
      localStorage.removeItem("cafw_token");
      // Reload so App reads the cleared auth state and returns to login page.
      if (typeof window !== "undefined") {
        window.location.reload();
      }
    }
    return Promise.reject(error);
  }
);

export default api;
