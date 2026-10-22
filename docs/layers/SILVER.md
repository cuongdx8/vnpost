# Silver hiện hành — thiết kế, HRM/VLP chưa có implementation

Giữ trạng thái hiện hành, không tạo Silver theo ngày. Khóa: HRM id, VLP orderCode. MERGE/UPSERT tìm khóa toàn bảng, kể cả partition cũ.

- Deduplicate theo khóa, giữ data_date lớn nhất.
- Bản mới hơn được cập nhật; bản cũ không ghi đè trạng thái mới.
- Cùng khóa/ngày/nội dung là replay; cùng khóa/ngày khác nội dung cần báo xung đột hoặc quy tắc đã chốt.
- Chuẩn hóa kiểu, khóa, mapping và giữ provenance.
- Không suy diễn action/status thành hard delete.

Gold đọc Silver current có thể mất phiên bản trung gian khi bỏ lỡ batch. Muốn đủ lịch sử cần batch/change feed hoặc snapshot có thể replay, hoặc điều phối phù hợp. Chưa tuyên bố đã có CDC/lịch sử Silver.

VLP phải chốt cách lấy cập nhật đơn cũ và grain bảng con parcel/fee/tracking trước khi thiết kế downstream.
