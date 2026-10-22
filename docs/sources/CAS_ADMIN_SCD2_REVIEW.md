# CAS Admin dim_org — draft review

Notebook JSON người dùng gửi để review. Giữ draft đã tách credentials/output; chưa sửa thuật toán và không đưa vào tool tạo job.

Nguồn silver.cas_admin.mcas_organization_standard; đích gold.dwh.dim_org. Business key UNIT_CODE; surrogate ORG_SKEY; hash 12 thuộc tính. Stage CLOSE/INSERT trong một MERGE, end=data_date−1, current='1'.

## Việc cần sửa trước triển khai

1. SQL_SOURCE lọc ingest_time theo LOAD_DATE ngày chạy thực tế; ETL_DATE chủ yếu ở log. Cần batch/watermark có thể replay.
2. Đọc Silver current có thể mất phiên bản trung gian khi bỏ lỡ batch.
3. Thêm business_hash vào bảng cũ chưa backfill gây thay đổi giả; cần migration hash.
4. MAX(ORG_SKEY)+ROW_NUMBER() cần một writer/cấp khóa khác. Kiểm tra current/key và surrogate trước MERGE.
5. Ngày Python máy và Spark session timezone chưa thống nhất Việt Nam.
6. Bỏ log changed=0 khó phân biệt nguồn rỗng/không thay đổi; lỗi log sau MERGE có thể che commit.
7. RUN_MODE chưa có initial branch. Đang từ chối thay đổi cùng ngày/ngày cũ, chưa xử lý late-arriving/correction đầy đủ.

Output baseline từng báo SCD2_CHANGED=0, bỏ log, query log rỗng. Chưa chứng minh Gold đầy đủ. Output đã bỏ khỏi source Git; bản gốc chỉ ở private handoff local.
