# Đóng góp vào AI SOFTWARE FACTORY

## Chuẩn đóng góp

- Mở Issue có mô tả mục tiêu, phạm vi, tiêu chí nghiệm thu và rủi ro.
- Tạo nhánh theo mẫu `feat/*`, `fix/*`, `docs/*`, `chore/*`; không commit trực tiếp lên `main` sau lần khởi tạo.
- Commit mô tả rõ thay đổi (`feat:`, `fix:`, `docs:`, `test:`, `chore:`).
- Mở Pull Request dựa trên mẫu có sẵn; không tự cho rằng CI đạt khi chưa thấy kết quả trên GitHub.
- Reviewer độc lập kiểm tra bằng chứng, đặc biệt phần xác thực, quyền truy cập, dữ liệu và gate.
- Merge và triển khai chỉ sau khi được chủ sở hữu phê duyệt.

## Chạy kiểm thử

```bash
python scripts/validate_factory.py
python -m unittest discover -s tests -v
python -m compileall -q factory_control scripts tests
```

## Chính sách dữ liệu

Repository là public. Không commit dữ liệu thật, database, file `.env`, secrets, token hoặc file bằng chứng nhạy cảm.
Không đính kèm bản ghi chứng cứ thật vào PR/Issue public. Nếu vô tình lộ secret, thu hồi ngay và xử lý theo `SECURITY.md`.

## Cấu hình bảo vệ đề xuất

Đề nghị bật branch protection cho `main`: yêu cầu PR, kiểm tra CI thành công, review ít nhất 1 người khi có thành viên độc lập,
ngăn force-push, ngăn xóa nhánh chính. Các cấu hình này cần thiết lập trên GitHub; **không mặc định đã bật**.
