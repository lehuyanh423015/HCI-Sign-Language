# TASK-0005 — Master Model Stabilization & Facial Capability Audit

- Ngày/Timezone: 2026-11-17, Asia/Saigon
- Branch/base commit: `feat/task-0005-master-stabilization` / `84837d050f3f874452228cf457d5a2d174748efd`
- Scope: promote neutral candidate, stabilize canonical rig, audit facial capability, prove Morph Target GLB transport, standardize ownership/export
- Overall status: **PASS technical foundation; production facial/NMM capability NOT YET TESTED**

## Executive summary

Neutral avatar đã được formalize thành `Master Avatar v1.0.0-rc.1` tại `blender/master/avatar_master.blend`. Canonical được tạo từ đúng blob candidate đã commit trong TASK-0004, không từ binary working đang có user change. Technical action được loại khỏi canonical copy, pose reset neutral, scene đặt 30 FPS/frame 1; geometry, Shape Key values, 137-bone hierarchy và known armature object rotation được giữ.

Rig ổn định về cấu trúc/binding và phù hợp làm shared-base candidate cho temporary final release. Facial audit tìm thấy head/neck/jaw/eye cùng facial deform bones có weights, nhưng không có production facial Shape Keys, dedicated control rig, visible eyeball/pupil asset hoặc NMM poses được duyệt. Morph Target transport đã được chứng minh bằng disposable diagnostic mesh trong cùng GLB với `TECH_HAND_CONTROL_TEST`; diagnostic target không tồn tại trong master.

## Initial repository status

- HEAD ban đầu: `84837d050f3f874452228cf457d5a2d174748efd` trên `feat/task-0004-neutral-avatar`; history chứa TASK-0001–0004 và chưa merge vào `main` (`origin/main` ở `dc22261`).
- Tạo branch: `feat/task-0005-master-stabilization`; không merge/push/reset/clean.
- User-owned changes có trước task:
  - `README.md`, giữ ngoài staging/commit.
  - `blender/master/avatar_master_neutral_candidate.blend`, working hash `BC2F154580DD97C2043812E867387054E1F9DE63DD6A61F8DB36E4FB868F49BE`, giữ nguyên và không dùng làm promotion input.
- Approved TASK-0004 blob lấy từ commit `5996ee48637d3d6daa3b7c43c4fc5319a0153e8a`, path `blender/master/avatar_master_neutral_candidate.blend`, SHA-256 `2D420B554F13555653D920100042A91F2575302D0EDB08696F8B5C392F50374F`.

## Environment and dependencies

| Component | Actual | Status |
|---|---|---|
| OS | Windows_NT 10.0.26300 x64 | PASS |
| Blender | 5.2.4 LTS, build `cd5dc428cce1` | PASS |
| Blender Python | 3.13.13 embedded | PASS |
| MPFB | 2.0.18, enabled/runtime initialized | PASS |
| Node.js | v24.14.1 | PASS |
| npm | 11.12.1 | PASS |
| `npm run doctor` | 0 required failures, 0 environment mismatches | PASS |

Evidence: `docs/reports/artifacts/TASK-0005-environment.json`.

## Master promotion details

| Asset | Role | SHA-256 after task | Preservation/status |
|---|---|---|---|
| `blender/avatar_master.blend` | Pre-neutral legacy source | `E15142798E8C573AA80243DE6D6F24B48CC517BBC5DD410DC1262AD1432480FA` | PASS — unchanged |
| committed neutral candidate blob | Approved promotion source | `2D420B554F13555653D920100042A91F2575302D0EDB08696F8B5C392F50374F` | PASS — extracted read-only from Git |
| working neutral candidate | User-owned working file | `BC2F154580DD97C2043812E867387054E1F9DE63DD6A61F8DB36E4FB868F49BE` | PASS — untouched/uncommitted |
| `blender/working/huy-anh/technical-hand-test.blend` | TASK-0003 technical source | `1FD50D320ECD212DDC17E26CC680CAD92210FBEC537E8A39CD8D10C70D801B25` | PASS — unchanged |
| `blender/working/huy-anh/technical-hand-test-neutral.blend` | Neutral technical source | `2D420B554F13555653D920100042A91F2575302D0EDB08696F8B5C392F50374F` | PASS — unchanged |
| `blender/master/avatar_master.blend` | Official canonical master RC | `A018FA9BC5129E91A320B2A1BB397D87781B757615F1CD2A7FE568945E010232` | PASS |

