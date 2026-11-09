# Roadmap (cập nhật 09/11/2026)

**Staging:** Railway đã chạy worker `simulation` v1.3.1 ghim commit `4b0f9f5`. Bản vá kiểm toán 1.3.2 không được tự triển khai lên worker đó.

| Level | Điều kiện đạt | Hiện trạng |
|---|---|---|
| 1 CONTROL | Dự án, nhiệm vụ, gate, audit | **MVP cục bộ có kiểm thử** |
| 2 CONNECTED | GitHub đồng bộ, CI, tiếp nhận issue, AI provider có xác minh | **Một phần**: GitHub + CI thật, issue intake kiểm thử giả lập; OpenAI/Gemini adapters đã kiểm thử offline, chưa có key |
| 3 EXECUTION | Sandbox tạo/sửa mã, chạy test, PR tự động có phê duyệt | **Chưa có** |
| 4 VERIFIED AUTOMATION | CI + kiểm toán độc lập + IAM + policy engine | **Chưa có** |
| 5 OPERATIONAL FACTORY | Hạ tầng 24/7, nhiều dự án, giám sát, quota, backup, deploy | **Chưa đạt**: có một worker simulation staging, chưa có IAM/backup/quota và production |

Ưu tiên thực hiện tiếp: cấu hình provider trên host → xác minh 1 run AI thật → thiết lập IAM/approval có danh tính → sandbox code runner → CI evidence → GitHub PR với write scope hạn chế → bảo vệ main → triển khai thử nghiệm rồi mới production.
