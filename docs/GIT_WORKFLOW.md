# Chuyển project và quản lý Git

## Repo root

Dùng chính folder data_pipeline làm repo root; không dùng thư mục mirror project cũ làm root. Tất cả link nội bộ tương đối, không phụ thuộc đường dẫn máy cũ.

Có hai cách chuyển:

- Copy toàn bộ folder trên máy: source + local credentials/private context vẫn có, nhưng .gitignore sẽ loại key khi Git quản lý.
- Git clone/ZIP source: chỉ có source/config công khai/mẫu; copy config/secrets/dev.local.json riêng từ máy gốc. File key không có trong ZIP source.

Mở project mới tại folder này, dùng prompt trong [WINDOW_CONTEXT](context/WINDOW_CONTEXT.md). Nếu local secrets không được chuyển thì source vẫn validate/test được nhưng tool tạo env chạy thật sẽ báo thiếu file key.

## Khởi tạo khi bạn sẵn sàng

Repo hiện đã khởi tạo nhánh `main`, remote `origin` https://github.com/cuongdx8/vnpost.git theo yêu cầu chủ dự án. Các lệnh dưới đây là quy trình tham khảo cho lần khởi tạo mới:

```bash
git init -b main
python3 scripts/validate_repository.py
python3 -B -m unittest discover -s tests -v
git status --short --ignored
git check-ignore config/secrets/dev.local.json .local/handoff/VNPOST_API_Pipeline_Context.md
```

Kiểm tra trước staging: secrets và .local phải được Git bỏ qua; notebook không lưu output/execution count; UAT/PROD không có key DEV. Không dùng git add -f cho file private.

```bash
git add README.md AGENTS.md .gitignore .gitattributes .editorconfig config docs notebooks scripts tests pipeline_manifest.json
git diff --cached --stat
git diff --cached --name-only
git commit -m "Organize VNPOST pipeline source and environment configuration"
```

Remote/repo URL do chủ dự án chỉ định: https://github.com/cuongdx8/vnpost.git. Kiểm tra trạng thái đồng bộ bằng `git status` và `git log`. Chưa thêm CI theo nhà cung cấp Git cụ thể; các lệnh validate/test dùng được trong CI sau này.

## Nhịp làm việc

- Một thay đổi nguồn/layer hoặc config có mục đích rõ trong một nhánh/commit; review notebook diff, giữ output sạch.
- Sửa source notebook có chủ đích thì cập nhật hash inventory, STATUS và WINDOW_CONTEXT nếu trạng thái/contract đổi.
- Công khai tên/mục đích key, giữ giá trị trong secrets local hoặc secret store của môi trường/CI. Không dùng key DEV cho PROD.
- .gitignore không xóa file đã được theo dõi trong repo có sẵn; luôn kiểm tra staged/tracked paths khi nhập source vào repo khác.

## ZIP source

```bash
python3 scripts/package_source.py
```

Tool validate trước khi đóng gói, bỏ .local, mọi secrets file trừ mẫu/README, generated job env, output và cache. ZIP nằm dưới dist, không chứa credentials thật. Chuyển key riêng nếu cần chạy môi trường DEV trên máy mới.
