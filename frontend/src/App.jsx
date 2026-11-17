
import { BrowserRouter, Routes, Route } from "react-router-dom";

import Header from "./components/Header";
import Home from "./pages/Home";
import Tours from "./pages/Tours";

import "./App.css";

function App() {
  return (
    <BrowserRouter>
      <Header />

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/tours" element={<Tours />} />
        <Route
          path="/login"
          element={<div className="page-content"><h1>Đăng nhập</h1></div>}
        />
        <Route
          path="/register"
          element={<div className="page-content"><h1>Đăng ký</h1></div>}
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
