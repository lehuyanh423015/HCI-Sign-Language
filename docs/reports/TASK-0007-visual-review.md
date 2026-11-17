# TASK-0007 — Automated Facial Visual QA & Demo Generation

- Ngày/Timezone: 2026-11-17 / Asia/Saigon
- Branch/base commit: `feat/task-0007-facial-visual-review` / `ef7d53a4d2fa2ec886692e20c88bc5ea459af521`
- Scope: tự động tạo review scene, 20 facial previews, 2 contact sheets, 2 video H.264, HTML gallery, automated QA và Three.js regression evidence
- Overall status: **PARTIAL — technical package PASS; visual quality còn issue; owner acceptance và linguistic validity NOT YET TESTED**

## Executive summary

Đã tạo một gói review hoàn chỉnh tại `docs/reports/artifacts/TASK-0007/visual-review/`. Chủ dự án không cần mở Blender: mở `index.html`, xem hai video trước, rồi xem `facial-contact-sheet.png` và `eye-gaze-contact-sheet.png` để so sánh.

Pipeline dùng đúng Blender 5.2.4, tự nhận diện `Human`, `Human.rig`, sáu eye objects, sáu `NMM_` Morph Targets và bốn technical clips từ candidate TASK-0006. Source candidate và canonical master không bị sửa. Hai video là technical demonstration, không phải cử chỉ Ngôn ngữ Ký hiệu Việt Nam đã xác minh.

Kết quả kỹ thuật cho thấy blink, gaze, lips, jaw, head/neck và hand + face có thể hoạt động. Hai issue trực quan chính là eye assemblies còn lộ/protrude rõ và brow deformation quá nhẹ để đọc tốt. Candidate có thể được giữ làm prototype tạm cho vòng correction có trọng tâm, nhưng **không nên promote thành canonical** trước khi owner duyệt.

## Initial repository status

Branch được tạo trực tiếp từ completed TASK-0006 commit `ef7d53a4d2fa2ec886692e20c88bc5ea459af521`. Trước TASK-0007 đã có các thay đổi không thuộc task và được bảo toàn, không stage:

- `README.md`
- `blender/master/avatar_master_neutral_candidate.blend`
- `docs/reports/artifacts/TASK-0004-browser-runtime.json`
- `docs/reports/artifacts/TASK-0004-browser-runtime.png`

Không reset, clean, merge hay push.

## Environment and dependencies

- Blender: `5.2.4 LTS`, `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe`.
- MPFB baseline: `2.0.18`; task không thay đổi MPFB/source rig.
- Node.js: `v24.14.1`; npm: `11.12.1`; Git: `2.45.1.windows.1`.
- Three.js: project dependency hiện hữu; route kiểm tra: `/technical-facial-viewer`.
- Encoder: FFmpeg system build có `libx264`; Blender API check qua `bpy.app.build_options.ffmpeg` không hợp lệ trên build này, vì vậy pipeline dùng executable FFmpeg đã cài sẵn, đúng fallback được task cho phép.

## Source assets và SHA-256 preservation

| Source | SHA-256 trước | SHA-256 sau | Status |
|---|---|---|---|
| `blender/master/avatar_master.blend` | `A018FA9BC5129E91A320B2A1BB397D87781B757615F1CD2A7FE568945E010232` | `A018FA9BC5129E91A320B2A1BB397D87781B757615F1CD2A7FE568945E010232` | PASS |
| `blender/working/huy-anh/task-0006-facial-foundation/avatar_master_facial_candidate.blend` | `4F4BA651A8E15B356FBA18625826E5A0EBF29CBF631746A6B295DA667B27A982` | `4F4BA651A8E15B356FBA18625826E5A0EBF29CBF631746A6B295DA667B27A982` | PASS |

Review scene là file riêng: `visual-review/facial-review-scene.blend`, SHA-256 `BE48A6516DAB931C297BF93874A1BA0B8BA40EDF42B1A5692B2603DB67E2AFE9`, size `2,392,953` bytes.

## Implemented changes

