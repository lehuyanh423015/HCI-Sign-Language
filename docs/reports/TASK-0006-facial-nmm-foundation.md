# TASK-0006 — Facial & Non-manual Marker Foundation Prototype

- Ngày/Timezone: 2026-11-17 / Asia/Saigon
- Branch/base commit: `feat/task-0006-facial-foundation` / `94bc083b107cb7ab94fce7480db18d829f171676`
- Scope: facial working candidate, visible eye assets, six NMM Morph Targets, four technical clips, morph-compatible GLB, isolated Three.js viewer, automated/browser evidence
- Overall status: **PASS về technical structure/runtime; owner visual acceptance và linguistic approval: NOT YET TESTED**

## 1. Executive summary

Đã tạo candidate `Master Avatar v1.0.0-rc.2` tách khỏi canonical, bổ sung six visible eye assets bind vào `eye.L/R`, six non-zero `NMM_` Morph Targets, head/neck/jaw/eye tests và four technical clips. `TECH_HAND_FACE_TEST` chứa finger, wrist, head/neck, jaw, eye và Morph Target weight channels trong cùng GLB.

`technical-facial-test.glb` có 9 meshes, 1 skin, six eye nodes, six core NMM targets, four positive-duration clips và Khronos Validator `0 errors / 0 warnings`. Trang `/technical-facial-viewer` load asset thật, tự discover NMM targets, điều khiển sliders/gaze/animation/camera/reset và đã qua Chrome headless runtime test. Không có clip nào được gọi là VSL đã xác minh.

## 2. Initial repository status

Trước task, working tree có user-owned changes bắt buộc bảo toàn:

- `README.md` — SHA-256 `15BD087AA12147E393B184FB7979CD186EF73AEA682AA3F79395AA65CA680487`.
- `blender/master/avatar_master_neutral_candidate.blend` — SHA-256 `BC2F154580DD97C2043812E867387054E1F9DE63DD6A61F8DB36E4FB868F49BE`.

Hai file này không bị overwrite/stage. Canonical source ban đầu:

- `blender/master/avatar_master.blend` — SHA-256 `A018FA9BC5129E91A320B2A1BB397D87781B757615F1CD2A7FE568945E010232`.
- Official manifest — SHA-256 `E2F33D230349488C581678C93DA80E666332474ADFD144B63C477900F2853EF4`.

## 3. Actual TASK-0005 base commit

Git history được đối chiếu và branch TASK-0006 được tạo từ completed TASK-0005 commit:

`94bc083b107cb7ab94fce7480db18d829f171676`

Không merge, không push, không reset/clean.

## 4. Environment and dependencies

- OS: Windows 10 build `10.0.26300`, x64.
- Blender: `5.2.4 LTS` tại `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe`.
- MPFB: `2.0.18`, initialization/build info `20261010`.
- Node.js: `v24.14.1`; npm: `11.12.1`; Git: `2.45.1.windows.1`.
- Three.js: `0.187.0`; React: `19.3.1`; Vite: `8.3.8`.
- `npm run doctor`: required checks `PASS`; MPFB/3D được xác minh bằng Blender scripts riêng, không suy diễn từ doctor.

## 5. Canonical master preservation

Canonical SHA-256 trước và sau: `A018FA9BC5129E91A320B2A1BB397D87781B757615F1CD2A7FE568945E010232` — **PASS, byte-for-byte unchanged**.

Official master manifest không sửa. Candidate và export preprocessing nằm ngoài canonical. Original neutral candidate/user README giữ đúng hashes nêu ở mục 2.

## 6. Facial working copy

- Blend: `blender/working/huy-anh/task-0006-facial-foundation/avatar_master_facial_candidate.blend`.
- Manifest: `avatar_master_facial_candidate.manifest.json`.
- Version/status: `1.0.0-rc.2` / `experimental-owner-review-candidate`.
- Final candidate SHA-256: `4F4BA651A8E15B356FBA18625826E5A0EBF29CBF631746A6B295DA667B27A982`.
- 137 bones và hierarchy SHA-256 `6A8C8B4B2C2E71446A79E478E15F3FFE1A646F24EFF86C3C9C158315AAFE72C2` được giữ nguyên.
- Existing 11 MPFB Shape Keys và values/coordinate hashes được preservation check `PASS` trong creation report.

