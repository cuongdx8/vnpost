# VNPOST — Data Pipeline

Bộ source chuẩn bị chuyển sang project mới và quản lý bằng Git. Luồng chính: **API → Landing JSON + manifest → Bronze Iceberg → Silver hiện hành → Gold**. Cập nhật: 22/10/2026, múi giờ Việt Nam.

## Bắt đầu đọc

1. [Window context cho project mới](docs/context/WINDOW_CONTEXT.md).
2. [Trạng thái và việc còn lại](docs/STATUS.md).
3. [Rule API ingest](docs/rules/API_INGEST.md) và [quy ước chung](docs/rules/PIPELINE_CONTRACT.md).
4. Rule layer: [Landing](docs/layers/LANDING.md), [Bronze](docs/layers/BRONZE.md), [Silver](docs/layers/SILVER.md), [Gold/SCD2](docs/layers/GOLD.md).
5. [Cấu hình môi trường và credentials](config/README.md), [chạy CP4D](docs/RUNBOOK.md), [chuyển project/Git](docs/GIT_WORKFLOW.md).

## Cấu trúc

```text
data_pipeline/
├── AGENTS.md
├── README.md
├── notebooks/
│   ├── landing/{hrm,vlp}/             # 3 notebook
│   ├── bronze/{hrm,vlp}/              # 3 notebook
│   ├── silver/{hrm,vlp}/              # Chưa có code
│   └── gold/
│       ├── hrm/                      # Chưa có code
│       ├── vlp/                      # Chưa có code
│       └── cas_admin/                # dim_org SCD2 draft
├── config/
│   ├── environments/{dev,uat,prod}.json
│   ├── credentials.catalog.json      # Tên/mục đích key, không có giá trị
│   └── secrets/
│       ├── secrets.example.json      # Đưa lên Git
│       └── dev.local.json            # Key DEV thật, Git bỏ qua
├── docs/{context,rules,layers,sources}/
├── scripts/                          # Tạo env, validate, đóng gói source
├── tests/                            # Test local
├── pipeline_manifest.json
├── .local/                           # Context gốc, backup, job env; Git bỏ qua
└── dist/                             # ZIP source; Git bỏ qua
```

Tên notebook: `NB_<layer>.<source>.<object>.ipynb`. Draft có hậu tố `.draft`. [Inventory](pipeline_manifest.json) ghi hash hiện hành, baseline và phụ thuộc.

## Phạm vi

| Nguồn/object | Landing | Bronze | Silver | Gold |
|---|---|---|---|---|
| HRM/unit | Có code; bàn giao initial 29.180 dòng | Có code; cần đối soát thật | Chưa có | Chưa có |
| HRM/employee | Có code; cần xác minh paging | Có code; cần đối soát thật | Chưa có | Chưa có |
| VLP/order_detail | Có code; cần probe/ingest thật | Có code; cần đối soát thật | Chưa có | Chưa có |
| CAS Admin/dim_org | Ngoài bộ này | Ngoài bộ này | Tham chiếu bảng nguồn | SCD2 draft, đã review |

Credentials hiện tại thuộc **DEV theo xác nhận chủ dự án**. URL VLP có hostname UAT; giữ nguyên và cần xác minh routing. UAT/PROD chưa được cấu hình.

## Kiểm tra source

Chạy từ repo root; tooling chỉ dùng thư viện chuẩn Python:

```bash
python3 scripts/validate_repository.py
python3 -B -m unittest discover -s tests -v
```

## Chuẩn bị biến CP4D

```bash
python3 scripts/build_job_env.py --environment dev --layer bronze --source hrm --object unit --etl-date 2026-10-21
```

Tạo `.local/jobs/dev/bronze.hrm.unit.env` với các dòng `NAME=value` để nhập vào CP4D job. Không in key ra terminal, không chạy notebook. `--dry-run` chỉ kiểm tra cấu hình và in tên biến.

Notebook đọc trực tiếp environment, không tự đọc JSON hoặc import module của repo trên CP4D. Cần truyền biến môi trường khi import source mới; cấu hình DEV không còn được nhúng làm default trong notebook.

## Mang sang project mới

Giữ toàn bộ folder này nếu cần cả source lẫn key local trên máy. Khi dùng Git clone/ZIP source, chuyển `config/secrets/dev.local.json` riêng vào đúng vị trí. Context nguyên bản chứa key chỉ nằm trong `.local/`.

```bash
python3 scripts/package_source.py
```

Kết quả: `dist/vnpost-data-pipeline-source.zip`, không chứa key thật/private handoff. Repo được khởi tạo trên nhánh `main`, remote `origin`: https://github.com/cuongdx8/vnpost.git. Credentials thật và private handoff được Git bỏ qua; trạng thái đồng bộ kiểm tra bằng `git status` và `git log`.
