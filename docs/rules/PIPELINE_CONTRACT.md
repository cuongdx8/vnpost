# Quy ước chung pipeline

## Ngày và provenance

- Timezone nghiệp vụ: Asia/Ho_Chi_Minh.
- ETL_Date: ngày batch YYYY-MM-DD, mặc định T−1; cùng ngày cho các layer của cùng batch.
- data_date: ngày batch, kiểu Date và partition Bronze. Không tự gán từ create/update nguồn.
- ingest_time: thời điểm extract trong manifest, giữ nguyên khi replay.
- run_id: ID thực thi layer hiện tại; không phải khóa nghiệp vụ.
- landing_run_id: ID extract của manifest đầu vào Bronze.
- raw_record: JSON đầy đủ, giữ nested/trường mới chưa có cột schema.

Initial nhiều năm hiện lưu vào một partition batch. Không tự tái dựng lịch sử từng ngày/SCD2 quá khứ từ một tập hiện hành.

## Replay và batch rỗng

API → Landing hoàn tất → Bronze → Silver → Gold. Bronze không gọi API. Mỗi source/object/ngày chỉ có một writer; không extract lại khi Bronze đang đọc.

Success với 0 dòng là batch rỗng hợp lệ. HTTP/API lỗi không phải batch rỗng. Bronze thay ngày bằng tập rỗng chỉ khi đầu vào đã chốt hợp lệ. Hai bên count=0 chưa chứng minh đã commit.

Không hard delete khi chưa có tín hiệu xóa/quy tắc nguồn. Không suy diễn action/status, bản ghi vắng mặt hoặc thiếu trang thành delete.

## Bằng chứng và log

Không có log không đồng nghĩa chưa có dữ liệu; thiếu output không chứng minh thành công. Kiểm tra manifest và dữ liệu thật theo ngày, count, landing_run_id, khi cần so nội dung. Lỗi log sau commit phải phân biệt với lỗi ghi dữ liệu.

Landing log console/S3; Bronze thêm Iceberg log. Schema: target_table, source_table, log_message, status, start_date, end_date, step, record_count. Không log token/key/full response nhân sự hoặc đơn hàng.

Cách kiểm tra độc lập tại [runbook](../RUNBOOK.md). Bổ sung tự động đối soát HRM đã hoàn tác theo yêu cầu; repo hiện không đưa lại tính năng đó.

## Source

Ghi rõ code đã có/runtime chưa xác minh, draft hoặc chưa triển khai. Cập nhật inventory/docs/context khi sửa source. Tách public config, secret và batch params; không thêm lại cờ confirm ngày/complete cũ.
