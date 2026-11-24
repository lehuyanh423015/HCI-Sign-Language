# TASK-0011B — Tinh chỉnh độ trung thực chuyển động S001 “Xin chào”

- Ngày/Timezone: 2026-11-23 — Asia/Saigon
- Worktree: `E:\University\Semester_7\HCI\BTL-worktrees\TASK-0011B`
- Branch/base commit: `feat/task-0011b-s001-motion-refinement` / `8f86e320e0f0a0c240493cd7fedd553b6b8fa9fc`
- Implementation commit: `3a379dc28e8132fb9059e06982a90442eded64eb`
- Scope: chỉ tinh chỉnh S001; không triển khai S002/S003; không sửa canonical master
- Overall status: `PASS` kỹ thuật — `WAITING_FOR_OWNER_REVIEW`; linguistic status `NOT YET TESTED`

## 1. Executive summary

TASK-0011B tạo một refined candidate riêng cho `S001_MAIN`, dựa trên Take 2 của video do owner cung cấp và kết quả review TASK-0011A. Tư thế v4 giảm độ dang ngang của khuỷu/cổ tay, tăng độ gập khuỷu, làm rõ pha dao động A–B bằng phối hợp cẳng tay và cổ tay, đồng thời thay đường nâng tay ban đầu bằng quỹ đạo thấp–gọn–đi lên. Bản v3, GLB v3, video nguồn và canonical master được giữ nguyên.

Kết quả hiện chỉ là technical draft. Không có kết luận rằng nội dung hoặc biến thể Hà Nội đã được kiểm chứng ngôn ngữ học.

## 2. Initial Git state

- Primary repository có các thay đổi do người dùng sở hữu, nên task dùng sibling worktree cô lập.
- Không reset, clean, stash, overwrite hoặc stage thay đổi tại primary worktree.
- Worktree TASK-0011B được tạo từ commit TASK-0011A đã xác minh: `8f86e320e0f0a0c240493cd7fedd553b6b8fa9fc`.
- Branch mới: `feat/task-0011b-s001-motion-refinement`.
- Không có upstream/remote publication được tạo trong task này.

## 3. Actual base commit

Base thực tế: `8f86e320e0f0a0c240493cd7fedd553b6b8fa9fc`.

Implementation commit sau khi hoàn tất source/evidence: `3a379dc28e8132fb9059e06982a90442eded64eb`.

## 4. Environment and dependencies

- Blender: `5.2.4 LTS` — PASS.
- MPFB: build info `20261010`, baseline project `2.0.18` — load thành công.
- Node.js: `v24.14.1`.
- npm workspace và dependency dùng từ repository hiện hữu; không cài dependency mới.
- FFmpeg/FFprobe hệ thống dùng để mã hóa và kiểm tra MP4.
- Chrome cài sẵn dùng cho headless runtime smoke test; không truy cập dịch vụ bên ngoài.

## 5. Master hash verification

- Canonical master: `blender/master/avatar_master.blend`.
- SHA-256 thực tế: `DCA77E3D11463C25B783310D057CFD64C38D04A6D89A0F181B27F9CA143C5FEC`.
- SHA-256 kỳ vọng: giống hệt — PASS.
- Bone hierarchy: 137 bone, signature `0A14E14E5899D4697732D0B0E3F6AC1D6531979B87A7CD23E2652865D9DC2F89` — PASS.
- Mesh/armature binding signature: `2AB953B2DE41A87BDB8C8AFFC408647236A18DAFDA3CA140011679A495D2F2C5` — PASS.
- Canonical master không bị sửa.

## 6. Reference and source provenance

