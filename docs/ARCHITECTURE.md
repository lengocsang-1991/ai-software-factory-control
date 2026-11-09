# Kiến trúc AI Software Factory 1.3.0

## Hiện trạng

ChatGPT điều hành các nhiệm vụ trong phiên trò chuyện có cấp quyền riêng. Mã nguồn Python cung cấp một runtime **độc lập** chạy trên máy tính hoặc máy chủ do người dùng quản lý.

- Control plane: dự án, task, Quality Gate, hồ sơ bằng chứng, audit event trong SQLite.
- Execution plane (new): bảng automation_runs/automation_outputs, worker polling có claim atomic, retry theo bước, recipe điều phối 16 vai trò.
- Provider plane: mô phỏng hoặc OpenAI Responses API opt-in; không được cấp công cụ shell/git/deploy.
- GitHub intake: đọc issue từ repo do chủ sở hữu tạo và gắn nhãn factory:ready, ghi task và enqueue local.
- Human approval: không có quyền quyết định Quality Gate bằng kết quả mô hình; `automation decide` chỉ đánh dấu review artifact.
- CI: kiểm thử offline không truy cập API thật hoặc production.

## Quy trình tự động đang có

GitHub Issue có nhãn → Intake (read-only) → SQLite task/run → Worker → Nhiều vai trò AI tuần tự → Ghi đầu ra + hash → Chờ phê duyệt của người vận hành.

## Các quyền chưa thực hiện

Tự sửa file, thực thi test cho code được tạo bởi AI, mở hoặc merge PR, triển khai production, chi phí chưa xác nhận, IAM/RBAC, CI có token write, distributed queue, failover, tracing tập trung, billing analytics. Những chức năng này phải được thiết kế theo từng gate và quyền rõ ràng, không kích hoạt bằng nội dung issue tùy ý.