Promotion changes only on new canonical copy:

- unassign/remove `TECH_HAND_CONTROL_TEST` and clear animation data;
- reset all `pose_bone.matrix_basis` to identity;
- set 30 FPS, frame range 1–1;
- add scene metadata `master_avatar_version=1.0.0-rc.1`;
- retain mesh data, Shape Keys/values, materials, bindings, rest hierarchy and armature object rotation.

Canonical re-open/audit by Blender 5.2.4: PASS. Manifest: `blender/master/avatar_master.manifest.json`.

## Rig integrity and bone inventory

- `Human.rig`: 137 bones, all `use_deform=true`; full name/parent/deform rows match TASK-0002 exactly.
- Hierarchy SHA-256: `5D6A61F33BE4EDBF08D06F0E9D85F5C118924254A2C0F1E5F7776F110F033BCE`.
- Five finger chains × three bones on both hands: PASS; wrist/finger controlled capability remains backed by TASK-0003/0004 evidence.
- `Human`, `EDU_NeutralTop`, `EDU_NeutralShorts`: parent and Armature modifier target `Human.rig`; all vertices carry at least one group membership — PASS.
- Canonical has no Action/NLA sign and neutral pose basis is identity — PASS.
- Full inventory: `docs/reports/artifacts/TASK-0005-bone-inventory.json`.

Generic `inspect_rig.py` intentionally reports `armature_object_transforms: FAIL` because Euler rotation is non-identity: `(-0.0550454631, 0.0029658440, -0.2448638231)`. TASK-0005 did not apply it. Dedicated audit confirms exact transform retained, hierarchy unchanged, static/animated exports valid, and prior Three.js pipeline compatible — policy is retain/do not blindly apply. A correction, if ever needed, requires separate world-space comparison/ADR.

## Facial topology findings

- `Human`: 19,158 raw vertices, 18,486 raw polygons, 154 raw connected components; largest visible/body component has 13,380 vertices. Head-region heuristic finds 3,334 raw vertices above the `neck03` threshold.
- Eyes and eyebrows are not separate Blender mesh objects. Facial deformation relies on integrated/disconnected geometry inside `Human` and bone weights.
- Close-up static GLB shows eyelid/mouth/nose surface geometry, but no visible eyeball/pupil asset appropriate for production eye direction.
- `jaw` has 911 weighted vertices; endpoint groups for `oris`, `oculi`, `orbicularis`, `levator`, `risorius` contain real weights. 28 of 50 audited head/neck/facial-name bones are direct weighted endpoints; intermediary bones also affect descendants.
- Geometry density and weights permit structural deformation, but current evidence does not prove clean production blink, eyebrow, viseme, cheek or extreme jaw poses. Loop quality/clipping across expressions remains NOT YET TESTED.

Agent visual inspection of `master-static-full.png` and `master-static-face.png`: exported neutral shape/clothing are present; facial surface is readable; eyes remain visually incomplete for gaze animation. Owner post-promotion visual sign-off is NOT YET TESTED.

## Existing Shape Key inventory

All keys belong to `Human`; slider range is 0–1. No key name contains facial semantics and none is accepted as a facial expression. Values were not changed in canonical.

| Shape Key | Current value | Moved vertices | Max delta (m) | Visible geometry delta | Facial suitability |
|---|---:|---:|---:|---|---|
| `Basis` | 1.0 | 0 | 0 | No | NO |
| `$md-$as-$fe-$yn` | 0.1650000066 | 19,150 | 0.1745699416 | Yes | NO |
| `$md-$as-$ma-$yn` | 0.1650000066 | 19,150 | 0.1140678384 | Yes | NO |
| `$md-$ca-$fe-$yn` | 0.1650000066 | 19,150 | 0.0955510456 | Yes | NO |
| `$md-$ca-$ma-$yn` | 0.1650000066 | 19,150 | 0.1328135736 | Yes | NO |
| `$md-$af-$fe-$yn` | 0.1650000066 | 19,158 | 0.0926483154 | Yes | NO |
| `$md-$af-$ma-$yn` | 0.1650000066 | 19,150 | 0.1900165058 | Yes | NO |
| `$md-universal-$fe-$yn-$av$mu-$av$wg` | 0.5 | 0 | 0 | No | NO |
| `$md-universal-$ma-$yn-$av$mu-$av$wg` | 0.5 | 0 | 0 | No | NO |
| `$md-$fe-$yn-$av$mu-$av$wg-$avcup-max$fi` | 0.0885665789 | 280 | 0.0081817372 | Yes | NO |
| `$md-$fe-$yn-$av$mu-$av$wg-maxcup-$av$fi` | 0.0884665772 | 700 | 0.0924307866 | Yes | NO |

