# TASK-0003 — 3D Technical Prototype, GLB Integration và Team Handoff

- Ngày/Timezone: 2026-11-17, Asia/Saigon
- Branch: `feat/task-0003-3d-prototype`
- Base commit: `2bfa409`
- Phạm vi: kiểm chứng rig, tạo technical animation, export/validate GLB, tích hợp Three.js, chuẩn hóa handoff và Agent reporting
- Trạng thái tổng thể: **PASS cho pipeline tự động; owner visual acceptance là NOT YET TESTED**

## A. Executive summary

Đã chứng minh pipeline Blender 5.2.4 → GLB → Three.js bằng fixture `TECH_HAND_CONTROL_TEST`. Fixture chỉ đóng/mở bàn tay phải để kiểm tra kỹ thuật, không phải và không được gán thành Ngôn ngữ Ký hiệu Việt Nam. Source `.blend` vẫn editable; GLB canonical có đúng một mesh, một skin và clip 1 giây; browser runtime thực tế tải/play được asset và các control hoạt động. Master không bị sửa.

## B. Blender 5.2.4 environment confirmation

- Blender: `5.2.4 LTS`, build `cd5dc428cce1` — **PASS**.
- Embedded Python: `3.13.13`; chạy riêng trong Blender — **PASS**.
- Node.js `24.14.1`, npm `11.12.1`, Git `2.45.1.windows.1` — **PASS**.
- Baseline active trong config/docs/doctor đã đổi sang Blender `5.2.4 LTS`; không khôi phục 4.5.16.
- Evidence: `docs/reports/artifacts/TASK-0003-environment.json`.

## C. MPFB status

MPFB `2.0.18` được tìm thấy, enabled và initialized trong Blender background process — **PASS**. Không cài, upgrade hoặc sửa Blender/MPFB.

## D. Master rig characteristics

Giữ nguyên kết quả TASK-0002: một mesh `Human`, một armature `Human.rig`, 137 deform bones, không control rig/IK/constraints, hai bàn tay có bone/weight; mỗi ngón có ba bone. Armature có object rotation khác identity. Cấu hình transform đang hoạt động được giữ nguyên; không `Apply Transform`, không thêm Rigify/IK/constraint.

Trước khi làm, repository có user-owned change chưa commit ở cuối `README.md`; thay đổi này được giữ trong working tree và loại khỏi task commit.

## E. Finger control and deformation tests

Script reusable `blender/scripts/test_rig_controls.py` tự probe cả ba local axes và hai hướng thay vì giả định axis. Kết quả:

| Control | Local direction chọn | Vertices moved | Max delta | Status |
|---|---:|---:|---:|---|
| `finger1-1.R` (thumb) | X+ | 260 | 0.023933 m | PASS |
| `finger2-1.R` (index) | X+ | 350 | 0.019666 m | PASS |
| `finger3-1.R` (middle) | X+ | 387 | 0.022738 m | PASS |
| `finger4-1.R` (ring) | X+ | 386 | 0.021286 m | PASS |
| `finger5-1.R` (little) | X+ | 346 | 0.014953 m | PASS |
| `wrist.R` | X− | 1,685 | 0.025626 m | PASS |
| `lowerarm01.R` | Y− | 1,940 | 0.014825 m | PASS |

Mỗi test chỉ author transform trên control mục tiêu; object/root transform ổn định; reset pose và evaluated mesh trở về chính xác. Automated deformation: **PASS**. Owner kiểm tra trực quan anatomy/clipping: **NOT YET TESTED**.

## F. FPS and transform decisions

- Scene working: 30 FPS, frame 1–30, nominal 1 giây.
- Không normalize/apply armature object transform vì rig/skin hiện hoạt động và không có bằng chứng cần thao tác phá hủy.
- Body/root/object transform không được key; chỉ 15 finger pose bones bên phải có animation.

## G. Technical animation specifications

- Action/clip: `TECH_HAND_CONTROL_TEST` dùng Blender 5.2 Action Slot API.
- Frame 1: open; frame 15: partially closed; frame 30: closed.
- 45 F-curves, 135 keyframe points, `BEZIER`, 15 right-finger bones.
- Working source: `blender/working/huy-anh/technical-hand-test.blend`.
- Reload validation sau khi lưu: action name/assignment, timing, bone set, frame set và editable `.blend` đều **PASS**.
- Preview frame 1/15/30 đã render. Agent inspection không thấy whole-character rotation hoặc distortion nghiêm trọng; đây không thay thế owner visual acceptance.

## H. GLB file and animation details

