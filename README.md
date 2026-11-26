
# HTTT16 – Hệ thống Quản lý Tour Du lịch Nội địa

## 1. Giới thiệu đề tài

Hệ thống quản lý và đặt tour du lịch nội địa,
được xây dựng nhằm hỗ trợ khách hàng tìm kiếm,
xem thông tin và đăng ký tour du lịch.

Hệ thống đồng thời hỗ trợ quản trị viên quản lý tour,
địa điểm, lịch khởi hành, khách hàng, hướng dẫn viên,
đơn đặt tour, thanh toán, đánh giá và thống kê doanh thu.

Dự án được phát triển theo mô hình Client – Server,
sử dụng ReactJS, Python FastAPI và MySQL.

## 2. Thông tin dự án

| Thông tin | Nội dung |
|---|---|
| Mã đề tài | HTTT16 |
| Tên đề tài | Hệ thống Quản lý Tour Du lịch Nội địa |
| Backend Version | 1.0.0 |
| Kiến trúc | Client – Server |
| API | RESTful API |
| Database | MySQL |
| Trạng thái | Đang phát triển Frontend |

## 3. Công nghệ sử dụng

### Frontend

- ReactJS
- Vite
- JavaScript
- HTML
- CSS

### Backend

- Python 3.11.5
- FastAPI
- SQLAlchemy ORM
- PyMySQL
- Pydantic
- Uvicorn
- PyJWT
- Argon2
- python-dotenv

### Database

- MySQL 9.3.0
- InnoDB
- UTF8MB4
- phpMyAdmin

### Công cụ phát triển

- Visual Studio Code
- Git
- GitHub
- Swagger UI
- PowerShell
- unittest

## 4. Kiến trúc hệ thống

```text
React Frontend
      |
      | HTTP / RESTful API / JSON
      |
FastAPI Backend
      |
      | SQLAlchemy ORM
      |
MySQL Database
```

Frontend giao tiếp với Backend thông qua RESTful API.

Backend chịu trách nhiệm xử lý nghiệp vụ,
xác thực, phân quyền, kiểm tra dữ liệu
và truy cập cơ sở dữ liệu.

## 5. Chức năng hệ thống

### 5.1. Khách vãng lai

- Xem danh sách tour du lịch.
- Tìm kiếm và lọc tour.
- Xem chi tiết tour.
- Xem địa điểm du lịch.
- Xem lịch khởi hành.
- Xem thông tin hướng dẫn viên công khai.
- Xem đánh giá tour.
- Đăng ký và đăng nhập.

### 5.2. Khách hàng

- Đăng nhập và đăng xuất.
- Quản lý thông tin cá nhân.
- Đổi mật khẩu.
- Tìm kiếm và lựa chọn tour.
- Đặt tour theo lịch khởi hành.
- Cung cấp thông tin hành khách.
- Xem lịch sử đặt tour.
- Theo dõi trạng thái đơn đặt tour.
- Hủy đơn đặt tour theo điều kiện.
- Tạo yêu cầu thanh toán.
- Theo dõi trạng thái thanh toán.
- Xem thông tin hướng dẫn viên khi đủ điều kiện.
- Đánh giá tour sau khi hoàn thành chuyến đi.
- Chỉnh sửa và xóa đánh giá của mình.

### 5.3. Quản trị viên

- Quản lý tài khoản khách hàng.
- Quản lý trạng thái tài khoản.
- Quản lý tour du lịch.
- Quản lý địa điểm du lịch.
- Quản lý địa điểm thuộc tour.
- Quản lý lịch khởi hành.
- Quản lý số lượng chỗ.
- Quản lý hướng dẫn viên.
- Phân công hướng dẫn viên.
- Kiểm tra trùng lịch hướng dẫn viên.
- Quản lý đơn đặt tour.
- Duyệt và từ chối đơn đặt tour.
- Xác nhận hoàn thành chuyến đi.
- Quản lý và xác nhận thanh toán.
- Quản lý đánh giá.
- Thống kê doanh thu.
- Theo dõi Dashboard quản trị.