Detailed per-key min/max/value/delta: `TASK-0005-master-facial-audit.json`.

## Facial bone inventory and controlled readiness

50 names match head/neck/facial semantics, including `head`, `neck01/02/03`, `jaw`, `eye.L/R`, `oculi*`, `orbicularis*`, `oris*`, `levator*`, `risorius*`, `temporalis*` and `special*`. Đây là deform rig trực tiếp, không có dedicated facial control bones/custom shapes/constraints.

| Bone test | Parent | Moved vertices | Max delta | Result |
|---|---|---:|---:|---|
| `head` | `neck03` | 4,451 | 0.015115 m | PASS |
| `neck02` | `neck01` | 4,494 | 0.021852 m | PASS |
| `jaw` | `head` | 1,029 | 0.009706 m | PASS structural |
| `eye.L` | `special05.L` | 40 | 0.000157 m | PASS structural |
| `eye.R` | `special05.R` | 40 | 0.000157 m | PASS structural |

Mỗi test rotate 6° trên copy tạm, chỉ author đúng pose bone, giữ object/root transform và reset mesh/pose chính xác. `PASS structural` không đồng nghĩa animation đẹp/anatomically correct.

## Facial capability matrix

| Feature | Existing support | Recommended method | Priority |
|---|---|---|---|
| Eyebrow raise | Không có brow Shape Key/control rõ ràng; nearby facial bones có nhưng pose quality chưa test | Shape Keys | High |
| Eye blink | Không blink Shape Key; `oculi/orbicularis` weighted bones tồn tại, chưa author/approve blink | Shape Keys | High |
| Eye direction | `eye.L/R` có weights và structural test PASS; thiếu visible eyeball/pupil asset | Eye bones + eye asset | High |
| Mouth open | `jaw` có weights và structural test PASS; articulation quality chưa test | Jaw bone + corrective Shape Keys | High |
| Lip shape | Nhiều `oris` endpoints có weights; không phoneme/viseme keys | Shape Keys | High |
| Cheek movement | `risorius/levator/temporalis` có weights; không expression đã duyệt | Shape Keys + existing deform bones | Medium |
| Head rotation | `head` test PASS | Existing head bone | High |
| Neck movement | `neck01/02/03`, `neck02` test PASS | Existing neck bones | High |
| Upper-body posture | Existing spine/clavicle/arm rig và prior controlled hand/arm tests | Existing rig | Medium |

## Morph Target proof of concept

Vì không có usable facial Shape Key, POC tạo `TASK0005_MorphProbe` disposable trên bản sao tạm, Shape Key `TASK0005_DIAGNOSTIC_MORPH` với keys frame 1/15/30. Master và technical sources không được save.

`docs/reports/artifacts/TASK-0005-morph-poc.glb`:

- 4 meshes, 1 skin, 1 Morph Target;
- animations: `TECH_HAND_CONTROL_TEST` và `TASK0005_DIAGNOSTIC_MORPH`;
- 1 `weights` channel target `TASK0005_MorphProbe`;
- 15 bone rotation channels;
- Khronos: 0 errors, 0 warnings, 1 informational unused UV;
- SHA-256 `B95096ED5BA8E3426FDF38B37B0F9220EE2F22B3112A8760253CD35E211203D8`.

Kết luận: static Morph Targets, animated weights và concurrent bone animation transport đều **PASS** trong Blender 5.2.4 → GLB. Production facial target design, naming, deformation quality và Three.js facial UI/runtime vẫn NOT YET TESTED.

## Export profiles

### `MASTER_STATIC`

- Purpose: neutral preview/reference, không sign/technical animation.
- Export-only shape mix bake; `Hide helpers` được apply; top four influences; skin/material giữ lại.
- Exact options verified: `export_format="GLB"`, `use_selection=True`, `export_animations=False`, `export_skins=True`, `export_armature_object_remove=True`, `export_rest_position_armature=True`, `export_apply=True`, `export_all_influences=False`, `export_morph=False`, cameras/lights off, Y-up.
- Output: `assets/exports/master/avatar-master-v1-rc1.glb`, 987,060 bytes, SHA-256 `85F94946A488944E9B568116D27D9A2B661255B4185B4DBC66789C4F6AE639FC`.
- Structure: 3 meshes, 3 primitives, 1 skin, 3 materials, 0 animations, 0 Morph Targets; Khronos 0 errors/warnings.

