# AI coding agent policy

Agent roles được định nghĩa trong `AGENTS/registry.json`. Phiên bản 1.3 có bộ điều phối text-only, **không chạy shell, tự sửa code, PR, merge hoặc deploy**.

1. Không giả định 16 vai trò tương đương 16 tiến trình AI luôn hoạt động.
2. Không đưa token, API key, OTP, dữ liệu cá nhân, SQLite DB lên repo.
3. Không chạy tác vụ tính phí khi thiếu `--confirm-cost` hoặc chưa có ủy quyền.
4. Bắt buộc lưu kết quả thật; output mô phỏng phải gắn nhãn `SIMULATED`, không được duyệt như kết quả thật.
5. Bằng chứng SHA-256 không chứng minh chất lượng công việc hoặc danh tính người duyệt.
6. Mọi sửa đổi mã nguồn phải theo nhánh riêng, PR, CI và phê duyệt. Không tự merge hoặc deploy.
7. Luôn chạy `python scripts/validate_factory.py` và `python -m unittest discover -s tests -v`.
8. Bảo mật read-only GitHub issue intake, không dùng `pull_request_target` với secrets hoặc code chưa được tin cậy.
