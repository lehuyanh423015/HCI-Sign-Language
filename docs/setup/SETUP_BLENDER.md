# Cài đặt và preflight Blender

## Baseline

- REQUIRED trên máy Huy Anh/Mien: Blender **5.2.4 LTS**, MPFB **2.0.18**.
- OPTIONAL trên máy web/QA nếu không thao tác 3D.
- TASK-0003 chính thức thay baseline cũ bằng 5.2.4 LTS theo yêu cầu owner. Không tìm/cài/khôi phục Blender 4.5.16 và không tự upgrade 5.2.4/MPFB.

Blender và app độc lập. MPFB là Blender extension, không phải npm package hoặc system pip package.

## MPFB manual check

1. Mở đúng Blender 5.2.4 LTS.
2. Vào `Edit > Preferences > Get Extensions/Add-ons` (tùy cách MPFB được cài).
3. Tìm MPFB, xác nhận enabled và không có error trong UI/System Console.
4. Ghi version/screenshot vào QA evidence. Không cài lại hoặc upgrade khi chưa backup và thống nhất.

TASK-0002/0003 xác minh MPFB 2.0.18 đã cài, enabled và load được trong profile Blender 5.2 (`bl_ext.user_default.mpfb`). Manifest yêu cầu Blender tối thiểu 4.2.

## Cấu hình executable theo máy

Ưu tiên biến `BLENDER_EXECUTABLE`. Trong Windows CMD:

```cmd
set "BLENDER_EXECUTABLE=C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
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

Canonical master: `blender/master/avatar_master.blend`, version `Master Avatar v1.0.0`. Kiểm tra hash/version trong `blender/master/master-avatar.manifest.json` trước khi tạo working copy.

`blender/avatar_master.blend` là pre-neutral legacy source; `blender/master/avatar_master_neutral_candidate.blend` và rc.3 trong `blender/working/huy-anh/task-0007a-facial-refinement/` được giữ để audit. Không ghi đè hoặc dùng các file này thay canonical. Canonical giữ bốn Action được gắn nhãn technical fixture nhưng không assign vào scene neutral; chúng không phải sign/lesson đã duyệt.

Tạo working copy trong CMD, không save trực tiếp master:

```cmd
mkdir blender\working\<member>\<task-or-sign>
copy /Y blender\master\avatar_master.blend blender\working\<member>\<task-or-sign>\Snnn.blend
certutil -hashfile blender\working\<member>\<task-or-sign>\Snnn.blend SHA256
```

Animator copy canonical vào working folder của mình, ghi master commit/hash vào handoff và chỉ save bằng Blender 5.2.4 LTS. Không apply non-identity armature rotation, rename bone hoặc đổi rest pose.

## Read-only preflight

Không chạy inspection trên source gốc. Tạo bản sao tạm rồi chạy từ repository root bằng CMD:

```cmd
mkdir "%TEMP%\hci-vsl-preflight"
copy /Y "blender\master\avatar_master.blend" "%TEMP%\hci-vsl-preflight\avatar_master_preflight.blend"

"%BLENDER_EXECUTABLE%" --background --python-exit-code 2 --python "blender\scripts\inspect_environment.py" -- --expected-version 5.2.4 --require-mpfb --output "%TEMP%\hci-vsl-preflight\environment.json"

"%BLENDER_EXECUTABLE%" "%TEMP%\hci-vsl-preflight\avatar_master_preflight.blend" --background --python-exit-code 3 --python "blender\scripts\inspect_rig.py" -- --expected-version 5.2.4 --expected-fps 30 --output "%TEMP%\hci-vsl-preflight\rig-inventory.json"

"%BLENDER_EXECUTABLE%" "%TEMP%\hci-vsl-preflight\avatar_master_preflight.blend" --background --python-exit-code 4 --python "blender\tests\test_preflight.py" -- --inspect-rig "blender\scripts\inspect_rig.py"
```

Scripts chỉ inventory Blender/MPFB, scene, object, mesh, modifier, vertex group, armature, full bone hierarchy, constraint và saved selection state. Chúng không gọi save, mode change, transform hay keyframe. Dùng `--python-exit-code` để critical Python failure trả nonzero. `preflight.py` chỉ còn là compatibility entry point; dùng hai script rõ trách nhiệm ở trên.

Trên máy Mien: checkout branch/commit, `npm ci`, tạo `.env.local`, chạy `npm run doctor`, sau đó chạy ba lệnh trên bằng đúng Blender 5.2.4 LTS. Gửi JSON + output và SHA-256 working copy cho Huy Anh; không save file preflight.

## Export GLB ở task sau

1. Dùng approved master revision và file `Snnn.blend` của animator.
2. Đảm bảo 30 FPS, root transforms, orientation, frame range và clip `Snnn_MAIN` theo hợp đồng.
3. Export glTF 2.0 dạng GLB, animations/skin/material cần thiết, vào `assets/exports/signs/Snnn.glb`.
4. Chạy `npm run validate:assets`.
5. Manual review trong browser và preview front/side; ghi evidence.
6. Chỉ sau technical + content approval mới copy/publish vào `apps/web/public/models/signs/` và cập nhật metadata.

Blender 5.2 Action Slots/export mode có thể làm tên clip khác dự kiến; luôn dùng validator kiểm tra clip thực tế. `ACTIONS` mode đã giữ đúng `TECH_HAND_CONTROL_TEST`; `ACTIVE_ACTIONS` từng xuất tên generic `Animation`. Không sửa metadata để hợp thức hóa export sai.

Master reference và facial transport profiles được định nghĩa tại `docs/architecture/MASTER_AVATAR.md`. Chạy:

```cmd
npm run validate:master-static
npm run validate:morph-poc
```

Morph POC chỉ là diagnostic GLB. Chưa có production facial Shape Keys, eyeball/pupil asset hoặc Three.js facial controller.

## Technical prototype TASK-0003

Baseline working source: `blender\working\huy-anh\technical-hand-test.blend`. Neutral working source: `blender\working\huy-anh\technical-hand-test-neutral.blend`. Viewer dùng canonical `assets\exports\technical\technical-hand-test-neutral.glb`; TASK-0003 GLB vẫn giữ làm baseline so sánh.

```cmd
npm run sync:technical-assets
npm run validate:technical-asset
npm run dev
```

Mở `http://localhost:5173/technical-viewer`. Fixture `TECH_HAND_CONTROL_TEST` không thuộc S001–S006 và không phải ký hiệu đã xác minh.
