# Gold — HRM

Chưa có notebook Gold trong bộ bàn giao. Cần xác minh Bronze và triển khai Silver trước khi chốt bảng đích, mapping và khóa dimension HRM.

Quy tắc thiết kế đã ghi nhận: Dimension Type 1 dùng MERGE/UPSERT; nếu dùng SCD2 thì có `HASH_DIFF`, `RECORD_START_DATE`, `RECORD_END_DATE`, `F_LATEST_RECORD_INDICATOR`, `GOLD_LOAD_TIME`. Chưa chốt object nào áp dụng Type 1 hay SCD2 trong bộ này; code và kiểm thử cần thực hiện riêng. Tập initial gộp nhiều năm vào ngày batch không tự tạo lịch sử SCD2 quá khứ.
