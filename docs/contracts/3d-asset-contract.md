# Hợp đồng asset 3D Blender ↔ Three.js

Owner phối hợp: Le Huy Anh (master/rig/export) và Doan Khanh Nhat (viewer). Mọi thay đổi hợp đồng phải được hai phía xem xét; thay đổi nội dung/approval cần Do Phuong Thao.

## A. Master rig

- Canonical master duy nhất là `blender/master/avatar_master.blend`, version `Master Avatar v1.0.0`; hash/version nằm trong `blender/master/master-avatar.manifest.json`.
- `blender/avatar_master.blend` là pre-neutral legacy source; `blender/master/avatar_master_neutral_candidate.blend` là nguồn promotion được giữ để truy vết. Cả hai không còn là canonical.
- Một canonical armature hierarchy. Không đổi bone name, parent, rest pose, scale hoặc thay rig độc lập.
- Master change dùng branch/PR riêng, ghi lý do, backup và skeleton signature trước/sau. Huy Anh điều phối; Mien không ghi đè master từ working file.
- Animator tạo file riêng từ approved revision và ghi master commit/hash trong handoff.
- TASK-0008 promote rc.3 đã owner duyệt: canonical mở ở frame 1 neutral, 30 FPS, không có Action/NLA được assign và giữ nguyên 137-bone hierarchy. Bốn Action được giữ trong data-block với nhãn technical fixture để tái sử dụng; không phải lesson content.

## B–C. ID, clip và file naming

| Loại | Mẫu | Ví dụ định danh |
|---|---|---|
| Sign ID | `Snnn` | `S001` |
| Action/clip | `<ID>_MAIN` | `S001_MAIN` |
| Blender source | `<ID>.blend` | `S001.blend` |
| GLB | `<ID>.glb` | `S001.glb` |
| Preview | `<ID>_front.mp4`, `<ID>_side.mp4` | `S001_front.mp4` |

ID chỉ là khóa kỹ thuật, không gán ý nghĩa ký hiệu khi chưa có metadata được xác minh.

## D. Animation conventions

- Blender 5.2.4 LTS, 30 FPS, frame start `1`; frame end đặt đúng cuối clip và ghi vào metadata sau export. Exported `AnimationClip.duration` là duration kỹ thuật thực tế.
- Frame 1 là neutral starting pose được Huy Anh phê duyệt. Không đổi rest pose để tạo animation. Giữ neutral ngắn ở đầu/cuối nếu content/reference yêu cầu, nhưng cả nhóm dùng cùng convention.
- 1 Blender unit = 1 metre. Armature/root ở location `(0,0,0)`, rotation `(0,0,0)`, scale `(1,1,1)` trước animation/export; apply transforms trong master, không tùy tiện apply ở sign file.
- Blender: Z-up, character nhìn về `-Y`. glTF exporter chuyển sang right-handed Y-up; front sau export kỳ vọng nhìn về `+Z`. Three.js camera mặc định đề xuất `(0, 1.45, 3.0)`, nhìn `(0, 1.25, 0)`; tinh chỉnh theo bounding box nhưng không xoay model để “sửa” export.
- Tránh root motion không cần thiết. Giữ tay, mặt trong frame, không clipping và không biến dạng mesh hỏng. Mặt/hand visibility, timing và motion correctness cần manual review.

## E. GLB packaging

Release đầu dùng **một self-contained GLB mỗi sign**, chứa model, armature/skin, material/texture cần thiết và đúng một clip chính. Lợi ích là tích hợp độc lập; chi phí là file lặp/lớn hơn. Shared-skeleton runtime hoặc retargeting chỉ được xem xét sau milestone Day 5 với ADR riêng.

Luồng file: working `.blend` → `assets/exports/signs/Snnn.glb` để kiểm tra → `apps/web/public/models/signs/Snnn.glb` khi approved technical/content gate.

Hai profile master/facial foundation:

