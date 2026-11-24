# TASK-0010 — First Sign Animation Pilot & Automated Pose Authoring

- Ngày/Timezone: 2026-11-21, Asia/Saigon
- Branch: `feat/task-0010-first-sign-animation-pilot`
- Base commit: `b030fcd7d63ee564354ba3d5b20ed479dd2b4b39` (`origin/main`, merge TASK-0009)
- Scope: pose authoring data-driven, technical animation fixture, Blender/GLB/visual/browser validation và handoff workflow
- Overall status: **PASS cho technical scope; BLOCKED cho real-sign pilot; linguistic NOT_APPLICABLE cho fixture; owner visual acceptance NOT YET TESTED**

## 1. Executive summary

TASK-0010 đã triển khai hệ thống pose authoring tái sử dụng trên Master Avatar v1.0.0: JSON Schema, pose library hai tay, local-axis finger mapping, Blender 5.2.4 Action/Slot generator, source/GLB validators, visual review automation và Three.js staging.

Repository không có reference VSL hợp lệ cho các sign Huy Anh sở hữu. Vì vậy không tạo hoặc suy diễn ký hiệu thật. Output là `TECH_POSE_AUTHORING_PILOT`, classification `TECHNICAL_FIXTURE_NOT_A_SIGN`, `sign_id: null`, linguistic status `NOT_APPLICABLE`; real-sign pilot là `BLOCKED`/`REFERENCE_PENDING`.

Các mốc phải phân biệt:

- Infrastructure ready: **PASS**.
- Technical animation completed: **PASS**.
- Real sign animation completed: **BLOCKED** vì thiếu reference.
- Linguistically verified sign: **không có**; fixture là `NOT_APPLICABLE`.

## 2. Initial Git status

Trước khi sửa:

- Local/remote base chứa TASK-0009: `b030fcd7d63ee564354ba3d5b20ed479dd2b4b39`.
- Remote: `origin https://github.com/lehuyanh423015/HCI-Sign-Language.git`.
- Worktree gốc ở branch `feat/task-0007a-facial-refinement` có user changes:
  - `README.md`
  - `blender/master/avatar_master_neutral_candidate.blend`
  - `docs/reports/artifacts/TASK-0004-browser-runtime.json`
  - `docs/reports/artifacts/TASK-0004-browser-runtime.png`
- Không reset/clean/stage/sửa bốn file trên trong worktree gốc.
- TASK-0010 được cô lập tại `node_modules/.task0010` trên branch mới.
- Remote branch TASK-0010 không tồn tại tại thời điểm bắt đầu.

## 3. Base commit

Branch được tạo từ `origin/main` sau khi fetch và xác nhận PR TASK-0009 đã merge:

```text
b030fcd Merge pull request #1 from lehuyanh423015/feat/task-0009-team-onboarding-animation-pipeline
73898a9 docs: record TASK-0009 publication
fb1fc13 feat: establish sign animation production pipeline
```

Không merge `main`, không rewrite history và không force push.

## 4. Master Avatar verification

- Canonical: `blender/master/avatar_master.blend`
- Version: `1.0.0`
- SHA-256 trước/sau: `DCA77E3D11463C25B783310D057CFD64C38D04A6D89A0F181B27F9CA143C5FEC`
- Blender: `5.2.4 LTS`
- MPFB baseline: `2.0.18`
- Rig: 137 bones
- Hierarchy SHA-256: `0A14E14E5899D4697732D0B0E3F6AC1D6531979B87A7CD23E2652865D9DC2F89`
- Canonical Master không bị sửa; mọi Blender mutation nằm trong isolated working copy.

## 5. Reference intake results

Ownership table xác định Huy Anh sở hữu S001–S003; Mien sở hữu S004–S006. Không chiếm sign của Mien.

S001–S003 hiện không có source reference, media, provenance, permission, regional variant hoặc movement breakdown đủ để tái dựng. Metadata/reference directories đều ở trạng thái chờ. Không tải ngẫu nhiên media Internet và không suy diễn gesture.

- Reference intake: `REFERENCE_PENDING`
- Actual sign pilot: `BLOCKED`
- Qualified linguistic review path: chưa có evidence

## 6. Assigned sign or fixture ID

