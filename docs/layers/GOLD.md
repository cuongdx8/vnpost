# Gold và SCD2

Gold HRM/VLP chưa có code. CAS Admin dim_org là draft riêng.

Dimension Type 1 dùng MERGE/UPSERT. SCD2 cần:

- Chốt business key, grain và tracked columns; không đưa technical run/date vào hash nghiệp vụ.
- HASH_DIFF hoặc tên tương đương có encoding ổn định, xử lý NULL rõ ràng, khớp downstream.
- Tối đa một current row/business key; surrogate key duy nhất cho từng phiên bản.
- Chốt khoảng hiệu lực: draft CAS dùng Date, end inclusive=ngày mới−1, current end=NULL.
- Grain ngày: cùng ngày khác nội dung là conflict nếu chưa có correction rule. Nhiều phiên bản/ngày cần timestamp.
- Đóng cũ/thêm mới trong thao tác ghi nhất quán; replay không thêm phiên bản.
- Có chính sách late-arriving/backfill, không tự chèn vào lịch sử chỉ dựa current start date.
- Load timestamp Gold: thiết kế dự án gọi GOLD_LOAD_TIME, CAS draft dùng REC_CREATE_DATE; cần chốt schema.

Không dựng lịch sử từ một tập initial hiện hành nhiều năm. Không coi ngày batch là ngày hiệu lực nghiệp vụ khi chưa chốt contract.

Xem [review CAS Admin](../sources/CAS_ADMIN_SCD2_REVIEW.md).
