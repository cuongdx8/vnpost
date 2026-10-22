# VNPOST data pipeline — hướng dẫn làm việc

Đọc README.md, docs/context/WINDOW_CONTEXT.md và docs/STATUS.md trước khi tiếp tục. Quy tắc trong docs/rules/, docs/layers/, docs/sources/.

- Source nằm tại notebooks/<layer>/<source>/. Không tạo bản chạy song song ở layout cũ.
- Key hiện có thuộc DEV theo xác nhận chủ dự án. Không đưa giá trị key vào code, docs, output, commit hoặc thông báo.
- Public config nằm tại config/environments/<environment>.json; key thật tại config/secrets/<environment>.local.json, được Git bỏ qua. Không suy ra UAT/PROD từ DEV.
- Giữ thuật toán API/Landing/Bronze hiện tại trừ khi có yêu cầu sửa. Bổ sung tự động đối soát HRM trước đây đã hoàn tác theo yêu cầu; không tự đưa lại.
- Test local, tạo env file và đọc source không chứng minh ingest thành công trên CP4D.
- Silver HRM/VLP và Gold HRM/VLP chưa triển khai; CAS Admin dim_org là draft cần xử lý review.
- ETL_Date/data_date là ngày batch. Không tự đổi sang ngày create/update nguồn. Bronze replay từ Landing, không gọi API.
- Không sửa tài liệu đồng bộ read-only của project cũ nếu được gắn thêm. Bản chứa credentials/backup local nằm dưới .local/.
- Sau sửa code, chạy python3 scripts/validate_repository.py và python3 -B -m unittest discover -s tests -v. Sửa notebook có chủ đích thì cập nhật SHA-256 inventory; không dùng cập nhật hash để che thay đổi ngoài phạm vi.
- Khi chuyển context, cập nhật STATUS và WINDOW_CONTEXT, phân biệt đã làm/chưa làm. Không commit/push/deploy hoặc tạo lịch nếu chưa được yêu cầu.
