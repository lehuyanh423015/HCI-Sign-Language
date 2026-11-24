# Quy trình pose authoring và sinh animation

Quy trình này dùng Blender 5.2.4 LTS, MPFB 2.0.18 và Master Avatar v1.0.0. Mọi lệnh Blender chạy trên working copy; không mở hoặc ghi đè `blender/master/avatar_master.blend` để author animation.

`TECH_POSE_AUTHORING_PILOT` là technical fixture phi ngôn ngữ, không phải ký hiệu VSL và không được đưa vào lesson catalog. Với sign thật, chỉ bắt đầu authoring sau khi metadata có reference hợp lệ, quyền sử dụng rõ ràng và đủ thông tin chuyển động.

## 1. Dữ liệu pose

- `blender/poses/technical-hand-poses.json` chứa các building block `neutral_hand`, `open_hand`, `closed_fist`, `index_flexed`, `thumb_flexed`, `relaxed_hand`.
- `blender/poses/technical-upper-body-poses.json` chứa neutral upper body.
- Tên finger bone dùng đúng rig MPFB: `finger1-*` đến `finger5-*`, hậu tố `.L` hoặc `.R` được module thêm theo phía.
- Giá trị pose là độ flex kỹ thuật. Đây không phải thư viện handshape VSL được duyệt.
- `finger_overrides` trong motion spec chỉ thay đổi joint được nêu; các bone ngoài pose/override được giữ nguyên cho tới khi pose khác hoặc reset thay đổi chúng.

`sign_pose_utils.py` không áp một Euler axis chung cho mọi ngón. Module thăm dò hướng biến dạng của từng PoseBone đối với lòng bàn tay cùng phía, chọn local flex axis và dấu phù hợp, sau đó tạo quaternion local. Nếu bone/hierarchy không đúng canonical rig, module dừng với lỗi thay vì đoán tên Mixamo/Rigify.

## 2. Motion specification

Schema nằm tại `docs/contracts/sign-motion-spec.schema.json`; ví dụ chạy được nằm tại `blender/animation-specs/TECH_POSE_AUTHORING_PILOT.json`.

Spec gồm:

- `identification`: sign hoặc fixture, source, Master version, animator, clip, FPS, dominant hand.
- `timing`: frame đầu, tổng frame, interpolation, meaningful interval và technical transition.
- `key_poses`: frame/hold, left/right pose, finger override, wrist/arm, head/neck/jaw và sáu NMM Morph Target hiện có.
- `review`: reference, technical, linguistic status và uncertainty.

Mỗi trường quan sát có `OBSERVED`, `ASSUMED_TECHNICAL`, `UNKNOWN` hoặc `NOT_APPLICABLE`. Không đổi `UNKNOWN` thành chuyển động tự suy diễn. Fixture bắt buộc có `sign_id: null`, `source_reference: null`, `linguistic_status: NOT_APPLICABLE`.

Kiểm tra spec trước khi mở Blender:

```cmd
npm run validate:motion-spec
```

## 3. Pipeline Windows CMD

Chạy từ root repository. Biến dưới đây chỉ để rút gọn ví dụ; có thể thay bằng đường dẫn Blender 5.2.4 LTS trên máy.

```cmd
set "BLENDER=C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
```

### Bước 1 — kiểm tra Master và tạo working copy

```cmd
npm run verify:master
"%BLENDER%" --background blender\master\avatar_master.blend --python blender\scripts\create_sign_working_copy.py -- --sign-id TECH_POSE_AUTHORING_PILOT --output blender\working\pilots\task-0010\TECH_POSE_AUTHORING_PILOT_base.blend --report docs\reports\artifacts\TASK-0010\working-copy-generation.json --frame-end 60 --expected-version "5.2.4 LTS"
```

Script từ chối ghi đè canonical Master hoặc output đã tồn tại. Với sign thật, thay ID bằng sign được giao (`Snnn`), giữ clip sau này là `Snnn_MAIN` và không dùng `--technical-fixture`.

### Bước 2 — sinh animation từ spec

```cmd
"%BLENDER%" --background blender\working\pilots\task-0010\TECH_POSE_AUTHORING_PILOT_base.blend --python blender\scripts\build_sign_animation.py -- --spec blender\animation-specs\TECH_POSE_AUTHORING_PILOT.json --pose-library blender\poses\technical-hand-poses.json --output-blend blender\working\pilots\task-0010\TECH_POSE_AUTHORING_PILOT.blend --report docs\reports\artifacts\TASK-0010\animation-build.json --expected-version "5.2.4 LTS"
```

Generator tạo Action/Slot Blender 5.2.4 cho armature (`OBJECT`) và Shape Keys (`KEY`), keyframe theo spec, giữ Action không liên quan và từ chối ghi đè output/Action nếu chưa cho phép rõ ràng.

