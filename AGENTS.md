# Quy tắc dành cho AI coding agents

1. Không giả định 16 vai trò Agent là 16 tiến trình đang chạy. Phải nêu rõ tool đã kết nối và hành động thực tế.
2. Không commit token, mật khẩu, OTP, dữ liệu thật, database cục bộ hay chứng cứ nghiệp vụ lên GitHub.
3. Chỉ sửa mã theo phạm vi Issue, trên nhánh riêng, qua Pull Request và phê duyệt; không tự merge hay deploy.
4. Không giả kết quả test, code review, CI, audit hoặc quyết định Quality Gate.
5. Với bản mã nguồn Python 1.2.0, chạy `python scripts/validate_factory.py` và `python -m unittest discover -s tests -v`.
6. Không public dashboard local; hệ thống chưa có authentication và RBAC.
7. Nếu thiếu thông tin hoặc quyền thực thi, báo chính xác `NOT_VERIFIED` hoặc `BLOCKED`.
