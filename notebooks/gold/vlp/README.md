# Gold — VLP

Chưa có notebook Gold trong bộ bàn giao. Grain của fact/dimension, mapping order/parcel/fee/tracking và khóa đích cần được thiết kế sau khi kiểm chứng Bronze và triển khai Silver.

Quy tắc dimension đã ghi nhận: Type 1 dùng MERGE/UPSERT; SCD2 dùng `HASH_DIFF`, `RECORD_START_DATE`, `RECORD_END_DATE`, `F_LATEST_RECORD_INDICATOR`, `GOLD_LOAD_TIME`. Quy tắc này chưa thay thế thiết kế fact hoặc chứng minh pipeline Gold đã triển khai. Cần giải quyết phạm vi cập nhật đơn cũ trước khi chốt tính đầy đủ của dữ liệu downstream.