- URL nguồn: `https://www.youtube.com/watch?v=4avGnxaLmb0`.
- Local owner-provided video: `blender/working/signs/S001/references/xin_chao-owner-provided.mp4`.
- SHA-256 nguồn local: `5A84E354C54EBD8446032ACC4C62FD9098E67063DFDAA76EE83B36D11A9100FB`.
- Take dùng để tinh chỉnh: local `00:03.05–00:05.00`.
- Mốc quan sát: `03.55`, `03.80`, `04.10`, `04.40`, `04.60` giây.
- Ảnh tham chiếu nội bộ được tái sử dụng từ TASK-0011A; không đóng gói video nguồn thành release artifact.
- Landmark tham chiếu là ước lượng 2D, sai số công bố `±0.10` shoulder span; không suy diễn chiều sâu bị che khuất.

## 7. Original v3 defects and preservation

Các lỗi owner nêu và được tái xác nhận:

- Khuỷu/cánh tay dang ngang quá rộng.
- Pha A–B gần như không thay đổi vị trí cổ tay, nên dao động khó đọc ở tốc độ bình thường.
- Đường nâng ban đầu thiên về mở ngang thay vì đi từ thấp/gần thân lên signing space.

Nguồn v3 giữ nguyên:

- `blender/working/signs/S001/S001.blend` — SHA-256 `207CE81CC6A6CDFA66E37B41899F530F1CE625388450D80FEA49F545FBA0A5D7`.
- `assets/exports/signs/S001.glb` — SHA-256 `7EC4FEB67058E6EAA37147F27BF74F222B82FD94B6254B126995D6A5604271B3`.

## 8. Shoulder/elbow correction

- Giữ vai/canonical rig nguyên vẹn; chỉ author rig-local rotation trong Action `S001_MAIN`.
- Lower-arm Z được tách thành schema riêng với miền `[-150, 150]` độ để mô tả khuỷu gập tự nhiên; không clamp ở biên generic `±90` chỉ để qua validation.
- Key pose chính dùng lower-arm Z khoảng `±125–145` độ; upper arm giữ ở mức gọn khoảng `±13–15` độ.
- Khoảng ngang chuẩn hóa ở `initial_open` giảm như sau:
  - elbow: `1.065 → 0.835` shoulder span, giảm khoảng `21.6%`;
  - wrist: `1.566 → 1.177`, giảm khoảng `24.8%`;
  - index fingertip: `1.882 → 1.452`, giảm khoảng `22.9%`.
- Ở `oscillation_b`, wrist giảm `1.567 → 1.034` (khoảng `34.0%`) và fingertip giảm `1.781 → 0.948` (khoảng `46.8%`).
- Front/3-quarter/close-up không cho thấy detached fingers, wrist inversion rõ ràng hoặc biến dạng khuỷu nghiêm trọng.

## 9. Handshape and palm correction

- Giữ handshape `open_hand`: năm ngón mở, spread, thumb abducted.
- Palm tiếp tục hướng broadly toward camera trong meaningful interval.
- Wrist A dùng tilt ngoài; B dùng tilt trong kết hợp thay đổi forearm bend, thay vì chỉ tăng một Euler wrist riêng lẻ.
- Hai tay được author theo local axes trái/phải của rig; không thay skeleton và không thêm hand contact giả định.
- Ảnh cận tay 1080p xác nhận ngón đầy đủ, không bị cắt khung và không có clipping rõ ràng.

## 10. Oscillation correction

- V3 có chênh lệch ngang wrist A–B chỉ khoảng `0.001` shoulder span.
- V4 có chênh lệch wrist A–B khoảng `0.216` shoulder span, đồng thời palm/fingertip đổi hướng rõ.
- Chuỗi meaningful giữ đúng quan sát: `INITIAL → A → B → A2 → FINAL`; bỏ pha B2 thừa của v3, không tạo thêm chu kỳ có ý nghĩa.
- Biên độ vẫn là technical approximation từ một camera frontal; không gán ý nghĩa ngôn ngữ cho số chu kỳ.

## 11. Initial and recovery motion correction

