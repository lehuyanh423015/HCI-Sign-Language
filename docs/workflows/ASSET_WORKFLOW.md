# Asset workflow

## Lock và working copy

1. Animator báo `LOCK: <file/sign ID>, master revision, dự kiến unlock` trong kênh nhóm.
2. Copy approved master vào `blender/working/huy-anh/` hoặc `blender/working/mien/`; không edit trực tiếp master.
3. Đặt file `Snnn.blend`. Không làm đồng thời cùng một sign/file.
4. Save versioned recovery local ngoài tracked production nếu cần; không xóa source cũ trong cleanup.

## Handoff package mỗi sign

- `blender/working/<owner>/Snnn.blend` hoặc link/commit có kiểm soát.
- `assets/exports/signs/Snnn.glb`.
- `Snnn_front.mp4` và `Snnn_side.mp4` (chia sẻ theo phương án dung lượng đã thống nhất).
- Metadata cập nhật nhưng chưa `approved` nếu thiếu expert evidence.
- Master revision/hash, Blender/MPFB version, FPS/frame range, exporter settings, known issues.

## Gates

1. Naming/metadata validation.
2. Blender preflight: armature, bone hierarchy, finger controls, mesh relation, action.
3. GLB structural validation và rig signature.
4. Nhat chạy browser controls/camera/lighting review.
5. Thao điều phối content/expert review, lưu evidence.
6. Publish chỉ khi đủ technical + content gate; `approved` không được suy ra từ structural PASS.

`assets/staging/` và preview render là local/transient mặc định. Production export là shared area và cần Huy Anh + Nhat phối hợp; metadata approval cần Thao.