- Canonical: `assets/exports/technical/technical-hand-test.glb`.
- Size: 6,056,496 bytes.
- SHA-256: `3396D475B3A88D5930E6D5D6093CA5665818C8109C0BEB04C2D067D6125DFBE5`.
- glTF 2.0; 1 scene, 139 nodes, 1 mesh, 1 skin; clip exact `TECH_HAND_CONTROL_TEST`, 1.0000 s, 15 channels/samplers, không thiếu/thừa target bones.
- Khronos validator: 0 errors, 1 warning `NODE_SKINNED_MESH_NON_ROOT`, 1 info `UNUSED_OBJECT` cho `TEXCOORD_0`. Warning được ghi nhận; runtime skin/animation vẫn PASS.
- Export dùng mode `ACTIONS` vì Blender 5.2 `ACTIVE_ACTIONS` đã làm mất tên clip trong lần thử đầu. Public copy được sinh bằng `npm run sync:technical-assets` và Git-ignore; canonical GLB là nguồn duy nhất được commit.

## I. Three.js viewer integration

Route `/technical-viewer` dùng `GLTFLoader`, `AnimationMixer`, `OrbitControls`; tìm clip theo exact name. Có loading/error state, pause/resume, replay, loop, 0.5×/1×, rotate, zoom, reset camera và close-up tay phải. Banner hiển thị đúng `TECHNICAL TEST - NOT VERIFIED SIGN LANGUAGE`; fixture không thuộc S001–S006.

Chrome headless qua DevTools Protocol thực sự render WebGL và xác minh animation time thay đổi, pause đứng yên, resume/replay/loop/speed/camera state đúng — **PASS**, không runtime exception. CUA helper không khởi tạo được do `helper_unknown_error: setup refresh had errors` — **SKIPPED**; fallback CDP cung cấp browser evidence thực tế.

HTTP smoke test: route 200; GLB 200 với `model/gltf-binary`, 6,056,496 bytes; hash HTTP khớp canonical — **PASS**.

## J. Test matrix

| Check | Kết quả thực tế | Status |
|---|---|---|
| `npm run doctor` với `BLENDER_EXECUTABLE` | 0 required failures, 0 environment mismatches | PASS |
| Blender environment + MPFB preflight | 6/6 checks | PASS |
| Controlled pose/deformation | 7/7 controls; exact reset | PASS |
| Animation creation | 45 curves, 135 keys, 15 bones | PASS |
| Saved `.blend` reload validation | 6/6 checks | PASS |
| GLB export/structure/clip/duration | Expected asset/clip, 1.0000 s | PASS |
| Khronos glTF validator | 0 errors, 1 documented warning | PASS |
| `npm ci --ignore-scripts` | 155 packages audited, 0 vulnerabilities | PASS |
| `npm run check` | typecheck, lint, data, sync, 7 tests, build, validators | PASS |
| Production build | 36 modules; JS 917.49 kB, gzip 247.22 kB | PASS |
| Build chunk size | Vite warning >500 kB | PASS WITH WARNING |
| HTTP route + GLB bytes/hash | 200/200, hash match | PASS |
| Chrome runtime animation/controls | 8/8 checks, 0 exceptions | PASS |
| CUA browser helper | Không khởi tạo được trong Windows sandbox | SKIPPED |
| Owner human visual inspection | Chưa có owner sign-off | NOT YET TESTED |
| Production S001–S006 GLBs | Không thuộc TASK-0003; vẫn pending | NOT YET TESTED |

## K. Evidence paths and previews

- `docs/reports/artifacts/TASK-0003-environment.json`
- `docs/reports/artifacts/TASK-0003-controlled-rig-test.json`
- `docs/reports/artifacts/TASK-0003-animation.json`
- `docs/reports/artifacts/TASK-0003-animation-reload.json`
- `docs/reports/artifacts/TASK-0003-glb-export.json`
- `docs/reports/artifacts/TASK-0003-glb-validation.json`
- `docs/reports/artifacts/TASK-0003-browser-runtime.json`
- `docs/reports/artifacts/TASK-0003-browser-runtime.png`
- `docs/reports/artifacts/task-0003-previews/technical-hand-test-frame-001.png`
- `docs/reports/artifacts/task-0003-previews/technical-hand-test-frame-015.png`
- `docs/reports/artifacts/task-0003-previews/technical-hand-test-frame-030.png`

## L. Master SHA-256 before and after

| Asset | Before | After | Status |
|---|---|---|---|
| `blender/avatar_master.blend` | `E15142798E8C573AA80243DE6D6F24B48CC517BBC5DD410DC1262AD1432480FA` | `E15142798E8C573AA80243DE6D6F24B48CC517BBC5DD410DC1262AD1432480FA` | PASS — unchanged |

Working `.blend` SHA-256: `1FD50D320ECD212DDC17E26CC680CAD92210FBEC537E8A39CD8D10C70D801B25`.

## M. Changed files

