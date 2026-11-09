# Release Security Checklist

- [ ] Đã xác minh quyền người triển khai.
- [ ] Không có secrets trong repo/artifacts.
- [ ] Xác thực/phân quyền được thử nghiệm.
- [ ] Đã kiểm tra dependencies, dữ liệu đầu vào.
- [ ] Đã phân tách DEV / TEST / PROD.
- [ ] Có bản backup và rollback plan.
- [ ] Có kết quả security test và independent audit.
- [ ] Gate 7 đã được người có thẩm quyền phê duyệt.
- [ ] Gate 8 có bằng chứng xác minh sau deploy.
