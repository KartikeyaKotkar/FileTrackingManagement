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

export interface TagReadRecord {
  id: number;
  epc: string;
  reader_name: string;
  antenna: number;
  timestamp: string;
  rssi: number;
  location: string;
  created_at: string;
}

export interface TagReadFilters {
  from_date?: string;
  to_date?: string;
  epc?: string;
  reader_name?: string;
}

export const postTagRead = async (payload: TagReadPayload) => {
  const response = await api.post("/api/tagreads", payload);
  return response.data;
};

export const getTagReads = async (filters?: TagReadFilters): Promise<TagReadRecord[]> => {
  const response = await api.get("/api/tagreads", { params: filters });
  return response.data.tag_reads;
};

export const downloadTagReadsExport = async (
  format: "csv" | "excel" | "pdf",
  filters?: TagReadFilters
): Promise<void> => {
  const response = await api.get(`/api/tagreads/export/${format}`, {
    params: filters,
    responseType: "blob",
  });
  
  const contentDisposition = response.headers["content-disposition"];
  let filename = `tag_reads_${new Date().toISOString().split("T")[0]}.${format === "excel" ? "xlsx" : format}`;
  if (contentDisposition) {
    const filenameMatch = contentDisposition.match(/filename=(.+)/);
    if (filenameMatch && filenameMatch[1]) {
      filename = filenameMatch[1].replace(/["']/g, "");
    }
  }

  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};