- Fixture ID/clip: `TECH_POSE_AUTHORING_PILOT`
- Classification: `TECHNICAL_FIXTURE_NOT_A_SIGN`
- Sign ID: `null`
- Source reference: `null`
- Linguistic status: `NOT_APPLICABLE`
- Lesson catalog integration: không thực hiện

## 7. Pose library implementation

`blender/poses/technical-hand-poses.json` cung cấp:

- `neutral_hand`
- `open_hand`
- `closed_fist`
- `index_flexed`
- `thumb_flexed`
- `relaxed_hand`

`blender/poses/technical-upper-body-poses.json` cung cấp neutral upper body. Các pose là technical rig controls, không phải handshape VSL được duyệt. Mỗi pose serialize affected joints, dùng được cho `.L`/`.R`, không tự thay đổi unrelated bones và reset về identity.

## 8. Motion specification format

`docs/contracts/sign-motion-spec.schema.json` dùng JSON Schema Draft 2020-12. Spec phân tách:

- identification/source/master/animator/clip/FPS;
- duration, key pose, hold, interpolation và technical transition;
- left/right hand, individual fingers, wrist, upper/lower arm;
- head, neck, jaw, gaze, eyebrow, mouth và Morph Targets;
- reference/technical/linguistic review và uncertainty.

Thông tin quan sát dùng `OBSERVED`; giả định kỹ thuật dùng `ASSUMED_TECHNICAL`; thiếu dữ liệu dùng `UNKNOWN`; không áp dụng dùng `NOT_APPLICABLE`. Validator bổ sung kiểm tra frame tăng dần/unique, duration, pose name và fixture không được nhận sign ID.

## 9. Animation generator implementation

`blender/scripts/build_sign_animation.py`:

- đọc working copy, spec và pose library;
- xác nhận identifier/master rig;
- tạo Blender 5.2.4 layered Action với `OBJECT` và `KEY` slots;
- tạo bone/morph keyframe, holds và interpolation;
- giữ Action không liên quan;
- từ chối ghi đè Action/output nếu không có authorization;
- lưu output `.blend` riêng và JSON build report.

`sign_pose_utils.py` cung cấp discovery, hierarchy validation, bone access, reset bone/hand/full pose, named pose, local rotation, morph application, keyframe và frame evaluation.

## 10. Bone mapping and control behavior

Finger families dùng đúng MPFB inventory: `finger1-*` đến `finger5-*` với `.L`/`.R`. Module không giả định Mixamo/Rigify và không áp một Euler axis chung. Với từng PoseBone/phía, module thăm dò hướng local làm joint tiến về palm cùng phía, chọn axis/dấu flex rồi tạo quaternion local.

Đã kiểm tra thực tế:

- invalid bone báo lỗi;
- right hand thay đổi độc lập trong khi left neutral;
- left hand thay đổi độc lập;
- `reset_hand` và full reset về identity;
- hierarchy canonical giữ nguyên.

## 11. Generated animation details

Output Blender:

- Base: `blender/working/pilots/task-0010/TECH_POSE_AUTHORING_PILOT_base.blend`
- Animation: `blender/working/pilots/task-0010/TECH_POSE_AUTHORING_PILOT.blend`
- Animation SHA-256: `665A8254C3334EE137A16C62A2EBEF41777D3300E916D6A9715C03E4CD96531C`

Fixture chứng minh right/left individual fingers, wrist, upper/lower arm, head/neck/jaw, NMM brow/lips, interpolation/hold và neutral reset. Đây là motion kỹ thuật được giả định rõ ràng, không chứa semantics VSL.

## 12. Actions, channels, frames and duration

- Action: `TECH_POSE_AUTHORING_PILOT`
- Frame range: 1–60
- FPS: 30
- Duration: 2.00 giây
- Key poses: 1, 12, 24, 36, 48, 60
- Interpolation: BEZIER, có holds theo spec
- Object slot: `OBHuman.rig`
- Key slot: `KEKey`
- Bone FCurves: 117
- Morph FCurves: 6
- Keyframe points: 1353
- Animated bones: 39, gồm 30 finger bones, hai wrists, bốn arm bones, `head`, `neck02`, `jaw`
- Animated morph inventory: đủ sáu `NMM_` targets; spec dùng brow/lips ở active poses và giữ/reset các target còn lại.