- Frame 1 vẫn là canonical neutral để giữ neutral-pose contract.
- Frame 5 thêm `pre_sign_gather_refined`: tay thấp, gọn, relaxed.
- Frame 8 thêm `bilateral_compact_lift_refined`: nâng lên theo đường gọn trước thân, tránh sweep ngang phóng đại.
- Frame 60 recovery trở lại neutral an toàn, nằm ngoài meaningful interval.
- Không ép pre-sign hand clasp vì chi tiết che khuất và rig không đủ bằng chứng để dựng chính xác.

## 12. Before/after comparison

- `reference-vs-refined-key-poses.png`: 5 key pose người thật so với v4.
- `v3-vs-v4-comparison.png`: v3/v4 cùng camera Blender.
- `shoulder-elbow-wrist-comparison.png`: overlay shoulder/elbow/wrist/fingertip ở Initial và B.
- `oscillation-comparison.png`: A/B/A2 của v3 và v4.
- Kết luận kỹ thuật: v4 gần signing space của reference hơn v3 và dao động đọc rõ hơn ở playback 1×. Owner vẫn cần xác nhận cảm nhận chuyển động.

## 13. Frame and timing changes

- FPS: 30.
- Timeline: frame `1–60`, duration 2.00 giây; giữ 60 frame vì selected take dài 1.95 giây và recovery kỹ thuật cần frame cuối.
- Meaningful interval đổi từ v3 sang `[8, 47]` để bám các mốc source.
- Key mapping refined:
  - F16: 03.55 — Initial open;
  - F23: 03.80 — A;
  - F32: 04.10 — B;
  - F41: 04.40 — A2;
  - F47: 04.60 — Final open.
- Technical transitions: F1, F5, F60.

## 14. Blender source details

- Source refined: `blender/working/signs/S001/refinements/task-0011b/S001_refined.blend`.
- SHA-256: `BD0F3877040257785D0CAA6EB8BA5E7B57F07A74445532D103A93981D9483063`.
- Action: duy nhất clip staging mong đợi `S001_MAIN`.
- 117 bone F-curves, 6 morph F-curves; 6 NMM Morph Targets vẫn tồn tại nhưng có giá trị neutral trong canonical clip.
- Blender validation: PASS tất cả check kỹ thuật; linguistic review `NOT YET TESTED`.

## 15. GLB export details

- GLB staging: `assets/exports/signs/staging/S001-task-0011b.glb`.
- SHA-256: `006109E192A82898F0C0997D0DC11F8E31BC08362DA34A517AE3B7A40C19B627`.
- Kích thước: `2,338,800` bytes.
- Một skin, 137 joints, clip duy nhất `S001_MAIN`, duration dương, bilateral arm controls và 6 NMM targets — PASS.
- Khronos validator: 0 errors — PASS.
- Blender exporter báo warning quen thuộc: một số source vertex có hơn 4 influence; exporter giữ 4 weight lớn nhất và normalize. Không có validator error.

## 16. Three.js staging results

- Route: `/technical-sign-preview`.
- Asset web staging: `s001-xin-chao-task-0011b-refined.glb`.
- Nhãn giữ nguyên: `TECHNICAL DRAFT — NOT LINGUISTICALLY APPROVED`, `LOCAL STAGING ONLY`.
- Headless Chrome smoke: 16/16 PASS.
- Đã kiểm tra: actual GLB ready, clip `S001_MAIN`, WebGL canvas, animation progress, pause/resume, replay, loop, 0.5×/1×, hand camera, camera reset, không runtime exception.
- Computer-use Windows UI: `SKIPPED` vì helper không khởi tạo sau recovery (`helper_unknown_error`); thay thế bằng Chrome DevTools headless smoke có evidence. Favicon 404 được ghi nhận riêng và không liên quan GLB/runtime.
- Không thêm S001 vào approved lesson catalog.

## 17. Visual review evidence

Gói chính: `docs/reports/artifacts/TASK-0011B/visual-review/`.

