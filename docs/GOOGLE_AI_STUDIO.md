# Nhập AI Software Factory vào Google AI Studio — Build mode

**Phiên bản mã nguồn:** 1.3.2 (Python 3.11+; runtime cục bộ / Railway staging).

## Cách 1 — Nhập trực tiếp từ GitHub

1. Truy cập https://aistudio.google.com/ và vào **Build**.
2. Trong hộp nhập yêu cầu, nhấn **Add files (+) → Import from GitHub**; cấp quyền đọc repository `lengocsang-1991/ai-software-factory-control` nếu AI Studio yêu cầu.
3. Chọn repository. **Mã nguồn ứng dụng hiện đang ở nhánh `feat/factory-control-v1.2`**, không nằm ở nhánh `main` (nhánh `main` chưa được hợp nhất). Nếu UI hỗ trợ chọn nhánh, chọn chính nhánh này.
4. Kiểm tra có các tệp `factory_control/automation.py`, `factory_control/store.py`, `pyproject.toml`, `railway.json` và `tests/test_audit_regressions.py`. Nếu chỉ thấy README hoặc không thể chọn nhánh, không coi quá trình nhập đã đầy đủ; dùng gói ZIP v1.3.2 thay thế.
5. Nhập nội dung từ `docs/AI_STUDIO_STARTER_PROMPT.md` để AI Studio phân tích và đề xuất/gia công giao diện mới trên bản sao mã nguồn.

Theo hướng dẫn Build mode của Google, AI Studio hỗ trợ Import from GitHub và đồng bộ mã nguồn hai chiều. Giao diện cụ thể có thể thay đổi; việc AI Studio hỗ trợ chọn nhánh không được xác minh trong phiên này.

## Cách 2 — Dùng ZIP

1. Tải gói phát hành `AI-SOFTWARE-FACTORY-CONTROL-1.3.2-AUDITED.zip` từ ChatGPT và giải nén trong môi trường phát triển riêng.
2. Kiểm tra checksum SHA-256 đối chiếu với manifest phát hành.
3. Dùng tính năng đính kèm tệp trong AI Studio để cung cấp các tệp cần phân tích, hoặc nhập repository như cách 1. **Không giả định Build mode có chức năng chạy trực tiếp một ZIP Python**.
4. Sử dụng prompt `docs/AI_STUDIO_STARTER_PROMPT.md` để thiết kế frontend/adapter tương thích môi trường AI Studio.

## Giới hạn kỹ thuật bắt buộc hiểu đúng

- AI Studio Build tạo ứng dụng web React / Node.js; `factory_control/` là **Python CLI + SQLite**, không có REST API xác thực cho AI Studio và không phải ứng dụng Node.js sẵn chạy.
- **Đừng dùng chế độ Run/Preview để giả định Python worker đã chạy trong AI Studio**. Nếu muốn điều khiển worker Railway từ một giao diện web mới, cần thiết kế backend có authentication/RBAC, API ký xác thực, rate limit và audit log.
- Worker Railway staging phiên bản 1.3.1 đã được ghim vào GitHub commit `4b0f9f5`; đẩy mã phiên bản 1.3.2 không tự cập nhật máy chủ đó.
- Không đính kèm API key, token GitHub, password, file `.db`, hồ sơ cá nhân hoặc dữ liệu nhạy cảm vào prompt, repo, Build mode hay ZIP.
- Không tự hợp nhất nhánh, không bật OpenAI/Gemini API có phí hoặc triển khai production chỉ vì được AI Studio đề xuất.

## Kiểm thử runtime Python trên máy tính/CI riêng

```bash
python scripts/validate_factory.py
python scripts/security_audit.py
python -m unittest discover -s tests -v
python -m factory_control init  # DB mặc định ở user state; có thể đặt AI_FACTORY_DB nếu cần
```

Các bước này kiểm tra ứng dụng Python; chúng không thay thế kiểm thử một ứng dụng React/Node.js nếu được AI Studio tạo ra.

Nguồn hướng dẫn: https://ai.google.dev/gemini-api/docs/aistudio-build-mode