### `ANIMATION_WITH_MORPHS`

- Thêm `export_animations=True`, `export_animation_mode="ACTIONS"`, `export_merge_animation="ACTION"`, frame range on, force sampling off, `export_morph=True`, morph normals on, morph tangents off.
- POC demonstrates transport only. Production source must use approved facial targets and exact sign clip names; diagnostic objects/actions are forbidden.
- Existing `TECH_HAND_CONTROL_TEST` workflow remains valid and `npm run check` continues validating TASK-0003/0004 assets.

Installed Blender 5.2.4 exporter property inventory and exact used settings are preserved in both export JSON reports.

## Implemented/generated files

- Canonical/versioning: `blender/master/avatar_master.blend`, `avatar_master.manifest.json`, master README.
- Blender automation: `stabilize_master.py`, `audit_master_avatar.py`, `export_master_profiles.py`; `render_glb_preview.py` adds `--view full|face`.
- GLB automation: `tools/verify-master-manifest.mjs`, `tools/validate-master-glb.mjs`; npm validation scripts/check gate.
- Architecture/contracts/setup/team: `MASTER_AVATAR.md`, overview, 3D contract, Blender setup, ownership, handoff.
- Outputs/evidence: static GLB, Morph POC GLB, JSON reports and full/face previews.

## Commands actually executed

```text
git switch -c feat/task-0005-master-stabilization
npm run doctor
blender.exe --version
blender.exe --background --python inspect_environment.py -- --expected-version 5.2.4 --require-mpfb ...
git archive --format=zip ... 5996ee4 blender/master/avatar_master_neutral_candidate.blend
blender.exe <committed-candidate-copy> --background --python stabilize_master.py -- --output blender/master/avatar_master.blend ...
blender.exe <temporary-master-copy> --background --python audit_master_avatar.py -- --baseline TASK-0002-rig-inventory.json ...
blender.exe <temporary-master-copy> --background --python inspect_rig.py -- --expected-version 5.2.4 --expected-fps 30 ...
blender.exe <temporary-master-copy> --background --python export_master_profiles.py -- --profile MASTER_STATIC ...
blender.exe <temporary-technical-copy> --background --python export_master_profiles.py -- --profile MORPH_POC ...
node tools/validate-master-glb.mjs --profile MASTER_STATIC ...
node tools/validate-master-glb.mjs --profile MORPH_POC ...
blender.exe --background --python render_glb_preview.py -- --view full ...
blender.exe --background --python render_glb_preview.py -- --view face ...
npm run check
Get-FileHash ... -Algorithm SHA256
```

Một PowerShell formatting-only command dùng format specifier `R` không hợp lệ và FAIL; chạy lại bằng `ConvertTo-Json -Compress` thành công. Không có asset/test result nào được tạo hoặc thay đổi bởi lần format lỗi.

## Test matrix

| Check | Evidence | Status |
|---|---|---|
| Blender/MPFB environment | 5.2.4 / 2.0.18 initialized | PASS |
| Approved source extraction | Git blob hash exact `2D420…` | PASS |
| Canonical opens/reloads | Blender 5.2.4 audit | PASS |
| Original/user binary preservation | Legacy + technical hashes unchanged; working candidate `BC2F…` untouched | PASS |
| Bone count/hierarchy | 137; matches TASK-0002; hierarchy hash recorded | PASS |
| Mesh/armature bindings | 3/3 meshes, all vertices grouped | PASS |
| Finger chains | 5 × 3 each side | PASS |
| Neutral master state | no actions, pose identity, 30 FPS | PASS |
| Generic identity-transform contract | non-identity rotation remains | FAIL by generic rule; retained/resolved by documented compatibility policy |
| Head/neck controlled deformation | 2/2 tests + exact reset | PASS |
| Jaw/eye structural deformation | 3/3 tests + exact reset | PASS structural |
| Existing Shape Key inventory | 11/11 measured | PASS |
| Production facial Shape Keys | none | NOT YET TESTED |
| Facial visual quality/NMM correctness | no production expressions | NOT YET TESTED |
| `MASTER_STATIC` GLB | structure + Khronos | PASS |
| Static Morph Target POC | target present | PASS |
| Animated Morph Target POC | weights channel present | PASS |
| Bone + Morph in same GLB | 15 rotations + weights channel | PASS |
| Full/face re-import renders | agent visual inspection | PASS agent visual |
| Owner post-promotion manual review | not executed in this task | NOT YET TESTED |
| `npm run check` | typecheck/lint/data/7 tests/build/all asset validators | PASS |
| Production `S001–S006` GLBs/content | remain pending | NOT YET TESTED |