- MP4: `S001-task-0011b-refined-1080p.mp4` — 1920×1080, 30 FPS, 60 actual Blender frames, 2.00 giây.
- MP4 SHA-256: `D879D2F3D0EA8917670D2DBB6408C90C51257B03CB9A885791B3AD60E5557940`.
- Upper body/front/3-quarter/left hand/right hand: PASS kiểm tra trực quan kỹ thuật.
- Label không bị cắt; main MP4 giữ camera cố định; cả hai tay nằm trong khung upper-body.
- Baseline v3 1080p được render cùng camera tại `visual-review/original-v3/`.
- Owner visual acceptance: `NOT YET TESTED`.

## 18. Commands actually executed

```text
git worktree add E:\University\Semester_7\HCI\BTL-worktrees\TASK-0011B -b feat/task-0011b-s001-motion-refinement 8f86e320...
node tools/validate-sign-motion-spec.mjs --spec blender/animation-specs/refinements/S001_MAIN_TASK0011B.json ...
node --test tools/tests/validate-sign-motion-spec.test.mjs
blender.exe -b blender/working/signs/S001/S001_base.blend --python blender/scripts/build_sign_animation.py -- ...
blender.exe -b .../S001_refined.blend --python blender/scripts/validate_sign_animation.py -- --sign-id S001 --expected-clip S001_MAIN ...
blender.exe -b .../S001_refined.blend --python blender/scripts/analyze_sign_landmarks.py -- ...
blender.exe -b .../S001_refined.blend --python blender/scripts/export_sign_animation.py -- --clip S001_MAIN ...
node tools/validate-sign-draft.mjs --asset assets/exports/signs/staging/S001-task-0011b.glb --clip S001_MAIN --sign-id S001 ...
npm run sync:technical-assets
npm run check
npm run build
npm run dev --workspace @hci-sign/web -- --host 127.0.0.1
node tools/browser-smoke-task0011b.mjs --url http://127.0.0.1:5173/technical-sign-preview ...
blender.exe -b .../S001_refined.blend --python blender/scripts/generate_pose_authoring_review.py -- ... --resolution-x 1920 --resolution-y 1080
python tools/generate-task0011b-comparisons.py
ffprobe ... S001-task-0011b-refined-1080p.mp4
git commit -m "feat: refine S001 motion fidelity for owner review"
```

Hai vòng candidate 1280×720 đã được dùng để chỉnh hình học. Sau khi chốt v2, các binary/render candidate-only được xóa an toàn; final source và evidence được giữ.

## 19. Test matrix

| Check | Evidence | Status |
|---|---|---|
| Canonical master SHA-256 | `DCA77E...C5FEC` | PASS |
| V3 `.blend` và GLB gốc không đổi | hash v3 và GLB nêu trên | PASS |
| Motion spec/schema | `motion-spec-validation-v2.json` | PASS |
| Motion schema unit tests | 3/3 | PASS |
| Blender version/source/master metadata | `blender-validation.json` | PASS |
| 137-bone hierarchy + binding | `blender-validation.json` | PASS |
| Neutral frame 1 + six NMM targets | `blender-validation.json` | PASS |
| Action/slot/frame range | `animation-build-final.json` | PASS |
| Landmark v3/v4 | `landmarks-v3.json`, `landmarks-v4-final.json` | PASS |
| GLB/Khronos | `glb-validation.json` | PASS |
| Visual review generation | `visual-review/visual-review.json` | PASS |
| MP4 1920×1080, 30 FPS, 60 frames | FFprobe + visual report | PASS |
| Three.js headless browser smoke | `browser-smoke.json` | PASS |
| Windows computer-use UI | helper không khởi tạo | SKIPPED |
| `npm run check` | toàn bộ workspace checks/tests/build | PASS |
| `npm run build` | Vite production build | PASS |
| Owner visual acceptance | chưa thực hiện | NOT YET TESTED |
| Linguistic validation | chưa có qualified reviewer | NOT YET TESTED |

## 20. Created and modified files

Nhóm chính:

