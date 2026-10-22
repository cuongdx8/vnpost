# Rule API ingest

Chọn profile môi trường tường minh. URL trong public profile, token/signing secret trong job environment. Giữ contract nguồn; không suy ra authentication hoặc request paging từ field response.

## Cửa sổ

Phân biệt cửa sổ API với ngày partition batch. HRM daily chưa đọc HRM_DATE_START/HRM_DATE_END; VLP có VLP_DATE_FROM/VLP_DATE_TO. Không đổi cách gán data_date nếu chưa thiết kế lại partition/replay/downstream.

## Chấp nhận response

- HTTP 200 chưa đủ: cần success is True và đúng dữ liệu/paging.
- Retry timeout/connection error/429/5xx có giới hạn theo code; không retry vô hạn hoặc coi lỗi là list rỗng.
- Kiểm tra thiếu/lặp trang, count/total và khóa thiếu/trùng. Total thay đổi phải dừng trước khi thay tập Landing.
- Không tự chọn một bản ghi khi cùng khóa khác nội dung.
- Giữ TLS theo cấu hình; không tắt xác minh/đổi cổng endpoint tùy tiện.

## Publish Landing

Lấy và validate xong trước khi xóa tập ngày cũ. Chỉ xóa đúng prefix nguồn/object/ngày; upload page rồi ghi manifest complete=true cuối cùng. Lỗi API trước xóa giữ tập cũ; lỗi upload không được chốt manifest cho tập thiếu.

S3 không atomic replace toàn thư mục. Manifest/checksum phát hiện thay đổi, không thay thế điều phối ngăn đọc/ghi đồng thời.

## Volume

HRM giữ response ngày trong RAM. VLP spool từng trang xuống disk, SQLite bắt trùng; cần đủ RAM cho một trang và disk cho cả tập. Rate VLP phải tính tổng job cùng gateway: baseline 5 request/giây/job, giới hạn 10 theo bàn giao, chưa kiểm tra lại.

Chi tiết nguồn: [HRM](../sources/HRM.md), [VLP](../sources/VLP.md). Quy tắc dựa trên code/bàn giao, không phải kiểm chứng API mới.