Các chức năng trên đã được triển khai
ở phạm vi Backend chính.
Giao diện Frontend sẽ được hoàn thiện
trong giai đoạn tiếp theo.

## 6. Các module Backend

| STT | Module | Chức năng |
|---|---|---|
| 1 | Authentication | Xác thực người dùng |
| 2 | Users | Quản lý tài khoản |
| 3 | Tours | Quản lý tour |
| 4 | Destinations | Quản lý địa điểm |
| 5 | Tour Destinations | Địa điểm thuộc tour |
| 6 | Tour Schedules | Quản lý lịch khởi hành |
| 7 | Bookings | Quản lý đặt tour |
| 8 | Payments | Quản lý thanh toán |
| 9 | Guides | Quản lý hướng dẫn viên |
| 10 | Guide Assignments | Phân công hướng dẫn viên |
| 11 | Reviews | Quản lý đánh giá |
| 12 | Dashboard | Thống kê quản trị |

Tại mốc Backend v1.0.0:

- 12 module nghiệp vụ.
- 56 API Paths.
- 72 API Operations.
- 11 bảng Database.

## 7. Cơ sở dữ liệu

Tên Database:

```text
quan_ly_tour_du_lich
```

Danh sách các bảng:

| STT | Tên bảng |
|---|---|
| 1 | users |
| 2 | destinations |
| 3 | tours |
| 4 | tour_destinations |
| 5 | tour_schedules |
| 6 | tour_guides |
| 7 | guide_assignments |
| 8 | bookings |
| 9 | booking_passengers |
| 10 | payments |
| 11 | reviews |

Database sử dụng:

- Primary Key.
- Foreign Key.
- Unique Key.
- AUTO_INCREMENT.
- InnoDB Storage Engine.
- Transaction.
- Row-Level Locking.

File khởi tạo Database:

```text
database/quan_ly_tour_du_lich.sql
```

File SQL chỉ chứa cấu trúc Database,
không chứa dữ liệu tài khoản hoặc khách hàng.

Xem thêm:
[Database README](database/README.md).

## 8. Bảo mật hệ thống

Backend đã triển khai các cơ chế:

- JWT Authentication.
- Role-Based Access Control.
- Argon2 Password Hashing.
- Login Rate Limiting.
- Token Version.
- Token Revocation.
- Data Validation.
- Input Normalization.
- Unicode Validation Error Handling.
- Money Validation.
- Search và Pagination Validation.
- CORS Configuration.
- Database Transaction.
- Database Error Handling.
- HTTP Security Header.
- Bảo vệ dữ liệu cá nhân trong API Response.

Các thông tin bí mật được cấu hình
thông qua biến môi trường.

Không đưa mật khẩu, JWT Secret Key,
Access Token hoặc dữ liệu cá nhân lên GitHub.

## 9. Cấu trúc dự án

```text
QL_TourDL/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routers/
│   │   ├── services/
│   │   ├── database.py
│   │   └── main.py
│   ├── tests/
│   ├── .env.example
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── src/
│   └── package.json
├── database/
│   ├── migrations/
│   ├── quan_ly_tour_du_lich.sql
│   └── README.md
├── docs/
│   └── frontend_security.md
├── .gitignore
└── README.md
```

Các thành phần được tạo riêng trên mỗi máy:

- backend/venv/
- backend/.env
- frontend/node_modules/

## 10. Yêu cầu môi trường

Trước khi chạy dự án, cần chuẩn bị:

- Python 3.11.5.
- MySQL Server 9.3.0.
- Node.js LTS tương thích với Vite.
- npm.
- Git.
- Visual Studio Code.
- phpMyAdmin hoặc MySQL Client.

Các phiên bản Python và MySQL trên
là phiên bản đã sử dụng trong quá trình phát triển.

## 11. Hướng dẫn cài đặt Backend

Sau khi Git Clone dự án:

### 11.1. Tạo môi trường Python

```powershell
cd backend

python -m venv venv

.\venv\Scripts\Activate.ps1

python -m pip install -r requirements.txt
```

### 11.2. Khởi tạo Database

