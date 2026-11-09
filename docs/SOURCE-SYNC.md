# Đồng bộ mã nguồn 1.2.0

Repository đã được khởi tạo với bộ tài liệu và cấu hình cộng tác GitHub. **Chưa coi đây là bản đồng bộ đầy đủ của 98 tệp nguồn.**

## Quy trình nhập mã từ gói ZIP 1.2.0 được cung cấp trong cuộc trò chuyện

1. Giải nén gói dự án chính thức; rà soát toàn bộ secrets và dữ liệu cá nhân trước khi nhập.
2. Kiểm tra tại thư mục gốc: `python scripts/validate_factory.py`, `python -m unittest discover -s tests -v`.
3. Trên nhánh `feat/factory-control-v1.2`, đưa mã nguồn Python, tests, cấu hình, 16 Agent, workflows và docs vào.
4. Đảm bảo GitHub Actions chạy kiểm thử trên commit, không tin vào kết quả giả định.
5. Mở Pull Request để review và phê duyệt trước merge.

**Không** ghi đè nhánh main chưa có review, không triển khai production và không tải SQLite state lên GitHub.
