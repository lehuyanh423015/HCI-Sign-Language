# TASK-0004 — Neutral Educational Avatar Sanitization and Handoff Readiness

- Ngày/Timezone: 2026-11-17, Asia/Saigon
- Branch: `feat/task-0004-neutral-avatar`
- Base commit: `8da36ac`
- Scope: neutralize presentation, preserve rig/action, export neutral GLB, browser smoke test, prepare master candidate và handoff
- Overall status: **PASS kỹ thuật; owner approval là NOT YET TESTED**

## 1. Task summary và mục tiêu

Đã tạo avatar giáo dục trung tính từ working source TASK-0003 mà không ghi đè master/source cũ. Avatar dùng áo ngắn tay teal, shorts slate và body material matte trung tính; không texture, không chi tiết thời trang, không tạo nội dung ký hiệu thật. Hands, wrists, forearms và elbows vẫn lộ rõ. Neutral GLB đã thay baseline GLB làm asset mặc định của technical viewer nhưng vẫn mang banner `TECHNICAL TEST - NOT VERIFIED SIGN LANGUAGE` và không thuộc S001–S006.

## 2. Initial repository status

- HEAD ban đầu: `8da36ac` trên `feat/task-0003-3d-prototype`.
- User-owned change ở cuối `README.md` tồn tại trước task và được giữ ngoài TASK-0004 commit.
- Nhánh mới: `feat/task-0004-neutral-avatar`.
- Không reset, clean, merge hoặc push.

## 3. Sources và SHA-256 preservation

| File | Before | After | Status |
|---|---|---|---|
| `blender/avatar_master.blend` | `E15142798E8C573AA80243DE6D6F24B48CC517BBC5DD410DC1262AD1432480FA` | `E15142798E8C573AA80243DE6D6F24B48CC517BBC5DD410DC1262AD1432480FA` | PASS — unchanged |
| `blender/working/huy-anh/technical-hand-test.blend` | `1FD50D320ECD212DDC17E26CC680CAD92210FBEC537E8A39CD8D10C70D801B25` | `1FD50D320ECD212DDC17E26CC680CAD92210FBEC537E8A39CD8D10C70D801B25` | PASS — unchanged |

Outputs:

- Working neutral: `blender/working/huy-anh/technical-hand-test-neutral.blend`, SHA-256 `2D420B554F13555653D920100042A91F2575302D0EDB08696F8B5C392F50374F`.
- Master candidate: `blender/master/avatar_master_neutral_candidate.blend`, cùng SHA-256 `2D420B554F13555653D920100042A91F2575302D0EDB08696F8B5C392F50374F`.

Candidate chưa được promote thành official master; cần owner review commit/hash này trước khi Huy Anh/Mien dùng cho production.

## 4. Neutralization strategy và thay đổi model

Chọn Option 1: procedural low-detail garment shells, không sửa topology/rest pose của `Human`.

- `EDU_NeutralTop`: 224 vertices, 144 polygons; torso shell + hai short sleeves; toàn bộ vertices có transferred body weights; `Armature` modifier trỏ `Human.rig`.
- `EDU_NeutralShorts`: 232 vertices, 130 polygons; hip shell + hai leg tubes + front/back modesty panels; toàn bộ vertices có transferred body weights.
- `EDU_Skin_Neutral`: body material matte neutral.
- `EDU_Top_Teal`, `EDU_Shorts_Slate`: neutral, rough, non-metallic materials.
- Textures: không có; không procedural shader phụ thuộc Blender.
- Sensitive anatomy được che bởi lower shell/panels; upper torso được che bởi top. Hands, wrists, forearms, elbows và lower legs không bị che.

Lần thử đầu cắt trực tiếp body polygons tạo mép răng cưa và lower silhouette không đạt — **FAIL visual**, đã bỏ và thay bằng procedural shells. Final Blender/browser evidence không dùng bản thử này.

## 5. Rig và animation compatibility

- 137-bone hierarchy giữ nguyên; armature object transform giữ nguyên trong `.blend`.
- Body, top và shorts đều bind đúng `Human.rig`.
- Reload validation: 13/13 automated checks — **PASS**.
- Controlled test trên neutral source: thumb/index/middle/ring/little/wrist/forearm 7/7 — **PASS**; mỗi test có localized evaluated mesh delta, object/root transform ổn định và exact reset.
- `TECH_HAND_CONTROL_TEST`: Action Slot/assignment giữ nguyên; 45 F-curves, 135 keyframe points, frame 1/15/30, 15 right-finger bones, 30 FPS — **PASS**.
- Frame 1 → 30 body evaluated delta: 1,506 vertices, max `0.122995 m`; không key unrelated bones.
- Blender full/hand previews frame 1/15/30 đã render và agent inspection không thấy clipping nghiêm trọng ở tay hoặc garment trong test action. Owner visual sign-off vẫn **NOT YET TESTED**.

