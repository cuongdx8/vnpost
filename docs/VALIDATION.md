# Kiểm tra local — 22/10/2026

- 7 notebook được parse: 6 notebook HRM/VLP và 1 CAS Admin SCD2 draft, tổng 75 code cell tính cả cell rỗng.
- Cú pháp Python hợp lệ, output rỗng, execution_count=None; inventory SHA-256 khớp source.
- 17 test local đạt: tạo biến cho 6 job, thực thi riêng config cell bằng environment giả, cô lập key theo layer, missing/mismatched environment, cấm DEV fallback, date window, output private, Git ignore và synthetic signing fixture.
- Đối chiếu AST: toàn bộ hàm xử lý hiện có trong 6 notebook HRM/VLP giữ nguyên so với backup trước khi tổ chức Git. Không đưa lại auto-verification đã hoàn tác.
- Scanner không tìm thấy giá trị key DEV hiện có trong tập source sẽ đóng gói/Git; không có đường dẫn tuyệt đối của máy cũ. Tool đọc key để so sánh local, chỉ báo số lượng và tên file nếu có lỗi, không in giá trị.
- Đã kiểm tra dry-run DEV HRM Unit Bronze với config thật: chỉ xác minh đủ biến, không thử kết nối.

Lệnh:

```bash
python3 scripts/validate_repository.py
python3 -B -m unittest discover -s tests -v
python3 scripts/package_source.py
```

Đây là kiểm tra source/cấu hình và mô phỏng offline. Chưa gọi API, S3, Spark/metastore hoặc CP4D; chưa khẳng định key còn hiệu lực, ingest thành công hoặc draft CAS dùng được cho production. Git ignore được kiểm tra bằng repo tạm trong test; repo source chính chưa git init.
