# Landing

Đã có code HRM Unit/Employee và VLP Order Detail. Landing độc lập Spark/metastore, gọi API và S3.

```text
s3://<bucket>/<source>/<object>/YYYYMMDD/page-000001.json
s3://<bucket>/<source>/<object>/YYYYMMDD/manifest.json
s3://<bucket>/<source>/<object>/_logs/YYYYMMDD/landing-<run_id>.json
```

Một tập hiện hành/object/ngày, không dùng runs/<run_id>. RUN_ID vẫn trong manifest/log. HRM manifest version=3; VLP version=1. Không trộn manifest/layout cũ với code mới.

Manifest chứa ngày, nguồn/object hoặc entity, run, ingest_time, count, page/count/SHA-256, complete. Ghi manifest cuối cùng sau khi kiểm tra/upload đủ trang; tên page tuần tự.

Batch rỗng hợp lệ vẫn có tập đã chốt theo contract. Không tạo manifest thành công từ API lỗi. Xem [API ingest](../rules/API_INGEST.md) và [quy ước chung](../rules/PIPELINE_CONTRACT.md).