- Refined source/spec: `blender/working/signs/S001/refinements/task-0011b/`, `blender/animation-specs/refinements/S001_MAIN_TASK0011B.json`.
- Staging GLB: `assets/exports/signs/staging/S001-task-0011b.glb`.
- Blender tooling: `analyze_sign_landmarks.py`, cập nhật `generate_pose_authoring_review.py`.
- Contract: cập nhật `docs/contracts/sign-motion-spec.schema.json` cho lower-arm rig-local range.
- Frontend staging: `SignAnimationPreviewPage.tsx`, test và technical asset sync.
- Browser/comparison tooling: `browser-smoke-task0011b.mjs`, `generate-task0011b-comparisons.py`.
- Evidence: `docs/reports/artifacts/TASK-0011B/`.
- Report chính thức: `docs/reports/TASK-0011B-s001-motion-refinement.md`.

## 21. Known issues and limitations

- Một camera frontal không xác định chính xác chiều sâu, palm normal hoặc local Euler tuyệt đối.
- Proportion người thật và canonical avatar khác nhau; landmark chỉ dùng để so sánh khoảng cách chiếu, không retarget body proportions.
- Facial smile/mouth shape của performer không được author vì vai trò NMM chưa xác minh.
- Clothing shoulder opening hiện rõ hơn ở góc 3/4 là đặc điểm mesh/trang phục hiện hữu; không có skeleton/object transform bất ngờ, nhưng owner nên quan sát deformation.
- Blender export warning về >4 joint influences vẫn là giới hạn pipeline đã biết.
- Browser visual UI automation bằng computer-use bị SKIPPED do lỗi helper; headless Chrome runtime test đã PASS thay thế.

## 22. Technical status

`PASS — WAITING_FOR_OWNER_REVIEW`.

Refined `.blend`, staging GLB, review MP4, comparison sheets, browser smoke và regression suite đã hoàn tất. Chưa được phép thay thế `S001.glb` gốc hoặc publish remote.

## 23. Linguistic review status

`NOT YET TESTED`.

Không có khẳng định rằng “Xin chào”, biến thể Hà Nội, số chu kỳ hoặc NMM đã được chuyên gia Ngôn ngữ Ký hiệu Việt Nam xác minh.

## 24. Git branch and commit information

- Active worktree: `E:\University\Semester_7\HCI\BTL-worktrees\TASK-0011B`.
- Branch: `feat/task-0011b-s001-motion-refinement`.
- Base: `8f86e320e0f0a0c240493cd7fedd553b6b8fa9fc`.
- Implementation/evidence commit: `3a379dc28e8132fb9059e06982a90442eded64eb`.
- Commit chứa report được tạo sau tài liệu này; exact final HEAD được ghi trong final response để tránh self-referential commit hash.
- Remote tracking branch: không tạo.

## 25. Confirmation of NO PUSH and owner acceptance checklist

Không push, không tạo PR, không merge, không tag/release, không force push và không sửa lịch sử.

- [ ] Xem MP4 refined 1080p ở tốc độ 1× và xác nhận chuyển động dễ đọc.
- [ ] So sánh `reference-vs-refined-key-poses.png` với performer.
- [ ] Xác nhận khuỷu/tay không còn dang quá rộng.
- [ ] Xác nhận pha A–B–A2 đủ rõ nhưng không bị phóng đại.
- [ ] Xác nhận đường nâng ban đầu phù hợp hơn v3.
- [ ] Kiểm tra left/right hand close-up, wrist và finger deformation.
- [ ] Xem góc 3/4 để chấp nhận depth/mesh deformation.
- [ ] Quyết định chấp nhận refined candidate hoặc yêu cầu vòng tinh chỉnh tiếp.
- [ ] Sau khi chấp nhận local, cấp quyền PUSH riêng nếu muốn publish branch.
- [ ] Sau push/PR, cấp quyền MERGE riêng nếu muốn tích hợp main.

## Next recommended tasks

Chỉ xử lý feedback owner cho S001 hoặc tiến hành Gate B khi có lệnh push rõ ràng. Không tự động bắt đầu S002/S003.

**Trạng thái dừng: `WAITING_FOR_OWNER_REVIEW`.**
