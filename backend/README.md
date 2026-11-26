
# Backend – HTTT16

## 1. Giới thiệu

Backend của hệ thống Quản lý Tour Du lịch Nội địa
được xây dựng bằng Python FastAPI, cung cấp RESTful API
cho giao diện ReactJS và kết nối cơ sở dữ liệu MySQL
thông qua SQLAlchemy ORM.

- Phiên bản Backend: 1.0.0
- Python: 3.11.5
- Database: MySQL 9.3.0
- API Port: 8001
- API Documentation: Swagger / OpenAPI

## 2. Công nghệ sử dụng

- Python
- FastAPI
- SQLAlchemy
- PyMySQL
- Pydantic
- JWT (PyJWT)
- Argon2
- python-dotenv
- Uvicorn
- unittest

## 3. Các module nghiệp vụ

1. Authentication
2. Users
3. Tours
4. Destinations
5. Tour Destinations
6. Tour Schedules
7. Bookings
8. Payments
9. Guides
10. Guide Assignments
11. Reviews
12. Dashboard

## 4. Cấu trúc Backend

```text
backend/
├── app/
│   ├── core/
│   ├── models/
│   ├── schemas/
│   ├── routers/
│   ├── services/
│   ├── database.py
│   └── main.py
├── tests/
├── .env.example
├── requirements.txt
└── README.md
```

Các thành phần được tạo riêng trên mỗi máy:

- venv/
- .env

Không đưa hai thành phần này lên GitHub.

## 5. Yêu cầu môi trường

Cài đặt các phần mềm sau trước khi chạy Backend:

- Python 3.11.5
- MySQL Server 9.3.0
- Git
- Visual Studio Code
- phpMyAdmin hoặc MySQL Client

Có thể sử dụng phiên bản tương thích khác,
nhưng cần kiểm thử lại trước khi phát triển.

## 6. Cài đặt Backend

Sau khi Git Clone dự án, mở PowerShell
tại thư mục gốc QL_TourDL.

### 6.1. Di chuyển vào thư mục Backend

```powershell
cd backend
```

### 6.2. Kiểm tra Python

```powershell
python --version
```

### 6.3. Tạo môi trường ảo

```powershell
python -m venv venv
```

### 6.4. Kích hoạt môi trường ảo

```powershell
.\venv\Scripts\Activate.ps1
```

### 6.5. Cài đặt thư viện

```powershell
python -m pip install -r requirements.txt
```

### 6.6. Kiểm tra thư viện

```powershell
python -m pip check
```

Kết quả mong muốn:

```text
No broken requirements found.
```

## 7. Khởi tạo Database

Khởi động MySQL Server.

Import file SQL:

```text
database/quan_ly_tour_du_lich.sql
```

Tên Database:

```text
quan_ly_tour_du_lich
```

Database gồm 11 bảng sử dụng InnoDB.

File SQL chỉ chứa cấu trúc bảng,
không chứa dữ liệu tài khoản hoặc khách hàng.

Không import file khởi tạo vào Database
đang chứa dữ liệu nghiệp vụ.

Không chạy lại Migration 001 và 002
nếu đã sử dụng file SQL mới nhất.

Xem hướng dẫn chi tiết tại
[Database README](../database/README.md).

## 8. Cấu hình biến môi trường

Tại thư mục backend, tạo file .env:

```powershell
Copy-Item .env.example .env
```

Chỉ chạy lệnh trên khi chưa có file .env.

Cấu hình nội dung phù hợp với MySQL trên máy local:

```ini
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=quan_ly_tour_du_lich

JWT_SECRET_KEY=
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

CORS_ORIGINS=http://localhost:5173
```

DB_USER và DB_PASSWORD phải phù hợp
với tài khoản MySQL trên máy đang sử dụng.

Tài khoản root chỉ là cấu hình minh họa cho local.

### 8.1. Tạo JWT Secret Key

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Sao chép kết quả vào JWT_SECRET_KEY trong file .env.

Mỗi thành viên sử dụng Secret Key riêng.

Không chia sẻ hoặc Commit file .env lên GitHub.

## 9. Kiểm tra Backend

### 9.1. Kiểm tra cú pháp

```powershell
python -m compileall -q app tests
```

### 9.2. Kiểm tra Import

```powershell
python -c "from app.main import app; print('Backend Import OK')"
```

### 9.3. Kiểm tra kết nối MySQL

```powershell
python -c "from app.database import test_connection; test_connection(); print('Database Connection OK')"
```

## 10. Khởi động Backend