- Thêm `blender/scripts/generate_facial_visual_review.py` với source hash guards và kiểm tra Blender version.
- Tạo studio review scene riêng; ẩn armature/control/debug/helper/camera-light cũ khỏi render.
- Tạo camera front, three-quarter, side và upper-body từ verified object references, không dùng object index hay manual selection.
- Render 20 states từ actual candidate controls. Nhãn được composite bằng FFmpeg ở mép dưới, không che facial features.
- Tạo contact sheets trong Blender, hai MP4 H.264 bằng FFmpeg, gallery tĩnh và owner checklist.
- Render 45 actual frames của `TECH_HAND_FACE_TEST`, làm chậm để quan sát và thêm neutral hold đầu/cuối; temporary frame sequence đã xóa sau encode.
- Không sửa geometry, Morph Target, rig, canonical master, TASK-0006 candidate hay production lesson UI.

## Generated image inventory

Tất cả previews là PNG `960×960` trong `visual-review/previews/`:

1. `01-neutral-front.png`
2. `02-neutral-three-quarter.png`
3. `03-neutral-side.png`
4. `04-brow-left.png`
5. `05-brow-right.png`
6. `06-brow-both.png`
7. `07-blink-left.png`
8. `08-blink-right.png`
9. `09-blink-both.png`
10. `10-lips-round.png`
11. `11-lips-spread.png`
12. `12-gaze-center.png`
13. `13-gaze-left.png`
14. `14-gaze-right.png`
15. `15-gaze-up.png`
16. `16-gaze-down.png`
17. `17-jaw-open.png`
18. `18-head-rotation.png`
19. `19-neck-movement.png`
20. `20-combined-facial-expression.png`

Comparison evidence:

- `facial-contact-sheet.png`: 20-state grid, `1440×1800`.
- `eye-gaze-contact-sheet.png`: center/left/right/up/down, `1600×320`.
- `gallery-browser.png`: Chrome headless screenshot xác nhận gallery render bằng local browser.
- `threejs-face.png`, `threejs-full.png`: browser regression screenshots của actual technical GLB.

## Generated video inventory

| File | Codec / resolution / FPS | Duration | SHA-256 | Status |
|---|---|---:|---|---|
| `facial-expressions-demo.mp4` | H.264 / 1920×1080 / 30 FPS | 22.800 s | `B53CE17DFE11B92DA472F8F48F87469AC24BA35C007395BD4668041DEB8E6820` | PASS |
| `hand-face-integration-demo.mp4` | H.264 / 1920×1080 / 30 FPS | 12.033 s | `2DBDA3C4AB7C73693E1360C39A27BF683B438698322987CD25836DF8A3F94C93` | PASS |

Video facial dùng actual rendered states, cross-fade mềm, nhãn rõ và trở về neutral. Video integration dùng actual `TECH_HAND_FACE_TEST`; thấy đồng thời cả hai tay, facial weight, gaze, jaw và head/neck. Đây là technical fixture, không phải production sign-language gesture.

## Objective visual QA

| Feature | Visual result | Issue | Status |
|---|---|---|---|
| Neutral face | Front, three-quarter và side render nhất quán; không có rig/debug overlay | Model có material rất sáng nhưng facial landmarks vẫn đọc được sau exposure correction | PASS |
| Eye positioning | Cả sáu eye objects render và gaze hoạt động ở năm hướng | Eyeballs còn lớn/lộ và protrude rõ ở front, three-quarter và side; cần correction có trọng tâm sau owner decision | FAIL |
| Eye blink | Left/right/both phân biệt rõ; full blink che phần lớn eye assembly | Blink còn mang tính prototype, dùng companion eye morph do eyelid topology hạn chế | PASS |
| Eyebrows | Left/right/both dùng đúng real Morph Targets | Delta quá nhẹ và không có eyebrow visual cue mạnh; khó nhận ra khi xem nhanh | FAIL |
| Lips | Round và spread khác nhau, không repurpose jaw | Biến dạng còn nhẹ và cần subjective polish nếu owner chấp nhận hướng | PASS |
| Jaw | Jaw-open rõ, mouth cavity nhìn thấy | Chưa phải production oral articulation | PASS |
| Head/neck | Rotation/movement đọc được và không xoay toàn character ngoài ý muốn | Biên độ nhỏ theo đúng technical test | PASS |
| Hand + face | Actual clip cho thấy tay/finger, face, eye, jaw, head/neck cùng hoạt động | Upper-body framing ưu tiên coexistence, chưa phải framing bài học hay cử chỉ được duyệt | PASS |

