# Hướng dẫn vận hành MVP 1.1

## 1. Phạm vi

Công cụ local giúp lưu trạng thái dự án/nhiệm vụ, chặn sai thứ tự Quality Gate và kiểm chứng hash SHA-256 của tệp tham chiếu. Không phát triển code bằng AI Agent tự động, không thay đổi GitHub, không triển khai production.

## 2. Cấu hình

- Python >=3.11; không có thư viện ngoài.
- Mở terminal tại gốc `AI-SOFTWARE-FACTORY/`.
- Chạy `python -m factory_control init`.
- Mặc định dữ liệu lưu ở `.factory-state/factory.db` và không được Git commit.
- Có thể sử dụng `--db /path/to/db` đặt trước lệnh `project`, `task`, `evidence`, `gate`, `report`, `serve` để tách môi trường.

## 3. Tạo và quản trị dự án

```bash
python -m factory_control project add --id APP-001 --name "Dự án 1" --owner "Chủ dự án"
python -m factory_control project list
python -m factory_control project show --id APP-001
python -m factory_control task add --id T-001 --project APP-001 --title "Soạn đặc tả" --owner "BA" --priority HIGH
python -m factory_control task status --id T-001 --set READY
python -m factory_control task status --id T-001 --set IN_PROGRESS
```

Task phải qua các trạng thái hợp lệ; `DONE` chỉ từ `WAITING_APPROVAL` kèm `--evidence-id` gắn đúng task.

## 4. Bằng chứng, phê duyệt

Cổng giai đoạn yêu cầu đúng loại bằng chứng:

| Cổng | Loại bằng chứng |
|---|---|
| 1 | `PRODUCT_BRIEF` |
| 2 | `SPEC` |
| 3 | `DESIGN` |
| 4 | `BUILD` |
| 5 | `TEST_REPORT` |
| 6 | `AUDIT_REPORT` |
| 7 | `RELEASE_APPROVAL` |
| 8 | `DEPLOYMENT_REPORT` |

Ví dụ (sau khi có `brief.md` thật và được duyệt):

```bash
python -m factory_control evidence add --project APP-001 --type PRODUCT_BRIEF --file ./brief.md --note "Bản đã rà soát"
python -m factory_control evidence verify --id 1
python -m factory_control gate decide --project APP-001 --number 1 --decision APPROVED --approver "Người có thẩm quyền" --evidence-id 1
python -m factory_control project advance --id APP-001
```

Chỉ được duyệt cổng hiện tại. Quyết định `REJECTED` chặn chuyển giai đoạn. `APPROVED` là bản ghi do operator nhập, **chưa phải chữ ký số hoặc phê duyệt đã xác minh**. File bằng chứng phải còn tồn tại nguyên vẹn tại thời điểm duyệt và chuyển giai đoạn.

## 5. Dashboard và kiểm thử

```bash
python -m factory_control serve --port 8765
python -m unittest discover -s tests -v
python scripts/validate_factory.py
```

Giao diện web là **read-only**, cố định ở 127.0.0.1. Không mở port qua Internet hoặc reverse-proxy. Dữ liệu minh họa trong tests chỉ là dữ liệu giả dùng để kiểm thử logic, không phải bằng chứng nghiệm thu dự án thực.

## 6. Sao lưu, phục hồi, bảo mật

- Dừng chương trình khi sao lưu; sử dụng SQLite backup API cho bản sao đang vận hành nếu cần online backup.
- Sao lưu cả `.factory-state/factory.db` và các tệp bằng chứng gốc trong kho riêng do người vận hành quản lý.
- Không đưa DB, khóa bí mật, token, dữ liệu cá nhân vào repository.
- Máy local đang dùng tài khoản hệ điều hành riêng; sản phẩm này chưa hỗ trợ RBAC, xác thực hoặc audit log chống sửa đổi.
- Các cổng kiểm soát logic không thay thế kiểm toán bảo mật và phê duyệt production thực.
