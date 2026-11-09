# Đồng bộ GitHub — AI Software Factory 1.3.1

Mã nguồn 1.3.1 đang được đưa lên nhánh `feat/factory-control-v1.2` trong Pull Request #1 để kế thừa bộ khung 1.2.0 đã có CI thành công.

**Kiểm thử local:** 29 bài (gồm kiểm thử workflow, idempotency, simulation vs API, gate, GitHub intake và bảo mật). Chưa chạy API AI thật hoặc worker thường trực trên máy chủ ngoài.

**Trước merge:** kiểm tra CI trên commit HEAD, rà soát các quyền và dữ liệu, chuẩn bị cấu hình secrets và yêu cầu phê duyệt chủ repository. Việc có CI success không đồng nghĩa production-ready.
