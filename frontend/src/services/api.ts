import axios from "axios";

export const api = axios.create({
  baseURL: "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  const userStr = localStorage.getItem("user");
  if (userStr) {
    const user = JSON.parse(userStr);
    config.headers["X-User-Role"] = user.role_id === 1 ? "admin" : "user";
    config.headers["X-User-Id"] = user.id.toString();
  }
  return config;
});