Khởi động MySQL Server.

Import file:

```text
database/quan_ly_tour_du_lich.sql
```

Không chạy lại các Migration
nếu đã sử dụng file SQL mới nhất.

### 11.3. Cấu hình biến môi trường

Trong thư mục backend,
tạo file .env từ .env.example nếu chưa tồn tại.

```powershell
Copy-Item .env.example .env
```

Cập nhật thông tin MySQL phù hợp
với môi trường local.

Tạo JWT Secret Key riêng:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Điền kết quả vào JWT_SECRET_KEY
trong file .env.

### 11.4. Khởi động Backend

```powershell
python -m uvicorn app.main:app --reload --port 8001
```

Truy cập:

- Backend: http://127.0.0.1:8001
- Swagger UI: http://127.0.0.1:8001/docs
- Health Check: http://127.0.0.1:8001/api/health

Hướng dẫn chi tiết:
[Backend README](backend/README.md).

## 12. Hướng dẫn chạy Frontend

Mở Terminal mới tại thư mục gốc dự án.

```powershell
cd frontend

node --version

npm --version

npm install

npm run dev
```

Nếu dự án có package-lock.json hợp lệ,
có thể sử dụng npm ci thay cho npm install
để cài đặt đúng phiên bản đã khóa.

Địa chỉ Frontend mặc định:

```text
http://localhost:5173
```

Địa chỉ Backend API:

```text
http://127.0.0.1:8001
```

Backend và Frontend cần chạy đồng thời
khi kiểm thử chức năng tích hợp API.

## 13. Kiểm thử hệ thống

Các phương pháp kiểm thử đã sử dụng:

- Unit Testing.
- Mock Integration Testing.
- HTTP API Testing.
- Authentication Testing.
- Authorization Testing.
- Privacy Testing.
- Search Validation Testing.
- Text Security Testing.
- Money Validation Testing.
- Database Consistency Testing.

Kết quả tại các mốc kiểm thử Backend trước đó:

| Hạng mục | Kết quả |
|---|---|
| Unit Test và Mock Test | 557/557 |
| Database Tables | 11 |
| InnoDB Tables | 11/11 |
| Database Consistency Checks | 10/10 |

Các kết quả trên phản ánh những bài kiểm thử
đã thực hiện tại từng mốc phát triển.

Chưa phải kết quả kiểm thử toàn bộ hệ thống
trong môi trường Production.

## 14. Quy trình làm việc nhóm

Các thành viên sử dụng chung mã nguồn GitHub,
nhưng có môi trường phát triển riêng.

Mỗi thành viên cần tự tạo:

- Python Virtual Environment.
- File .env.
- JWT Secret Key.
- MySQL Database local.
- Tài khoản kiểm thử.
- Dữ liệu nghiệp vụ mẫu.

Trước khi bắt đầu phát triển:

```powershell
git switch main

git pull --ff-only origin main
```

Chỉ chuyển nhánh và cập nhật khi đã xử lý
các thay đổi local chưa được lưu.

Tạo nhánh phát triển riêng:

```powershell
git switch -c feature/frontend
```

Tên nhánh cần phù hợp với công việc được phân công.

Sau khi hoàn thành chức năng:

```powershell
git status

git diff --check

git add .
```

Kiểm tra nội dung đã stage:

```powershell
git diff --cached --stat

git diff --cached --check

git diff --cached --name-only
```

Sau khi xác nhận không chứa dữ liệu bí mật:

```powershell
git commit -m "feat(frontend): cap nhat chuc nang"

git push -u origin HEAD
```

Sử dụng Pull Request để kiểm tra
và hợp nhất mã nguồn vào nhánh chính.

## 15. Quy định bảo mật mã nguồn

Không Commit các thành phần:

- File .env.
- Thư mục venv.
- Thư mục node_modules.
- JWT Secret Key.
- Access Token.
- Mật khẩu.
- Password Hash.
- Database Dump chứa dữ liệu thật.
- Thông tin cá nhân của khách hàng.

Chỉ sử dụng dữ liệu giả lập
trong môi trường phát triển và kiểm thử.

