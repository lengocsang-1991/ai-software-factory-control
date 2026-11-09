# Agent hướng dẫn dành cho công cụ hỗ trợ lập trình

Áp dụng cho toàn repository:

1. Không ghi token, mật khẩu, OTP, khóa, dữ liệu khách hàng hoặc bằng chứng nghiệp vụ vào code, commit hay log.
2. Tránh giả định Agent đang chạy. Các thư mục `AGENTS/*` chỉ là đặc tả thiết kế.
3. Mọi thay đổi code phải đi qua nhánh riêng, PR, kiểm thử và phê duyệt; không tự merge hay tự deploy.
4. Chỉ thay đổi những phần thuộc phạm vi nhiệm vụ. Giữ hoạt động tương thích Python 3.11+.
5. Chạy `python scripts/validate_factory.py` và `python -m unittest discover -s tests -v` trước khi đề nghị review.
6. Không sửa trạng thái `APPROVED`/`DONE` để né Quality Gate. Không dùng dữ liệu thử làm bằng chứng thực tế.
7. Không triển khai hệ thống ra Internet: dashboard không có đăng nhập và chỉ hỗ trợ localhost.
8. Nếu thiếu công cụ hoặc chưa xác minh GitHub identity, ghi trạng thái `NOT_VERIFIED` và báo rõ giới hạn.

Xem `DOCUMENTATION/architecture/ARCHITECTURE.md` và `SECURITY.md`.
