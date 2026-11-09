# Ma trận hành động và phê duyệt

| Hành động | Mặc định | Điều kiện thực hiện |
|---|---|---|
| Nghiên cứu, đặc tả, tạo khung cục bộ | Được phép | Không đụng tài nguyên chưa được cấp quyền |
| Đọc repository đích | Chưa cấp | Chỉ định đúng owner/repo mới và quyền đọc |
| Ghi/sửa/xóa mã nguồn | Chờ phê duyệt | Xác nhận phạm vi, branch và sao lưu phù hợp |
| Tạo PR / Merge | Chờ phê duyệt | Phê duyệt cụ thể |
| Thay đổi production / quyền / chi phí | Chờ phê duyệt | Phê duyệt cụ thể của người điều hành |
| Đánh dấu test/audit PASSED | Không tự suy đoán | Phải có evidence độc lập tương ứng |
