# TASK-0007A — Focused Facial Refinement: Eye Geometry & Eyebrow Readability

- Ngày/Timezone: 2026-11-18 / Asia/Saigon
- Branch/base commit: `feat/task-0007a-facial-refinement` / `191df0c4423a3a79eaac014a97881b74519262bd`
- Objectives: giảm eye size/protrusion, tăng brow readability, giữ toàn bộ facial/hand compatibility, tạo candidate rc.3 + GLB + before/after package
- In scope: six eye objects và hai `NMM_BROW_RAISE_*` Shape Keys trên working copy
- Out of scope: canonical, TASK-0006 source, rig rebuild, lip/mouth redesign, clothing/body, production VSL content, frontend redesign
- Overall status: **PASS về structural, animation, GLB, Three.js và agent visual QA; owner acceptance: NOT YET TESTED**

## 1. Executive summary

Đã tạo `Master Avatar v1.0.0-rc.3` tại `blender/working/huy-anh/task-0007a-facial-refinement/avatar_master_facial_refined_candidate.blend` từ source TASK-0006 mà không sửa source.

Hai eye assemblies được thu nhỏ có đo đạc và lùi sâu thêm theo trục `eye.L/R`. Eyeball diameter giảm `22%` (`24.600 mm → 19.188 mm`); protrusion proxy so với facial-surface median giảm `56.15%` (`11.053 mm → 4.847 mm`). Iris và pupil được scale/reposition theo eyeball mới, vẫn bind `1.0` vào đúng eye bone.

Hai brow targets giữ nguyên tên và đúng 198 affected vertices mỗi bên. Full max delta tăng từ `6.280 mm` lên `14.463 mm`; interpolation 0.5 đạt `7.232 mm`, lớn hơn full delta cũ và đọc được rõ hơn trong cropped comparison. Không thêm target, không sửa neutral body geometry, không đụng lips/blink Shape Keys.

Refined GLB có 9 meshes, skin, six eye nodes, six NMM targets và four technical clips; Khronos `0 errors / 0 warnings`. Existing `/technical-facial-viewer` PASS toàn bộ runtime controls khi nạp refined GLB. Candidate **sẵn sàng cho owner review và temporary-release gate**, nhưng chưa được coi là accepted/promoted cho Master Avatar v1 cho tới khi owner tick checklist.

## 2. Actual TASK-0007 base commit

Branch được tạo từ commit TASK-0007 thực tế:

`191df0c4423a3a79eaac014a97881b74519262bd` — `feat: add automated facial visual review`

Không đoán base, không reset/clean/merge/push.

## 3. Initial Git status

Các user-owned/unrelated changes tồn tại trước task và được bảo toàn, không stage:

- `README.md`
- `blender/master/avatar_master_neutral_candidate.blend`
- `docs/reports/artifacts/TASK-0004-browser-runtime.json`
- `docs/reports/artifacts/TASK-0004-browser-runtime.png`

Remote: `origin https://github.com/lehuyanh423015/HCI-Sign-Language.git`. Task không push.

## 4. Environment and dependencies

- Blender: `5.2.4 LTS`, build `2026-11-10`, đúng project baseline.
- MPFB: `2.0.18`, initialization build `20261010`.
- Node.js: `v24.14.1`; npm: `11.12.1`; Git: `2.45.1.windows.1`.
- FFmpeg: system executable có `libx264`; outputs H.264 1920×1080 30 FPS.
- Three.js/React/Vite: project dependencies hiện hữu; không thêm dependency.

## 5. Source file paths and preservation hashes

| File | SHA-256 trước | SHA-256 sau | Status |
|---|---|---|---|
| `blender/master/avatar_master.blend` | `A018FA9BC5129E91A320B2A1BB397D87781B757615F1CD2A7FE568945E010232` | same | PASS |
| `blender/working/huy-anh/task-0006-facial-foundation/avatar_master_facial_candidate.blend` | `4F4BA651A8E15B356FBA18625826E5A0EBF29CBF631746A6B295DA667B27A982` | same | PASS |
| `docs/reports/artifacts/TASK-0007/visual-review/facial-review-scene.blend` | `BE48A6516DAB931C297BF93874A1BA0B8BA40EDF42B1A5692B2603DB67E2AFE9` | same | PASS |

