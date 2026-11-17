# Cài đặt và preflight Blender

## Baseline

- REQUIRED trên máy Huy Anh/Mien: Blender **4.5.16**, MPFB tương thích với bản này.
- OPTIONAL trên máy web/QA nếu không thao tác 3D.
- Không thay đổi Blender hiện có trong TASK-0001. Audit ngày 2026-11-17 chỉ phát hiện Blender 5.2.4 LTS trong `C:\Program Files\Blender Foundation`; vì khác baseline nên trạng thái là `FAIL`, không phải PASS.

Blender và app độc lập. MPFB là Blender extension, không phải npm package hoặc system pip package.

## MPFB manual check

1. Mở đúng Blender 4.5.16.
2. Vào `Edit > Preferences > Get Extensions/Add-ons` (tùy cách MPFB được cài).
3. Tìm MPFB, xác nhận enabled và không có error trong UI/System Console.
4. Ghi version/screenshot vào QA evidence. Không cài lại hoặc upgrade khi chưa backup và thống nhất.

## Asset hiện có

`blender/avatar_master.blend` tồn tại trước scaffold và được giữ nguyên. Đây là master **candidate**, chưa xác minh MPFB, armature, bone hierarchy hoặc action compatibility. Không Save bằng Blender version khác. Tạo working copy theo asset workflow trước khi kiểm tra ở TASK-0002.

## Read-only preflight chuẩn bị sẵn

Sau khi tạo working copy và set `BLENDER_PATH`, chạy từ repository root bằng CMD:

```cmd
"%BLENDER_PATH%" "blender\working\huy-anh\avatar_preflight.blend" --background --python "blender\scripts\preflight.py"
```

Script chỉ inventory Blender version, MPFB candidate, armature/bones, finger-name candidates, mesh/armature relation và Actions; không gọi save/mutate. TASK-0001 **chưa chạy** lệnh này. Kiểm tra tên ngón chỉ là heuristic, phải manual review.

## Export GLB ở task sau

1. Dùng approved master revision và file `Snnn.blend` của animator.
2. Đảm bảo 30 FPS, root transforms, orientation, frame range và clip `Snnn_MAIN` theo hợp đồng.
3. Export glTF 2.0 dạng GLB, animations/skin/material cần thiết, vào `assets/exports/signs/Snnn.glb`.
4. Chạy `npm run validate:assets`.
5. Manual review trong browser và preview front/side; ghi evidence.
6. Chỉ sau technical + content approval mới copy/publish vào `apps/web/public/models/signs/` và cập nhật metadata.

Blender 4.5 Action Slots/NLA có thể làm tên/selection export khác dự kiến; luôn kiểm tra clip thực tế trong GLB. Không sửa metadata để hợp thức hóa export sai.