- Baseline/config: `.env.example`, `README.md` (chỉ task hunks), `tools/doctor.mjs`, Blender/setup/contract/ADR docs.
- Blender automation/source: `blender/scripts/{rig_control_utils,test_rig_controls,create_technical_animation,export_technical_glb,validate_technical_animation}.py`, working `.blend`.
- GLB pipeline: `assets/exports/technical/`, `tools/{sync-technical-assets,validate-technical-asset}.mjs`, package manifests/lockfile.
- Web: technical viewer/page, routes/nav/styles/tests, `tools/test-technical-viewer.mjs`.
- Team/process: `AGENTS.md`, handoff/ownership docs, `AGENT_TASK_PROTOCOL.md`, report template và evidence/report TASK-0003.
- `.gitignore` chỉ bỏ generated public GLB/temporary working artifacts theo policy; public technical README vẫn được commit.

## N. Git branch and commit information

- Branch: `feat/task-0003-3d-prototype`.
- Base: TASK-0002 commit `2bfa409`.
- Remote: `origin` trỏ tới repository owner đã cung cấp; task không push/merge.
- Final commit hash chưa thể tự ghi vào chính report trong cùng commit. Actual hash được nêu trong final Agent response theo protocol.
- User-owned dòng cuối `README.md` được bảo toàn ngoài task commit.

## O. Team onboarding readiness

`HANDOFF.md`, `OWNERSHIP.md`, Windows/Blender setup và asset contract đã mô tả clone/install/run, ownership Huy Anh–Mien–Nhat–Thao, working-copy discipline, GLB consumer flow, branch/PR/test/blocker protocol. Git LFS 3.5.1 có mặt và endpoint được nhận diện nhưng chưa có tracking patterns, auth/upload chưa được thử; chưa bật LFS tự động vì các binary prototype hiện dưới giới hạn GitHub và migration cần PR/quota decision riêng.

## P. Owner manual acceptance checklist

- [ ] Mở ba preview frame 1/15/30, xác nhận bàn tay chuyển open → partial → closed và không clipping/distortion không chấp nhận được.
- [ ] Mở `technical-hand-test.blend` bằng Blender 5.2.4, scrub frame 1/15/30 và xác nhận body đứng yên, Action editable.
- [ ] Chạy `npm run sync:technical-assets`, `npm run dev`, mở `http://localhost:5173/technical-viewer` và thử rotate/zoom cùng mọi control.
- [ ] Xác nhận banner unverified rõ ràng và fixture không xuất hiện trong catalog S001–S006.
- [ ] Review warning `NODE_SKINNED_MESH_NON_ROOT`; chấp nhận cấu hình hiện tại hoặc mở task riêng nếu muốn chuẩn hóa hierarchy.
- [ ] Review diff/commit rồi mới push và tạo PR; không merge tự động.

## Q. Remaining problems and limitations

- Human/owner visual sign-off: **NOT YET TESTED**.
- GLB không có material/texture; đủ cho technical deformation nhưng chưa phải visual production asset.
- Khronos còn 1 warning về skinned mesh non-root và 1 info về unused UV.
- Bundle Three.js tạo Vite chunk warning >500 kB; chưa cần tối ưu cho prototype, nên code-split trước production.
- CUA helper bị lỗi khởi tạo; Chrome CDP test thay thế đã PASS.
- Git LFS upload/quota/auth chưa được kiểm chứng.

## R. Commands actually executed và proposed next tasks

Các lệnh chính đã thực sự chạy:

```text
git switch -c feat/task-0003-3d-prototype 2bfa409
blender.exe --background <TASK-0002 working copy> --python blender/scripts/test_rig_controls.py -- ...
blender.exe --background blender/avatar_master.blend --python blender/scripts/create_technical_animation.py -- ...
blender.exe --background blender/working/huy-anh/technical-hand-test.blend --python blender/scripts/export_technical_glb.py -- ...
blender.exe --background --python blender/scripts/inspect_environment.py -- --output docs/reports/artifacts/TASK-0003-environment.json --expected-version 5.2.4 --require-mpfb
blender.exe --background blender/working/huy-anh/technical-hand-test.blend --python blender/scripts/validate_technical_animation.py -- --report docs/reports/artifacts/TASK-0003-animation-reload.json
npm ci --ignore-scripts
npm run doctor
npm run check
npm run test:technical-viewer
Invoke-WebRequest http://127.0.0.1:4173/technical-viewer
Invoke-WebRequest http://127.0.0.1:4173/models/technical/technical-hand-test.glb
git lfs version
git lfs env
```

Đề xuất sau khi owner manual acceptance và PR TASK-0003 được duyệt: mở task riêng để xử lý validator warning nếu cần; thống nhất Git LFS policy; sau đó mới lập kế hoạch production animation S001–S006 với reference/approval thật. Không tự động bắt đầu task kế tiếp.
