
import { Link } from "react-router-dom";
import { Search, MapPin, CalendarDays } from "lucide-react";

function Home() {
  return (
    <main>
      <section className="hero">
        <div className="hero-content">
          <h1>Khám phá vẻ đẹp Việt Nam</h1>
          <p>
            Hành trình tuyệt vời bắt đầu từ đây.
            Khám phá những điểm đến hấp dẫn trên khắp Việt Nam.
          </p>

          <Link to="/tours" className="explore-btn">
            <Search size={19} />
            Khám phá tour ngay
          </Link>
        </div>
      </section>

      <section className="features">
        <h2>Tại sao chọn VietTour?</h2>

        <div className="feature-grid">
          <div className="feature-card">
            <MapPin size={32} />
            <h3>Điểm đến đa dạng</h3>
            <p>Khám phá những địa danh nổi tiếng Việt Nam.</p>
          </div>

          <div className="feature-card">
            <CalendarDays size={32} />
            <h3>Lịch trình linh hoạt</h3>
            <p>Dễ dàng lựa chọn thời gian phù hợp.</p>
          </div>

          <div className="feature-card">
            <Search size={32} />
            <h3>Đặt tour dễ dàng</h3>
            <p>Tìm kiếm và đăng ký tour nhanh chóng.</p>
          </div>
        </div>
      </section>
    </main>
  );
}

export default Home;
