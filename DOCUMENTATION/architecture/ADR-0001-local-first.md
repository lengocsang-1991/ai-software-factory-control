# ADR-0001 — Local-first control plane

**Ngày:** 2026-11-09
**Trạng thái:** Accepted for MVP only

## Bối cảnh

Chưa được cấp hạ tầng tập trung, IAM hoặc nguồn dữ liệu production. Cần kiểm thử được logic
quản lý dự án và Quality Gate nhưng không tạo rủi ro lộ dữ liệu.

## Quyết định

Dùng Python 3.11+ + SQLite local, dashboard HTTP loopback chỉ đọc, không phụ thuộc dịch vụ ngoài.
GitHub dùng lưu nguồn và CI; không đồng bộ trạng thái nghiệp vụ lên repository.

## Hệ quả

Ưu điểm: dễ chạy/test, ít phụ thuộc, không yêu cầu secret. Hạn chế: không có đa người dùng,
RBAC, HA, chống sửa dữ liệu, đồng bộ hay xác minh người phê duyệt.
Không được coi đây là kiến trúc production.