## 13. GLB export results

- Path: `assets/exports/technical/task-0010/tech-pose-authoring-pilot.glb`
- SHA-256: `993A979FD7CAAD7B8F6CC8874894097C4A67A72510276F4A0AB9CEB5A3A8E76F`
- Size: 2,341,612 bytes
- glTF: 2.0 Binary
- Meshes: 9
- Skins: 1
- Joints: 137
- Clips: đúng một clip `TECH_POSE_AUTHORING_PILOT`
- Khronos glTF Validator: 0 errors, 0 warnings
- Exporter warning: một số source vertices có hơn bốn joint influences; Blender chọn bốn weight cao nhất và normalize. Validator không báo lỗi/warning GLB.

Không export diagnostic camera/light/object và không đưa asset vào educational sign path.

## 14. Blender validation results

`pose-utils-tests.json`, `source-contract-validation.json` và `pose-pilot-validation.json` ghi PASS cho:

- Blender 5.2.4, master metadata, 137 bones/hierarchy/bindings;
- six core NMM targets;
- neutral frame 1 và reset frame 60;
- expected Action/Slot, positive range và channel set;
- independent right frame 12/24, left frame 36, both frame 48;
- bone + Morph Target animation coexist;
- evaluated mesh finite, không detached eye theo programmatic binding checks;
- object-level transforms không đổi ngoài spec.

Visual anatomy/realism không được suy ra từ numerical checks.

## 15. Three.js runtime results

Route `/technical-sign-preview` tái sử dụng `TechnicalViewer`, chỉ đổi staged URL/clip/status. Browser report cuối:

- GLB/canvas ready: PASS, exact clip 2.00s
- Animation progresses: PASS
- Pause/resume/replay: PASS
- Loop toggle: PASS
- 0.5×/1× speed toggle: PASS
- Camera reset/right-hand inspection: PASS
- Runtime exceptions: 0
- `/technical-viewer` regression: PASS toàn bộ cùng check set

Lượt browser đầu FAIL duy nhất `animation_progresses` vì metric được đọc ở 0.00 trước khi React UI flush; các controls sau đó chứng minh time đã tiến. Test được sửa thành bounded polling 8 × 150 ms và lượt chạy lại PASS.

## 16. Visual evidence inventory

Thư mục `docs/reports/artifacts/TASK-0010/visual-review/` gồm:

- `upper-body-frame-024.png`
- `left-hand-frame-036.png`
- `right-hand-frame-024.png`
- `front-frame-048.png`
- `three-quarter-frame-048.png`
- `raw/key-pose-001.png` đến `key-pose-060.png` cho sáu key poses
- `key-pose-contact-sheet.png`
- `tech-pose-authoring-pilot.mp4`

MP4: H.264, 640×640, 30 FPS, 60 frames, 2.000s, 52,861 bytes, SHA-256 `98B9D823E50B7BAF16A82BFC7B0A3F540206CE72E6EE24FA0AB60C7E1BEF767C`.

Ảnh/video dùng actual Blender scene/action, có fixture/clip, frame/time và warning. Visual package generation là PASS; owner manual visual acceptance vẫn `NOT YET TESTED`.

## 17. Actual commands executed

Các lệnh chính đã chạy thực tế (rút gọn đường dẫn worktree, không thay đổi outcome):

