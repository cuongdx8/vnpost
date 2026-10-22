# HRM — Unit và Employee

URL trong profile; token trong secrets/job environment. Endpoint Unit: /api/nhansu/danhsachdonvi. Employee: /api/nhansu/danhsachnhansu.

Request được ghi nhận thành công: POST JSON, đồng thời Authorization Bearer và access_token trong body. Không đổi sang body-only/form/query token hoặc JSON-RPC.

Daily: date_start=ETL_Date, date_end=ETL_Date+1. Chưa suy ra inclusive/exclusive của API từ cách truyền này. Cần success is True, result là list. Unit đọc một response; Employee kiểm tra paging/total.

Employee có bằng chứng trang đầu 1.000 dòng, total=158658. Chưa xác minh tên request paging. HRM_PAGE_PARAM/HRM_SIZE_PARAM để trống tới khi có tên thật; không suy ra từ pageindex/pagesize response. Count<total khi thiếu paging phải dừng trước khi thay Landing. Cần xác minh total có theo filter ngày.

## Unit initial đã ghi nhận

```text
ETL_Date=2026-10-21
date_start=2020-01-01
date_end=2026-10-22
count=29180
manifest complete=true; files=1
```

Initial được sửa trực tiếp trên CP4D theo ảnh/log bàn giao. Source local vẫn daily. Chỉ đặt HRM_DATE_START/HRM_DATE_END chưa có tác dụng; snippet chưa được tích hợp. Bronze replay dùng cùng ETL_Date và manifest còn hợp lệ.

Baseline đã bỏ cờ confirm date/complete. HRM giữ response trong RAM. Chưa đối soát nguồn độc lập ngoài count API.
