# Hướng dẫn người điều hành

1. Giao mục tiêu, phạm vi và tiêu chí nghiệm thu cho từng ứng dụng.
2. Khởi tạo Product Brief theo `PROJECTS/project-template`.
3. Ghi Project ID duy nhất; cập nhật registry, task và status, không trộn repo/quyền của các dự án.
4. Chỉ định owner mỗi task; yêu cầu log/bằng chứng trước khi xác nhận hoàn thành.
5. Duyệt từng gate phù hợp; đặc biệt mã nguồn, PR, hợp nhất, production và chi phí cần phê duyệt cụ thể.
6. Hệ thống chỉ thao tác trên công cụ nào được xác minh và có quyền; không suy đoán Agent đang tự chạy.
7. Sau khi chỉ định GitHub mới, thực hiện thủ tục `INTEGRATIONS/github/SETUP.md`.

## Lệnh thường dùng

- **Thực hiện:** làm công việc được cấp phép, có công cụ.
- **Tiếp tục:** đọc lại task status và evidence thực tế rồi tiếp tục.
- **Kiểm toán:** đánh giá bằng chứng, phân tách chưa kiểm chứng và lỗi thực tế.
- **Hoàn thiện:** rà soát thiếu sót và xử lý phần được phép.
- **Triển khai:** xác minh môi trường, quyền, Quality Gate và phê duyệt trước.

## Ứng dụng cục bộ 1.1

- Sử dụng `python -m factory_control init` để khởi tạo SQLite độc lập với registry mẫu.
- `python -m factory_control project list` để kiểm tra danh mục thực.
- `python -m factory_control gate list --project APP-001` kiểm tra trạng thái Quality Gate.
- `python -m factory_control serve` để mở dashboard chỉ đọc ở localhost.
- Tài liệu lệnh đầy đủ: `DOCUMENTATION/operating-guides/QUICKSTART.md`.
- Bản ghi phê duyệt local chưa xác minh danh tính; không thay thế quy trình phê duyệt production.