## 7. Eye asset implementation

Tạo sáu mesh objects có material trung tính:

| Object | Role | Material |
|---|---|---|
| `NMM_Eyeball.L/R` | sclera | `NMM_Eye_Sclera` |
| `NMM_Iris.L/R` | iris | `NMM_Eye_Iris` |
| `NMM_Pupil.L/R` | pupil | `NMM_Eye_Pupil` |

Position/orientation lấy trực tiếp từ `eye.L/R` head/tail axes; assembly được lùi 4 mm theo trục bone sau browser visual QA để giảm độ lộ cầu mắt. Không thêm bone mới.

## 8. Eye bone binding results

Mỗi vertex của left/right assembly có weight `1.0` tới `eye.L`/`eye.R` tương ứng và Armature modifier trỏ `Human.rig`:

- Eyeball: `366/366` weighted vertices mỗi bên.
- Iris: `218/218` mỗi bên.
- Pupil: `142/142` mỗi bên.
- Center/left/right gaze đã render; viewer còn expose up/down với small local rotations.

## 9. New Morph Target inventory

| Target | Moved vertices | Max delta | Neutral/range | Status |
|---|---:|---:|---|---|
| `NMM_BROW_RAISE_L` | 202 | 0.006280 m | 0 / [0,1] | PASS |
| `NMM_BROW_RAISE_R` | 202 | 0.006280 m | 0 / [0,1] | PASS |
| `NMM_EYE_BLINK_L` | 766 | 0.005586 m | 0 / [0,1] | PASS |
| `NMM_EYE_BLINK_R` | 766 | 0.005586 m | 0 / [0,1] | PASS |
| `NMM_LIPS_ROUND` | 1373 | 0.008437 m | 0 / [0,1] | PASS |
| `NMM_LIPS_SPREAD` | 1373 | 0.005205 m | 0 / [0,1] | PASS |

Eye meshes có matching blink companion targets để pupil/iris rút vào và flatten ở full blink; body keys vẫn là real non-zero eyelid deformation.

## 10. Shape Key deformation results

- Neutral, single/both blink, brows raised, lips round/spread và combined states đều có preview riêng.
- Vòng render đầu cho manual states giống nhau vì Action đang active: **FAIL được phát hiện và sửa** bằng cách detach Action trước manual evidence.
- Vòng blink tiếp theo làm orbit biến dạng nhưng pupil còn mở: **FAIL visual được phát hiện và sửa** bằng local eyelid mask + companion eye morph.
- Final full blink đọc được rõ, không có zero-delta target. Brow/lip deformation còn nhẹ và cần owner polish trước production.

## 11. Jaw, head and neck results

- `head`, `neck02`, `jaw`, `eye.L/R` có controlled rotation channels và reset về neutral: **PASS**.
- Không đổi root/rest pose, armature object transform hoặc bone hierarchy.
- Jaw open evidence dùng `jaw` rotation; lip keys không repurpose jaw.

## 12. Facial animation clips

| Clip | Frames/FPS | Main channels | Status |
|---|---|---|---|
| `NMM_BLINK_TEST` | 1–30 / 30 | blink weights + eye scale | PASS |
| `NMM_BROW_TEST` | 1–30 / 30 | left/right brow weights | PASS |
| `NMM_MOUTH_TEST` | 1–30 / 30 | jaw + round/spread weights | PASS |
| `TECH_HAND_FACE_TEST` | 1–45 / 30 | fingers, wrist, head, neck, jaw, eyes, NMM weights | PASS |

Actions use Blender 5.2 Action/Slot APIs và `use_fake_user` để survive save/reopen.

## 13. Combined hand-and-face result

Candidate validator xác nhận `TECH_HAND_FACE_TEST` có right finger chains, `wrist.R`, `head`, `neck02`, `jaw`, `eye.L/R`, brow/blink/lip weight curves. Evidence `12-combined-hand-face.png` dùng upper-body frame để thấy đồng thời tay và mặt: **PASS technical integration**.

## 14. GLB structure and validation