```text
git fetch origin --prune
git worktree add ... -b feat/task-0010-first-sign-animation-pilot origin/main
git status --short
git rev-parse HEAD
git rev-parse origin/main
Get-FileHash -Algorithm SHA256 blender\master\avatar_master.blend

npm run validate:motion-spec
npm test -- --runInBand
python -m py_compile blender/scripts/sign_pose_utils.py ...

"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --background blender\master\avatar_master.blend --python blender\scripts\test_sign_pose_utils.py -- ...
"...\blender.exe" --background blender\master\avatar_master.blend --python blender\scripts\create_sign_working_copy.py -- --sign-id TECH_POSE_AUTHORING_PILOT ...
"...\blender.exe" --background ...\TECH_POSE_AUTHORING_PILOT_base.blend --python blender\scripts\build_sign_animation.py -- --spec ... --pose-library ...
"...\blender.exe" --background ...\TECH_POSE_AUTHORING_PILOT.blend --python blender\scripts\validate_sign_animation.py -- --sign-id TECH_POSE_AUTHORING_PILOT --expected-clip TECH_POSE_AUTHORING_PILOT ...
"...\blender.exe" --background ...\TECH_POSE_AUTHORING_PILOT.blend --python blender\scripts\validate_pose_authoring_pilot.py -- ...
"...\blender.exe" --background ...\TECH_POSE_AUTHORING_PILOT.blend --python blender\scripts\export_sign_animation.py -- --clip TECH_POSE_AUTHORING_PILOT --technical-fixture ...
npm run validate:pose-pilot
"...\blender.exe" --background ...\TECH_POSE_AUTHORING_PILOT.blend --python blender\scripts\generate_pose_authoring_review.py -- ...
ffprobe -v error -count_frames -select_streams v:0 -show_entries ... tech-pose-authoring-pilot.mp4

npm run sync:technical-assets
npm run sync:technical-assets:check
cd apps\web && npm run dev -- --host 127.0.0.1 --port 4173
npm run test:sign-preview
node tools/test-technical-viewer.mjs --url http://127.0.0.1:4173/technical-viewer ...
npm run check
npm run build
git diff --check
```

Failed-attempt evidence:

- Lượt visual đầu dùng `scene.render.image_settings.file_format = "FFMPEG"`; Blender 5.2 enum không hỗ trợ giá trị này. Script được đổi sang PNG sequence + system FFmpeg H.264 và PASS.
- Lượt browser đầu FAIL race condition metric như mục 15; test polling sau sửa PASS.
- `npm test -- --runInBand` PASS nhưng npm cảnh báo unknown config `--runInBand`; full `npm run check` sau đó chạy không có option này và PASS.

## 18. Test matrix

| Check | Evidence | Status |
|---|---|---|
| Canonical Master hash | `npm run verify:master`, SHA-256 nêu trên | PASS |
| Blender 5.2.4 compatibility | Blender reports | PASS |
| Pose library load | `pose-utils-tests.json` | PASS |
| Pose reset/full reset | `pose-utils-tests.json`, `pose-pilot-validation.json` | PASS |
| Independent left/right fingers | cùng evidence | PASS |
| Invalid bone handling | `pose-utils-tests.json` | PASS |
| Motion schema/spec | `motion-spec-validation.json`, 3 Node tests | PASS |
| Keyframe generation/Action Slots | `animation-build.json` | PASS |
| Source `.blend` validation | `source-contract-validation.json`, `pose-pilot-validation.json` | PASS |
| GLB/Khronos validation | `glb-validation.json` | PASS |
| Preview package generation | `visual-review.json` | PASS |
| MP4 codec/frame/duration | ffprobe: H.264/60/2.000s | PASS |
| Evidence package readability | contact sheet/stills inspected for pose separation and labels | PASS |
| Visual/anatomical quality acceptance | `visual-review.json`, checklist below | NOT YET TESTED |
| Three.js staging runtime | `sign-preview-browser.json` | PASS |
| Existing technical viewer regression | `technical-viewer-regression.json` | PASS |
| Node tests | 7/7 | PASS |
| React tests | 5/5 | PASS |
| Typecheck/lint/full project checks | `npm run check` | PASS |
| Production build | `npm run build` | PASS; Vite chunk-size warning |
| Linguistic review of fixture | technical fixture, no sign semantics | NOT_APPLICABLE |
| Real sign pilot | no suitable reference | BLOCKED |

## 19. Files changed

Nhóm implementation chính:

- `blender/scripts/sign_pose_utils.py`
- `blender/scripts/build_sign_animation.py`
- `blender/scripts/test_sign_pose_utils.py`
- `blender/scripts/validate_pose_authoring_pilot.py`
- `blender/scripts/generate_pose_authoring_review.py`
- cập nhật `create_sign_working_copy.py`, `validate_sign_animation.py`, `export_sign_animation.py`
- `blender/poses/*.json`
- `blender/animation-specs/TECH_POSE_AUTHORING_PILOT.json`
- `docs/contracts/sign-motion-spec.schema.json`
- Node validators/tests và package scripts
- Three.js staging page/test, sync manifest và browser test polling
- README, contract, handoff và `docs/workflows/SIGN_POSE_AUTHORING.md`
- isolated Blender/GLB/visual/browser evidence trong TASK-0010 paths.