Phân loại quyết định:

- Technical correctness: **PASS** cho generation pipeline, inventory, encoding, source preservation và runtime regression.
- Visual quality: **FAIL/PARTIAL** do eye positioning và brow readability.
- Owner acceptance: **NOT YET TESTED**.
- Linguistic validity: **NOT YET TESTED**; không có qualified Deaf/native signer hoặc VSL specialist review.

## Three.js regression results

`npm run check`: **PASS** cho typecheck, lint, canonical data sync, unit tests, production build, asset validators, facial GLB validator và master verification. Lesson S001–S006 vẫn được validator báo `NOT YET TESTED` vì chưa có lesson GLB; đây là trạng thái dự án có sẵn, không phải regression TASK-0007.

Chrome headless test trên `/technical-facial-viewer`: **PASS** cho:

- GLB/canvas ready.
- Actual morph inventory.
- Four clip inventory.
- Pause, replay/progress, loop và speed.
- Morph slider và eye gaze control.
- Face/full camera presets.
- Reset all.

Evidence: `visual-review/threejs-regression.json`, `threejs-face.png`, `threejs-full.png`.

## HTML gallery và automated QA

- `index.html` mở trực tiếp bằng local Chrome với relative images/videos: **PASS**.
- Browser screenshot: `gallery-browser.png`.
- `automated-visual-qa.json`: overall `PASS`; canonical/candidate hashes, objects, targets, clips, exact preview count, contact sheets, videos, separate review scene và gallery đều `PASS`.
- Final inventory command: exact 20 preview names, required package files, gallery references, no `_hand_face_frames`, no `.blend1`: **PASS**.

## Failed/resolved checks

- Lần generation đầu: gallery formatting dùng Python `%` với CSS percent gây `ValueError`: **FAIL, resolved** bằng placeholder replacement; rerun hoàn chỉnh.
- Vòng visual review đầu: label plaque che khuôn mặt và lighting làm mất facial detail: **FAIL, resolved** bằng post-render lower-edge label, exposure correction và rerender toàn bộ package.
- `bpy.app.build_options.ffmpeg`: attribute không tồn tại trong Blender build: **FAIL cho cách probe đó, resolved** bằng executable discovery và actual H.264 encode/probe.
- Không có failure bị ghi thành PASS trước khi fix và rerun.

## Created and modified files

- `blender/scripts/generate_facial_visual_review.py`
- `docs/reports/TASK-0007-visual-review.md`
- `docs/reports/artifacts/TASK-0007/visual-review/` gồm review scene, 20 previews, 2 contact sheets, 2 MP4, HTML, automated QA JSON, browser/Three.js evidence và owner checklist.

Các user-owned changes nêu ở Initial repository status không thuộc TASK-0007 và không được stage.

## Commands actually executed

```text
git status --short --branch
git log / git show / git merge-base
Get-FileHash -Algorithm SHA256 <canonical> <TASK-0006-candidate>
npm run doctor
node tools/validate-facial-asset.mjs
blender.exe --background <TASK-0006-candidate> --python blender/scripts/generate_facial_visual_review.py -- --output-directory <visual-review> --review-blend <review-scene>
ffmpeg / ffprobe video encoding, metadata probe và temporary midpoint extraction
npm run check
npm run dev -- --host 127.0.0.1 --port 4173
node tools/test-facial-viewer.mjs --report <TASK-0007-threejs-report> --face-screenshot <TASK-0007-face> --full-screenshot <TASK-0007-full>
chrome.exe --headless=new --allow-file-access-from-files --screenshot=<gallery-browser.png> <index.html>
PowerShell exact preview/package/gallery/temp-file validation
```

## Test matrix

