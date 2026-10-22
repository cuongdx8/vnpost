# VLP — order_detail

API code vnp.eoms.order.page.detail.sub, app VLP, scheme VLP-EOMS. URL theo môi trường; URL được giao có hostname UAT, credentials hiện phân loại DEV theo chủ dự án.

Outer body là chuỗi JSON. Sign là MD5 lowercase của canonical inner body + & + secret. Sort key theo Java; flatten object đệ quy không thêm prefix; array giữ thứ tự. Không ký appCode/appApiCode/schemeCode, không dùng chữ ký cố định khi request thay đổi.

Response: success, data.tableData; paging data.paging.currentPage/pageSize/totalCount. Một API gộp order/parcel/fee/tracking theo spec bàn giao. Code bắt thiếu/lặp trang, total thay đổi, trùng orderCode, pageSize khác request và max pages.

## Cửa sổ

- VLP_DATE_FROM inclusive, VLP_DATE_TO exclusive ở mức ngày; mặc định ETL_Date → ETL_Date+1.
- createTimeEnd được trừ 1 đơn vị do spec ghi end inclusive.
- VLP_TIME_UNIT mặc định milliseconds; spec chỉ ghi Long, cần xác minh thật.
- Chỉ có filter createTime, chưa có update-time; daily chưa bảo đảm thu thay đổi/tracking đơn cũ.
- probe_api() đọc một trang, không ghi/xóa Landing. VLP_ORDER_CODE chỉ dùng probe; extract từ chối lọc một đơn.

Landing spool disk + SQLite. Bronze giữ 89 trường mẫu dạng string/JSON cùng raw_record và technical fields, không explode nested.

Initial mẫu có sẵn: ETL_Date=2026-10-21, VLP_DATE_FROM=2020-01-01, VLP_DATE_TO=2026-10-22. Chưa có bằng chứng ingest thật.

Signing self-test trong source mới dùng secret giả dành cho fixture. Key thật đã tách khỏi code; không thay thuật toán ký request.