## 16. Tiến độ thực hiện

### Giai đoạn 1 – Phân tích và thiết kế

- [x] Phân tích yêu cầu đề tài.
- [x] Xác định các chức năng nghiệp vụ chính.
- [x] Thiết kế cơ sở dữ liệu.

### Giai đoạn 2 – Database Development

- [x] Khởi tạo MySQL Database.
- [x] Xây dựng 11 bảng dữ liệu.
- [x] Thiết lập các ràng buộc dữ liệu.
- [x] Chuẩn hóa Database Schema.
- [x] Bổ sung Database Migration.
- [x] Kiểm tra tính nhất quán dữ liệu.

### Giai đoạn 3 – Backend Development

- [x] Khởi tạo FastAPI.
- [x] Kết nối MySQL.
- [x] Xây dựng Models và Schemas.
- [x] Xây dựng RESTful API.
- [x] Xây dựng Authentication.
- [x] Xây dựng Authorization.
- [x] Hoàn thiện 12 module nghiệp vụ chính.
- [x] Bổ sung các cơ chế bảo mật Backend.
- [x] Kiểm thử Backend theo phạm vi đã xác định.

### Giai đoạn 4 – Developer Environment Setup

- [x] Chuẩn hóa requirements.txt.
- [x] Chuẩn bị .env.example.
- [x] Chuẩn hóa .gitignore.
- [x] Chuẩn hóa Database Schema.
- [x] Xây dựng Backend README.
- [x] Cập nhật README dự án.
- [X] Hoàn thiện hướng dẫn Developer Setup.
- [X] Xây dựng script dữ liệu mẫu.
- [X] Kiểm thử môi trường sau Git Clone.

### Giai đoạn 5 – React Frontend Development

- [x] Khởi tạo ReactJS và Vite ban đầu.
- [x] Xây dựng giao diện và điều hướng ban đầu.
- [ ] Chuẩn hóa cấu trúc Frontend.
- [ ] Cấu hình kết nối Backend API.
- [ ] Xây dựng Authentication Frontend.
- [ ] Xây dựng giao diện khách hàng.
- [ ] Xây dựng giao diện quản trị viên.
- [ ] Tích hợp các module Backend.
- [ ] Responsive Design.
- [ ] Kiểm thử Frontend.

### Giai đoạn 6 – Hoàn thiện hệ thống

- [ ] System Integration Testing.
- [ ] Kiểm thử bảo mật trên trình duyệt.
- [ ] Hoàn thiện các yêu cầu Production.
- [ ] Hoàn thiện UML.
- [ ] Hoàn thiện báo cáo đồ án.
- [ ] Deployment.

## 17. Giới hạn hiện tại

Backend đã hoàn thành phạm vi nghiệp vụ chính
và sẵn sàng tích hợp React Frontend.

Các nội dung cần tiếp tục hoàn thiện:

- HTTPS và HSTS.
- Content Security Policy.
- Request Body Size Limit.
- Distributed Rate Limiting.
- Kiểm thử đồng thời nâng cao.
- Date và Path Validation.
- Kiểm thử bảo mật Frontend.
- Kiểm thử lại các trường hợp đã bỏ qua.

Thanh toán hiện tại sử dụng xác nhận thủ công,
chưa tích hợp cổng thanh toán thực tế.

## 18. Thành viên thực hiện

| STT | Họ và tên | MSSV |
|---|---|---|---|
| 1 | Bùi Anh Dũng | 23050155 |
| 2 | Nguyễn Quang Hoài Đức | 23050181 |

## 19. Tài liệu liên quan

- [Backend Documentation](backend/README.md)
- [Database Documentation](database/README.md)
- [Frontend Security](docs/frontend_security.md)

## 20. Trạng thái dự án

Backend v1.0.0 đã hoàn thành phạm vi nghiệp vụ chính.

Dự án đang chuẩn bị môi trường làm việc nhóm
và chuyển sang giai đoạn React Frontend Development.

Hệ thống Quản lý Tour Du lịch Nội địa.