TASK-0007 không tạo thêm model candidate ngoài TASK-0006 source; toàn bộ `docs/reports/artifacts/TASK-0007/` có `git diff` count `0` sau task. Tree object ban đầu: `a0ac97786b136f7b773897767b31107daddfeea7`.

Refined output mới:

- Blend SHA-256: `0D9D2ECE642540B792A79F36003FEE1FBB47C6966FFB8A953B7B7F5F043CCAB7`.
- Version/status: `1.0.0-rc.3` / `experimental-owner-review-candidate`.
- 137 bones; hierarchy SHA-256 `6A8C8B4B2C2E71446A79E478E15F3FFE1A646F24EFF86C3C9C158315AAFE72C2`.
- `neutral_body_geometry_unchanged`: PASS.
- Non-brow body Shape Keys, including blink/lips và MPFB keys: byte-coordinate hashes unchanged trong creation validation.

## 6. Eye geometry findings before correction

Actual geometry được đo từ eye `Basis` Shape Keys và trục local của `eye.L/R`, không dùng object index hay arbitrary global scale.

| Measurement | Left | Right | Finding |
|---|---:|---:|---|
| Eyeball diameter | 24.599994 mm | 24.599992 mm | Quá lớn so với visible eyelid aperture |
| Iris diameter | 12.399996 mm | 12.399995 mm | Làm eye assembly đọc như attached sphere |
| Pupil diameter | 5.600000 mm | 5.599998 mm | Tỷ lệ theo iris cũ |
| Protrusion vs socket-proxy median | 11.053184 mm | 11.053184 mm | Lộ rõ ở front, 3/4 và side |
| Left/right center symmetry | x-sum `0`; y diff `0.000015 mm`; z diff `0` | — | Symmetry ban đầu tốt |

`socket_proxy` là facial `Basis` vertices trong deterministic elliptical annulus quanh eye-bone center, giới hạn facial forward surface; đây là geometry proxy tái lập, không được mô tả như anatomical scan.

## 7. Eye geometry changes

- Eyeball scale đồng đều theo local lateral/forward/up: `0.78`.
- Eye center lùi `3.5 mm` theo hướng ngược eye-bone forward axis.
- Iris axis scale: lateral/up `0.76`, depth `0.75`; center đặt lại tại `0.91 × refined radius`.
- Pupil scale đồng đều `0.75`; center đặt lại tại `1.015 × refined radius`.
- Không apply armature transform, không đổi bone/rest pose, không đổi object transform convention.
- Rebuild companion blink coordinates từ refined `Basis`, retract `16 mm` ở full blink để tiếp tục occlude eye assembly.
- Mọi eye vertex vẫn có weight `1.0` tới đúng `eye.L/R` và Armature modifier `Human.rig`.

## 8. Eye measurements before and after

| Measurement | Before | After | Change | Status |
|---|---:|---:|---:|---|
| Eyeball diameter L/R | 24.600 mm | 19.188 mm | −22.00% | PASS |
| Protrusion proxy L/R | 11.053 mm | 4.847 mm | −56.15% | PASS |
| Iris diameter L/R | 12.400 mm | 9.424 mm | −24.00% | PASS |
| Pupil diameter L/R | 5.600 mm | 4.200 mm | −25.00% | PASS |
| Diameter symmetry | diff `0.000002 mm` | diff `<0.000002 mm` | preserved | PASS |
| Depth symmetry | equal | diff `0.000014 mm` | within numerical tolerance | PASS |

Agent visual inspection của actual renders: eyes không còn đọc như sphere gắn ngoài mặt; sclera/iris/pupil vẫn nhìn thấy; front, 3/4 và side đều cải thiện rõ. Side view cho thấy protrusion giảm đáng kể nhưng eye vẫn không biến mất sau lid.

