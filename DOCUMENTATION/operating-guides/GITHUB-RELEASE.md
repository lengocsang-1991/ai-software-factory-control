# Quy trình phát hành trên GitHub

**Repository:** `lengocsang-1991/ai-software-factory-control` (public)

1. Xác minh GitHub login và owner bằng connector thật; không suy đoán từ URL.
2. Rà soát dữ liệu/sources trước khi public: không chứa secrets, dữ liệu thật, database local.
3. Giữ `main` ổn định; phát triển trên `feat/*`, `fix/*` và tạo Pull Request.
4. Chạy `python scripts/validate_factory.py` và `python -m unittest discover -s tests -v`.
5. Đợi GitHub Actions CI có kết quả đạt trên commit thực tế; không suy diễn từ test local.
6. Kiểm tra sự thay đổi, rủi ro và người phê duyệt; merge khi được chủ sở hữu cho phép.
7. Tạo tag/release sau khi kiểm tra đường dẫn/commit; triển khai production là quy trình riêng.

**Giới hạn:** Công cụ hiện có không đủ bằng chứng rằng branch protection, required reviewers
hoặc private vulnerability reporting đã được bật. Chủ repository phải cấu hình GitHub Settings.
