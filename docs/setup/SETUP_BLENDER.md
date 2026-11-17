# Cài đặt và preflight Blender

## Baseline

- REQUIRED trên máy Huy Anh/Mien: Blender **4.5.16**, MPFB tương thích với bản này.
- OPTIONAL trên máy web/QA nếu không thao tác 3D.
- Không tự upgrade/downgrade. Audit TASK-0002 ngày 2026-11-17 chỉ phát hiện Blender 5.2.4 LTS tại `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe`; vì khác baseline nên trạng thái project vẫn là `FAIL`, không phải PASS. Bản 5.2 chỉ được dùng để kiểm tra read-only trên working copy.

Blender và app độc lập. MPFB là Blender extension, không phải npm package hoặc system pip package.

## MPFB manual check

1. Mở đúng Blender 4.5.16.
2. Vào `Edit > Preferences > Get Extensions/Add-ons` (tùy cách MPFB được cài).
3. Tìm MPFB, xác nhận enabled và không có error trong UI/System Console.
4. Ghi version/screenshot vào QA evidence. Không cài lại hoặc upgrade khi chưa backup và thống nhất.

TASK-0002 xác minh MPFB 2.0.18 đã cài, enabled và load được trong **profile Blender 5.2** (`bl_ext.user_default.mpfb`). Manifest yêu cầu Blender tối thiểu 4.2. Không tồn tại profile cấu hình 4.5 trên máy audit, vì vậy trạng thái MPFB trong Blender 4.5 vẫn là `NOT YET TESTED`; extension giữa hai Blender version không tự động dùng chung cấu hình.

## Cấu hình executable theo máy

Ưu tiên biến `BLENDER_EXECUTABLE`. Trong Windows CMD:

```cmd
set "BLENDER_EXECUTABLE=C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"
npm run doctor
```

Để doctor nhớ theo repository nhưng không commit đường dẫn cá nhân:

```cmd
copy .env.example .env.local
notepad .env.local
npm run doctor
```

Đặt `BLENDER_EXECUTABLE=<absolute path>` trong `.env.local`; file này bị Git-ignore. Thứ tự ưu tiên của doctor: `--blender`, environment `BLENDER_EXECUTABLE`, `.env.local`, legacy `BLENDER_PATH`, PATH, thư mục cài chuẩn. Direct Blender commands vẫn cần `set BLENDER_EXECUTABLE=...` trong CMD hiện tại.

## Asset hiện có

`blender/avatar_master.blend` tồn tại trước scaffold và được giữ nguyên. Đây là master **candidate**, chưa xác minh MPFB, armature, bone hierarchy hoặc action compatibility. Không Save bằng Blender version khác. Tạo working copy theo asset workflow trước khi kiểm tra ở TASK-0002.

## Read-only preflight

Không chạy inspection trên source gốc. Tạo bản sao tạm rồi chạy từ repository root bằng CMD:

```cmd
mkdir "%TEMP%\hci-vsl-preflight"
copy /Y "blender\avatar_master.blend" "%TEMP%\hci-vsl-preflight\avatar_master_preflight.blend"

"%BLENDER_EXECUTABLE%" --background --python-exit-code 2 --python "blender\scripts\inspect_environment.py" -- --expected-version 4.5.16 --require-mpfb --output "%TEMP%\hci-vsl-preflight\environment.json"

"%BLENDER_EXECUTABLE%" "%TEMP%\hci-vsl-preflight\avatar_master_preflight.blend" --background --python-exit-code 3 --python "blender\scripts\inspect_rig.py" -- --expected-version 4.5.16 --expected-fps 30 --output "%TEMP%\hci-vsl-preflight\rig-inventory.json"

"%BLENDER_EXECUTABLE%" "%TEMP%\hci-vsl-preflight\avatar_master_preflight.blend" --background --python-exit-code 4 --python "blender\tests\test_preflight.py" -- --inspect-rig "blender\scripts\inspect_rig.py"
```

Scripts chỉ inventory Blender/MPFB, scene, object, mesh, modifier, vertex group, armature, full bone hierarchy, constraint và saved selection state. Chúng không gọi save, mode change, transform hay keyframe. Dùng `--python-exit-code` để critical Python failure trả nonzero. `preflight.py` chỉ còn là compatibility entry point; dùng hai script rõ trách nhiệm ở trên.

Trên máy Mien: checkout branch/commit, `npm ci`, tạo `.env.local`, chạy `npm run doctor`, sau đó chạy ba lệnh trên bằng đúng Blender 4.5.16. Gửi JSON + output và SHA-256 working copy cho Huy Anh; không save file preflight.

## Export GLB ở task sau

1. Dùng approved master revision và file `Snnn.blend` của animator.
2. Đảm bảo 30 FPS, root transforms, orientation, frame range và clip `Snnn_MAIN` theo hợp đồng.
3. Export glTF 2.0 dạng GLB, animations/skin/material cần thiết, vào `assets/exports/signs/Snnn.glb`.
4. Chạy `npm run validate:assets`.
5. Manual review trong browser và preview front/side; ghi evidence.
6. Chỉ sau technical + content approval mới copy/publish vào `apps/web/public/models/signs/` và cập nhật metadata.

Blender 4.5 Action Slots/NLA có thể làm tên/selection export khác dự kiến; luôn kiểm tra clip thực tế trong GLB. Không sửa metadata để hợp thức hóa export sai.
