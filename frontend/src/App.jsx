
import { BrowserRouter, Routes, Route } from "react-router-dom";

import Header from "./components/Header";
import Home from "./pages/Home";
import Tours from "./pages/Tours";
import Login from "./pages/Login";
import Register from "./pages/Register";

import "./App.css";

function App() {
  return (
    <BrowserRouter>
      <Header />

      {/* Điều hướng giữa các trang của hệ thống */}
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/tours" element={<Tours />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