- `MASTER_STATIC`: canonical neutral character, skin/material, không animation, không Morph Target; export reference ở `assets/exports/master/avatar-master-v1-rc1.glb`.
- `ANIMATION_WITH_MORPHS`: future sign source có canonical skeleton, bone Action và approved facial Morph Targets/weight animation. TASK-0005 chỉ chứng minh transport bằng diagnostic probe; không phải production facial readiness.

Profile exact options và limitations nằm trong `docs/architecture/MASTER_AVATAR.md`. Diagnostic Morph Target không được đưa vào master/production GLB.

## F. Blender 5.2 Actions/Slots và Three.js

- Blender 5.2 dùng slotted Actions và exporter có nhiều animation mode. Tạo Action Slot đúng `OBJECT` target. Với một clip technical/production đã cô lập, dùng `ACTIONS` mode; TASK-0003 chứng minh `ACTIVE_ACTIONS` tạo tên generic `Animation`, còn `ACTIONS` giữ đúng Action name.
- Trong bản export copy, chỉ giữ/bật action intended, đặt tên `Snnn_MAIN`; nếu dùng NLA thì một track/strip intended, không mute, không strip thừa. Chọn export mode Action/NLA nhất quán trong preset được duyệt.
- Sau mỗi export phải kiểm tra JSON/Three `gltf.animations`: có đúng clip expected và duration > 0. Nếu exporter tạo tên khác, sửa pipeline/source rồi export lại; không đổi metadata để che lỗi tùy tiện.
- MPFB body có nonzero shape-key mix và `Hide helpers` MASK modifier. Trên export-only copy phải bake current shape mix, dùng `export_apply=True` để loại helper geometry nhưng giữ Armature modifier, giới hạn 4 skin influences cho Three.js và không save ngược vào working/master source.
- Có thể dùng `export_armature_object_remove=True` khi validator/runtime xác nhận; TASK-0004 neutral GLB đạt 0 Khronos errors/warnings với cấu hình này.
- Viewer dùng `GLTFLoader`, chọn clip bằng exact name, tạo `AnimationMixer`, `clipAction`. Play/pause giữ time; replay đặt time về 0; loop dùng `LoopRepeat` khi bật và `LoopOnce` khi tắt; speed dùng `mixer.timeScale = 0.5` hoặc `1`. Reset dừng action, đặt time 0, phục hồi model transform và camera/controls defaults.
- Rotate/zoom do OrbitControls; tắt pan nếu UI không cần. Ánh sáng tối thiểu: ambient/hemisphere + key directional, không phụ thuộc Blender scene lights. Camera phải fit toàn thân và ưu tiên thấy tay/mặt.

## G. Validation gates

Tự động (`npm run validate:assets`) có thể kiểm tra:

- file đọc được, magic/version/length GLB hợp lệ;
- có expected clip, mesh và skin;
- joint-name/parent hierarchy signature giống giữa các sign;
- approved metadata không trỏ đến file thiếu.

Khi có asset thật nên bổ sung Khronos glTF Validator trong CI/task tiếp theo. Structural PASS **không** chứng minh animation đúng.

Manual bắt buộc:

- mở trong browser/GLTFLoader; play, pause, replay, loop, 0.5×/1× và reset;
- kiểm tra duration/timing, camera, lighting, texture, global rotation/scale;
- kiểm tra front/side preview: clipping, hand/finger/face, mesh deformation;
- expert/content verification và evidence theo `VERIFICATION_PROTOCOL.md`.

Kết quả dùng đúng nhãn `PASS`, `FAIL`, `SKIPPED`, `NOT YET TESTED`; `SKIPPED` không phải `PASS`.

## H. Rig compatibility

Validator tạo signature từ joint names và parent hierarchy của mỗi GLB; khác signature là `FAIL`, không silently accept. Trước export, preflight cũng phải so armature bone count/name/parent và mesh Armature modifiers với canonical snapshot. Nếu khác: dừng publish, giữ file, báo Huy Anh, xác định master revision; không rename/retarget tự động trong deadline nếu chưa có quyết định chung.
