
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../services/api";

function Register() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    full_name: "",
    email: "",
    password: "",
    phone: ""
  });

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // Cập nhật dữ liệu khi người dùng nhập vào biểu mẫu
  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value
    });
  };

  // Gửi thông tin đăng ký đến FastAPI
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await api.post("/auth/register", {
        ...form,
        phone: form.phone || null
      });

      navigate("/login");
    } catch (err) {
      const detail = err.response?.data?.detail;

      setError(
        typeof detail === "string"
          ? detail
          : "Đăng ký thất bại. Vui lòng kiểm tra thông tin."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="auth-page">
      <h2>Đăng ký tài khoản</h2>

      <form onSubmit={handleSubmit}>
        <input
          name="full_name"
          placeholder="Họ và tên"
          value={form.full_name}
          onChange={handleChange}
          minLength={2}
          required
        />

        <input
          name="email"
          type="email"
          placeholder="Email"
          value={form.email}
          onChange={handleChange}
          required
        />

        <input
          name="password"
          type="password"
          placeholder="Mật khẩu (ít nhất 8 ký tự)"
          value={form.password}
          onChange={handleChange}
          minLength={8}
          required
        />

        <input
          name="phone"
          type="tel"
          placeholder="Số điện thoại (không bắt buộc)"
          value={form.phone}
          onChange={handleChange}
        />

        {error && <p role="alert">{error}</p>}

        <button type="submit" disabled={loading}>
          {loading ? "Đang đăng ký..." : "Đăng ký"}
        </button>
      </form>

      <p>
        Đã có tài khoản? <Link to="/login">Đăng nhập</Link>
      </p>
    </main>
  );
}

export default Register;
