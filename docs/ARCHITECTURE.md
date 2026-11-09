# Kiến trúc — thiết kế 1.2.0

Người điều hành → ChatGPT Central Control → AI Orchestrator (đề xuất) → 16 Agent (đặc tả) → công cụ được cấp quyền → kiểm thử → kiểm toán → Quality Gate → phê duyệt → triển khai.

## Kiến trúc MVP cục bộ
- Python CLI xử lý quản lý dự án, nhiệm vụ, trạng thái, bằng chứng và gate.
- SQLite cục bộ lưu sự kiện và bản ghi; dashboard chỉ đọc dùng HTTP localhost.
- GitHub dùng lưu mã nguồn, PR và CI; không tự chạy Agent.
- 8 giai đoạn: Ý tưởng, SPEC, Thiết kế, Lập trình, Kiểm thử, Kiểm toán, Phê duyệt, Triển khai.

## Nợ kỹ thuật
Chưa có Agent runtime, hàng đợi, IAM/RBAC, hệ thống phê duyệt có xác thực, evidence store bất biến, CI/CD production, sao lưu tập trung, observability và tích hợp Google AI Studio.

Không tuyên bố hệ thống tự động khi chưa triển khai đầy đủ.
