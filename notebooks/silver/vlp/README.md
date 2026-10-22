# Silver — VLP

Chưa có notebook Silver trong bộ bàn giao. Đầu vào dự kiến: `bronze.vlp.order_detail`; khóa nguồn `orderCode`.

Thiết kế đã ghi nhận: MERGE/UPSERT trạng thái hiện hành khi `data_date` mới hơn, tìm khóa cả các partition cũ; deduplicate theo khóa và ngày lớn nhất; cùng khóa/cùng ngày khác nội dung cần quy tắc xử lý xung đột. Không có Silver theo ngày hoặc cơ chế hard delete suy diễn.

Bronze giữ nested data dạng JSON string và `raw_record`. Việc tách parcel/fee/tracking thành bảng con cần thiết kế grain, khóa và mapping riêng. Cần làm rõ cách bắt cập nhật đơn cũ trước khi khẳng định Silver phản ánh đủ trạng thái nguồn; xem `../../../docs/STATUS.md`.
