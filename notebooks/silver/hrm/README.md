# Silver — HRM

Chưa có notebook Silver trong bộ bàn giao. Phạm vi tiếp theo là `unit` và `employee`, sau khi Bronze được xác minh.

Thiết kế đã ghi nhận: giữ trạng thái hiện hành; MERGE/UPSERT theo khóa nguồn `id`, tìm khóa cả các partition cũ; chỉ nhận bản có `data_date` mới hơn. Deduplicate theo khóa và giữ ngày lớn nhất. Cùng khóa/cùng ngày khác nội dung cần quy tắc xử lý xung đột. Không tạo Silver theo ngày hoặc suy diễn hard delete từ việc bản ghi không xuất hiện.

Đầu vào dự kiến: `bronze.hrm.unit`, `bronze.hrm.employee`. Schema và code thực thi chưa được triển khai; xem `../../../docs/STATUS.md`.
