# HTTT16 – Hệ thống Quản lý Tour Du lịch Nội địa

## 1. Giới thiệu đề tài

Dự án xây dựng website quản lý và đặt tour du lịch nội địa, hỗ trợ khách hàng tìm kiếm, xem thông tin và đăng ký tour; đồng thời giúp quản trị viên quản lý tour, lịch khởi hành, khách hàng, hướng dẫn viên, đơn đặt tour và doanh thu.

Đây là đồ án phát triển ứng dụng sử dụng ReactJS, Python FastAPI và MySQL.

## 2. Công nghệ sử dụng

| Thành phần | Công nghệ |
|---|---|
| Frontend | ReactJS, Vite |
| Backend | Python, FastAPI |
| Database | MySQL (XAMPP) |
| ORM | SQLAlchemy |
| API | RESTful API |
| Xác thực | JWT |
| Công cụ | VS Code, Git, GitHub, phpMyAdmin |

## 3. Chức năng dự kiến

### Khách hàng
- Đăng ký, đăng nhập và đăng xuất.
- Tìm kiếm, xem danh sách và chi tiết tour.
- Đặt tour theo lịch khởi hành.
- Xem lịch sử đặt tour.
- Theo dõi trạng thái thanh toán.
- Đánh giá tour sau khi tham gia.

### Quản trị viên
- Quản lý tài khoản khách hàng.
- Thêm, sửa, xóa và tìm kiếm tour.
- Quản lý lịch khởi hành và số lượng chỗ.
- Quản lý và phân công hướng dẫn viên.
- Duyệt đơn đặt tour.
- Quản lý thanh toán và phản hồi.
- Thống kê doanh thu.

## 4. Cấu trúc dự án

```text
QL_TourDL/
├── frontend/       # ReactJS + Vite
├── backend/        # Python FastAPI
├── database/       # Các file SQL
├── docs/           # Tài liệu và sơ đồ UML
├── .gitignore
└── README.md
```

## 5. Tiến độ thực hiện

- [x] Phân tích yêu cầu ban đầu của đề tài.
- [x] Khởi tạo ReactJS bằng Vite.
- [x] Xây dựng giao diện trang chủ ban đầu.
- [x] Xây dựng thanh điều hướng.
- [x] Tạo cơ sở dữ liệu MySQL.
- [x] Tạo 11 bảng dữ liệu.
- [ ] Kết nối FastAPI với MySQL.
- [ ] Xây dựng RESTful API quản lý tour.
- [ ] Xây dựng đăng nhập và phân quyền JWT.
- [ ] Hoàn thiện nghiệp vụ đặt tour.
- [ ] Hoàn thiện giao diện quản trị.
- [ ] Kiểm thử hệ thống.
- [ ] Hoàn thành UML và báo cáo.

## 6. Hướng dẫn chạy Frontend

Yêu cầu: Đã cài Node.js và npm.

```bash
cd frontend
npm install
npm run dev
```

Truy cập địa chỉ được Vite hiển thị, thông thường là:

`http://localhost:5173`

## 7. Cơ sở dữ liệu

Tên database: `quan_ly_tour_du_lich`

Hệ quản trị: MySQL thông qua XAMPP/phpMyAdmin.

Các bảng hiện có:

1. users
2. destinations
3. tours
4. tour_destinations
5. tour_schedules
6. tour_guides
7. guide_assignments
8. bookings
9. booking_passengers
10. payments
11. reviews

## 8. Ghi chú phát triển

**Giai đoạn 1 – Hoàn thành**

- Khởi tạo môi trường Frontend.
- Cài đặt các thư viện ReactJS.
- Xây dựng giao diện ban đầu và hệ thống điều hướng.

**Giai đoạn 2 – Hoàn thành**

- Thiết kế cơ sở dữ liệu quan hệ.
- Tạo thành công 11 bảng trên MySQL.
- Xác định các quan hệ khóa chính, khóa ngoại.

**Giai đoạn 3 – Chuẩn bị thực hiện**

- Cấu hình Python FastAPI.
- Kết nối MySQL bằng SQLAlchemy.
- Xây dựng API lấy danh sách và chi tiết tour.
- Kết nối API với giao diện ReactJS.

## 9. Thành viên thực hiện

- Sinh viên 1: Chưa cập nhật.
- Sinh viên 2: Chưa cập nhật.

## 10. Trạng thái dự án

Đang phát triển – Frontend cơ bản và Database đã hoàn thành; Backend và các chức năng nghiệp vụ đang được triển khai.
