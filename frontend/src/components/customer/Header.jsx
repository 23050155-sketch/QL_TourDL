
import { Link } from "react-router-dom";
import { Plane, UserRound } from "lucide-react";

function Header() {
  return (
    <header className="header">
      <Link to="/" className="logo">
        <Plane size={26} />
        <span>VietTour</span>
      </Link>

      <nav className="nav">
        <Link to="/">Trang chủ</Link>
        <Link to="/tours">Danh sách tour</Link>
        <Link to="/login">Đăng nhập</Link>
        <Link to="/register" className="register-btn">
          <UserRound size={17} />
          Đăng ký
        </Link>
      </nav>
    </header>
  );
}

export default Header;
