import axios from "axios";

// Cấu hình kết nối API đến Backend FastAPI
const api = axios.create({
  baseURL: "http://127.0.0.1:8001/api",
  timeout: 10000
});

// Tự động gửi JWT cho các API cần xác thực
api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem("access_token");

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

export default api;