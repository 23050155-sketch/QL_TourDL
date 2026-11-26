import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { Toaster } from "sonner";

import "./index.css";
import App from "./App.jsx";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <App />

    {/* Hệ thống thông báo dùng chung */}
    <Toaster
      position="top-right"
      richColors
      closeButton
      duration={4000}
      visibleToasts={3}
      theme="light"
      expand={false}
    />
  </StrictMode>
);