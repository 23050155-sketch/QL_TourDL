
import { useEffect, useState } from "react";
import api from "../../../services/api";

function Tours() {
  const [tours, setTours] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchTours() {
      try {
        const response = await api.get("/tours/");
        setTours(response.data);
      } catch (err) {
        console.error(err);
        setError("Không thể tải danh sách tour.");
      } finally {
        setLoading(false);
      }
    }

    fetchTours();
  }, []);

  if (loading) {
    return <main className="page-content">Đang tải tour...</main>;
  }

  if (error) {
    return <main className="page-content">{error}</main>;
  }

  return (
    <main className="page-content">
      <h1>Danh sách tour du lịch</h1>

      {tours.length === 0 ? (
        <p>Hiện chưa có tour nào.</p>
      ) : (
        <div className="tour-grid">
          {tours.map((tour) => (
            <div className="tour-card" key={tour.id}>
              {tour.image_url && (
                <img
                  src={tour.image_url}
                  alt={tour.title}
                  className="tour-image"
                />
              )}

              <div className="tour-content">
                <h3>{tour.title}</h3>

                <p>
                  Thời gian: {tour.duration_days} ngày,
                  {" "}{tour.duration_nights} đêm
                </p>

                <p className="tour-price">
                  {Number(tour.base_price).toLocaleString("vi-VN")} đ
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}

export default Tours;
