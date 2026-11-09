# Tích hợp GitHub — trạng thái xác minh 09/11/2026

- Tài khoản xác thực qua GitHub connector: **`lengocsang-1991`**.
- GitHub App đã được cài trên tài khoản đó; quyền đọc và ghi repository được kiểm tra.
- Repository đích: [lengocsang-1991/ai-software-factory-control](https://github.com/lengocsang-1991/ai-software-factory-control).
- Repository có quyền truy cập **public**. Không push state, token, bằng chứng nhạy cảm.
- Cấu hình đích lưu ở `INTEGRATIONS/github/target.json`; đừng nhầm cấu hình này là credential.

## Kiểm tra an toàn trước phát hành

```bash
python scripts/check_github_target.py --authenticated-login lengocsang-1991 --repository lengocsang-1991/ai-software-factory-control
```

Lệnh chỉ là **guard cục bộ** so khớp tên tài khoản; nó không xác thực API hay cấp quyền push.
Sau đó kiểm tra chính thức identity qua GitHub integration, rà soát tệp, tạo nhánh, PR,
chạy GitHub Actions và xin phê duyệt hợp nhất. Không tự động triển khai production.

Xem `DOCUMENTATION/operating-guides/GITHUB-RELEASE.md`.