## 9. Eye bone compatibility

- `NMM_Eyeball.L`, `NMM_Iris.L`, `NMM_Pupil.L`: fully weighted vào `eye.L`.
- Right equivalents: fully weighted vào `eye.R`.
- Five gaze directions render được: center, left, right, up, down.
- Left/right/both blink render được sau eye correction.
- Eye bones, parenting, modifiers và gaze angles giữ nguyên contract.
- Three.js gaze control và reset PASS trên refined GLB.

## 10. Eyebrow findings before correction

Eyebrow không phải separate geometry; visible movement nằm trong main `Human` head mesh. Mỗi target ảnh hưởng 198 vertices và left/right không overlap ngoài neutral support region.

| Target | Moved vertices | Max delta | Mean delta | Max at 0.5 |
|---|---:|---:|---:|---:|
| `NMM_BROW_RAISE_L` | 198 | 6.280 mm | 1.437 mm | 3.140 mm |
| `NMM_BROW_RAISE_R` | 198 | 6.280 mm | 1.437 mm | 3.140 mm |

Nhiều vertices có delta rất nhỏ nên full state khó đọc trên material trắng, đặc biệt khi eye geometry cũ chiếm visual attention.

## 11. Eyebrow Morph Target changes

- Giữ nguyên exact target names và exact affected-vertex set.
- Vertical delta nhân `2.0`.
- Thêm tối đa `2 mm` strength-weighted smooth lift theo căn bậc hai normalized original lift; vertices có original delta nhỏ nhận chuyển động đọc được hơn mà không tạo hard edge.
- Forward delta nhân `1.35` để giữ form brow ridge khi nâng.
- Không sửa `Basis`, eyelid blink, lips, MPFB Shape Keys hoặc eye objects từ brow targets.

Final metrics cho cả hai sides:

- Moved vertices: `198` (unchanged).
- Max delta: `14.463029 mm`.
- Mean delta: `3.658833 mm`.
- Max upward delta: `14.399886 mm`.
- Mean upward delta: `3.645639 mm`.

## 12. Interpolation results

| Target/value | 0.0 | 0.5 | 1.0 | Status |
|---|---:|---:|---:|---|
| `NMM_BROW_RAISE_L` max delta | 0 | 7.231515 mm | 14.463029 mm | PASS |
| `NMM_BROW_RAISE_R` max delta | 0 | 7.231515 mm | 14.463029 mm | PASS |
| Both together | neutral | visible bilateral half lift | clear bilateral full lift | PASS |

Evidence `04`–`06` dùng eye/brow crop với BEFORE/AFTER rows và 0.0/0.5/1.0 columns. Independent left/right movement và combined state đều đọc được, không thấy severe forehead distortion hoặc eye movement ngoài control.

## 13. Full facial regression results

| Control | Result | Status |
|---|---|---|
| Gaze center/left/right/up/down | Iris/pupil theo eye bones, không floating rõ | PASS |
| Blink left/right/both | Body lid + refined companion morph tiếp tục đóng | PASS |
| Brow left/right/both | Independent và combined; 0.5/1.0 readable | PASS |
| `NMM_LIPS_ROUND` | Non-zero target giữ nguyên và render được | PASS |
| `NMM_LIPS_SPREAD` | Non-zero target giữ nguyên và render được | PASS |
| Jaw | Bone `jaw` mở đúng; lip targets không repurpose | PASS |
| Head/neck | Controlled small rotations, root không xoay ngoài ý muốn | PASS |
| `TECH_HAND_FACE_TEST` | Hand/finger, eye, brow, jaw, head/neck và weights cùng tồn tại | PASS |

`facial-regression-demo.mp4` kết thúc bằng actual 45-frame `TECH_HAND_FACE_TEST`, làm chậm 4× để owner quan sát. Đây là technical fixture, không phải production sign-language gesture.

## 14. GLB export and validation