```powershell
python -m uvicorn app.main:app --reload --port 8001
```

Các địa chỉ truy cập:

| Địa chỉ | Chức năng |
|---|---|
| http://127.0.0.1:8001 | Backend |
| http://127.0.0.1:8001/api/health | Health Check |
| http://127.0.0.1:8001/docs | Swagger UI |
| http://127.0.0.1:8001/redoc | ReDoc |
| http://127.0.0.1:8001/openapi.json | OpenAPI |

Kết quả Health Check mong muốn:

```json
{
    "status": "success",
    "database": "connected"
}
```

Nhấn Ctrl + C để dừng Backend.

Tham số --reload chỉ sử dụng khi phát triển local.

## 11. Kiểm tra số lượng API

```powershell
python -c "from app.main import app; paths = app.openapi()['paths']; print('Total API Paths:', len(paths)); print('Total API Operations:', sum(len(methods) for methods in paths.values()))"
```

Số lượng tại mốc Backend v1.0.0:

- API Paths: 56
- API Operations: 72
- Module nghiệp vụ: 12

## 12. Authentication và Authorization

Backend sử dụng JWT Bearer Token.

Hệ thống hỗ trợ hai vai trò:

- admin
- customer

Các API được bảo vệ yêu cầu Access Token hợp lệ.

Header xác thực:

```http
Authorization: Bearer <access_token>
```

Tài khoản Customer có thể đăng ký thông qua API.

Tài khoản Admin cần được khởi tạo riêng
trên Database local.

Không sử dụng tài khoản thật làm dữ liệu kiểm thử.

## 13. Bảo mật Backend

Các cơ chế đã triển khai:

- JWT Authentication.
- Role-Based Access Control (RBAC).
- Argon2 Password Hashing.
- Login Rate Limiting.
- Token Version và Token Revocation.
- Data Validation.
- Input Normalization.
- Unicode Validation Error Handling.
- Money Validation.
- CORS Configuration.
- Database Transaction và Row Lock.
- Database Exception Handler.
- HTTP X-Content-Type-Options.
- Bảo vệ dữ liệu cá nhân trong API Response.

Không Commit:

- File .env.
- JWT Secret Key.
- Access Token.
- Mật khẩu hoặc Password Hash.
- Dữ liệu cá nhân của khách hàng.
- Database Dump chứa dữ liệu thật.

## 14. Kiểm thử

Các bài kiểm thử được lưu trong thư mục tests/.

Backend sử dụng:

- Unit Test.
- Mock Integration Test.
- HTTP API Security Test.
- Database Consistency Check.

Kết quả tại các mốc kiểm thử trước đó:

- 557/557 Unit Test và Mock Test đạt yêu cầu.
- 11/11 bảng sử dụng InnoDB.
- 10/10 quy tắc nhất quán Database đạt yêu cầu.

Một số bài kiểm thử HTTP cần Backend đang chạy,
tài khoản kiểm thử và dữ liệu nghiệp vụ phù hợp.

Không chạy các bài kiểm thử thay đổi dữ liệu
trên Database Production.

## 15. Xử lý lỗi thường gặp

### ModuleNotFoundError

Kiểm tra đã kích hoạt venv và cài đặt thư viện chưa.

