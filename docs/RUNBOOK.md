# Vận hành trên CP4D

## Chuẩn bị

1. Chọn đúng environment profile và local secrets, xem [config](../config/README.md).
2. Chạy scripts/build_job_env.py cho đúng layer/source/object/ngày. File .env tạo ra chỉ chuẩn bị biến, không thực thi pipeline.
3. Import notebook từ notebooks/ bằng Local file vào CP4D; truyền các dòng NAME=value vào job Advanced configuration. Không source/eval file như shell.
4. Landing dùng Python có requests/boto3. Bronze dùng Python with Spark và connector như runtime mẫu đã hoạt động; tên runtime riêng chưa bảo đảm metastore hoạt động.
5. Restart kernel/Run All khi muốn chạy pipeline. Nếu chỉ kiểm tra dữ liệu thì chạy các cell import/config/hàm rồi cell query chỉ đọc; bỏ qua cell ghi.

Source mới yêu cầu PIPELINE_ENV và kết nối từ job environment, không còn credentials/URL DEV default trong notebook. Không tự chia sẻ os.environ giữa notebook; cùng ETL_Date cho Landing/Bronze.

## Daily và initial

Landing xong mới chạy Bronze. Không chạy lại Landing cùng nguồn/object/ngày trong khi Bronze đọc. Mặc định T−1 Việt Nam; xóa override ngày/cửa sổ initial khi chuyển daily.

HRM Unit initial đã ghi nhận: ETL_Date=2026-10-21, cửa sổ 2020-01-01 → 2026-10-22, 29.180 dòng. Replay Bronze không gọi API và dùng đúng ngày này nếu manifest hiện hành vẫn khớp.

HRM source local còn daily; muốn tái extract initial cần sửa body extract hoặc tích hợp tham số riêng theo yêu cầu. HRM_DATE_START/HRM_DATE_END chưa được đọc; tool từ chối date window override cho HRM để tránh tạo cấu hình không có tác dụng.

VLP initial dùng --date-from/--date-to trên tool tạo Landing env. probe_api() chỉ gọi một trang, không ghi Landing; đừng chạy extract để test một order. Cần xác minh thời gian/secret/routing trước ingest thật.

## Khi không có log: kiểm tra dữ liệu trước khi chạy lại

Đừng kết luận chưa có dữ liệu hoặc gọi lại API chỉ vì log không hiện. Khi kernel sẵn sàng, kiểm tra đúng notebook và biến ETL_Date, TABLE_NAME, RUN_ID, stage, committed; thiếu biến sau restart không chứng minh chưa commit.

Snippet chỉ đọc sau các cell import/config/hàm; dùng cho 6 notebook HRM/VLP, không dùng CAS draft:

```python
from pyspark.sql import functions as F

check_s3 = init_landing() if "init_landing" in globals() else init_s3()
try:
    key = DAY_PREFIX + "/manifest.json"
    manifest_check = json.loads(check_s3.get_object(
        Bucket=BUCKET_NAME, Key=key
    )["Body"].read())
    expected_entity = ENTITY if "ENTITY" in globals() else "order_detail"
    actual_entity = manifest_check.get("entity", manifest_check.get("object"))
    if (manifest_check.get("complete") is not True
            or manifest_check.get("data_date") != ETL_Date
            or actual_entity != expected_entity):
        raise ValueError("Manifest chưa chốt hoặc sai ngày/object")
    if type(manifest_check.get("count")) is not int or manifest_check["count"] < 0:
        raise ValueError("Manifest count không hợp lệ")
    print("Landing:", TABLE_NAME, ETL_Date, manifest_check["count"], flush=True)
    # init_spark() dùng getOrCreate theo mẫu; không chạy cell ghi Bronze.
    check_spark = init_spark()
    check_spark.conf.set("spark.sql.session.timeZone", "Asia/Ho_Chi_Minh")
    check_spark.catalog.refreshTable(TABLE_NAME)
    groups = (check_spark.table(TABLE_NAME)
        .filter(F.col("data_date") == F.lit(ETL_Date).cast("date"))
        .groupBy("run_id", "landing_run_id").count().collect())
    for group in groups:
        print(group.asDict(), flush=True)
    actual = sum(group["count"] for group in groups)
    same_run = all(group["landing_run_id"] == manifest_check["run_id"] for group in groups)
    current_manifest = json.loads(check_s3.get_object(
        Bucket=BUCKET_NAME, Key=key
    )["Body"].read())
    if current_manifest != manifest_check:
        raise ValueError("Landing đã bị thay thế khi đang đối soát")
    if actual == 0 and manifest_check["count"] == 0:
        print("Hai bên rỗng; cần bằng chứng commit batch rỗng.", flush=True)
    elif actual == manifest_check["count"] and same_run:
        print("Count và landing_run_id khớp manifest; chưa so toàn bộ nội dung.", flush=True)
    else:
        print("Chưa khớp: kiểm tra ngày/table/run trước khi replay.", flush=True)
finally:
    check_s3.close()
```

Đây là query count/provenance, không so nội dung mọi bản ghi hoặc chứng minh API trả đủ dữ liệu. Lỗi metastore/kết nối nghĩa là chưa xác minh được; không kết luận bảng không có dữ liệu. Snippet không gọi API hoặc đọc/ghi bảng log.

## Lỗi và lịch

Phân biệt đã commit/lỗi log với lỗi ghi. Bronze replay từ Landing đã chốt, không gọi lại API để sửa log/metastore. Không tắt TLS/đổi endpoint ngẫu nhiên. Lịch 04:30 Việt Nam mới là dự kiến bàn giao; chưa tạo job/schedule trong repo này.