| Check | Evidence | Status |
|---|---|---|
| Blender 5.2.4 environment | `npm run doctor`, Blender generation log | PASS |
| Canonical master hash unchanged | before/after SHA-256 | PASS |
| TASK-0006 candidate hash unchanged | before/after SHA-256 | PASS |
| Separate automated review scene | `facial-review-scene.blend`, QA JSON | PASS |
| Exact 20 previews | inventory validation | PASS |
| Two contact sheets | visual inspection + QA JSON | PASS |
| Facial demo MP4 | ffprobe + frame inspection | PASS |
| Hand + face MP4 | ffprobe + frame inspection | PASS |
| HTML local browser rendering | `gallery-browser.png` | PASS |
| Automated QA report | `automated-visual-qa.json` | PASS |
| Frontend typecheck/lint/tests/build | `npm run check` | PASS |
| Facial GLB structure | `validate-facial-asset.mjs` via `npm run check` | PASS |
| Three.js viewer controls/runtime | `threejs-regression.json` | PASS |
| Eye positioning visual quality | multi-angle previews/contact sheet | FAIL |
| Brow readability visual quality | brow previews/contact sheet | FAIL |
| Owner visual acceptance | owner chưa review | NOT YET TESTED |
| Linguistic/content approval | qualified review chưa thực hiện | NOT YET TESTED |

## Evidence and generated artifacts

Thư mục chính: `docs/reports/artifacts/TASK-0007/visual-review/`.

Thứ tự owner nên mở:

1. `index.html` — trang tổng hợp, không cần Blender.
2. `facial-expressions-demo.mp4` — xem facial states theo trình tự.
3. `hand-face-integration-demo.mp4` — xem coexistence tay và mặt.
4. `facial-contact-sheet.png` — so sánh 20 states.
5. `eye-gaze-contact-sheet.png` — so sánh năm hướng mắt.
6. `owner-acceptance-checklist.md` — ghi quyết định.

## Known issues and limitations

- Eye scale/depth/socket fit chưa đạt visual quality production; đây là defect rõ nhất.
- Brow raise có real non-zero deformation nhưng quá nhẹ để giao tiếp rõ trong review nhanh.
- Blink phụ thuộc companion eye morph do eyelid topology TASK-0006 còn hạn chế.
- Lips round/spread đọc được nhưng cần owner quyết định trước khi sculpt/polish.
- White neutral material làm avatar mang phong cách prototype; task chỉ điều chỉnh review lighting, không redesign material/geometry.
- Contact sheets/video chứng minh kỹ thuật, không chứng minh semantic hay linguistic correctness.

## Git branch and commit information

- Branch: `feat/task-0007-facial-visual-review`.
- Base TASK-0006: `ef7d53a4d2fa2ec886692e20c88bc5ea459af521`.
- Final local commit: commit chứa báo cáo này; exact hash được ghi trong final response vì commit hash chỉ tồn tại sau khi report được commit.
- Merge/push: **không thực hiện**.

## Outstanding blockers

Không có blocker cho việc xem gói technical review. Hai gate còn mở:

- Owner phải quyết định có chấp nhận candidate làm prototype tạm và cho phép focused eye/brow correction hay không.
- Qualified linguistic reviewer phải review riêng trước khi gán semantic VSL hoặc dùng trong nội dung bài học.

## Owner manual acceptance checklist

- [ ] Mở `index.html`, phát được cả hai video.
- [ ] Neutral front/three-quarter/side phù hợp hướng giáo dục trung tính.
- [ ] Chấp nhận hoặc yêu cầu sửa eye scale/depth/socket fit.
- [ ] Five gaze directions đọc được và không quá mức.
- [ ] Left/right/both blink đọc được; chấp nhận giới hạn companion morph tạm thời.
- [ ] Left/right/both brow raise đủ rõ hoặc yêu cầu focused correction.
- [ ] Lips round/spread và jaw open phân biệt được.
- [ ] Head/neck movement và hand + face coexistence phù hợp technical prototype.
- [ ] Xác nhận không coi demo này là Vietnamese Sign Language đã xác minh.
- [ ] Chỉ promote candidate bằng task/commit riêng sau acceptance.

Owner decision hiện tại: **NOT YET TESTED**.

## Next recommended tasks

Sau khi owner review, nếu đồng ý tiếp tục: tạo một task riêng để sửa đúng hai điểm eye depth/scale/socket fit và brow readability; giữ source hash guard, tạo before/after multi-angle regression, rồi yêu cầu owner duyệt lại. Chỉ lên kế hoạch linguistic review sau khi visual prototype ổn định. Không tự động bắt đầu task kế tiếp.