- Output: `assets/exports/technical/technical-facial-test.glb`.
- Final size: `2,455,308` bytes.
- Final SHA-256: `615CCB9697B51CC4938C98556D0292950DFD4A05D9334D2BE5E8140070EFB68D`.
- Structure: 9 meshes, 1 skin, six eye nodes, six core NMM names, four clips.
- Every clip has positive duration; `TECH_HAND_FACE_TEST` có right-hand bone, head/jaw/eye và `weights` channels.
- Khronos: `0 errors`, `0 warnings`, `1 info`, `0 hints` — **PASS**.
- `TASK0005_DIAGNOSTIC_MORPH` không tồn tại trong deliverable.

Export-only preprocessing bake current MPFB macro mix, rồi evaluate `Hide helpers` cho base + từng target (`19,158 → 13,380` vertices). Six NMM targets được rebuild trên masked topology; Action/Slot được nối qua same-name NLA tracks. Candidate `.blend` không được save sau preprocessing.

## 15. Three.js viewer implementation

- Route: `/technical-facial-viewer`; old `/technical-viewer` giữ nguyên.
- Asset: `/models/technical/technical-facial-test.glb` qua reproducible sync script.
- Tự discover actual `morphTargetDictionary`; UI chỉ expose present `NMM_` targets.
- Six sliders cập nhật mọi body/eye binding cùng name.
- Gaze: center/left/right/up/down qua actual `eye.L/R` objects.
- Animation: clip select, play/pause/replay/loop/0.5×–1×.
- Camera: full/face, orbit/zoom; reset phục hồi morphs, gaze, camera, animation state.
- Banner đúng: `TECHNICAL FACIAL TEST — NOT VERIFIED SIGN LANGUAGE`.

## 16. Browser runtime results

Chrome headless/WebGL checks đều `PASS`:

- GLB/canvas ready; filename/status đúng.
- Six NMM target names và four clips present.
- Actual slider event, gaze preset, camera presets.
- Pause, replay/progress, loop, speed, reset-all.
- Không có `Runtime.exceptionThrown`.
- Existing `/technical-viewer` regression: `PASS` toàn bộ controls.

## 17. Visual evidence

- Candidate previews: `docs/reports/artifacts/TASK-0006/previews/01-neutral-face.png` … `12-combined-hand-face.png`.
- Re-imported GLB: `docs/reports/artifacts/TASK-0006/glb-preview-face.png`.
- Browser: `browser-face.png`, `browser-full.png`.
- JSON: `candidate-creation.json`, `candidate-validation.json`, `glb-export.json`, `glb-validation.json`, `browser-runtime.json`.

Programmatic/agent visual QA: **PASS cho technical inspectability**. Huy Anh owner manual acceptance: **NOT YET TESTED**.

## 18. Linguistic/content review

**NOT YET TESTED.** Không có qualified Deaf/native signer hoặc Vietnamese Sign Language specialist review trong task. Clip/target chỉ là technical deformation; không gán semantic VSL và không tích hợp lesson catalog.

## 19. Created and modified files

- Blender: `create_facial_foundation.py`, `validate_facial_foundation.py`, `export_facial_glb.py`, candidate `.blend` + manifest.
- GLB/tooling: `technical-facial-test.glb`, `validate-facial-asset.mjs`, `sync-technical-assets.mjs`.
- Web: `TechnicalFacialViewer.tsx`, `TechnicalFacialViewerPage.tsx`, routes/nav/CSS/tests.
- Browser: `test-facial-viewer.mjs`.
- Docs: facial contract, MASTER_AVATAR/HANDOFF additions, TASK-0006 report/evidence.
- User-owned `README.md` và neutral candidate không thuộc commit. TASK-0004 browser evidence bị regression command regenerate trong working tree và cũng bị loại khỏi TASK-0006 commit.

## 20. Commands actually executed

```text
git status --short --branch
git log / git show / Get-FileHash ...
npm run doctor
node tools/verify-master-manifest.mjs
blender.exe --background blender/master/avatar_master.blend --python blender/scripts/create_facial_foundation.py -- ...
blender.exe --background <facial-candidate> --python blender/scripts/validate_facial_foundation.py -- ...
blender.exe --background <facial-candidate> --python blender/scripts/export_facial_glb.py -- ...
node tools/validate-facial-asset.mjs
blender.exe --background --python blender/scripts/render_glb_preview.py -- --input technical-facial-test.glb ...
npm run sync:technical-assets
npm run sync:technical-assets:check
npm run typecheck
npm run lint
npm test
npm run build
npm run dev -- --host 127.0.0.1 --port 4173   # từ apps/web
npm run test:facial-viewer
npm run test:neutral-viewer
npm run check
```

