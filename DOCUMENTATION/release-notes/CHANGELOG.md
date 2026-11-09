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

## 1.3.2 — 09/11/2026 (kiểm toán và vá lỗi trên nhánh ứng dụng hiện có)

- Chặn giả mạo nhãn simulation để một bản mô phỏng không thể bị coi là kết quả AI thật.
- Kiểm tra thứ tự, vai trò, dấu simulation, hash của toàn bộ đầu ra trước khi Agent tiếp tục và trước khi duyệt.
- Bổ sung `automation recover` để xử lý run bị ngắt thủ công, không tự động lặp lời gọi API tốn phí.
- Khóa giao dịch SQLite trước các chuyển trạng thái nhiệm vụ/gate/stage; kiểm tra cả byte count của bằng chứng.
- Sửa GitHub Issues pagination (giới hạn 300 và lỗi tường minh khi vượt); xử lý phản hồi sai kiểu an toàn.
- Từ chối phản hồi OpenAI/Gemini không hoàn tất hoặc sai schema; kiểm soát model id.
- Từ chối Host lạ trên dashboard localhost (giảm DNS rebinding).
- Sửa script guard để không nhận việc so khớp chuỗi là bằng chứng xác thực OAuth; CI dùng context thực tế của GitHub Actions.
- Thêm static safety preflight, regression tests và hướng dẫn nhập vào Google AI Studio.
- Sửa đường dẫn SQLite mặc định khi cài package, tránh ghi vào thư mục site-packages không có quyền; giữ dữ liệu cũ nếu có.
- Staging Railway chạy 1.3.1 ghim commit `4b0f9f5`, **không tự cập nhật** khi đẩy code kiểm toán.
