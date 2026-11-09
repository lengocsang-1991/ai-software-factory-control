# Đồng bộ mã nguồn AI Software Factory 1.2.0

## Trạng thái được xác minh ngày 09/11/2026

- Đã đưa 98 tệp trong bộ khung cục bộ vào nhánh `feat/factory-control-v1.2` cùng 12 tệp tài liệu/quy tắc GitHub đã tạo ở bước khởi tạo.
- Commit mã nguồn: `1dba7429ca22d535ce7e93080be5a8fb0274170e`.
- Mã nguồn `factory_control/store.py` và workflow `.github/workflows/ci.yml` đã được đọc lại trực tiếp từ GitHub.
- GitHub Actions run **42598659341** đã **success** ở Python 3.11, 3.12, 3.13.
- Pull Request **#1** đang ở trạng thái **Draft**; **chưa merge vào main**; chưa triển khai production.

## Hướng dẫn kiểm chứng

```bash
python scripts/validate_factory.py
python -m unittest discover -s tests -v
```

Theo dõi tại [Pull Request #1](https://github.com/lengocsang-1991/ai-software-factory-control/pull/1) và [CI Run #42598659341](https://github.com/lengocsang-1991/ai-software-factory-control/actions/runs/42598659341).

## Bước kiểm soát còn lại

Rà soát toàn bộ thay đổi, kiểm tra an toàn thông tin, thiết lập quy tắc bảo vệ nhánh main, lấy phê duyệt chính thức trước merge. Không coi MVP là production-ready hoặc hệ thống Agent đang tự chạy.
