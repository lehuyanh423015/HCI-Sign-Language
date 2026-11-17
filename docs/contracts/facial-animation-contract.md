# Facial Animation Contract

Contract này áp dụng cho prototype facial/NMM kỹ thuật bắt đầu từ TASK-0006. Nó không xác nhận ý nghĩa Ngôn ngữ Ký hiệu Việt Nam của bất kỳ biểu cảm nào.

## 1. Morph Target naming

- Facial Morph Target dùng prefix `NMM_`, chữ hoa và `_` phân tách semantic component.
- Side dùng suffix `_L`/`_R` theo skeleton hiện có.
- Core set TASK-0006: `NMM_BROW_RAISE_L`, `NMM_BROW_RAISE_R`, `NMM_EYE_BLINK_L`, `NMM_EYE_BLINK_R`, `NMM_LIPS_ROUND`, `NMM_LIPS_SPREAD`.
- Không rename, repurpose hoặc quảng bá 11 MPFB macro/body Shape Keys thành facial controls.

## 2. Value range

- Neutral = `0.0`, full technical deformation = `1.0`.
- Authoring/runtime control nằm trong `[0, 1]`; animation không dùng giá trị âm hoặc overshoot nếu chưa có corrective QA.
- Target phải có non-zero vertex delta; key rỗng bị coi là `FAIL`.

## 3. Neutral pose convention

- Frame 1, 30 FPS; tất cả `NMM_` weight = `0`, eye/head/neck/jaw neutral, pose basis không làm thay đổi canonical rest pose.
- Facial candidate là working copy; canonical `blender/master/avatar_master.blend` không chứa các control/Action này.

## 4. Eye bone conventions

- Eye assembly trái/phải bind bằng Armature modifier và weight `1.0` tới `eye.L`/`eye.R` tương ứng.
- Gaze dùng rotation nhỏ: left/right khoảng `±7°`; up/down phải giữ trong giới hạn tương đương và được visual QA.
- TASK-0006 dùng `NMM_Eyeball.*`, `NMM_Iris.*`, `NMM_Pupil.*`; không thêm eye bone mới.
- Blink kết hợp body Morph Target với companion Morph Target trên eye assembly để tránh pupil còn lộ do topology eyelid hiện tại còn hạn chế.

## 5. Head and neck conventions

- Dùng `head`, `neck01`, `neck02`, `neck03`; không tạo whole-character/root rotation ngoài chủ ý.
- Rotation phải nhỏ, có reset về neutral và không đổi hierarchy/rest transform.

## 6. Jaw conventions

- Jaw opening dùng bone `jaw`; mouth Shape Keys chỉ điều khiển lip shape/corrective, không thay thế jaw rotation.
- Jaw, lips và head/neck phải được kiểm tra đồng thời trước handoff.

## 7. Animation clip naming

- Facial technical clips dùng `NMM_<PURPOSE>_TEST`.
- Clip kết hợp tay–mặt dùng `TECH_HAND_FACE_TEST`.
- TASK-0006 gồm `NMM_BLINK_TEST`, `NMM_BROW_TEST`, `NMM_MOUTH_TEST`, `TECH_HAND_FACE_TEST`; tất cả 30 FPS và duration dương.
- Các clip này là technical fixtures, không phải sign/lesson content.

## 8. GLB export requirements

- Blender **5.2.4 LTS**, skin, armature, eye meshes, materials, NMM Morph Targets, bone channels và weight channels phải cùng tồn tại.
- MPFB macro mix được bake trên export-only copy; `Hide helpers` được đánh giá cho base và từng `NMM_` target; không save preprocessing vào candidate.
- Blender Action/Slot được nối qua NLA tracks cùng tên và export với `NLA_TRACKS` + merge `NLA_TRACK`.
- Giới hạn bốn skin influences theo baseline hiện tại; exporter có thể normalize bốn weight cao nhất.
- Không export camera/light/debug mesh hoặc `TASK0005_DIAGNOSTIC_MORPH`.

## 9. Three.js mapping

- Runtime tự khám phá `mesh.morphTargetDictionary`; UI chỉ expose target có prefix `NMM_` thực sự tồn tại.
- Slider cập nhật mọi mesh binding cùng target name, đặc biệt blink body + eye assembly.
- Gaze ánh xạ `eye.L`/`eye.R`; reset phục hồi quaternion neutral.
- Viewer kỹ thuật dùng `/technical-facial-viewer` và `/models/technical/technical-facial-test.glb`, tách khỏi lesson catalog.

## 10. Concurrent hand and face animation

- `TECH_HAND_FACE_TEST` phải có right-finger channels, wrist/arm khi phù hợp, `head`/`neck`, `jaw`, eye channels và ít nhất một `weights` channel.
- Bone animation và Morph Target animation phải nằm trong cùng GLB/clip name sau merge; kiểm tra không chỉ dựa vào export command.

## 11. Validation requirements

- Blender environment/hash check; candidate inventory; 137-bone hierarchy; original MPFB key preservation; eye binding; non-zero deltas.
- GLB: mesh, skin, six eye nodes, six core target names, bốn clip, positive duration, combined channels và Khronos validator `0` error.
- Web: typecheck, lint, unit route test, build, browser runtime test, camera/gaze/sliders/playback/reset và regression `/technical-viewer`.
- Structural `PASS`, visual review và linguistic review là ba lớp độc lập.

## 12. Content approval requirements

- Banner bắt buộc: `TECHNICAL FACIAL TEST — NOT VERIFIED SIGN LANGUAGE`.
- Trạng thái linguistic/content TASK-0006: `NOT YET TESTED` cho tới khi có qualified Deaf/native signer hoặc chuyên gia VSL review.
- Huy Anh duyệt master/rig/candidate; Mien chỉ animate trên working copy; Nhat consume GLB contract; Thao điều phối evidence/content gate.
- Không promote candidate thành canonical, không đưa clip vào lesson catalog và không gán semantic VSL chỉ dựa trên technical `PASS`.

## Current prototype limitation

Topology eyelid/lip của base mesh giới hạn độ tinh tế. Blink dùng companion eye morph để tạo trạng thái đóng đọc được rõ; brow/lip targets còn nhẹ và cần owner visual polish trước production. Candidate `v1.0.0-rc.2` chỉ sẵn sàng cho owner review, chưa sẵn sàng cho production NMM.
