# Release checklist — AI Software Factory Control 1.1

## Đã hoàn thành cục bộ

- [x] CLI tạo dự án, nhiệm vụ, đổi trạng thái và xuất báo cáo
- [x] SQLite giữ lịch sử sự kiện theo dự án
- [x] 8 Quality Gate và quy tắc không vượt cổng
- [x] SHA-256 tham chiếu bằng chứng và phát hiện sửa file
- [x] Dashboard chỉ đọc, bind localhost
- [x] Unit/integration tests chạy bằng stdlib
- [x] Quyền GitHub mặc định chưa sử dụng

## Chưa đạt mức production — bắt buộc giải quyết trước khi triển khai thực tế

- [x] Người điều hành xác nhận **tài khoản GitHub đích**: `lengocsang-1991`
- [ ] Kết nối ChatGPT GitHub với **đúng** `lengocsang-1991` (hiện connector đang ở tài khoản khác)
- [ ] Xác nhận tên repo, chế độ truy cập và quyền tạo/cập nhật
- [ ] Tạo repo trên GitHub đúng tài khoản; commit và xác minh CI chạy thành công
- [ ] Thiết lập danh tính và phân quyền người phê duyệt (SSO/OIDC/RBAC); chống giả mạo phê duyệt
- [ ] Tăng cường audit log bất biến / chữ ký số và lưu trữ bằng chứng có chính sách lưu giữ
- [ ] Định nghĩa tác vụ AI Agent runtime và cơ chế sandbox, quyền hạn, kiểm soát chi phí
- [ ] Tích hợp thật Codex, Google AI Studio, Graphify (nếu dùng), GitHub và hệ thống điều phối được cấp quyền
- [ ] Triển khai kiểm thử bảo mật, threat modeling, thử tải và phục hồi
- [ ] Hạ tầng production, backup/restore, quan sát và rollback thực tế
- [ ] Tổ chức kiểm toán độc lập và phê duyệt phát hành bằng chứng thật

**Không được đánh dấu các mục đang bỏ trống là đã hoàn thành.**
