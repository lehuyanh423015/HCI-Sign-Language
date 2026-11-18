# Hợp đồng sản xuất sign animation

Hợp đồng này dùng Master Avatar v1.0.0 làm baseline kỹ thuật. `Snnn` chỉ là ID; technical fixture không phải Ngôn ngữ Ký hiệu Việt Nam (VSL) đã xác minh. Technical `PASS` không suy ra linguistic `PASS`.

## 1. Thu thập reference

Thao hoặc content owner ghi nguồn, URL/tác giả/ngày, media có quyền sử dụng, gloss/biến thể nếu đã xác lập và quan sát chuyển động vào `blender/working/signs/Snnn/sign.json`. Chỉ chuyển `REFERENCE_READY` khi evidence thật có thể truy vết. Không được đặt `APPROVED` nếu thiếu qualified linguistic reviewer.

## 2. Tạo working copy

Canonical `blender/master/avatar_master.blend` là bất biến. Từ repository root, dùng Blender 5.2.4:

```cmd
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b blender\master\avatar_master.blend --python blender\scripts\create_sign_working_copy.py -- --sign-id S001 --output blender\working\signs\S001\S001.blend --report blender\working\signs\S001\evidence\working-copy.json
```

Script kiểm tra SHA-256/version/hierarchy, từ chối ghi đè master hoặc output đã tồn tại, đặt 30 FPS, frame 1–120, neutral pose, source metadata và không assign runtime Action. Không dùng Save As từ master để ghi đè file người khác.

## 3. Sản xuất animation

- Clip chính tên chính xác `Snnn_MAIN`; frame 1 neutral; frame cuối khớp clip.
- Dùng body, hai tay, năm chuỗi ngón mỗi tay, head/neck/jaw/eye và sáu `NMM_` targets khi reference yêu cầu.
- Không thêm/xóa/rename/reparent bone; không sửa rest pose, bindings, geometry hoặc tên Morph Target.
- NMM hoạt động kỹ thuật không đồng nghĩa phù hợp ngôn ngữ. Chỉ animate theo reference.

## 4. Kiểm tra Blender

```cmd
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b blender\working\signs\S001\S001.blend --python blender\scripts\validate_sign_animation.py -- --sign-id S001 --expected-clip S001_MAIN --output blender\working\signs\S001\evidence\blender-validation.json
```

Validator kiểm tra Blender 5.2.4, master 1.0.0/hash, 137 bones/hierarchy, bindings, sáu targets, 30 FPS, timeline, Action/duration và neutral frame 1. Manual review vẫn bắt buộc cho hand shape, clipping, deformation, timing, mặt và gaze.

## 5. Export và package validation

Export chạy trong process background và chỉ thay đổi bản in-memory:

```cmd
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b blender\working\signs\S001\S001.blend --python blender\scripts\export_sign_animation.py -- --clip S001_MAIN --output assets\exports\signs\S001.glb --report blender\working\signs\S001\evidence\glb-export.json
npm run validate:sign-packages
```

GLB phải là glTF 2.0 self-contained, có mesh/skin, skeleton tương thích, exact clip/duration dương, Morph Targets cần thiết và 0 Khronos error. Package phải có `.blend`, GLB, preview và evidence khi đã vào production/review; placeholder `REFERENCE_PENDING` được ghi `NOT YET TESTED`, không được biến thành `PASS`.

## 6. Preview và review

Tạo front/side image hoặc video trong `previews/`, evidence JSON trong `evidence/`, reference trong `references/` và export thử trong `exports/`. Mở `/technical-sign-preview` để kiểm tra staged GLB: play/pause/replay, loop, 0.5×/1× và camera. Trang này nằm ngoài lesson catalog.

## 7. Linguistic gate và integration

Qualified reviewer quyết định độ chính xác của ký hiệu; ghi reviewer, notes, date và evidence thật. Chỉ khi reference `PASS`, technical `PASS`, linguistic `PASS` và browser review `PASS` mới chuyển `APPROVED`, copy GLB sang production lesson path và cập nhật `data/signs.json`. Không publish technical fixture hoặc draft.

## Trạng thái chuẩn

`NOT_STARTED` → `REFERENCE_PENDING` → `REFERENCE_READY` → `IN_PRODUCTION` → `TECHNICAL_REVIEW` → `LINGUISTIC_REVIEW` → `APPROVED` hoặc `REJECTED`. Review checks dùng `PASS`, `FAIL`, `SKIPPED`, `NOT YET TESTED` đúng nghĩa.
