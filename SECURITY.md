# Security Policy

## Phạm vi

Dự án hiện là **MVP chạy cục bộ**. Không công khai dashboard hay dùng thông tin thật trong thử nghiệm.

## Báo cáo lỗ hổng

Không mở Issue công khai nếu có thể làm lộ chi tiết khai thác, credential hoặc dữ liệu. Sử dụng **GitHub Private Vulnerability Reporting**
(nếu được chủ repository bật) hoặc kênh riêng được chủ sở hữu chỉ định. Không đưa bí mật vào chat.

## Kiểm soát hiện có

- SQLite cục bộ, HTTP chỉ bind `127.0.0.1`; API dashboard chỉ đọc.
- Nhật ký thao tác dự án/nhiệm vụ; băm SHA-256 của chứng cứ đính kèm.
- `.gitignore` ngăn cơ sở dữ liệu local và file secret thông thường.
- CI có kiểm tra cấu trúc và unit test; không dùng credential production.

## Hạn chế còn tồn tại

- Không có authentication/RBAC/chữ ký phê duyệt; trường approver là dữ liệu tự nhập.
- SHA-256 không chứng minh chủ sở hữu, nguồn gốc, tính bất biến hoặc tính hợp pháp của chứng cứ.
- SQLite lưu trên máy cá nhân, chưa có backup/khôi phục tập trung hoặc audit log chống giả mạo.
- Không có kiểm định xâm nhập độc lập; không được coi là phù hợp production.

## Quản lý secret

Không commit token/PAT/OTP/API key. Dùng cơ chế cấp quyền của nền tảng và các secret store được quản trị.
Nếu lộ, lập tức thu hồi/xoay khóa và kiểm tra lịch sử Git; chỉ xóa ở phiên bản mới là chưa đủ.

## Bổ sung Agent runtime v1.3.0

- OpenAI provider yêu cầu API key qua biến môi trường của host và `--confirm-cost`; không có key mặc định.
- Agent chỉ tạo văn bản; không cấp shell, file write, git write, quyền merge, deploy hay chuyển tiếp secrets.
- GitHub Issue intake chỉ đọc, giới hạn đúng chủ repository `lengocsang-1991` và nhãn `factory:ready`.
- Dữ liệu đầu ra API được lưu trong SQLite trên host; tránh nhập thông tin cá nhân/secret trong objective, issue hoặc log.
- `automation decide --actor` là khai báo bằng văn bản, **chưa xác thực danh tính**.
- Worker chạy nền cần một máy chủ và quản trị secrets/chi phí riêng. Không chạy dài hạn trong phiên ChatGPT.
