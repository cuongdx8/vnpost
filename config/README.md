# Môi trường, URL và key

## File nào lưu gì

| File | Nội dung | Git |
|---|---|---|
| environments/dev.json | URL/config từ code hiện tại | Có |
| environments/uat.json, prod.json | Mẫu, để trống giá trị chưa được cung cấp | Có |
| credentials.catalog.json | Tên/mục đích key, vị trí local; chưa biết expiry | Có |
| secrets/secrets.example.json | Mẫu key với giá trị trống | Có |
| secrets/dev.local.json | 8 biến credentials DEV lấy từ code được giao | Không |
| secrets/uat.local.json, prod.local.json | Key đúng môi trường khi được cung cấp | Không |
| .local/jobs/<environment>/*.env tại repo root | Biến job đã ghép, chứa key | Không |

Các key hiện có thuộc **DEV theo xác nhận chủ dự án**. Chưa xác minh hiệu lực key. VLP URL được giao có hostname uat-vlp-edi; profile DEV giữ nguyên để bảo toàn cấu hình. Không xem hostname này là bằng chứng key thuộc UAT và không tự gán key DEV vào UAT.

## Cấu hình

Xem [DEV](environments/dev.json), [UAT](environments/uat.json), [PROD](environments/prod.json). Profile lưu URL S3/HRM/VLP/HMS/AMS/CAS/CPG, bucket, user, truststore, instance và catalog. Registry [credentials](credentials.catalog.json) chỉ lưu tên/mục đích, không có giá trị.

- Không có default DEV ngầm trong notebook. Truyền PIPELINE_ENV và biến kết nối cần thiết vào job.
- Landing cần S3 và key của đúng API; không cần metastore để extract.
- Bronze cần S3 + metastore/Spark; file env được tạo không mang token API.
- ACCESS_KEY1/SECRET_KEY1 dành cho warehouse. Bỏ trống thì dùng cặp S3 chính như baseline; có thể truyền cặp riêng qua environment.
- Thêm môi trường bằng public profile đúng URL/bucket/user/instance và secrets file có nhãn environment khớp. Tool từ chối thiếu cấu hình/nhầm nhãn, không mượn key DEV.

## File key môi trường mới

Sao chép secrets.example.json thành <environment>.local.json, sửa environment và điền key đúng môi trường. Trên hệ thống hỗ trợ POSIX, đặt mode 600; file DEV hiện tại đã đặt mode 600. JSON được đọc như dữ liệu, không eval/source.

## Tạo env CP4D

Chạy từ repo root:

```bash
python3 scripts/build_job_env.py --environment dev --layer landing --source hrm --object unit --etl-date 2026-10-21 --dry-run
python3 scripts/build_job_env.py --environment dev --layer bronze --source hrm --object unit --etl-date 2026-10-21
python3 scripts/build_job_env.py --environment dev --layer landing --source vlp --object order_detail --etl-date 2026-10-21 --date-from 2020-01-01 --date-to 2026-10-22
```

--dry-run chỉ in tên biến. Lệnh thường ghi file trong .local/jobs/; --output chỉ được trỏ vào .local/. Tạo lại sẽ thay nội dung file env đó. File là NAME=value để nhập CP4D, không chạy như shell script. Tool không gọi API, S3, Spark hoặc tạo job/schedule.

Tool không kế thừa biến shell vào cấu hình được xuất. Trên CP4D cần restart kernel hoặc dùng job environment mới để tránh biến cũ trong RAM. Notebook không tự chia sẻ os.environ và không tự đọc file JSON này.
