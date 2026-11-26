import { BrowserRouter, Routes, Route } from "react-router-dom";

// Import Component Customer
import Header from "./components/customer/Header";

// Import các trang Customer
import Home from "./pages/customer/home/Home";
import Tours from "./pages/customer/tours/Tours";

// Import các trang xác thực
import Login from "./pages/auth/Login";
import Register from "./pages/auth/Register";

// Import CSS
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
