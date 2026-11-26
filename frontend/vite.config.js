import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// Cấu hình Vite cho hệ thống quản lý Tour du lịch
export default defineConfig({
  plugins: [
    react(),
    tailwindcss()
  ]
});