### Bước 3 — kiểm tra source Blender

```cmd
"%BLENDER%" --background blender\working\pilots\task-0010\TECH_POSE_AUTHORING_PILOT.blend --python blender\scripts\validate_sign_animation.py -- --sign-id TECH_POSE_AUTHORING_PILOT --expected-clip TECH_POSE_AUTHORING_PILOT --output docs\reports\artifacts\TASK-0010\source-contract-validation.json --expected-version "5.2.4 LTS"
"%BLENDER%" --background blender\working\pilots\task-0010\TECH_POSE_AUTHORING_PILOT.blend --python blender\scripts\validate_pose_authoring_pilot.py -- --build-report docs\reports\artifacts\TASK-0010\animation-build.json --output docs\reports\artifacts\TASK-0010\pose-pilot-validation.json --expected-version "5.2.4 LTS"
```

Validator kiểm tra 137 bone, hierarchy/bindings, object transform, Action/Slot, channel theo spec, independent hands, reset, NMM và mesh deformation. Numerical checks không thay thế đánh giá hình ảnh/anatomy.

### Bước 4 — xuất và kiểm tra GLB

```cmd
"%BLENDER%" --background blender\working\pilots\task-0010\TECH_POSE_AUTHORING_PILOT.blend --python blender\scripts\export_sign_animation.py -- --clip TECH_POSE_AUTHORING_PILOT --output assets\exports\technical\task-0010\tech-pose-authoring-pilot.glb --report docs\reports\artifacts\TASK-0010\glb-export.json --technical-fixture --expected-version "5.2.4 LTS"
npm run validate:pose-pilot
```

GLB technical fixture ở namespace riêng. Không copy nó vào sign package hoặc lesson data.

### Bước 5 — tạo visual review

Máy cần `ffmpeg.exe` trong `PATH` để ghép PNG sequence thành H.264 MP4.

```cmd
"%BLENDER%" --background blender\working\pilots\task-0010\TECH_POSE_AUTHORING_PILOT.blend --python blender\scripts\generate_pose_authoring_review.py -- --output-directory docs\reports\artifacts\TASK-0010\visual-review --report docs\reports\artifacts\TASK-0010\visual-review.json --expected-version "5.2.4 LTS"
```

Kiểm tra contact sheet, cận hai tay, front/three-quarter và MP4. `visual-review.json` PASS chỉ xác nhận package được tạo; owner visual acceptance vẫn là `NOT YET TESTED` cho tới khi người phụ trách xem.

### Bước 6 — sync và xem trên browser

```cmd
npm run sync:technical-assets
npm run sync:technical-assets:check
cd apps\web
npm run dev -- --host 127.0.0.1 --port 4173
```

Mở `http://127.0.0.1:4173/technical-sign-preview`. Kiểm tra exact clip, play/pause/replay, loop, 0.5×/1×, reset camera, cận tay và status. Trong terminal thứ hai ở repository root:

```cmd
npm run test:sign-preview
```

## 4. Sửa, reset và tái sinh

Sửa JSON pose/spec rồi tạo output mới; không sửa tay trực tiếp canonical Master. `PoseAuthor.reset_bone`, `reset_hand` và `reset_full_pose` đưa transform local về identity. Frame reset phải được khai báo trong spec khi cần; pipeline không tự ép mọi sign thật về neutral.

Do generator bảo vệ output, để tái sinh hãy dùng tên/version output mới hoặc chỉ thay thế artifact do chính task sở hữu sau khi đã xác nhận target. Không dùng `git clean`, `git reset --hard` hoặc xóa working file của thành viên khác.

## 5. Nhận biết incompatibility

Dừng và báo blocker nếu gặp một trong các dấu hiệu:

- Master hash khác `DCA77E3D11463C25B783310D057CFD64C38D04A6D89A0F181B27F9CA143C5FEC`.
- Blender khác `5.2.4 LTS` hoặc MPFB khác baseline `2.0.18`.
- Bone count khác 137, hierarchy/binding hash sai, thiếu `Human`/`Human.rig`.
- Thiếu finger chain `.L`/`.R`, thiếu sáu NMM target hoặc Action Slot không có `OBJECT`/`KEY`.
- Validator báo transform/object/channel ngoài spec thay đổi.

Không vá bằng cách đổi tên/add bone hoặc sửa canonical Master trong sign task.

## 6. Chia sẻ giữa Huy Anh và Mien

Cả hai animator dùng cùng schema, pose library và scripts. Mỗi người chỉ tạo working copy/package cho sign đã được ownership table giao; không copy `.blend` của nhau làm canonical. Khi sign thật có reference, thêm spec riêng, giữ provenance/uncertainty và gửi linguistic review; technical PASS không đồng nghĩa linguistic PASS.
