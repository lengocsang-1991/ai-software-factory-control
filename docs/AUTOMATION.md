# AI Software Factory — cơ chế tự động hóa v1.3.1

## Phạm vi đã triển khai

- Hàng đợi tác vụ có trạng thái trong SQLite; không ghi dữ liệu khách hàng lên GitHub.
- Ba recipe: `discovery` (7 Agent), `design-review` (8 Agent), `full-review` (16 Agent).
- Worker tuần tự có quản lý lỗi, retry, nhật ký và đầu ra mỗi bước kèm SHA-256.
- Provider mặc định `simulation` để thử hệ thống, **không dùng làm căn cứ phê duyệt**.
- Provider OpenAI Responses API hoặc Google Gemini Interactions API chỉ phát sinh chi phí khi tự cấu hình `OPENAI_API_KEY`, chỉ định model và chạy worker có `--confirm-cost`.
- Kết quả từ mô hình là **bản dự thảo/chuyên gia đánh giá**, không phải mã nguồn đã biên dịch hoặc bản kiểm toán độc lập thực sự.
- `automation decide` là quyết định nhập bởi người dùng, chưa có xác minh danh tính/ chữ ký số.
- Không có quyền chạy shell, sửa code, tạo PR, merge, triển khai production trong Agent runtime.

## Cài đặt

Python 3.11+, không yêu cầu thư viện bên ngoài ở chế độ local.

```bash
python -m factory_control init
python -m factory_control project add --id DEMO-01 --name "Ứng dụng thử nghiệm" --owner operator --repository lengocsang-1991/ai-software-factory-control
python -m factory_control automation enqueue --project DEMO-01 --objective "Đặc tả hệ thống đặt lịch" --recipe discovery
python -m factory_control worker --provider simulation
python -m factory_control automation list --project DEMO-01
```

Để **chạy bằng AI thật** (trên máy người dùng hoặc máy chủ do người dùng quản lý):

```bash
# Đặt OPENAI_API_KEY bằng secret manager của máy chủ; không ghi trong repository hay trong chat.
# Bắt buộc đặt OPENAI_MODEL; xác định giá model và giới hạn chi phí trước khi chạy.
python -m factory_control automation enqueue --project DEMO-01 --objective "Rà soát API" --recipe discovery --provider openai
python -m factory_control worker --provider openai --confirm-cost
```

`automation show --run RUN-...` hiển thị từng đầu ra. Sau khi kiểm tra bản dự thảo, có thể dùng:

```bash
python -m factory_control automation decide --run RUN-... --decision APPROVED --actor operator --note "Đã duyệt tài liệu, chưa duyệt phát hành"
```

**Quan trọng:** phê duyệt một run không đồng nghĩa phê duyệt Quality Gate; gate vẫn cần hồ sơ bằng chứng riêng. Người dùng chưa cấu hình khóa API nào trong repository và chưa xác nhận chi phí.

## GitHub Issues → hàng đợi local (chỉ đọc)

Trên repository thuộc `lengocsang-1991`, chủ tài khoản có thể tạo Issue và tự gắn nhãn **`factory:ready`**. Nội dung issue bị coi là dữ liệu không đáng tin cậy, không được chuyển thành lệnh hệ thống hoặc tool action. Intake chỉ nhận issue được **chính `lengocsang-1991` tạo**, không nhận PR, issue người khác hoặc repository ngoài tài khoản này.

```bash
python -m factory_control automation intake --project DEMO-01 --enqueue --provider simulation
# Sau khi đánh giá chi phí có thể dùng --provider openai khi lập hàng đợi, worker phải có --confirm-cost
```

Intake không sửa hoặc bình luận trên GitHub; chỉ ghi tác vụ local. Tác vụ được tạo theo mã idempotent; lần nhập lặp không tạo thêm run cho cùng task.

## Vận hành thường trực

Chạy trên máy chủ tự quản lý, bằng user không có quyền root, dùng dịch vụ `systemd` theo mẫu trong `deploy/systemd/`. Worker tự polling hàng đợi local; để tự động tiếp nhận GitHub Issue theo lịch cần chạy `automation intake` qua cron/systemd timer do chủ hệ thống cấu hình. ChatGPT trong cuộc trò chuyện **không phải** worker chạy nền.

Không dùng trực tiếp SQLite local như hàng đợi đa máy. Production cần Postgres, các khóa định danh worker/nhân sự, lease/heartbeat, giới hạn quota/cost và audit log bất biến.

## Rủi ro và tiêu chí phát hành tiếp

- Chưa xác minh API key, kết nối AI thực tế, tính phí hoặc phản hồi của nhà cung cấp.
- Chưa có tool-backed code execution, unit test thực thi theo từng thay đổi mã, PR tự động có kiểm soát hoặc deployment.
- Chưa có xác thực người phê duyệt, RBAC, kiểm thử xâm nhập, sao lưu/khôi phục tập trung.
- Mọi quyết định merge, deploy, chi phí và tăng quyền phải có ủy quyền riêng.

## Google AI Studio / Gemini Interactions API (adapter đã kiểm thử offline)

Theo tài liệu Gemini Interactions API được Google khuyến nghị, dùng Gemini qua endpoint `https://generativelanguage.googleapis.com/v1beta/interactions` với `store=false` và không cấp tool. Chỉ chạy khi **người vận hành** đã cấu hình `GEMINI_API_KEY`, `GEMINI_MODEL` từ secret manager trên host có quyền truy cập:

```bash
python -m factory_control automation enqueue --project DEMO-01 --objective "Rà soát yêu cầu" --recipe design-review --provider gemini
python -m factory_control worker --provider gemini --confirm-cost
```

Mọi lời gọi AI có thể phát sinh chi phí, phụ thuộc chính sách của nhà cung cấp. **Chưa kiểm tra API thật hoặc quyền dùng model trên tài khoản Google AI Studio của người dùng**.

Nếu đã tự chạy bản thử nghiệm 1.3.0 bằng SQLite, hãy sao lưu trước khi nâng cấp; 1.3.1 không cung cấp migration tự động cho database thử nghiệm cũ chứa bảng `automation_runs`. Không chuyển database thử nghiệm thành production.
