# Window context — bàn giao sang project mới

Cập nhật: 22/10/2026, Asia/Ho_Chi_Minh. File này không chứa giá trị key; có thể đưa lên Git và dùng làm context mở đầu.

## Mục tiêu

Quản lý toàn bộ source API pipeline VNPOST trong một repo Git, phân layer/nguồn, giữ cấu hình theo môi trường, phát triển tiếp từ trạng thái có bằng chứng. Các hệ thống: CP4D 5.3/OpenShift, S3 IBM ESS, Spark/Iceberg/watsonx.data; EDB là downstream datamart theo context dự án.

## Đọc theo thứ tự

1. [README](../../README.md), [AGENTS](../../AGENTS.md).
2. [STATUS](../STATUS.md), [quy ước](../rules/PIPELINE_CONTRACT.md), [API ingest](../rules/API_INGEST.md).
3. [Config](../../config/README.md), [runbook](../RUNBOOK.md).
4. Rule các layer và source liên quan trong docs/layers/, docs/sources/.

## Source hiện có

6 notebook triển khai Landing/Bronze HRM Unit, HRM Employee và VLP Order Detail tại notebooks/<layer>/<source>/. Gold CAS Admin dim_org có một draft từ notebook người dùng gửi review. Silver/Gold HRM/VLP chưa có code. Inventory và hash tại pipeline_manifest.json.

Đã tách config/secret và xóa output, chưa sửa thuật toán ingest/write. Source notebook chạy trên CP4D bằng environment variables; không import tooling repo hoặc tự đọc JSON. PIPELINE_ENV chọn dev/uat/prod; dùng scripts/build_job_env.py tạo các dòng NAME=value rồi đưa vào CP4D Advanced configuration.

## Môi trường và key

- Chủ dự án xác nhận key đang có là DEV. File thật: config/secrets/dev.local.json, mode 600 và Git bỏ qua.
- URL/public config: config/environments/dev.json. URL VLP giữ từ code có hostname UAT; cần xác minh routing, không tự thay bằng URL đoán.
- UAT/PROD là mẫu chưa điền, không có credentials. Không dùng DEV fallback.
- credentials.catalog.json mô tả tên/mục đích, chưa có bằng chứng expiry/hiệu lực key.
- Khi clone Git/giải nén ZIP source, key thật không đi kèm; cần chuyển file DEV local riêng. Không yêu cầu người dùng dán key vào chat hoặc commit key.
- Context nguyên văn chứa secrets và backup trước tổ chức nằm trong .local/handoff/ trên máy, không có trong source Git/ZIP.

## Quyết định quan trọng

- ETL_Date là ngày batch, data_date=ETL_Date; Bronze atomic overwrite partition ngày. Không DELETE rồi APPEND và không đổi ngày sang create/update nguồn tự phát.
- Một tập Landing hiện hành/ngày, layout YYYYMMDD, page + manifest chốt cuối. HRM manifest v3, VLP v1. Không dùng lại layout runs/run_id cũ.
- Bronze không gọi API; ingest_time giữ từ manifest; run_id là lần Bronze, landing_run_id là lần Landing.
- HTTP 200 chưa đủ, cần success=true và dữ liệu/paging hợp lệ. Lỗi không được coi là batch rỗng.
- Không hard delete khi chưa có tín hiệu/quy tắc nguồn.
- Silver thiết kế current MERGE theo khóa/ngày mới hơn, tìm khóa xuyên partition. Chưa có implementation.
- Gold Type 1/SCD2 theo nghiệp vụ; CAS draft còn lỗi filter ngày/replay/hash migration/cấp khóa/logging. Chưa được xem là job production.

## Trạng thái đã biết

HRM Unit initial Landing được ghi nhận 29.180 dòng, manifest complete=true, ETL_Date=2026-10-21, cửa sổ 2020-01-01 → 2026-10-22. Thay đổi initial được sửa trên CP4D; source local vẫn daily, chưa hỗ trợ HRM_DATE_START/HRM_DATE_END.

Employee chỉ có bằng chứng trang đầu 1.000/158658; chưa biết tên request paging và total có theo filter không. Không suy ra request pageindex/pagesize từ field response.

VLP có code/mô phỏng, chưa chứng minh ingest thực tế; chưa xác minh epoch unit, filter ngày tạo và cập nhật đơn cũ. Daily createTime chưa bảo đảm tracking/status mới của đơn cũ.

Không có log không chứng minh chưa ghi; lỗi log có thể xảy ra sau commit. Cần query dữ liệu/manifest thật theo ngày/count/landing_run_id. Hai bên rỗng chưa chứng minh commit batch rỗng.

## Yêu cầu đã hoàn tác

Người dùng từng yêu cầu luôn kiểm tra HRM Landing→Bronze; phần code tự động đối soát, test và docs bổ sung sau đó đã được yêu cầu hoàn tác toàn bộ. Repo hiện giữ nguyên phần logic baseline sau hoàn tác. Không tự đưa lại auto-verification khi chỉ tổ chức repo/config. Runbook vẫn giải thích cách kiểm tra độc lập theo yêu cầu vận hành.

## Việc tiếp theo

Tạo project mới từ repo, chuyển key local riêng, chạy validate/tests. Sau đó xác minh VLP Bronze và HRM Unit initial trên CP4D, xác định Employee paging, probe VLP và chốt cập nhật đơn cũ. Chỉ tiếp tục Silver/Gold/lập lịch khi có đối soát Bronze và thiết kế phù hợp.

Git được khởi tạo trên nhánh `main`, remote `origin` https://github.com/cuongdx8/vnpost.git theo yêu cầu chủ dự án để đưa source lên GitHub. Kiểm tra commit và trạng thái đồng bộ bằng `git log` / `git status`. Validation và 17 test offline đạt. Chưa deploy hoặc tạo schedule. Không có kernel/phiên đăng nhập/dữ liệu CP4D đi kèm context này.

## Prompt mở project mới

> Đọc AGENTS.md, README.md, docs/context/WINDOW_CONTEXT.md và docs/STATUS.md làm bàn giao dự án VNPOST. Tiếp tục theo trạng thái có bằng chứng, phân biệt code/test local với chạy CP4D. Source theo notebooks/layer/source; URL theo config/environments, key thật ở secrets local được Git bỏ qua. Giữ ngày batch và thuật toán baseline, không đưa lại phần auto-verification HRM đã hoàn tác. Kiểm tra việc còn lại trước khi sửa đúng layer/nguồn được yêu cầu.