- Path: `assets/exports/technical/task-0007a/technical-facial-refined-test.glb`.
- Size: `2,455,392` bytes.
- SHA-256: `D59AE5422E9B759006FE9D666B6CA56AD1183D157DF666B33813FAE923A492AB`.
- Actual Blender 5.2.4 exporter; separate path, không overwrite TASK-0006 GLB.
- 9 meshes, 1 skin, six eye nodes, six core NMM targets, four named clips.
- Morph weights, hand channels, head/jaw/eye channels trong combined clip: PASS.
- Khronos Validator: `0 errors`, `0 warnings`, `1 info`, `0 hints` — PASS.
- Export-only macro mix/mask preprocessing không save ngược candidate.

## 15. Three.js regression results

Refined GLB được copy **tạm thời** vào generated web path `/models/technical/technical-facial-test.glb`, test bằng existing `/technical-facial-viewer`, sau đó `npm run sync:technical-assets` restore original web asset.

| Check | Status |
|---|---|
| Canvas/actual GLB ready | PASS |
| Six actual Morph Target names | PASS |
| Four clip inventory | PASS |
| Pause/replay/progress/loop/0.5× | PASS |
| Morph slider actual value | PASS |
| Gaze control | PASS |
| Face/full camera | PASS |
| Reset all | PASS |

Swap evidence:

- Original/refreshed web GLB hash: `615CCB9697B51CC4938C98556D0292950DFD4A05D9334D2BE5E8140070EFB68D`.
- Temporary refined test hash: `D59AE5422E9B759006FE9D666B6CA56AD1183D157DF666B33813FAE923A492AB`.
- Restored web hash equals original: PASS.

## 16. Generated image inventory

Required comparisons in `docs/reports/artifacts/TASK-0007A/visual-review/`:

1. `01-eye-front-before-after.png`
2. `02-eye-three-quarter-before-after.png`
3. `03-eye-side-before-after.png`
4. `04-brow-left-before-after.png`
5. `05-brow-right-before-after.png`
6. `06-brow-both-before-after.png`
7. `07-eye-gaze-regression.png`
8. `08-eye-blink-regression.png`
9. `09-full-face-neutral-before-after.png`
10. `facial-refinement-contact-sheet.png`

Raw reproducible renders: `visual-review/raw/before/` và `visual-review/raw/after/`. Temporary combined frame sequence đã xóa sau successful encode.

Additional browser evidence:

- `visual-review/gallery-browser.png`.
- `docs/reports/artifacts/TASK-0007A/threejs-refined-face.png`.
- `docs/reports/artifacts/TASK-0007A/threejs-refined-full.png`.

## 17. Generated video inventory

| File | Duration | Codec/resolution/FPS | SHA-256 | Status |
|---|---:|---|---|---|
| `eye-refinement-demo.mp4` | 12.867 s | H.264 / 1920×1080 / 30 | `5F4BF8D256A732E61CBB2D1D43ADBE6929E2A3077299075D05677CD055DD03DA` | PASS |
| `eyebrow-refinement-demo.mp4` | 12.367 s | H.264 / 1920×1080 / 30 | `1EFF8407D4259D01668F97DB24DE8DDE7DCCD0ED22F42BCAA8361C9497F97E66` | PASS |
| `facial-regression-demo.mp4` | 15.133 s | H.264 / 1920×1080 / 30 | `330803201605839C7A17C08EC6DF9E43F4F10BE509B44ADA1D914500CAB1FC0B` | PASS |

## 18. Visual quality assessment

| Feature | Before | After | Status |
|---|---|---|---|
| Eye size | 24.6 mm sphere dominates face | 19.188 mm, integrated within lid aperture | PASS |
| Eye depth | 11.053 mm protrusion proxy | 4.847 mm; side silhouette greatly reduced | PASS |
| Eye socket fit | Reads as external sphere | Sclera edge largely contained by upper/lower lids | PASS |
| Eye symmetry | Numerically symmetric | Preserved within `<0.00002 mm` depth difference | PASS |
| Gaze | Functional but oversized assembly | Five directions remain visible without detached iris/pupil | PASS |
| Blink | Functional companion morph | Left/right/both still close after resize/recess | PASS |
| Left eyebrow | Full movement difficult to see | 0.5 and 1.0 visible; correct side independent | PASS |
| Right eyebrow | Full movement difficult to see | 0.5 and 1.0 visible; correct side independent | PASS |
| Combined eyebrows | Weak bilateral ridge change | Bilateral half/full lift readable, smooth | PASS |

