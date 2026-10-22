# Trạng thái — 22/10/2026

## Bằng chứng hệ thống từ bàn giao

| Nguồn/object | Có bằng chứng trong bàn giao | Chưa xác nhận |
|---|---|---|
| HRM/unit Landing | Initial 29.180 dòng, 1 file, manifest complete=true; ETL_Date=2026-10-21, cửa sổ 2020-01-01 → 2026-10-22 | Đối soát độc lập với nguồn; hiệu lực token hiện tại |
| HRM/unit Bronze | Có code | Chưa có log/query đối soát ingest thành công |
| HRM/employee | API trang 1 có 1.000 dòng, total=158658 | Tên request paging, total scope, lấy đủ trang, ingest Bronze |
| VLP/order_detail | Có code và kết quả mô phỏng/signature được báo trong phiên cũ | API/ingest/Bronze thực tế, epoch unit và cập nhật đơn cũ |
| CAS Admin/dim_org | Draft có output lưu changed=0, bỏ log/query rỗng | Gold đầy đủ, job dùng được cho backfill/production |
| Silver/Gold HRM/VLP | Có quy tắc thiết kế | Chưa triển khai code |

Các bằng chứng trên là ghi nhận lịch sử, chưa được kiểm tra lại trên CP4D trong project local.

## Công việc ở repo hiện tại

- Tổ chức 6 notebook HRM/VLP theo notebooks/layer/source; thêm notebook CAS Admin SCD2 đã review dưới dạng draft.
- Tách URL/public config theo DEV/UAT/PROD; DEV lấy giá trị được giao, UAT/PROD chưa cấu hình.
- Tách 8 biến credentials hiện tại sang config/secrets/dev.local.json, Git bỏ qua. DEV do chủ dự án xác nhận; chưa xác minh key còn hiệu lực.
- Bỏ credentials default và output khỏi source. Notebook đọc job environment; tool tạo file env không chạy pipeline.
- Lưu context gốc và backup trong .local/handoff/, không có trong Git/ZIP source.
- Tạo README, API/layer rules, source notes, context chuyển project, hướng dẫn Git và tooling/test local.
- Giữ thuật toán ingest/write đã bàn giao. Bổ sung tự động đối soát HRM trước đó đã hoàn tác và không được đưa lại.
- Khởi tạo Git nhánh `main`, gắn remote `origin` https://github.com/cuongdx8/vnpost.git theo yêu cầu chủ dự án để đưa source lên GitHub. Secrets và private handoff được Git bỏ qua.
- Validation đạt; 17 test offline đạt trước khi tạo commit đầu tiên.
- Chưa gọi API/S3/Spark/CP4D, chưa deploy hoặc tạo lịch.

## Thứ tự tiếp tục

1. Tạo project/repo mới từ bộ source này, chuyển file secrets DEV riêng, đọc WINDOW_CONTEXT rồi validate source.
2. Xác minh VLP Bronze theo trạng thái cuối bàn giao: đúng notebook/table/ngày, kernel/cell, stage/committed, manifest/count/landing_run_id.
3. HRM Unit Bronze đối soát tập initial với ETL_Date=2026-10-21, kỳ vọng theo bàn giao 29.180 dòng nhưng phải đọc manifest hiện hành.
4. HRM Employee xác minh request paging và total scope, không đoán field.
5. Probe VLP: secret/routing URL, epoch unit, filter ngày tạo; chốt cách lấy cập nhật đơn cũ.
6. Thiết kế Silver và Gold sau khi Bronze xác nhận; xử lý review CAS Admin trước khi dùng draft.

## Các quyết định còn mở

- URL VLP trong DEV profile có hostname UAT; cần xác minh routing đúng môi trường.
- HRM initial window params chưa tích hợp; baseline daily vẫn date_start=ETL_Date.
- Gold cần lịch sử đủ phiên bản thì phải chốt replay/change feed trước khi dựa Silver current.
- Lịch 04:30 Việt Nam là dự kiến từ bàn giao, chưa tạo automation/job.

Cập nhật trạng thái bằng log/query đã quan sát được. Chạy test local không nâng trạng thái thành ingest thành công.

## Kiểm tra local

17 test offline đạt; 7 notebook/75 code cell được kiểm tra cú pháp và inventory. Xem [phạm vi validation](VALIDATION.md). Kết quả không thay thế đối soát CP4D.
