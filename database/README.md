# Database – HTTT16

## 1. Thông tin Database

- Tên Database: quan_ly_tour_du_lich
- Hệ quản trị: MySQL
- Phiên bản đã sử dụng: MySQL 9.3.0
- Storage Engine: InnoDB
- Character Set: utf8mb4
- Table Collation: utf8mb4_0900_ai_ci
- Tổng số bảng: 11

## 2. Khởi tạo Database mới

Import file quan_ly_tour_du_lich.sql bằng phpMyAdmin hoặc MySQL Client trên môi trường chưa có các bảng của dự án.

File SQL chứa đầy đủ cấu trúc bảng, Primary Key, Foreign Key, Unique Key và AUTO_INCREMENT.

File không chứa dữ liệu tài khoản, mật khẩu hoặc thông tin khách hàng.

Sau khi khởi tạo, cần tạo tài khoản và dữ liệu kiểm thử riêng.

## 3. Database Migration

- 001_add_reviews_unique.sql: Bổ sung ràng buộc duy nhất cho đánh giá Tour.
- 002_add_token_version.sql: Bổ sung cột token_version phục vụ thu hồi JWT Token.

Hai Migration chỉ dành cho Database phiên bản cũ chưa được cập nhật.

Không chạy lại Migration nếu đã khởi tạo từ file SQL mới nhất.

## 4. Bảo mật

- Không đưa dữ liệu cá nhân lên GitHub.
- Không đưa mật khẩu hoặc password hash lên GitHub.
- Không đưa file .env chứa thông tin bí mật lên GitHub.
- Sao lưu Database trước khi thay đổi cấu trúc.
- Không import file khởi tạo vào Database đang có dữ liệu.

## 5. Kết quả kiểm tra

- 11/11 bảng sử dụng InnoDB.
- 10/10 quy tắc kiểm tra tính nhất quán dữ liệu đạt yêu cầu.
- Không phát hiện bản ghi vi phạm các quy tắc đã kiểm tra.