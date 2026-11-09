# Chính sách bảo mật & phê duyệt

- Người điều hành giữ quyền quyết định cuối cùng, quyết định cấp quyền cho từng dự án.
- Không yêu cầu/ghi mật khẩu, OTP, private key, API key trong cuộc trò chuyện, git hay báo cáo.
- Sử dụng OAuth/ứng dụng chính thức hoặc secret store được phê duyệt.
- Mọi thao tác **thay đổi mã nguồn**, **ghi đè/xóa dữ liệu**, **tạo PR**, **merge**, **đổi quyền truy cập**, **triển khai production**, **phát sinh chi phí** phải có phê duyệt riêng theo tài liệu nguồn.
- Phân tách môi trường DEV / TEST / PROD. Tối thiểu hóa quyền truy cập.
- Logs và evidence phải được kiểm soát; không ghi thông tin nhạy cảm.
- Không ngụy tạo log, báo cáo đạt chuẩn hoặc dữ liệu kiểm thử.
- Nếu chưa chứng minh quyền được cấp: chỉ phân tích, đề xuất, tạo bản nháp cục bộ.