Layered decision:

- Structural correctness: **PASS**.
- Functional animation: **PASS**.
- Agent visual quality assessment: **PASS for technical prototype**.
- Owner acceptance: **NOT YET TESTED**.
- Linguistic validity: **NOT YET TESTED**.

## 19. Known limitations

- Base mesh không có separate textured eyebrow geometry; readability dựa trên brow/forehead surface deformation và studio shadow.
- Blink vẫn dùng companion eye morph vì eyelid topology hiện tại không đủ cho production lid wrap.
- White prototype skin/material làm subtle facial form khó đọc hơn realistic shaded character.
- Socket proxy là deterministic mesh-surface measurement, không phải anatomical measurement.
- NLA exporter vẫn có warning source >4 influences và normalize top four theo baseline; Khronos output sạch.
- Candidate chưa có owner subjective approval và chưa có qualified VSL/NMM linguistic review.

## 20. Failed/resolved checks

- First refinement run: `reference_key` lấy sai từ `key_blocks`: **FAIL, resolved** trước save; source không đổi.
- First after-inspection: bounds đọc mesh base thay vì eye `Basis`: **FAIL, resolved**; invalid measurements không dùng làm PASS.
- First video assembly: FFmpeg `drawbox` dùng `W/H` thay vì `iw/ih`: **FAIL, resolved** bằng assemble-only; không render giả.
- First brow visual pass: 0.5 còn quá subtle: **FAIL visual, resolved** bằng strength-weighted lift trên cùng 198 vertices và rerender toàn bộ AFTER evidence.

## 21. Actual commands executed

```text
git status --short --branch
git log / git rev-parse / git switch -c feat/task-0007a-facial-refinement 191df0c...
Get-FileHash -Algorithm SHA256 <canonical> <TASK-0006-candidate> <TASK-0007-review-scene>
npm run doctor
blender.exe --background <TASK-0006-candidate> --python blender/scripts/inspect_facial_geometry.py -- --report <before.json>
blender.exe --background <TASK-0006-candidate> --python blender/scripts/refine_facial_candidate.py -- ...
blender.exe --background <refined-candidate> --python blender/scripts/inspect_facial_geometry.py -- --report <after.json>
blender.exe --background <refined-candidate> --python blender/scripts/validate_refined_facial_candidate.py -- ...
blender.exe --background <before/refined> --python blender/scripts/generate_facial_refinement_review.py -- --variant before|after ...
blender.exe --background <refined> --python blender/scripts/generate_facial_refinement_review.py -- --assemble-only ...
blender.exe --background <refined> --python blender/scripts/export_refined_facial_glb.py -- ...
node tools/validate-facial-asset.mjs --asset assets/exports/technical/task-0007a/technical-facial-refined-test.glb --report ...
Copy-Item <refined-glb> apps/web/public/models/technical/technical-facial-test.glb   # temporary test swap
npm run dev -- --host 127.0.0.1 --port 4173
node tools/test-facial-viewer.mjs --report <TASK-0007A-report> --face-screenshot ... --full-screenshot ...
npm run sync:technical-assets
npm run sync:technical-assets:check
npm run check
npm run build
chrome.exe --headless=new --allow-file-access-from-files --screenshot=<gallery-browser.png> <index.html>
ffmpeg midpoint frame extraction for three final videos
```

## 22. Test matrix

