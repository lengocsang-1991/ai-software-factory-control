# Quy tắc chuyển trạng thái

`BACKLOG → READY → IN_PROGRESS → TESTING → AUDITING → WAITING_APPROVAL → DONE`, có thể chuyển `BLOCKED` hoặc `FAILED` tại bất kỳ bước nào phù hợp. `NOT_VERIFIED` dùng khi chưa đủ bằng chứng.

Chuyển trạng thái yêu cầu nhật ký lý do, người chịu trách nhiệm và bằng chứng. `DONE` không có nghĩa đã triển khai production.

**Các hành động cần phê duyệt riêng:** ghi/chỉnh sửa/xóa mã nguồn và dữ liệu, tạo PR, merge, thay đổi quyền, cấu hình hoặc triển khai production, phát sinh chi phí.