## 6. Export correction và GLB details

Canonical GLB: `assets/exports/technical/technical-hand-test-neutral.glb`.

- Size: 992,780 bytes.
- SHA-256: `E54DEB2F58B84FEB0C957562E48DA4DD772E71D3950451A52B1B22CBFB245FF0`.
- glTF 2.0; 140 nodes, 3 meshes, 1 shared skin, 3 materials, 0 textures.
- Clip exact `TECH_HAND_CONTROL_TEST`, 1.0000 s, 15 channels/samplers, expected finger targets only.
- Khronos validator: 0 errors, 0 warnings, 1 informational `UNUSED_OBJECT` cho unused UV attribute — **PASS**.

MPFB-specific export fix:

1. Body có 10 nonzero shape-key values; current mix được bake trên export-only process, world mesh delta trước/sau bằng 0. `.blend` vẫn giữ shape keys.
2. `Human` có `Hide helpers` MASK modifier: raw 19,158 vertices, evaluated visible body 13,380 vertices. Export ban đầu không apply modifier nên helper anatomy xuất hiện trong GLB — **visual FAIL dù structural PASS**.
3. Final export dùng `export_apply=True` để apply non-Armature modifiers, giữ skin; giới hạn 4 influences/vertex cho Three.js; `export_armature_object_remove=True`; không export morph targets.
4. Re-import final GLB vào clean Blender scene ở frame 1/15 cho hình dạng đúng — **PASS**.

## 7. Three.js viewer và HTTP results

- Viewer mặc định dùng deterministic path `/models/technical/technical-hand-test-neutral.glb`.
- Camera full/hand presets suy ra front/up từ skeleton (`shoulder01.L/R`, `head`, `pelvis`) thay vì giả định cố định.
- Chrome headless/CDP: GLB+canvas ready, animation progression, pause, resume, replay, loop, speed và camera controls 8/8 — **PASS**, 0 runtime exceptions.
- Browser full screenshot chụp ở neutral time `0.00s` cho avatar covered, normal face/body/limbs; close-up cho right hand animation readable.
- HTTP: page 200; GLB 200, `model/gltf-binary`, 992,780 bytes; downloaded hash khớp canonical — **PASS**.
- Windows computer-use helper được retry đúng recovery protocol nhưng dừng với `windows sandbox failed: helper_unknown_error: setup refresh had errors` — **SKIPPED**. CDP fallback cung cấp runtime evidence thực tế.

## 8. Test matrix

| Check | Actual result | Status |
|---|---|---|
| Original master/source hashes | Cả hai unchanged | PASS |
| Neutral creation checks | 7/7 | PASS |
| Neutral reload/binding/coverage | 13/13 | PASS |
| Controlled rig movement | 7/7 | PASS |
| TECH action compatibility | 45 curves, 135 keys, 15 bones | PASS |
| Blender source previews | Full + hand, frames 1/15/30 | PASS (agent visual) |
| Initial polygon-cut garment | Ragged/unsuitable; discarded | FAIL (resolved) |
| Initial neutral GLB visual | MPFB helpers leaked because MASK was not applied | FAIL (resolved) |
| Final GLB structure/animation | 3 meshes, 1 skin, 1.0000 s | PASS |
| Khronos validator | 0 errors, 0 warnings | PASS |
| Final GLB re-import frame 1/15 | Visible body/garments correct | PASS |
| Browser runtime | 8/8, 0 exceptions | PASS |
| HTTP bytes/hash | 200, exact hash match | PASS |
| `npm run check` | typecheck/lint/tests/build/data/assets | PASS |
| Vite bundle warning | Main JS >500 kB | PASS WITH WARNING |
| Windows computer-use helper | Helper init failed after retry | SKIPPED |
| Owner educational/visual approval | Chưa có owner sign-off | NOT YET TESTED |

Một CLI attempt dùng `test_rig_controls.py --report` thất bại vì script yêu cầu `--output`; chạy lại với đúng argument đã PASS 7/7. Không coi lần thất bại là test PASS.

## 9. Evidence