Các failed/resolved trials được giữ trong task history: wrong `reference_key` collection API, Actions bị orphan khi chưa `use_fake_user`, ACTION export thiếu weight slots, unbaked `Hide helpers` gây visual deformation. Không trial nào được ghi `PASS` trước khi fix và rerun.

## 21. Test matrix

| Check | Evidence | Status |
|---|---|---|
| Blender 5.2.4 environment | `npm run doctor` + Blender logs | PASS |
| Canonical hash/master manifest | hash + `verify:master` | PASS |
| Candidate separate/137 bones/hierarchy | `candidate-validation.json` | PASS |
| Original 11 MPFB keys preserved | `candidate-creation.json` | PASS |
| Six non-zero NMM targets | candidate validation | PASS |
| Six eye objects/binding | candidate validation | PASS |
| Head/neck/jaw/eye channels | candidate validation/previews | PASS |
| Combined hand + face | candidate/GLB validation | PASS |
| GLB Morph + bone channels | `glb-validation.json` | PASS |
| Khronos Validator | 0 errors / 0 warnings | PASS |
| Re-imported GLB visual | `glb-preview-face.png` | PASS |
| Web typecheck/lint/tests/build | npm logs | PASS |
| Facial browser runtime | `browser-runtime.json` | PASS |
| Existing technical viewer regression | TASK-0004 runtime regeneration | PASS |
| Owner visual acceptance | checklist below | NOT YET TESTED |
| Linguistic/content approval | qualified reviewer unavailable | NOT YET TESTED |

## 22. Known issues and limitations

- Eyelid topology chưa đủ cho production blink; companion eye morph là kỹ thuật prototype đã document.
- Brow/lip deltas đọc được nhưng còn nhẹ; cần sculpt/control-rig polish ở task sau nếu owner duyệt hướng này.
- Visible eyes vẫn cần owner đánh giá tỷ lệ/socket từ nhiều góc camera; browser visual đã giảm độ lộ bằng 4 mm offset.
- NLA exporter sample all bones thành `412` channels/clip, tăng file size; functional và validator-clean nhưng có thể optimize sau.
- Blender exporter báo source có >4 influences và chọn/normalize top four theo project baseline.
- Facial control rig animator-friendly lớn, viseme set và production corrective shapes ngoài scope.

## 23. Git branch and commit information

- Branch: `feat/task-0006-facial-foundation`.
- Base: `94bc083b107cb7ab94fce7480db18d829f171676`.
- Final commit: ghi trong final response sau khi report được stage/commit.
- Remote push/merge: **không thực hiện**.

## 24. Outstanding blockers and owner manual acceptance checklist

Không có blocker cho technical prototype. Các gate trước promotion:

- [ ] Huy Anh mở candidate bằng Blender 5.2.4 và duyệt neutral face từ front/side/3/4.
- [ ] Duyệt eye depth/scale/material và five gaze directions, không floating/intersection nghiêm trọng.
- [ ] Duyệt full-weight six NMM targets và pairwise interaction.
- [ ] Scrub four clips; xác nhận neutral start/end và `TECH_HAND_FACE_TEST` simultaneous channels.
- [ ] Mở `/technical-facial-viewer`, thử sliders/gaze/playback/reset trên GPU/browser mục tiêu.
- [ ] Xác nhận candidate chỉ được promote bằng task/commit riêng; không thay canonical tự động.
- [ ] Thao điều phối qualified linguistic review trước khi bất kỳ NMM nào vào lesson content.

## 25. Recommended TASK-0007 scope

Nếu owner chấp thuận prototype: polish eyelid/brow/lip topology và corrective targets; giảm eye exposure theo multi-angle review; xây animator-friendly facial control layer nhỏ; optimize NLA/export sampling; tạo neutral/interaction regression renders; tổ chức qualified VSL NMM review và chỉ sau đó mới đề xuất promotion candidate.

Không tự động bắt đầu TASK-0007.
