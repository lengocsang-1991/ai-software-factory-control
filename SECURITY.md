# Security Policy

**MVP 1.2.0 không phải production-ready.**

## Nguyên tắc
- Không đưa secrets, token, mật khẩu, API key, OTP hoặc dữ liệu cá nhân vào repository.
- GitHub dùng quản lý code và CI; dữ liệu điều hành cục bộ không được commit.
- Dashboard cục bộ chỉ được chạy tại 127.0.0.1; không có đăng nhập/RBAC.
- Approval nhập qua CLI chưa xác thực danh tính; hash SHA-256 không chứng minh tính hợp pháp của bằng chứng.
- Không triển khai production trước khi có IAM, audit log bảo vệ chống sửa, backup, security review và approval.

## Báo lỗ hổng
Không công bố chi tiết lỗ hổng trong Issue public. Dùng Private Vulnerability Reporting nếu được bật, hoặc kênh riêng do chủ repo chỉ định. Thu hồi/xoay vòng secret ngay khi phát hiện lộ lọt.