Canonical master, S001–S006 metadata/packages và lesson catalog không đổi.

## 20. Known limitations

- Không có valid VSL reference; không có real-sign output.
- Owner chưa xác nhận anatomy/timing/pose aesthetics; vẫn `NOT YET TESTED`.
- Một phần label ở ảnh cận có thể bị tay/arm che theo depth của actual scene; exact label đầy đủ vẫn có trên contact sheet và video.
- Generic base working-copy report được tạo trước khi fixture linguistic semantics được chuẩn hóa nên ghi `NOT YET TESTED`; final generated `.blend`, build/export/specialized validation và viewer đều ghi `NOT_APPLICABLE`. Script hiện tại đã sửa cho các working copy sau.
- Blender export log có warning >4 joint influences; GLB/Khronos vẫn 0 warning/error.
- Vite cảnh báo bundle chính >500 kB; không gây build/runtime failure và code splitting nằm ngoài scope.
- FFmpeg phải có trong `PATH` để tái sinh MP4.

## 21. Linguistic review status

- Fixture: `NOT_APPLICABLE`.
- Real sign: `REFERENCE_PENDING` / `BLOCKED`.
- Không có qualified reviewer evidence.
- Không có asset nào được đánh dấu APPROVED hoặc đưa vào lesson catalog.

## 22. Actual branch and commit

- Branch: `feat/task-0010-first-sign-animation-pilot`
- Base: `b030fcd7d63ee564354ba3d5b20ed479dd2b4b39`
- Implementation commit: `70e4ac123a492a29e04b1c3d061863a47a25c155` (`feat: add automated pose authoring pilot`).
- Report publication commit trước push: `f69971b74c93d2d0e7e9bf96b4e1bcfa28a501eb` (`docs: record TASK-0010 implementation`).
- Push-status follow-up commit: ghi trong final response vì commit không thể tự chứa hash của chính nó.

## 23. Remote push status

- Remote/auth URL đã xác nhận: `origin` trỏ đúng GitHub repository.
- Remote branch preflight: branch không tồn tại trước push.
- Push status: **PASS**; local và remote cùng ở `f69971b74c93d2d0e7e9bf96b4e1bcfa28a501eb` trước follow-up này.
- Upstream: `origin/feat/task-0010-first-sign-animation-pilot`.
- Pull Request URL: `https://github.com/lehuyanh423015/HCI-Sign-Language/pull/new/feat/task-0010-first-sign-animation-pilot`.
- Không push `main`, không merge, không force push.

## 24. Owner manual acceptance checklist

- [ ] Mở `key-pose-contact-sheet.png`, xác nhận sáu pose đọc được và frame 1/60 neutral.
- [ ] Xem cận tay trái/phải, xác nhận không severe clipping/detached fingers.
- [ ] Xem front/three-quarter, xác nhận arm/wrist/head movement chấp nhận được cho technical fixture.
- [ ] Xem `tech-pose-authoring-pilot.mp4`, xác nhận timing/holds/reset.
- [ ] Mở `/technical-sign-preview`, thử pause/replay/loop/0.5×/camera trên máy owner.
- [ ] Xác nhận fixture không xuất hiện trong lesson catalog.
- [ ] Cung cấp reference/provenance/permission và reviewer path cho một sign Huy Anh sở hữu trước real-sign authoring.

## 25. Recommended TASK-0011 scope

Chỉ bắt đầu task mới sau owner approval. Đề xuất TASK-0011 là reference intake và linguistic review gate cho đúng một sign Huy Anh sở hữu: khóa source/provenance/permission/region, lập observed-motion breakdown, author `Snnn_MAIN` bằng pipeline TASK-0010, rồi technical + qualified linguistic review. Nếu reference vẫn thiếu, không tạo semantic animation và không tự động mở rộng pose library thành purported VSL handshapes.

Không tự động bắt đầu TASK-0011.