- `docs/reports/artifacts/TASK-0004-neutral-avatar-creation.json`
- `docs/reports/artifacts/TASK-0004-neutral-avatar-validation.json`
- `docs/reports/artifacts/TASK-0004-rig-compatibility.json`
- `docs/reports/artifacts/TASK-0004-neutral-glb-export.json`
- `docs/reports/artifacts/TASK-0004-neutral-glb-validation.json`
- `docs/reports/artifacts/TASK-0004-browser-runtime.json`
- `docs/reports/artifacts/TASK-0004-browser-full.png`
- `docs/reports/artifacts/TASK-0004-browser-runtime.png`
- `docs/reports/artifacts/task-0004-previews/before-neutralization-full-frame-001.png`
- `docs/reports/artifacts/task-0004-previews/neutral-avatar-full-frame-{001,015,030}.png`
- `docs/reports/artifacts/task-0004-previews/neutral-avatar-hand-frame-{001,015,030}.png`
- `docs/reports/artifacts/task-0004-previews/neutral-glb-reimport-frame-{001,015}.png`

`neutral-glb-raw-mesh-frame-001.png` là diagnostic cho MPFB hidden helpers, không phải final acceptance preview.

## 10. Files created/modified

- Blender: neutral creation/validation/re-import scripts, export script improvements, working source và master candidate.
- Assets: neutral canonical GLB và technical export README.
- Web: neutral asset path, skeleton-derived camera, page copy/test.
- Tooling: parameterized validator, two-file sync, enhanced browser screenshots, package scripts/check gate.
- Docs: asset contract, Blender setup, handoff, TASK-0004 report và evidence.
- User-owned `README.md` line không thuộc task commit.

## 11. Commands actually executed

```text
git switch -c feat/task-0004-neutral-avatar
Get-FileHash blender\avatar_master.blend -Algorithm SHA256
Get-FileHash blender\working\huy-anh\technical-hand-test.blend -Algorithm SHA256
blender.exe --background blender\working\huy-anh\technical-hand-test.blend --python blender\scripts\create_neutral_avatar.py -- ...
blender.exe --background blender\working\huy-anh\technical-hand-test-neutral.blend --python blender\scripts\validate_neutral_avatar.py -- ...
blender.exe --background blender\working\huy-anh\technical-hand-test-neutral.blend --python blender\scripts\test_rig_controls.py -- --output ...
blender.exe --background blender\working\huy-anh\technical-hand-test-neutral.blend --python blender\scripts\export_technical_glb.py -- --no-morphs --bake-shape-key-mix --apply-non-armature-modifiers --remove-armature-object ...
blender.exe --background --python blender\scripts\render_glb_preview.py -- --input assets\exports\technical\technical-hand-test-neutral.glb ...
npm run sync:technical-assets
npm run validate:neutral-asset
npm run check
npm run test:neutral-viewer
Invoke-WebRequest http://127.0.0.1:4173/technical-viewer
Invoke-WebRequest http://127.0.0.1:4173/models/technical/technical-hand-test-neutral.glb
```

## 12. Git information và handoff recommendation

- Branch: `feat/task-0004-neutral-avatar`.
- Base: `8da36ac`.
- Final commit hash không thể tự ghi vào chính report trong cùng commit; actual hash sẽ được nêu trong final Agent response.
- Không push/merge.

**Recommendation:** source đủ điều kiện làm recommended shared-base candidate về mặt kỹ thuật. Chưa gọi là approved official master cho tới khi owner hoàn tất checklist dưới đây. Sau approval, Huy Anh ghi candidate commit/hash vào handoff; Mien tạo working copies riêng; Nhat chỉ consume canonical GLB/sync command; Thao tiếp tục giữ fixture ngoài approved learning catalog.

## 13. Remaining issues và owner manual acceptance checklist

Known limitations:

- Garment là low-detail functional prototype, không phải production clothing; sleeve/shorts fit cần owner xem ở nhiều góc.
- Shape keys vẫn có trong `.blend` nhưng final technical GLB bake current mix và không mang morph targets. Facial production cần task riêng.
- Vite bundle vẫn có warning >500 kB.
- Git LFS remote upload/quota vẫn chưa kiểm chứng.

Owner checklist:

- [ ] Avatar không còn lộ sensitive body parts ở front/side/back.
- [ ] Presentation đủ neutral và phù hợp giáo dục.
- [ ] Hands, wrists, forearms, elbows và shoulders rõ ràng.
- [ ] Scrub `TECH_HAND_CONTROL_TEST` frame 1/15/30 trong Blender; không clipping/deformation lớn.
- [ ] Mở technical viewer, thử full/hand camera, rotate/zoom và mọi playback control.
- [ ] Xem browser full/close-up và GLB re-import previews; xác nhận không còn MPFB helper geometry.
- [ ] Chấp thuận `avatar_master_neutral_candidate.blend` và commit/hash cụ thể trước handoff production.

Không tự động bắt đầu task tiếp theo.
