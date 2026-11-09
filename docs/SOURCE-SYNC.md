# Đồng bộ GitHub — AI Software Factory 1.3.2

**Repository:** `lengocsang-1991/ai-software-factory-control`.
**Nhánh mã nguồn ứng dụng:** `feat/factory-control-v1.2` — tiếp tục dùng nhánh này, không tạo nhánh mới.
**Nhánh chính `main`:** chưa hợp nhất PR #1, không tự sửa.

## Kiểm toán 09/11/2026

- Rà soát các tệp Python chính, CI, bảo mật và tài liệu; đối chiếu GitHub blob SHA với gói nguồn 1.3.1.
- Bản vá 1.3.2 bổ sung regression tests, xử lý worker bị ngắt, đầu ra giả mạo, GitHub pagination, đối chiếu SQLite gate, xác thực Host của dashboard và kiểm tra provider response.
- **46 bài kiểm thử cục bộ đã đạt** trước khi đẩy. Phải kiểm tra riêng GitHub Actions của commit HEAD mới nhất trước khi tuyên bố CI đã đạt.
- `scripts/security_audit.py` quét source working tree, không xác minh Git history hay an toàn hệ thống đã triển khai.

## Trạng thái hạ tầng

Railway staging đang chạy worker `simulation` tại **commit ghim `4b0f9f5`**. Đẩy bản vá 1.3.2 lên GitHub không tự cập nhật container; phải có phê duyệt triển khai riêng.

## Google AI Studio

Xem `docs/GOOGLE_AI_STUDIO.md` và `docs/AI_STUDIO_STARTER_PROMPT.md`. Google AI Studio Build sử dụng React/Node.js; Python CLI không thể giả định sẽ chạy trong môi trường Build. Nếu không thể chọn nhánh đang dùng từ giao diện AI Studio, dùng ZIP hoặc lựa chọn nhập mã phù hợp, không tự hợp nhất main.

**Trước merge/deploy:** review bảo mật, xác minh test CI thật, giám sát chi phí, backup, quyền người duyệt và nhận phê duyệt rõ ràng từ chủ repo. Không coi 1.3.2 là production-ready.
