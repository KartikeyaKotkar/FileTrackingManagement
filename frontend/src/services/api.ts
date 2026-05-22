import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
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
    config.headers["X-User-Dept-Id"] = user.department_id ? user.department_id.toString() : "0";
  }
  return config;
});

export interface TagReadPayload {
  epc: string;
  readerName: string;
  antenna: number;
  timestamp: string;
  rssi: number;
  location: string;
}

export const postTagRead = async (payload: TagReadPayload) => {
  const response = await api.post("/api/tagreads", payload);
  return response.data;
};