## Evidence and artifact hashes

| Artifact | SHA-256 |
|---|---|
| `TASK-0005-environment.json` | `5A21A677F994228D7D75B89609F009B8809E89EA53CAEA87CECCF88CF6F38E88` |
| `TASK-0005-master-promotion.json` | `24F6AE88A462BF2886AB2E864CAAC574815AB85BB706423C6B73803862FC0E61` |
| `TASK-0005-bone-inventory.json` | `CD58FDFE5BA5B6DAF4956C3B2F30F011E4E39B67575C16B575E5F5ACCB89B247` |
| `TASK-0005-master-facial-audit.json` | `228C5EC9EC95687AB87974C422D99DDD55082EDA65671936226F0C73137B0226` |
| `TASK-0005-master-static-export.json` | `679204F845D7500EE47CABCB954F3A55ACD45F104605549AF032C9957D92AA18` |
| `TASK-0005-master-static-validation.json` | `D1164AAFFDCDFE81460BB3379F6CC47227F77BC6D25F4CFD1B73F288EBC01F59` |
| `TASK-0005-morph-poc-export.json` | `3CA0C486965BC448E4909B441F66D958F641E11BEFBF18450A9FBA2BB279F21C` |
| `TASK-0005-morph-poc-validation.json` | `0A9472C01AFFFDEACCA46B172DA4949839825A83FA53C9962EF5E44563CD9374` |
| `master-static-full.png` | `A03FC697D0E34FAB9E4C70AE9B51C7ECF1FBF3AA87DFAF061AE1A00E7AF3D2E0` |
| `master-static-face.png` | `BE4E9A136D5A6B8D3B0356167985C9C0867B24978553CCD3C6A05F18A1169406` |

## Known issues, limitations and blockers

- Facial production is not ready: no approved expression/viseme targets, blink/brow poses, visible eye/pupil asset, NMM spec or Three.js facial controller.
- Direct deform rig has no animator-friendly control layer; adding one is not automatically justified and must not change canonical hierarchy/export signature.
- Non-identity armature rotation is retained because current pipeline is proven compatible; generic inventory continues reporting it as FAIL by design.
- `MASTER_STATIC`/Morph POC have one Khronos informational unused UV, 0 errors/warnings.
- Garments remain low-detail functional geometry; extreme head/upper-body/facial poses need clipping QA.
- Vite main bundle remains >500 kB warning.
- Git LFS remote auth/quota remains unverified.
- No blocking issue prevents temporary final release as a neutral static/hand-animation foundation; blockers apply to production facial/NMM claims.

## Git branch and commit information

- Branch: `feat/task-0005-master-stabilization`.
- Base: `84837d050f3f874452228cf457d5a2d174748efd`.
- Final commit hash cannot be embedded in the same commit; actual hash is stated in the final Agent response.
- No merge/push. User-owned README/candidate changes remain outside task commit.

## Owner manual acceptance checklist

- [ ] Open `blender/master/avatar_master.blend` in Blender 5.2.4 and confirm no Action assigned.
- [ ] Verify manifest SHA-256 with `npm run verify:master`.
- [ ] Inspect neutral pose/clothing from front, side and back.
- [ ] Confirm non-identity armature rotation is intentionally retained; do not Apply Transform.
- [ ] Pose head/neck/jaw conservatively on a working copy and inspect clipping/weight quality.
- [ ] Review full/face static GLB previews; acknowledge eye/pupil limitation.
- [ ] Confirm animator handoff uses exact canonical commit/hash, not candidate/technical source.

## Next recommended task

TASK-0006 nên là **Facial/NMM Foundation Prototype**, không phải production VSL animation: define facial target naming/acceptance, add visible eye assets compatible với canonical skeleton, prototype blink/brow/jaw/lip targets trên working copy, export bone+Morph clip, add Three.js weight controller/test và obtain visual/content review. Không tạo male/female variants hoặc semantic sign claims trong cùng task.

Không tự động bắt đầu TASK-0006.