```powershell
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### Không kết nối được MySQL

Kiểm tra:

- MySQL Server đã hoạt động.
- DB_HOST và DB_PORT chính xác.
- DB_USER và DB_PASSWORD chính xác.
- Database đã được khởi tạo.

### JWT Secret Key không hợp lệ

Kiểm tra JWT_SECRET_KEY trong file .env.

Secret Key phải có độ dài tối thiểu 32 byte.

### Cổng 8001 đang được sử dụng

Kiểm tra có Backend khác đang chạy hay không.

Dừng tiến trình Backend cũ nếu không còn sử dụng.

### Frontend bị lỗi CORS

Kiểm tra CORS_ORIGINS trong file .env.

Địa chỉ Frontend mặc định:

```text
http://localhost:5173
```

Khởi động lại Backend sau khi thay đổi cấu hình.

## 16. Làm việc nhóm

Mỗi thành viên nên sử dụng riêng:

- Môi trường venv.
- File .env.
- MySQL Database local.
- JWT Secret Key.
- Tài khoản và dữ liệu kiểm thử.

Các thành viên sử dụng chung mã nguồn trên GitHub.

Nên phát triển trên nhánh feature riêng
và sử dụng Pull Request khi hợp nhất mã nguồn.

## 17. Trạng thái Backend

Backend v1.0.0 đã hoàn thành phạm vi nghiệp vụ chính
và sẵn sàng tích hợp React Frontend.

Các nội dung cần tiếp tục trước khi triển khai Production:

- HTTPS và HSTS.
- Content Security Policy.
- Request Body Size Limit.
- Distributed Rate Limiting.
- Kiểm thử đồng thời nâng cao.
- Hoàn thiện các trường hợp Date và Path Validation.
- Kiểm thử bảo mật trên trình duyệt.
- Kiểm thử lại các trường hợp đã bỏ qua.

Thanh toán hiện tại sử dụng quy trình xác nhận thủ công,
chưa tích hợp cổng thanh toán thực tế.

## 18. Tài liệu liên quan

- [README dự án](../README.md)
- [Database README](../database/README.md)
- [Frontend Security](../docs/frontend_security.md)



## 19. Khởi tạo dữ liệu mẫu (Demo Data Seeder)

Backend cung cấp script `scripts/seed_demo_data.py`
để tự động khởi tạo dữ liệu mẫu phục vụ phát triển
và kiểm thử hệ thống.

### 19.1. Điều kiện sử dụng

- MySQL đang hoạt động.
- Đã import cấu trúc Database từ file SQL.
- Đã cài đặt các thư viện trong requirements.txt.
- Đã cấu hình file .env.
- Database mục tiêu phải trống.
- Chỉ sử dụng trong môi trường phát triển local.
- Không chạy đồng thời với tiến trình ghi dữ liệu khác.

### 19.2. Chạy script

Mở Terminal tại thư mục backend và kích hoạt venv.

```powershell
.\venv\Scripts\Activate.ps1
```

Khởi tạo dữ liệu trên Database kiểm thử:

```powershell
python -m scripts.seed_demo_data --database quan_ly_tour_du_lich_test
```

Khởi tạo dữ liệu trên Database phát triển chính
(chỉ áp dụng khi Database hoàn toàn trống):

```powershell
python -m scripts.seed_demo_data --database quan_ly_tour_du_lich
```

Nhập tên Database để xác nhận và thiết lập mật khẩu
cho các tài khoản Demo.

Không cần thay đổi DB_NAME trong file .env khi chạy script.

### 19.3. Số lượng dữ liệu mẫu

| Bảng | Số lượng |
|---|---:|
| users | 11 |
| destinations | 20 |
| tours | 15 |
| tour_destinations | 45 |
| tour_schedules | 30 |
| tour_guides | 10 |
| guide_assignments | 20 |
| bookings | 40 |
| booking_passengers | 100 |
| payments | 25 |
| reviews | 8 |
| Tổng cộng | 324 |

### 19.4. Tài khoản Demo

| Email | Role | Status |
|---|---|---|
| admin@example.com | admin | active |
| customer01@example.com | customer | active |
| customer02@example.com | customer | active |
| customer03@example.com | customer | active |
| customer04@example.com | customer | active |
| customer05@example.com | customer | active |
| customer06@example.com | customer | active |
| customer07@example.com | customer | active |
| customer08@example.com | customer | active |
| customer09@example.com | customer | active |
| customer10@example.com | customer | inactive |

Mật khẩu do người chạy script tự thiết lập.

Mật khẩu được băm riêng cho từng tài khoản bằng
cơ chế bảo mật hiện có của Backend.

Không lưu mật khẩu trong mã nguồn hoặc tài liệu.

### 19.5. Cơ chế bảo vệ dữ liệu

- Chỉ cho phép kết nối MySQL local.
- Kiểm tra Database mục tiêu trước khi thực hiện.
- Yêu cầu xác nhận tên Database.
- Từ chối chạy nếu Database đã có dữ liệu.
- Không xóa hoặc ghi đè dữ liệu hiện có.
- Sử dụng SQLAlchemy ORM và Transaction.
- Sử dụng Decimal để tính toán tiền tệ.
- Kiểm tra tính nhất quán trước khi Commit.
- Rollback Transaction chưa Commit khi xảy ra lỗi.

### 19.6. Kết quả kiểm thử

Script đã được chạy thành công trên Database
quan_ly_tour_du_lich_test.

- Tổng số bản ghi: 324.
- Số bảng được tạo dữ liệu: 11/11.
- Kiểm tra tính nhất quán nội bộ: PASSED.
- Transaction: COMMITTED.

Dữ liệu mẫu chỉ phục vụ phát triển và kiểm thử,
không sử dụng trong môi trường Production.
