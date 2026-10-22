# Bronze

Đã có 3 notebook đọc Landing vào Iceberg; không gọi lại API. Runtime cần Spark, Iceberg và connector watsonx.data phù hợp CP4D.

1. Đọc đúng manifest nguồn/object/ngày; kiểm tra version/complete/run/count và checksum page.
2. Kiểm tra khóa HRM id hoặc VLP orderCode; không nhận thiếu/trùng.
3. Cột nghiệp vụ StringType giữ số 0 đầu; object/list thành JSON string; raw_record giữ toàn bản ghi.
4. Thêm data_date, ingest_time, run_id, landing_run_id.
5. Atomic overwrite partition data_date=ETL_Date; không DELETE rồi APPEND. Schema khác cần review migration.
6. Ghi log và đối soát thật; lỗi log sau commit không chứng minh partition chưa được ghi.

Replay thay lại partition, không append bản sao. HRM tạo frame từ RAM. VLP stage NDJSON ở <source>/<object>/_bronze_stage/<run_id>/ cho Spark đọc rồi dọn trong finally. Stage tạm không phải tập Landing đã chốt.

Không explode parcel/track ở Bronze. Không đưa lại tính năng tự động đối soát HRM đã hoàn tác; xem kiểm tra độc lập tại [runbook](../RUNBOOK.md).
