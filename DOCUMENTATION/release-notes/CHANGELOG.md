# Changelog

## 1.0 (khởi tạo bộ khung)
- Cấu trúc quản trị, 16 định nghĩa Agent, workflow 8 giai đoạn, quality gates và mẫu báo cáo.
- Chưa có release phần mềm hay kết nối sản xuất.

## 1.1.0 — 09/11/2026

- Thêm control-plane local chạy bằng Python stdlib + SQLite.
- Thêm CLI `project/task/evidence/gate/report/serve` và dashboard read-only.
- Thêm ràng buộc Quality Gate và evidence SHA-256, lịch sử sự kiện.
- Thêm test chức năng/âm tính và cấu hình GitHub Actions chạy test (chưa kết nối repo).
- Không có live Agent, xác thực RBAC, tích hợp Cloud/GitHub hoặc production deployment.

## 1.1.1 — 09/11/2026 (kết nối GitHub đích: cấu hình an toàn)

- Ghi nhận owner đích `lengocsang-1991` theo thông tin người điều hành cung cấp.
- Phát hiện GitHub connector đang thuộc tài khoản khác, chặn mọi thao tác GitHub thực tế.
- Bổ sung `INTEGRATIONS/github/target.json`, hướng dẫn kết nối lại và script guard kiểm tra owner (không kết nối mạng, không ghi repo).
- Bổ sung kiểm thử chặn sai GitHub account; chưa tạo hoặc cập nhật repository nào.

## 1.2.0 — 09/11/2026 (định hình repository GitHub chuẩn)

- Xác minh kết nối GitHub đúng `lengocsang-1991`; repository đích đã tồn tại.
- Cập nhật README và hướng dẫn tích hợp, không giữ trạng thái kết nối cũ sai lệch.
- Bổ sung hướng dẫn đóng góp, mã nhận diện owner, mẫu Issue/PR, tài liệu kiến trúc và an ninh.
- Chuẩn hóa metadata Python, CI kiểm thử đa phiên bản 3.11–3.13.
- Vẫn là MVP cục bộ, chưa có Agent runtime, RBAC hoặc triển khai production.