| Check | Evidence | Status |
|---|---|---|
| Blender 5.2.4 / MPFB 2.0.18 | Blender logs | PASS |
| Canonical/TASK-0006/TASK-0007 preservation | before/after SHA-256 + no TASK-0007 diff | PASS |
| Separate rc.3 candidate | candidate + manifest | PASS |
| 137 bones/hierarchy/armature transform | candidate validation | PASS |
| Neutral body + non-brow Shape Keys preserved | creation report | PASS |
| Measured eye diameter/depth improvement | before/after inspection JSON | PASS |
| Eye binding/symmetry/blink targets | candidate validation | PASS |
| Brow 0.0/0.5/1.0 interpolation | metrics + images 04–06 | PASS |
| Gaze/blink/lips/jaw/head/neck | regression renders/video | PASS |
| Combined hand + face | actual 45 frames/video + action channels | PASS |
| Refined GLB export | `glb-export.json` | PASS |
| GLB/Khronos validation | `glb-validation.json` | PASS |
| Three.js refined GLB runtime | `threejs-regression.json` | PASS |
| Existing web asset restored | swap hash evidence + sync check | PASS |
| `npm run check` | typecheck/lint/tests/build/validators | PASS |
| Explicit `npm run build` | Vite production build | PASS |
| Lesson GLBs S001–S006 | project validator reports pending | NOT YET TESTED |
| Owner visual acceptance | checklist chưa được owner tick | NOT YET TESTED |
| Linguistic/content approval | qualified reviewer chưa review | NOT YET TESTED |

## 23. Generated files

- Blender scripts:
  - `inspect_facial_geometry.py`
  - `refine_facial_candidate.py`
  - `validate_refined_facial_candidate.py`
  - `generate_facial_refinement_review.py`
  - `export_refined_facial_glb.py`
- Candidate:
  - `blender/working/huy-anh/task-0007a-facial-refinement/avatar_master_facial_refined_candidate.blend`
  - `avatar_master_facial_refined_candidate.manifest.json`
- GLB: `assets/exports/technical/task-0007a/technical-facial-refined-test.glb`.
- Reports/evidence: `docs/reports/artifacts/TASK-0007A/`.
- Owner gallery: `docs/reports/artifacts/TASK-0007A/visual-review/index.html`.
- Task report: `docs/reports/TASK-0007A-facial-refinement.md`.

## 24. Git branch and final commit hash

- Branch: `feat/task-0007a-facial-refinement`.
- Base: `191df0c4423a3a79eaac014a97881b74519262bd`.
- Final local commit: commit chứa report này; exact hash được ghi trong final response sau khi report được commit.
- Merge/push: không thực hiện.

## 25. Owner acceptance checklist

- [ ] Mở `visual-review/index.html` và phát được cả ba video.
- [ ] Xác nhận front eye size/depth tự nhiên hơn.
- [ ] Xác nhận three-quarter/side không còn excessive protrusion.
- [ ] Xác nhận iris/pupil đủ rõ, không floating/clipping nghiêm trọng ở five gaze directions.
- [ ] Xác nhận left/right/both blink acceptable với companion-morph limitation.
- [ ] Xác nhận left brow 0.5/1.0 đủ đọc.
- [ ] Xác nhận right brow 0.5/1.0 đủ đọc.
- [ ] Xác nhận both brows không excessive/severe forehead distortion.
- [ ] Xác nhận lips/jaw/head/neck và hand + face regression acceptable.
- [ ] Xác nhận candidate chỉ là technical prototype, không phải VSL đã xác minh.
- [ ] Quyết định có cho phép promotion riêng thành temporary Master Avatar v1 hay yêu cầu thêm correction.

Owner acceptance hiện tại: **NOT YET TESTED**.

## 26. Recommendation for TASK-0008

Nếu owner chấp nhận rc.3: TASK-0008 nên là promotion/release-readiness task riêng, không tiếp tục sculpt ngầm. Task đó cần đóng băng candidate hash, tạo promotion manifest/changelog, cập nhật web asset mapping có kiểm soát, chạy full regression và giữ linguistic gate tách biệt. Nếu owner chưa chấp nhận, chỉ sửa đúng issue owner ghi trên comparison package rồi rerun cùng metrics.

Không tự động bắt đầu TASK-0008.
