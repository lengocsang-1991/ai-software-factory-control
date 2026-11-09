# Prompt khởi đầu cho Google AI Studio (sao chép phần dưới)

Trong vai chuyên gia kiến trúc phần mềm, bảo mật, kiểm thử và giao diện AI, hãy nghiên cứu **toàn bộ repository Python `lengocsang-1991/ai-software-factory-control` ở nhánh `feat/factory-control-v1.2`**. Căn cứ vào `docs/AUDIT-2026-11-09.md`, `README.md`, `AGENTS.md`, `docs/GOOGLE_AI_STUDIO.md`, mã nguồn `factory_control/` và thư mục `tests/`.

Mục tiêu: **xây dựng giao diện web React + backend Node.js mới, phục vụ quản lý công việc AI Software Factory**, theo phong cách chuyên nghiệp, tiếng Việt. Không mô phỏng rằng Python CLI đang chạy trong AI Studio.

Yêu cầu:

1. Trước hết hãy lập bảng phần nào đã tồn tại thật trong Python, phần nào chưa có; không phóng đại 16 vai trò thành 16 Agent tự trị.
2. Dựng UI dashboard cho danh sách dự án, nhiệm vụ, 8 Quality Gate, lịch sử Agent run và trạng thái phê duyệt. Dùng **dữ liệu giả gắn nhãn DEMO** nếu backend thật chưa kết nối.
3. Có bộ REST API Node.js **được thiết kế với authentication và RBAC**, đặt secret chỉ ở server. Tuyệt đối không lấy/công khai `.db` hoặc đọc dữ liệu staging từ mạng công cộng.
4. Chỉ tạo một bản phát triển mới theo cấu trúc tách biệt (chẳng hạn `aistudio-web/`), không thay thế `factory_control/` hoặc phá các bài kiểm thử Python.
5. Nếu chưa có API Gateway được cấp quyền, không cố kết nối trực tiếp worker Railway. Nêu giao thức đề xuất và chờ phê duyệt để triển khai API thật.
6. Không dùng shell/git/deploy qua đầu ra mô hình khi chưa có quyền rõ ràng. Không tự merge nhánh `main`, không bật OpenAI/Gemini API tính phí và không công bố URL production.
7. Tạo test cho UI/API mới, viết tài liệu vận hành, mô tả các giới hạn còn tồn tại và báo cáo kết quả test trung thực.

Hãy bắt đầu bằng **bản phân tích kiến trúc và kế hoạch kỹ thuật**, sau đó chỉ sinh mã giao diện demo an toàn, không tự triển khai hạ tầng.
